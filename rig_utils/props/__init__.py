from .settings import (
    RigUtilsSettings,
    get_settings,
)

__all__ = [
    RigUtilsSettings,
    get_settings,
]

classes = (RigUtilsSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
