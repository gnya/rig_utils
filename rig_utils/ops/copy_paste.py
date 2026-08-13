from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Operator

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class POSE_OT_rig_utils_copy_bone_transform(Operator):
    bl_idname = "pose.rig_utils_copy_bone_transform"
    bl_label = "Copy Bone Transform"
    bl_description = "Copy bone transform (World Space)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "POSE"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        return super().execute(context)


class POSE_OT_rig_utils_paste_bone_transform(Operator):
    bl_idname = "pose.rig_utils_paste_bone_transform"
    bl_label = "Paste Bone Transform"
    bl_description = "Paste bone transform (World Space)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "POSE"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        return super().execute(context)
