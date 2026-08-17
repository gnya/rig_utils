from bpy.types import Context, Panel

from rig_utils.core import is_asset
from rig_utils.ops import (
    OBJECT_OT_rig_utils_add_asset_select,
    OBJECT_OT_rig_utils_update_asset,
    POSE_OT_rig_utils_copy_bone_transform,
    POSE_OT_rig_utils_paste_bone_transform,
    POSE_OT_rig_utils_show_animated_bones,
    POSE_OT_rig_utils_show_modified_bones,
)


class VIEW3D_PT_rig_utils(Panel):
    bl_idname = "VIEW3D_PT_rig_utils"
    bl_label = "Rig Utils"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            OBJECT_OT_rig_utils_add_asset_select.bl_idname,
            text="Add Asset",
            icon="ADD",
        )
        layout.operator(
            OBJECT_OT_rig_utils_update_asset.bl_idname,
            text="Update Asset",
            icon="FILE_REFRESH",
        )

        group = layout.column(align=True)
        group.operator(
            POSE_OT_rig_utils_copy_bone_transform.bl_idname,
            text="Copy (World Space)",
            icon="COPYDOWN",
        )
        group.operator(
            POSE_OT_rig_utils_paste_bone_transform.bl_idname,
            text="Paste (World Space)",
            icon="PASTEDOWN",
        )

        group = layout.column(align=True)
        group.operator(
            POSE_OT_rig_utils_show_modified_bones.bl_idname,
            text="Show Modified",
            icon="HIDE_OFF",
        )
        group.operator(
            POSE_OT_rig_utils_show_animated_bones.bl_idname,
            text="Show Animated",
            icon="HIDE_OFF",
        )


class VIEW3D_PT_rig_utils_settings(Panel):
    bl_idname = "VIEW3D_PT_rig_utils_settings"
    bl_label = "Rig Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.active_object

        return (
            is_asset(obj)
            and "preview_subsurf" in obj  # type: ignore
            and "render_subsurf" in obj  # type: ignore
        )

    def draw(self, context: Context):
        obj = context.active_object

        if obj is None:
            raise RuntimeError("Object is not selected.")

        layout = self.layout

        if "physics" in obj and "inertia" in obj:
            layout.prop(obj, '["physics"]', text="Physics")
            layout.prop(obj, '["inertia"]', text="Inertia", slider=True)

        if "preview_subsurf" in obj and "render_subsurf" in obj:
            group = layout.column(align=True)
            group.prop(obj, '["preview_subsurf"]', text="Preview Subsurf", slider=False)
            group.prop(obj, '["render_subsurf"]', text="Render Subsurf", slider=False)
