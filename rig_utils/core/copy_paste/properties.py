from bpy.types import PoseBone
from idprop.types import IDPropertyArray

from .types import CopyBoneProps


# ボーンのカスタムプロパティを取得する
def get_custom_properties(bone: PoseBone) -> CopyBoneProps:
    props: CopyBoneProps = {}

    for key, value in bone.items():
        value_type = type(value).__name__.upper()

        if isinstance(value, IDPropertyArray):
            if value.typecode in ["f", "d"]:
                value_type = "FLOAT_ARRAY"
            elif value.typecode == "i":
                value_type = "INT_ARRAY"
            elif value.typecode == "b":
                value_type = "BOOL_ARRAY"
            else:
                raise TypeError(f"Unsupported IDPropertyArray type: {value.typecode}")

            value = value.to_list()
        elif not isinstance(value, (float, int, bool, str)):
            raise TypeError(f"Unsupported custom property type: {value_type})")

        props[key] = {"value": value, "type": value_type}

    return props


# ボーンにカスタムプロパティを設定する
def set_custom_properties(bone: PoseBone, props: CopyBoneProps):
    for key, prop in props.items():
        if key in bone:
            match prop["type"]:
                case "FLOAT":
                    value = float(prop["value"])
                case "INT":
                    value = int(prop["value"])
                case "BOOL":
                    value = bool(prop["value"])
                case "STR":
                    value = str(prop["value"])
                case "FLOAT_ARRAY":
                    value = [float(v) for v in prop["value"]]
                case "INT_ARRAY":
                    value = [int(v) for v in prop["value"]]
                case "BOOL_ARRAY":
                    value = [bool(v) for v in prop["value"]]
                case _:
                    raise ValueError(
                        f"Unsupported custom property type: {prop['type']}"
                    )
        else:
            raise KeyError(f"Missing custom property: {key}")

        bone[key] = value
