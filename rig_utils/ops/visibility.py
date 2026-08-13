from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.props import BoolProperty
from bpy.types import Context, Event, Operator

from rig_utils.core import (
    get_animated_bones,
    get_modified_bones,
    show_only_bones,
)

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class POSE_OT_rig_utils_show_modified_bones(Operator):
    bl_idname = "pose.rig_utils_show_modified_bones"
    bl_label = "Show Modified Bones"
    bl_description = "Show modified bones\n* Shift to show all bones"
    bl_options = {"REGISTER", "UNDO"}

    include_hidden: BoolProperty(default=False)

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "POSE"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None or obj.data is None:
            return {"CANCELLED"}

        target_bones = get_modified_bones(obj)

        show_only_bones(target_bones, obj.pose, obj.data, self.include_hidden)

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.include_hidden = event.shift

        return self.execute(context)


class POSE_OT_rig_utils_show_animated_bones(Operator):
    bl_idname = "pose.rig_utils_show_animated_bones"
    bl_label = "Show Animated Bones"
    bl_description = "Show animated bones\n* Shift to show all bones"
    bl_options = {"REGISTER", "UNDO"}

    include_hidden: BoolProperty(default=False)

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "POSE"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None or obj.data is None:
            return {"CANCELLED"}

        target_bones = get_animated_bones(obj)

        show_only_bones(target_bones, obj.pose, obj.data, self.include_hidden)

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.include_hidden = event.shift

        return self.execute(context)
