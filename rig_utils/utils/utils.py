from __future__ import annotations

import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from bpy.types import Context, PoseBone

if TYPE_CHECKING:
    from bpy._typing.rna_enums import EventTypeItems


# 内部で使用されているボーンかどうかを判別します
def is_internal_bones(bone_name: str):
    splited = re.split(r"[-_]", bone_name)

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
    context: Context,
    category: str,
    idname: str,
    type: EventTypeItems,
    shift: bool = False,
    ctrl: bool = False,
    alt: bool = False,
):
    wm = context.window_manager
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
def unregister_keymap(context: Context, category: str, idname: str):
    wm = context.window_manager
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


# ボーンのトランスフォームにキーフレームを打つ
def insert_transform_keyframe(bone: PoseBone):
    bone.keyframe_insert(data_path="location", group=bone.name)

    if bone.rotation_mode == "QUATERNION":
        bone.keyframe_insert(data_path="rotation_quaternion", group=bone.name)
    elif bone.rotation_mode == "AXIS_ANGLE":
        bone.keyframe_insert(data_path="rotation_axis_angle", group=bone.name)
    else:
        bone.keyframe_insert(data_path="rotation_euler", group=bone.name)

    bone.keyframe_insert(data_path="scale", group=bone.name)
