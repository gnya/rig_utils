from collections.abc import Callable
from typing import Literal

from bpy.types import Object
from bpy.utils import flip_name
from mathutils import Matrix

from rig_utils.utils import is_internal_bones, is_selected_bone

Axis = Literal["X", "-X", "Y", "-Y", "Z", "-Z"]


def generate_convert_func(
    axis: tuple[Axis, Axis, Axis] = ("X", "Y", "Z")
) -> Callable[[Matrix], Matrix]:
    def convert_func(matrix: Matrix) -> Matrix:
        xyz = ["XYZ".index(a[-1]) for a in axis]
        sign = [1.0 if a[0] != "-" else -1.0 for a in axis]

        P = Matrix(
            [
                [sign[i] if j == i_xyz else 0.0 for j in range(3)]
                for i, i_xyz in enumerate(xyz)
            ]
        ).to_4x4()

        return P @ matrix @ P.inverted()

    return convert_func


LEGACY_MIGRATIONS: dict[str, tuple[str, Callable[[Matrix], Matrix]]] = {
    "root": (
        "CTR_root",
        generate_convert_func(("X", "-Z", "Y")),
    ),
    "torso": (
        "CTR_torso",
        generate_convert_func(("X", "-Z", "Y")),
    ),
    "hips": (
        "CTR_hips",
        generate_convert_func(("X", "-Z", "Y")),
    ),
    "chest": (
        "CTR_chest",
        generate_convert_func(("X", "-Z", "Y")),
    ),
    "shoulder.L": (
        "CTR_shoulder.L",
        generate_convert_func(),
    ),
    "neck": (
        "CTR_neck",
        generate_convert_func(),
    ),
    "head": (
        "CTR_head",
        generate_convert_func(),
    ),
    "thigh_fk.L": (
        "CTR_leg_fk_thigh.L",
        generate_convert_func(),
    ),
    "shin_fk.L": (
        "CTR_leg_fk_shin.L",
        generate_convert_func(),
    ),
    "foot_fk.L": (
        "CTR_foot_fk.L",
        generate_convert_func(),
    ),
    "toe_fk.L": (
        "CTR_toe_fk.L",
        generate_convert_func(),
    ),
    "thigh_ik_target.L": (
        "CTR_leg_ik_pole.L",
        generate_convert_func(("X", "-Y", "-Z")),
    ),
    "foot_ik.L": (
        "CTR_foot_ik.L",
        generate_convert_func(),
    ),
    "foot_spin_ik.L": (
        "CTR_foot_spin_ik.L",
        generate_convert_func(("-X", "-Y", "Z")),
    ),
    "toe_ik.L": (
        "CTR_toe_ik.L",
        generate_convert_func(),
    ),
    "foot_heel_ik.L": (
        "CTR_heel_ik.L",
        generate_convert_func(("-X", "-Y", "-Z")),
    ),
    "upper_arm_fk.L": (
        "CTR_arm_fk_upperarm.L",
        generate_convert_func(),
    ),
    "forearm_fk.L": (
        "CTR_arm_fk_forearm.L",
        generate_convert_func(),
    ),
    "hand_fk.L": (
        "CTR_hand_fk.L",
        generate_convert_func(),
    ),
    "upper_arm_ik_target.L": (
        "CTR_arm_ik_pole.L",
        generate_convert_func(("-X", "-Y", "-Z")),
    ),
    "hand_ik.L": (
        "CTR_hand_ik.L",
        generate_convert_func(),
    ),
    "f_index.01_master.L": (
        "CTR_finger_index_fk.L",
        generate_convert_func(("-X", "Y", "-Z")),
    ),
    "f_middle.01_master.L": (
        "CTR_finger_middle_fk.L",
        generate_convert_func(("-X", "Y", "-Z")),
    ),
    "f_ring.01_master.L": (
        "CTR_finger_ring_fk.L",
        generate_convert_func(("-X", "Y", "-Z")),
    ),
    "f_pinky.01_master.L": (
        "CTR_finger_pinky_fk.L",
        generate_convert_func(("-X", "Y", "-Z")),
    ),
    "thumb.01_master.L": (
        "CTR_thumb_fk.L",
        generate_convert_func(("-X", "Y", "-Z")),
    ),
    "palm.L": (
        "CTR_palm.L",
        generate_convert_func(("-X", "Y", "-Z")),
    ),
}


def convert_legacy_transform(src: Object, dst: Object):
    for dst_bone in dst.pose.bones:
        if is_selected_bone(dst_bone) and not is_internal_bones(dst_bone.name):
            if dst_bone.name in LEGACY_MIGRATIONS:
                src_bone_name, convert = LEGACY_MIGRATIONS[dst_bone.name]
            elif flip_name(dst_bone.name) in LEGACY_MIGRATIONS:
                src_bone_name, convert = LEGACY_MIGRATIONS[flip_name(dst_bone.name)]
                src_bone_name = flip_name(src_bone_name)
            else:
                src_bone_name, convert = "", None

            if convert is not None:
                src_bone = src.pose.bones[src_bone_name]

                matrix = src.convert_space(
                    pose_bone=src_bone,
                    matrix=src_bone.matrix,
                    from_space="POSE",
                    to_space="LOCAL",
                )
                dst_bone.matrix = dst.convert_space(
                    pose_bone=dst_bone,
                    matrix=convert(matrix),
                    from_space="LOCAL",
                    to_space="POSE",
                )
