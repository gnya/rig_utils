from bpy.types import Armature, Object, Pose
from idprop.types import IDPropertyGroup

from rig_utils.utils import is_internal_bones


# 指定されたボーンをすべて表示してそれ以外を非表示にします
def show_only_bones(
    target_bones: set[str],
    pose: Pose,
    armature: Armature,
    include_hidden: bool = False,
):
    bones = pose.bones
    layers = armature.layers

    if include_hidden:
        for bone in bones:
            if bone.name in target_bones:
                for i in range(32):
                    layers[i] |= bone.bone.layers[i]

    # target_bonesのボーンを表示、そうでないボーンを非表示にする
    for bone in bones:
        if any([(bone.bone.layers[i] and layers[i]) for i in range(32)]):
            bone.bone.hide = bone.name not in target_bones

    for i in range(32):
        armature.layers[i] = layers[i]


# アニメーションが設定されたボーンの一覧を取得します
def get_animated_bones(obj: Object) -> set[str]:
    if obj.animation_data is None or obj.animation_data.action is None:
        return set()

    bone_names: set[str] = set()

    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path.startswith('pose.bones["'):
            bone_name = fcurve.data_path.split('"')[1]
            bone_names.add(bone_name)

    return set([n for n in bone_names if not is_internal_bones(n)])


# レストポーズから変更されたボーンの一覧を取得します
def get_modified_bones(obj: Object) -> set[str]:
    bone_names: set[str] = set()

    for bone in obj.pose.bones:
        if not bone.matrix_basis.is_identity:
            bone_names.add(bone.name)

        for key, value in bone.items():
            if not isinstance(value, IDPropertyGroup):
                prop_ui = bone.id_properties_ui(key)

                if value != prop_ui.as_dict().get("default"):
                    bone_names.add(bone.name)

    return set([n for n in bone_names if not is_internal_bones(n)])


# オーバーライドされたボーンの一覧を取得します（マテリアルオーバーライド利用時限定）
def get_overrided_bones(obj: Object) -> set[str]:
    if obj.override_library is None:
        return set()

    bone_names: set[str] = set()

    for prop in obj.override_library.properties:
        if prop.rna_path.startswith('pose.bones["'):
            bone_name = prop.rna_path.split('"')[1]
            bone_names.add(bone_name)

    return set([n for n in bone_names if not is_internal_bones(n)])
