import os
import re

import bpy
from bpy.types import Collection, Object

_assets_path_cache: list[tuple[str, str]] = []
_assets_collection_cache: list[str] = []


# 与えられたオブジェクトがアセットかどうかを判別します
def is_asset(obj: Object | None) -> bool:
    if obj is None:
        return False
    elif obj.type not in ["EMPTY", "ARMATURE"]:
        return False

    return re.fullmatch(r"[A-Z]+_(rig|root)", obj.name) is not None


# ディレクトリ内の最新のアセットを取得します
def _latest_asset_file(files: list[str]) -> str | None:
    asset_files: list[tuple[str, int]] = []

    for file in files:
        if match := re.fullmatch(r"[A-Z]+_v(\d+).*\.blend", file):
            asset_files.append((file, int(match.group(1))))

    if len(asset_files) == 0:
        return None

    asset_files = sorted(asset_files, key=lambda f: f[1])

    return asset_files[-1][0]


# アセットのパスの一覧を取得します
def _load_assets_path(dir: str) -> list[tuple[str, str]]:
    assets: list[tuple[str, str]] = []

    for dir, _, files in os.walk(dir):
        if not os.path.basename(dir).startswith(("@", ".", "_")):
            if (file := _latest_asset_file(files)) is not None:
                assets.append((dir, file))

    return assets


# アセットのパスの一覧をキャッシュします
def cache_assets_path(dir: str):
    global _assets_path_cache
    _assets_path_cache = _load_assets_path(dir)


# アセットのパスの一覧のキャッシュを取得します
def cached_assets_path() -> list[tuple[str, str]]:
    return _assets_path_cache


# アセットのコレクションの一覧を取得します
def _load_assets_collection(path: str) -> list[str]:
    collections: list[str] = []

    with bpy.data.libraries.load(path, link=False) as (data_from, _):
        for collection in data_from.collections:
            if re.fullmatch(r"[A-Z]+", collection):
                collections.append(collection)

    return collections


# アセットのコレクションの一覧をキャッシュします
def cache_assets_collection(path: str):
    global _assets_collection_cache
    _assets_collection_cache = _load_assets_collection(path)


# アセットのコレクションの一覧のキャッシュを取得します
def cached_assets_collection() -> list[str]:
    return _assets_collection_cache


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
    latest_file = _latest_asset_file(os.listdir(current_dir))

    if latest_file is None:
        raise FileNotFoundError("Latest asset file doesn't exist")

    return (current_dir, current_file, latest_file)


# アセットを指定されたパスで再読込します
def set_asset_path(obj: Object, path: str):
    lib = obj.override_library.reference.library
    lib.filepath = path
    lib.reload()
