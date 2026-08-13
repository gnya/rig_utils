from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Context, Event, Operator

from rig_utils.core import (
    get_asset_collections,
    get_asset_path,
    get_assets_path,
    has_override_library,
    is_asset,
    load_asset,
    set_asset_path,
)

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

_assets_path_cache: list[tuple[str, str, str]] = []
_asset_collections_cache: list[tuple[str, str, str]] = []


class OBJECT_OT_rig_utils_add_asset_select(Operator):
    bl_idname = "object.rig_utils_add_asset_select"
    bl_label = "Add Asset"
    bl_description = "Add asset"
    bl_options = {"REGISTER", "UNDO"}

    def _assets_path(self, context: Context) -> list[tuple[str, str, str]]:
        return _assets_path_cache

    asset_path: EnumProperty(name="Asset Path", items=_assets_path)

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        dir = "D:\\01 gnya\\12 FRENZ 2024\\asset"

        global _assets_path_cache
        _assets_path_cache = []

        for dir, file in get_assets_path(dir):
            path = os.path.join(dir, file)
            _assets_path_cache.append((path, file, f'"{path}"'))

        wm = context.window_manager

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
        return _asset_collections_cache

    asset_path: StringProperty(name="Asset Path")

    asset_collection: EnumProperty(name="Asset Collection", items=_assets_collection)

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        global _asset_collections_cache
        _asset_collections_cache = []

        for collection in get_asset_collections(self.asset_path):
            _asset_collections_cache.append((collection, collection, ""))

        wm = context.window_manager

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

        return is_asset(obj) and has_override_library(obj)

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
