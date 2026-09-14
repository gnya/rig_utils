from bpy.types import Context, Header, SpaceView3D, VIEW3D_HT_header

from rig_utils.ops import (
    RENDER_OT_rig_utils_render_preview,
)


def draw_header(self: Header, context: Context):
    layout = self.layout

    space: SpaceView3D = context.space_data  # type: ignore

    if space.region_3d.view_perspective == "CAMERA":
        layout.operator(
            RENDER_OT_rig_utils_render_preview.bl_idname,
            text="Render Preview",
            icon="RENDER_ANIMATION",
        )


def inject():
    VIEW3D_HT_header.append(draw_header)


def eject():
    VIEW3D_HT_header.remove(draw_header)
