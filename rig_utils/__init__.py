bl_info = {
    "name": "Rig Utils",
    "author": "gnya",
    "version": (0, 0, 1),
    "blender": (3, 6, 0),
    "description": "",
    "category": "Utility",
}


from . import ops, props, ui


def register():
    props.register()
    ops.register()
    ui.register()


def unregister():
    props.unregister()
    ops.unregister()
    ui.unregister()
