import bpy
from bpy.types import Object

from rig_utils.utils import is_selected_bone


# 選択されたボーンの位置にエンプティを追加します
def add_empty_at_bones(obj: Object):
    for bone in obj.pose.bones:
        if is_selected_bone(bone):
            empty = bpy.data.objects.new(f"EMPTY_{bone.name}", None)
            empty.empty_display_type = "PLAIN_AXES"
            empty.empty_display_size = (bone.head - bone.tail).length * 2.0
            empty.matrix_world = obj.matrix_world @ bone.matrix
            bpy.context.scene.collection.objects.link(empty)

            constraint = bone.constraints.new("COPY_TRANSFORMS")
            constraint.target = empty
