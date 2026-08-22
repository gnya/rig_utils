from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Operator

from rig_utils.core import add_step_modifier, remove_step_modifier
from rig_utils.props import get_settings

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class OBJECT_OT_rig_utils_add_step_modifier(Operator):
    bl_idname = "object.rig_utils_add_step_modifier"
    bl_label = "Add Step Modifier"
    bl_description = "Add step modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.active_object is not None

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        settings = get_settings(context.scene)

        add_step_modifier(
            obj,
            settings.channel_frame_step,
            settings.channel_frame_offset,
        )

        return {"FINISHED"}


class OBJECT_OT_rig_utils_remove_step_modifier(Operator):
    bl_idname = "object.rig_utils_remove_step_modifier"
    bl_label = "Remove Step Modifier"
    bl_description = "Remove step modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.active_object is not None

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        remove_step_modifier(obj)

        return {"FINISHED"}
