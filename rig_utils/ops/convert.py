from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.props import IntProperty
from bpy.types import Context, Event, Operator

from rig_utils.core import convert_legacy_animation, convert_legacy_transform
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


class POSE_OT_rig_utils_convert_legacy_animation(Operator):
    bl_idname = "pose.rig_utils_convert_legacy_animation"
    bl_label = "Convert Legacy Animation"
    bl_description = "Convert legacy animation"
    bl_options = {"REGISTER", "UNDO"}

    frame_start: IntProperty(
        name="Start Frame",
        default=0,
        min=0,
    )

    frame_end: IntProperty(
        name="End Frame",
        default=1,
        min=1,
    )

    step: IntProperty(
        name="Frame Step",
        default=2,
        min=1,
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        return (
            context.mode == "POSE"
            and len(context.selected_pose_bones_from_active_object) > 0
        )

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        wm = context.window_manager

        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end

        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        layout = self.layout

        layout.use_property_split = True
        layout.prop(self, "frame_start", text="Start Frame")
        layout.prop(self, "frame_end", text="End Frame")
        layout.prop(self, "step", text="Frame Step")

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        dst_obj = context.active_object

        if dst_obj is None:
            return {"CANCELLED"}

        settings = get_settings(context.scene)
        src_obj = settings.convert_legacy_src

        if src_obj is None:
            return {"CANCELLED"}

        wm = context.window_manager

        wm.progress_begin(self.frame_start, self.frame_end)

        for frame in convert_legacy_animation(
            context,
            src_obj,
            dst_obj,
            self.frame_start,
            self.frame_end,
            self.step,
        ):
            wm.progress_update(frame)

        wm.progress_end()

        return {"FINISHED"}
