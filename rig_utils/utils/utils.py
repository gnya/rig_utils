from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import bpy
from bpy.types import Context, PoseBone

if TYPE_CHECKING:
    from bpy._typing.rna_enums import EventTypeItems


# 内部で使用されているボーンかどうかを判別します
def is_internal_bones(bone_name: str):
    splited = bone_name.split("-", 1)

    if len(splited) == 1:
        return False

    return splited[0] in ["DEF", "VIS", "MCH", "ORG"]


# 表示状態を考慮してボーンが選択されていているかどうかを返します
def is_selected_bone(bone: PoseBone):
    layers = bone.bone.id_data.layers

    return bone.bone.select and any(
        [(bone.bone.layers[i] and layers[i]) for i in range(32)]
    )


# キーマップを追加します
def register_keymap(
    category: str,
    idname: str,
    type: EventTypeItems,
    shift: bool = False,
    ctrl: bool = False,
    alt: bool = False,
):
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.get(category)

    if km is None:
        km = wm.keyconfigs.addon.keymaps.new(name=category)

    km.keymap_items.new(
        idname,
        type=type,
        value="PRESS",
        shift=shift,
        ctrl=ctrl,
        alt=alt,
    )


# キーマップを削除します
def unregister_keymap(category: str, idname: str):
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.get(category)

    if km is not None:
        km.keymap_items.remove(km.keymap_items.get(idname))

        if len(km.keymap_items) == 0:
            wm.keyconfigs.addon.keymaps.remove(km)


# カーソルの状態を待機中に変更する
@contextmanager
def wait_cursor(context: Context) -> Generator[None, None, None]:
    context.window.cursor_set("WAIT")

    try:
        yield
    finally:
        context.window.cursor_set("DEFAULT")
