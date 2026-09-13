from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Context, Operator

from rig_utils.core import render_preview

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class RENDER_OT_rig_utils_render_preview(Operator):
    bl_idname = "render.rig_utils_render_preview"
    bl_label = "Render Preview"
    bl_description = "Render preview"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        render_preview()

        return {"FINISHED"}
