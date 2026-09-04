from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Context, Event, Operator

from rig_utils.core import (
    cache_assets_collection,
    cache_assets_path,
    cached_assets_collection,
    cached_assets_path,
    get_asset_path,
    has_override_library,
    is_asset_root,
    load_asset,
    set_asset_path,
)
from rig_utils.utils import wait_cursor

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class OBJECT_OT_rig_utils_add_asset_select(Operator):
    bl_idname = "object.rig_utils_add_asset_select"
    bl_label = "Add Asset"
    bl_description = "Add asset"
    bl_options = {"REGISTER", "UNDO"}

    def _assets_path(self, context: Context) -> list[tuple[str, str, str]]:
        return [(os.path.join(d, f), f, f'"{d}"') for d, f in cached_assets_path()]

    asset_path: EnumProperty(name="Asset Path", items=_assets_path)

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        addon = context.preferences.addons["rig_utils"]
        wm = context.window_manager

        with wait_cursor(context):
            cache_assets_path(addon.preferences.asset_dir)

        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "asset_path", text="Asset Path")

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        bpy.ops.object.rig_utils_add_asset_select_collection(
            "INVOKE_DEFAULT",
            asset_path=self.asset_path,
        )

        return {"FINISHED"}


class OBJECT_OT_rig_utils_add_asset_select_collection(Operator):
    bl_idname = "object.rig_utils_add_asset_select_collection"
    bl_label = "Add Asset"
    bl_description = "Add asset"
    bl_options = {"REGISTER", "UNDO"}

    def _assets_collection(self, context: Context) -> list[tuple[str, str, str]]:
        return [(c, c, "") for c in cached_assets_collection()]

    asset_path: StringProperty(name="Asset Path")

    asset_collection: EnumProperty(name="Asset Collection", items=_assets_collection)

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        wm = context.window_manager

        with wait_cursor(context):
            cache_assets_collection(self.asset_path)

        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "asset_collection", text="Asset Collection")

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        bpy.ops.object.rig_utils_add_asset(
            "INVOKE_DEFAULT",
            asset_path=self.asset_path,
            asset_collection=self.asset_collection,
        )

        return {"FINISHED"}


class OBJECT_OT_rig_utils_add_asset(Operator):
    bl_idname = "object.rig_utils_add_asset"
    bl_label = "Add Asset"
    bl_description = "Add asset"
    bl_options = {"REGISTER", "UNDO"}

    asset_path: StringProperty(name="Asset Path")

    asset_collection: StringProperty(name="Asset Collection")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        wm = context.window_manager

        return wm.invoke_confirm(self, event)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if load_asset(self.asset_path, self.asset_collection) is None:
            return {"CANCELLED"}

        return {"FINISHED"}


class OBJECT_OT_rig_utils_update_asset(Operator):
    bl_idname = "object.rig_utils_update_asset"
    bl_label = "Update Asset"
    bl_description = "Update asset (Empty or Armature)"
    bl_options = {"REGISTER", "UNDO"}

    latest_path: StringProperty(default="")

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.active_object

        return is_asset_root(obj) and has_override_library(obj)

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        dir, current_file, latest_file = get_asset_path(obj)

        if current_file == latest_file:
            self.report({"INFO"}, "This asset is the latest.")

            return {"CANCELLED"}

        wm = context.window_manager
        self.latest_path = bpy.path.relpath(os.path.join(dir, latest_file))

        return wm.invoke_confirm(self, event)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        set_asset_path(obj, self.latest_path)

        return {"FINISHED"}
