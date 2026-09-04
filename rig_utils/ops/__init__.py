from .asset import (
    OBJECT_OT_rig_utils_add_asset,
    OBJECT_OT_rig_utils_add_asset_select,
    OBJECT_OT_rig_utils_add_asset_select_collection,
    OBJECT_OT_rig_utils_update_asset,
)
from .convert import (
    POSE_OT_rig_utils_convert_legacy_transform,
)
from .copy_paste import (
    POSE_OT_rig_utils_copy_bone_transform,
    POSE_OT_rig_utils_paste_bone_transform,
)
from .empty import (
    POSE_OT_rig_utils_add_empty_at_bones,
)
from .keyframe import (
    OBJECT_OT_rig_utils_add_step_modifier,
    OBJECT_OT_rig_utils_remove_step_modifier,
)
from .visibility import (
    POSE_OT_rig_utils_show_animated_bones,
    POSE_OT_rig_utils_show_modified_bones,
    POSE_OT_rig_utils_show_overrided_bones,
)

classes = (
    OBJECT_OT_rig_utils_add_asset,
    OBJECT_OT_rig_utils_add_asset_select,
    OBJECT_OT_rig_utils_add_asset_select_collection,
    POSE_OT_rig_utils_add_empty_at_bones,
    POSE_OT_rig_utils_convert_legacy_transform,
    OBJECT_OT_rig_utils_update_asset,
    POSE_OT_rig_utils_copy_bone_transform,
    POSE_OT_rig_utils_paste_bone_transform,
    OBJECT_OT_rig_utils_add_step_modifier,
    OBJECT_OT_rig_utils_remove_step_modifier,
    POSE_OT_rig_utils_show_animated_bones,
    POSE_OT_rig_utils_show_modified_bones,
    POSE_OT_rig_utils_show_overrided_bones,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
