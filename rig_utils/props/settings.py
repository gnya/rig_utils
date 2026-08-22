from __future__ import annotations

from bpy.props import EnumProperty, IntProperty, PointerProperty
from bpy.types import Object, PropertyGroup, Scene


class RigUtilsSettings(PropertyGroup):
    PROP_NAME = "rig_utils_settings"

    def _poll_convert_legacy_src(self, obj: Object) -> bool:
        return obj.type == "ARMATURE"

    copy_transform_space: EnumProperty(
        items=[
            (
                "WORLD",
                "World",
                "World space",
                "ORIENTATION_GLOBAL",
                0,
            ),
            (
                "POSE",
                "Pose",
                "Pose space",
                "POSE_HLT",
                1,
            ),
            (
                "LOCAL_WITH_PARENT",
                "Local With Parent",
                "Local space with parent",
                "ORIENTATION_PARENT",
                2,
            ),
            (
                "LOCAL",
                "Local",
                "Local space",
                "ORIENTATION_LOCAL",
                3,
            ),
        ],
        name="Copy Transform Space",
        description="Copy transform space",
        default=0,
    )

    convert_legacy_src: PointerProperty(
        type=Object,
        name="Convert Legacy Source",
        description="Convert legacy source",
        poll=_poll_convert_legacy_src,
    )

    channel_frame_step: IntProperty(
        name="Channel Frame Step",
        description="Channel frame step",
        default=2,
    )

    channel_frame_offset: IntProperty(
        name="Channel Frame Offset",
        description="Channel frame offset",
        default=1,
    )

    @staticmethod
    def register():
        setattr(
            Scene,
            RigUtilsSettings.PROP_NAME,
            PointerProperty(type=RigUtilsSettings),
        )

    @staticmethod
    def unregister():
        delattr(Scene, RigUtilsSettings.PROP_NAME)


def get_settings(id: Scene) -> RigUtilsSettings:
    return getattr(id, RigUtilsSettings.PROP_NAME)
