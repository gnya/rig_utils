from collections.abc import Iterator

from bpy.types import FCurve, Object


# アクションにあるFCurveにステップ補間モディファイアを設定する
def _add_step_modifier(fcurve: FCurve, step: int, offset: int):
    stepped = fcurve.modifiers.new("STEPPED")
    stepped.frame_step = step
    stepped.frame_offset = offset


# アクションにあるFCurveのステップ補間モディファイアを削除する
def _remove_step_modifier(fcurve: FCurve):
    for modifier in list(fcurve.modifiers):
        if modifier.type == "STEPPED":
            fcurve.modifiers.remove(modifier)

    # そのままだとグラフエディタが更新されないのでupdateを呼ぶ
    # ref: https://blender.stackexchange.com/questions/157435
    fcurve.modifiers.update()


# オブジェクトのアクションにあるFCurveのイテレーターを返す
def _iter_action_fcurve(obj: Object) -> Iterator[FCurve]:
    if obj.animation_data is not None:
        if obj.animation_data.action is not None:
            for fcurve in obj.animation_data.action.fcurves:
                yield fcurve

        for track in obj.animation_data.nla_tracks:
            for strip in track.strips:
                if strip.action is not None:
                    for fcurve in strip.action.fcurves:
                        yield fcurve


# アクションにあるFCurveにステップ補間モディファイアを設定する
def add_step_modifier(obj: Object, step: int, offset: int):
    for fcurve in _iter_action_fcurve(obj):
        _remove_step_modifier(fcurve)
        _add_step_modifier(fcurve, step, offset)


# アクションにあるFCurveのステップ補間モディファイアを削除する
def remove_step_modifier(obj: Object):
    for fcurve in _iter_action_fcurve(obj):
        _remove_step_modifier(fcurve)
