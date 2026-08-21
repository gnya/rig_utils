from collections.abc import Callable

import bpy
from bpy.types import Object, PoseBone
from mathutils import Matrix

from .dependencies import calc_depth_by_bone
from .types import CopyBoneMatrix, CopyBoneSpace


# ボーンのトランスフォームを取得する
def get_transform(bone: PoseBone, space: CopyBoneSpace) -> CopyBoneMatrix:
    return [
        list(r)
        for r in bone.id_data.convert_space(
            pose_bone=bone,
            matrix=bone.matrix,
            from_space="POSE",
            to_space=space,
        )
    ]


# ボーンにトランスフォームを設定する
def set_transform(bone: PoseBone, space: CopyBoneSpace, matrix: CopyBoneMatrix):
    bone.matrix = bone.id_data.convert_space(
        pose_bone=bone,
        matrix=Matrix(matrix),
        from_space=space,
        to_space="POSE",
    )


# ロックされたトランスフォームの値を復元する
def restore_locked_transform(bone: PoseBone, matrix_basis: Matrix):
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
def insert_auto_keyframes(obj: Object, bone_names: list[str]):
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


# ボーンのトランスフォームを適用する
def apply_bone_transform(
    obj: Object,
    bone_names: list[str],
    apply: Callable[[PoseBone], None],
):
    bones = obj.pose.bones
    depth_by_bone = calc_depth_by_bone(obj)

    # ある深さに対するボーンの一覧を格納した辞書を計算する
    # ただし、ボーンはbone_dataが存在するもののみ
    bones_by_depth: dict[int, list[str]] = {}

    for bone_name in bone_names:
        if (depth := depth_by_bone.get(bone_name)) is not None:
            bones_by_depth.setdefault(depth, []).append(bone_name)

    # 深さが浅いものから順番にトランスフォームを適用する
    for depth in sorted(bones_by_depth):
        for bone_name in bones_by_depth[depth]:
            bone = bones[bone_name]
            matrix_basis = bone.matrix_basis.copy()

            apply(bone)

            restore_locked_transform(bone, matrix_basis)

        bpy.context.view_layer.update()

    insert_auto_keyframes(obj, bone_names)
