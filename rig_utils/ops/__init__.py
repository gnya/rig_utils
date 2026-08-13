from .asset import (
    OBJECT_OT_rig_utils_update_asset,
)
from .copy_paste import (
    POSE_OT_rig_utils_copy_bone_transform,
    POSE_OT_rig_utils_paste_bone_transform,
)
from .visibility import (
    POSE_OT_rig_utils_show_animated_bones,
    POSE_OT_rig_utils_show_modified_bones,
)

classes = (
    OBJECT_OT_rig_utils_update_asset,
    POSE_OT_rig_utils_copy_bone_transform,
    POSE_OT_rig_utils_paste_bone_transform,
    POSE_OT_rig_utils_show_animated_bones,
    POSE_OT_rig_utils_show_modified_bones,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
