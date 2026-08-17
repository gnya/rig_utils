import json
from json.decoder import JSONDecodeError

import bpy
from bpy.types import Object

from rig_utils.utils import is_internal_bones

from .dependencies import calc_dependencies_by_bone
from .properties import get_custom_properties, set_custom_properties
from .transform import (
    get_transform,
    insert_auto_keyframes,
    restore_locked_transform,
    set_transform,
)
from .types import CopyBoneData, CopyBoneSpace


# ボーンのトランスフォームをワールド座標系でコピーする
def copy_bone_transform(
    obj: Object,
    space: CopyBoneSpace = "WORLD",
):
    bone_data: CopyBoneData = {}
    bones = obj.pose.bones

    for bone in bones:
        if bone.bone.select and not is_internal_bones(bone.name):
            bone_data[bone.name] = {
                "matrix": get_transform(bone, space),
                "props": get_custom_properties(bone),
            }

    data = {"space": space, "bone_data": bone_data}
    wm = bpy.context.window_manager
    wm.clipboard = json.dumps(data)


# あるボーンに対する深さを格納した辞書を計算する
def _calc_depth_by_bone(obj: Object) -> dict[str, int]:
    dependencies_by_bone = calc_dependencies_by_bone(obj)
    depth_by_bone: dict[str, int] = {}

    # みているボーンが依存しているボーンの一覧を計算する
    def _calc_depth(dependencies: set[str]) -> int | None:
        if len(dependencies) == 0:
            # ボーンが何にも依存していないならdepthは0
            return 0

        max_depth = 0

        # みているボーンが依存しているボーンが依存しているボーンをみて一番深いdepthを探す
        for dependency in dependencies:
            if dependency not in depth_by_bone:
                return None

            max_depth = max(max_depth, depth_by_bone[dependency])

        # dependencyがすべてdepth_by_boneに含まれるならmax_depth+1がボーンのdepthとなる
        return max_depth + 1

    while dependencies_by_bone:
        resolved = False

        for bone_name, dependencies in list(dependencies_by_bone.items()):
            if (depth := _calc_depth(dependencies)) is not None:
                depth_by_bone[bone_name] = depth
                dependencies_by_bone.pop(bone_name)
                resolved = True

        if not resolved:
            # 依存関係が循環している場合は例外を送出する
            raise RuntimeError(
                f"Dependency cycle detected: {len(dependencies_by_bone)}"
            )

    return depth_by_bone


# ボーンのトランスフォームをワールド座標系でペーストする
def paste_bone_transform(obj: Object) -> bool:
    try:
        wm = bpy.context.window_manager
        data = json.loads(wm.clipboard)
    except JSONDecodeError:
        return False

    space: CopyBoneSpace = data["space"]
    bone_data: CopyBoneData = data["bone_data"]
    bones = obj.pose.bones
    depth_by_bone = _calc_depth_by_bone(obj)

    # ある深さに対するボーンの一覧を格納した辞書を計算する
    # ただし、ボーンはbone_dataが存在するもののみ
    bones_by_depth: dict[int, list[str]] = {}

    for bone_name in bone_data:
        if (depth := depth_by_bone.get(bone_name)) is not None:
            bones_by_depth.setdefault(depth, []).append(bone_name)

    # 深さが浅いものから順番にトランスフォームを適用する
    for depth in sorted(bones_by_depth):
        for bone_name in bones_by_depth[depth]:
            bone = bones[bone_name]
            matrix_basis = bone.matrix_basis.copy()

            set_transform(bone, space, bone_data[bone_name]["matrix"])
            set_custom_properties(bone, bone_data[bone_name]["props"])

            restore_locked_transform(bone, matrix_basis)

        bpy.context.view_layer.update()

    insert_auto_keyframes(obj, bone_data.keys())

    return True
