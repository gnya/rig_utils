from bpy.types import Object, PoseBone
from bpy.utils import flip_name
from mathutils import Matrix

from rig_utils.utils import is_internal_bones, is_selected_bone

from .transform import apply_bone_transform


def convert_transform(src: PoseBone, dst: PoseBone):
    src_local = src.matrix_basis
    src_rest = src.bone.matrix_local

    # 旧ボーンのローカル行列をポーズ座標系に変換する
    src_parent_pose = src.parent.matrix if src.parent else Matrix.Identity(4)
    src_parent_rest = src.parent.bone.matrix_local if src.parent else Matrix.Identity(4)
    src_pose = src.bone.convert_local_to_pose(
        src_local,
        src_rest,
        parent_matrix=src_parent_pose,
        parent_matrix_local=src_parent_rest,
    )

    # レスト時の行列との差分を求める
    rot_delta = src_pose.to_3x3() @ src_rest.to_3x3().inverted()
    loc_delta = src_pose.translation - src_rest.translation

    # 新ボーンのポーズ行列をレスト時の行列に差分を加えたものから求める
    dst_rest = dst.bone.matrix_local
    dst_pose = (rot_delta @ dst_rest.to_3x3()).to_4x4()
    dst_pose.translation = loc_delta + dst_rest.translation

    # 新ボーンのポーズ行列をローカル座標系に変換する
    dst_parent_pose = dst.parent.matrix if dst.parent else Matrix.Identity(4)
    dst_parent_rest = dst.parent.bone.matrix_local if dst.parent else Matrix.Identity(4)
    dst.matrix_basis = dst.bone.convert_local_to_pose(
        dst_pose,
        dst_rest,
        parent_matrix=dst_parent_pose,
        parent_matrix_local=dst_parent_rest,
        invert=True,
    )


LEGACY_MAPPING: dict[str, str] = {
    "root": "CTR_root",
    "torso": "CTR_torso",
    "hips": "CTR_hips",
    "chest": "CTR_chest",
    "shoulder.L": "CTR_shoulder.L",
    "neck": "CTR_neck",
    "head": "CTR_head",
    "thigh_fk.L": "CTR_leg_fk_thigh.L",
    "shin_fk.L": "CTR_leg_fk_shin.L",
    "foot_fk.L": "CTR_foot_fk.L",
    "toe_fk.L": "CTR_toe_fk.L",
    "thigh_ik_target.L": "CTR_leg_ik_pole.L",
    "foot_ik.L": "CTR_foot_ik.L",
    "foot_spin_ik.L": "CTR_foot_spin_ik.L",
    "toe_ik.L": "CTR_toe_ik.L",
    "foot_heel_ik.L": "CTR_heel_ik.L",
    "upper_arm_fk.L": "CTR_arm_fk_upperarm.L",
    "forearm_fk.L": "CTR_arm_fk_forearm.L",
    "hand_fk.L": "CTR_hand_fk.L",
    "upper_arm_ik_target.L": "CTR_arm_ik_pole.L",
    "hand_ik.L": "CTR_hand_ik.L",
    "f_index.01_master.L": "CTR_finger_index_fk.L",
    "f_middle.01_master.L": "CTR_finger_middle_fk.L",
    "f_ring.01_master.L": "CTR_finger_ring_fk.L",
    "f_pinky.01_master.L": "CTR_finger_pinky_fk.L",
    "thumb.01_master.L": "CTR_thumb_fk.L",
    "palm.L": "CTR_palm.L",
}


def legacy_mapping(key: str) -> str:
    if key in LEGACY_MAPPING:
        return LEGACY_MAPPING[key]
    elif flip_name(key) in LEGACY_MAPPING:
        return flip_name(LEGACY_MAPPING[flip_name(key)])
    else:
        return ""


def convert_legacy_transform(src: Object, dst: Object):
    bone_names = [
        b.name
        for b in dst.pose.bones
        if is_selected_bone(b) and not is_internal_bones(b.name)
    ]

    def _apply(dst_bone: PoseBone):
        src_bone = src.pose.bones.get(legacy_mapping(dst_bone.name))

        if src_bone is not None:
            convert_transform(src_bone, dst_bone)

    apply_bone_transform(dst, bone_names, _apply)
