from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy
from bpy.props import StringProperty
from bpy.types import Context, Event, Operator

from rig_utils.core import (
    get_asset_path,
    has_override_library,
    is_asset,
    set_asset_path,
)

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


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

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        set_asset_path(obj, self.latest_path)

        return {"FINISHED"}

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
