from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Operator

from rig_utils.core import add_empty_at_bones

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class POSE_OT_rig_utils_add_empty_at_bones(Operator):
    bl_idname = "pose.rig_utils_add_empty_at_bones"
    bl_label = "Add Empty at Bones"
    bl_description = "Add empty at bones"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return (
            context.mode == "POSE"
            and len(context.selected_pose_bones_from_active_object) > 0
        )

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        add_empty_at_bones(obj)

        return {"FINISHED"}
