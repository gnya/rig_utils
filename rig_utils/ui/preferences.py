from bpy.props import StringProperty
from bpy.types import AddonPreferences, Context


class RigUtilsPreferences(AddonPreferences):
    bl_idname = "rig_utils"

    asset_dir: StringProperty(name="Asset Directory", default="//", subtype="DIR_PATH")

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "asset_dir", text="Asset Directory")
