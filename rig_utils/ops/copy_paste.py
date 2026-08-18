from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Operator

from rig_utils.core import copy_bone_transform, paste_bone_transform
from rig_utils.props import get_settings
from rig_utils.utils import register_keymap, unregister_keymap

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class POSE_OT_rig_utils_copy_bone_transform(Operator):
    bl_idname = "pose.rig_utils_copy_bone_transform"
    bl_label = "Copy Bone Transform"
    bl_description = "Copy bone transform"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "POSE"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        settings = get_settings(context.scene)

        copy_bone_transform(obj, settings.copy_transform_space)

        return {"FINISHED"}

    @staticmethod
    def register():
        register_keymap(
            "Pose",
            POSE_OT_rig_utils_copy_bone_transform.bl_idname,
            type="C",
            shift=True,
            alt=True,
        )

    @staticmethod
    def unregister():
        unregister_keymap(
            "Pose",
            POSE_OT_rig_utils_copy_bone_transform.bl_idname,
        )


class POSE_OT_rig_utils_paste_bone_transform(Operator):
    bl_idname = "pose.rig_utils_paste_bone_transform"
    bl_label = "Paste Bone Transform"
    bl_description = "Paste bone transform"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "POSE"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None:
            return {"CANCELLED"}

        if not paste_bone_transform(obj):
            return {"CANCELLED"}

        return {"FINISHED"}

    @staticmethod
    def register():
        register_keymap(
            "Pose",
            POSE_OT_rig_utils_paste_bone_transform.bl_idname,
            type="V",
            shift=True,
            alt=True,
        )

    @staticmethod
    def unregister():
        unregister_keymap(
            "Pose",
            POSE_OT_rig_utils_paste_bone_transform.bl_idname,
        )
