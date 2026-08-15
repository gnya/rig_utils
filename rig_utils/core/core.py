import os
import re

import bpy
from bpy.types import Armature, Collection, Object, Pose


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


# 内部で使用されているボーンかどうかを判別します
def is_internal_bons(bone_name: str):
    splited = bone_name.split("-", 1)

    if len(splited) == 1:
        return False

    return splited[0] in ["DEF", "VIS", "MCH", "ORG"]


# アニメーションが設定されたボーンの一覧を取得します
def get_animated_bones(obj: Object) -> set[str]:
    if obj.animation_data is None or obj.animation_data.action is None:
        return set()

    bone_names: set[str] = set()

    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path.startswith('pose.bones["'):
            bone_name = fcurve.data_path.split('"')[1]
            bone_names.add(bone_name)

    return set([n for n in bone_names if not is_internal_bons(n)])


# レストポーズから変更されたボーンの一覧を取得します
def get_modified_bones(obj: Object) -> set[str]:
    bone_names: set[str] = set()

    for bone in obj.pose.bones:
        if not bone.matrix_basis.is_identity:
            bone_names.add(bone.name)

    return set([n for n in bone_names if not is_internal_bons(n)])


# ディレクトリ内の最新のアセットを取得します
def _get_asset_file(files: list[str]) -> str | None:
    asset_files: list[tuple[str, int]] = []

    for file in files:
        if match := re.fullmatch(r"[A-Z]+_v(\d+).*\.blend", file):
            asset_files.append((file, int(match.group(1))))

    if len(asset_files) == 0:
        return None

    asset_files = sorted(asset_files, key=lambda f: f[1])

    return asset_files[-1][0]


# アセットのパスの一覧を取得します
def get_assets_path(dir: str) -> list[tuple[str, str]]:
    assets: list[tuple[str, str]] = []

    for dir, _, files in os.walk(dir):
        if os.path.basename(dir).startswith(("@", ".", "_")):
            continue

        file = _get_asset_file(files)

        if file is None:
            continue

        assets.append((dir, file))

    return assets


# アセットのコレクションの一覧を取得します
def get_asset_collections(path: str) -> list[str]:
    collections: list[str] = []

    with bpy.data.libraries.load(path, link=False) as (data_from, _):
        for collection in data_from.collections:
            if re.fullmatch(r"[A-Z]+", collection):
                collections.append(collection)

    return collections


# アセットを読み込みます
def load_asset(path: str, collection: str) -> Collection | None:
    with bpy.data.libraries.load(path, link=True) as (data_from, data_to):
        if collection not in data_from.collections:
            return None

        data_to.collections = [collection]

    link: Collection = data_to.collections[0]  # type: ignore
    override = link.override_hierarchy_create(
        bpy.context.scene,
        bpy.context.view_layer,
        reference=link,
        do_fully_editable=True,
    )

    return override


# 外部のアセットに依存しているかを判別します
def has_override_library(obj: Object | None) -> bool:
    return obj is not None and obj.override_library is not None


# アセットのパスを取得します
def get_asset_path(obj: Object) -> tuple[str, str, str]:
    lib = obj.override_library.reference.library
    current_path = bpy.path.abspath(lib.filepath)
    current_dir = os.path.dirname(current_path)
    current_file = os.path.basename(current_path)
    latest_file = _get_asset_file(os.listdir(current_dir))

    if latest_file is None:
        raise RuntimeError("Latest asset file doesn't exist.")

    return (current_dir, current_file, latest_file)


# アセットを指定されたパスで再読込します
def set_asset_path(obj: Object, path: str):
    lib = obj.override_library.reference.library
    lib.filepath = path
    lib.reload()
