from __future__ import annotations

from bpy.props import EnumProperty, PointerProperty
from bpy.types import PropertyGroup, Scene


class RigUtilsSettings(PropertyGroup):
    PROP_NAME = "rig_utils_settings"

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
