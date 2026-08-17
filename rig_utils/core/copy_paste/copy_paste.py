import json
from json.decoder import JSONDecodeError

import bpy
from bpy.types import Object, PoseBone
from mathutils import Matrix

from rig_utils.utils import is_internal_bones

from .dependencies import calc_dependencies_by_bone


# ボーンのトランスフォームをワールド座標系でコピーする
def copy_bone_transform(obj: Object):
    matrices: dict[str, list[list[float]]] = {}
    bones = obj.pose.bones

    for bone in bones:
        if bone.bone.select and not is_internal_bones(bone.name):
            matrix = obj.convert_space(
                pose_bone=bone,
                matrix=bone.matrix,
                from_space="POSE",
                to_space="WORLD",
            )
            matrices[bone.name] = [list(r) for r in matrix.row]

    wm = bpy.context.window_manager
    wm.clipboard = json.dumps(matrices)


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
                f"Dependency cycle detected. : {len(dependencies_by_bone)}"
            )

    return depth_by_bone


# ロックされたトランスフォームの値を復元する
def _restore_locked_transform(bone: PoseBone, matrix_basis: Matrix):
    translation, quaternion, scale = matrix_basis.decompose()

    for i, locked in enumerate(bone.lock_location):
        if locked:
            bone.location[i] = translation[i]

    if bone.rotation_mode == "QUATERNION":
        if not bone.lock_rotations_4d and bone.lock_rotation_w:
            bone.rotation_quaternion[0] = quaternion[0]

        for i, locked in enumerate(bone.lock_rotation):
            if locked:
                bone.rotation_quaternion[i + 1] = quaternion[i + 1]
    elif bone.rotation_mode == "AXIS_ANGLE":
        if not bone.lock_rotations_4d and bone.lock_rotation_w:
            bone.rotation_axis_angle[0] = quaternion.angle

        for i, locked in enumerate(bone.lock_rotation):
            if locked:
                bone.rotation_axis_angle[i + 1] = quaternion.axis[i]
    else:
        euler = quaternion.to_euler(bone.rotation_mode)

        for i, locked in enumerate(bone.lock_rotation):
            if locked:
                bone.rotation_euler[i] = euler[i]

    for i, locked in enumerate(bone.lock_scale):
        if locked:
            bone.scale[i] = scale[i]


# 自動キーイングを利用している場合には自動でキーを打つ
def _insert_auto_keyframes(obj: Object, bone_names: list[str]):
    bones = obj.pose.bones

    if bpy.context.tool_settings.use_keyframe_insert_auto:
        match bpy.context.tool_settings.auto_keying_mode:
            case "ADD_REPLACE_KEYS":
                options = set()
            case "REPLACE_KEYS":
                options = {"INSERTKEY_REPLACE"}

        for bone_name in bone_names:
            if (bone := bones.get(bone_name)) is not None:
                bone.keyframe_insert("location", group=bone.name, options=options)

                if bone.rotation_mode == "QUATERNION":
                    bone.keyframe_insert(
                        "rotation_quaternion", group=bone.name, options=options
                    )
                else:
                    bone.keyframe_insert(
                        "rotation_euler", group=bone.name, options=options
                    )

                bone.keyframe_insert("scale", group=bone.name, options=options)


# ボーンのトランスフォームをワールド座標系でペーストする
def paste_bone_transform(obj: Object) -> bool:
    try:
        wm = bpy.context.window_manager
        matrices: dict[str, list[list[float]]] = json.loads(wm.clipboard)
    except JSONDecodeError:
        return False

    bones = obj.pose.bones
    depth_by_bone = _calc_depth_by_bone(obj)

    # ある深さに対するボーンの一覧を格納した辞書を計算する
    # ただし、ボーンはmatricesに存在するもののみ
    bones_by_depth: dict[int, list[str]] = {}

    for bone_name in matrices:
        if (depth := depth_by_bone.get(bone_name)) is not None:
            bones_by_depth.setdefault(depth, []).append(bone_name)

    # 深さが浅いものから順番にトランスフォームを適用する
    for depth in sorted(bones_by_depth):
        for bone_name in bones_by_depth[depth]:
            bone = bones[bone_name]
            matrix_basis = bone.matrix_basis.copy()

            bone.matrix = obj.convert_space(
                pose_bone=bone,
                matrix=Matrix(matrices[bone_name]),
                from_space="WORLD",
                to_space="POSE",
            )

            _restore_locked_transform(bone, matrix_basis)

        bpy.context.view_layer.update()

    _insert_auto_keyframes(obj, matrices.keys())

    return True
