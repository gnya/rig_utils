import re

from bpy.types import Armature, Object, Pose


# 与えられたオブジェクトがアセットかどうかを判別します
def is_asset(obj: Object | None) -> bool:
    if obj is None:
        return False
    elif obj.type not in ["EMPTY", "ARMATURE"]:
        return False

    return re.fullmatch(r"[A-Z]+_(rig|root)", obj.name) is not None


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
        for b in bones:
            if b.name in target_bones:
                for i in range(32):
                    layers[i] |= b.bone.layers[i]

    # target_bonesのボーンを表示、そうでないボーンを非表示にする
    for b in bones:
        if any([(b.bone.layers[i] and layers[i]) for i in range(32)]):
            b.bone.hide = b.name not in target_bones

    for i in range(32):
        armature.layers[i] = layers[i]


# 内部で使用されているボーンかどうかを判別します
def is_internal_bons(bone_name: str):
    splited = bone_name.split("-", 1)

    if len(splited) == 1:
        return False

    return splited[0] in ["DEF", "VIS", "MCH", "ORG"]


# アニメーションが設定されたボーンの一覧を取得します
def get_animated_bones(obj: Object) -> set[str]:
    bone_names = set()

    if obj.animation_data.action is None:
        return bone_names

    for f in obj.animation_data.action.fcurves:
        if f.data_path.startswith('pose.bones["'):
            bone_name = f.data_path.split('"')[1]
            bone_names.add(bone_name)

    return set([n for n in bone_names if not is_internal_bons(n)])


# レストポーズから変更されたボーンの一覧を取得します
def get_modified_bones(obj: Object) -> set[str]:
    bone_names = set()

    for b in obj.pose.bones:
        if not b.matrix_basis.is_identity:
            bone_names.add(b.name)

    return set([n for n in bone_names if not is_internal_bons(n)])
