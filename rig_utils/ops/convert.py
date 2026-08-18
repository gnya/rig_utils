from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Operator

from rig_utils.core import convert_legacy_transform
from rig_utils.props import get_settings

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class POSE_OT_rig_utils_convert_legacy_transform(Operator):
    bl_idname = "pose.rig_utils_convert_legacy_transform"
    bl_label = "Convert Legacy Transform"
    bl_description = "Convert legacy transform"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return (
            context.mode == "POSE"
            and len(context.selected_pose_bones_from_active_object) > 0
        )

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        dst_obj = context.active_object

        if dst_obj is None:
            return {"CANCELLED"}

        settings = get_settings(context.scene)
        src_obj = settings.convert_legacy_src

        if src_obj is None:
            return {"CANCELLED"}

        convert_legacy_transform(src_obj, dst_obj)

        return {"FINISHED"}
