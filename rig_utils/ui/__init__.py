from .rig import (
    VIEW3D_PT_rig_utils,
    VIEW3D_PT_rig_utils_settings,
)

classes = (
    VIEW3D_PT_rig_utils,
    VIEW3D_PT_rig_utils_settings,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
