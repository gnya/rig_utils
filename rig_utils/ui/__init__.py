from .panel import (
    VIEW3D_PT_rig_utils,
    VIEW3D_PT_rig_utils_settings,
)
from .preferences import (
    RigUtilsPreferences,
)

classes = (
    RigUtilsPreferences,
    VIEW3D_PT_rig_utils,
    VIEW3D_PT_rig_utils_settings,
)


def register():
    from bpy.utils import register_class

    from .inject import inject

    for cls in classes:
        register_class(cls)

    inject()


def unregister():
    from bpy.utils import unregister_class

    from .inject import eject

    for cls in classes:
        unregister_class(cls)

    eject()
