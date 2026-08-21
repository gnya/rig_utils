import json
from json.decoder import JSONDecodeError

import bpy
from bpy.types import Object, PoseBone

from rig_utils.utils import is_internal_bones, is_selected_bone

from .transform import (
    CopyBoneData,
    CopyBoneSpace,
    apply_bone_transform,
    get_custom_properties,
    get_transform,
    set_custom_properties,
    set_transform,
)


# ボーンのトランスフォームをコピーする
def copy_bone_transform(
    obj: Object,
    space: CopyBoneSpace = "WORLD",
):
    bone_data: CopyBoneData = {}
    bones = obj.pose.bones

    for bone in bones:
        if is_selected_bone(bone) and not is_internal_bones(bone.name):
            bone_data[bone.name] = {
                "matrix": get_transform(bone, space),
                "props": get_custom_properties(bone),
            }

    data = {"space": space, "bone_data": bone_data}
    wm = bpy.context.window_manager
    wm.clipboard = json.dumps(data)


# ボーンのトランスフォームをペーストする
def paste_bone_transform(obj: Object) -> bool:
    try:
        wm = bpy.context.window_manager
        data = json.loads(wm.clipboard)
    except JSONDecodeError:
        return False

    space: CopyBoneSpace = data["space"]
    bone_data: CopyBoneData = data["bone_data"]

    def _apply(bone: PoseBone):
        set_transform(bone, space, bone_data[bone.name]["matrix"])
        set_custom_properties(bone, bone_data[bone.name]["props"])

    apply_bone_transform(obj, bone_data.keys(), _apply)

    return True
