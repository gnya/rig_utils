from collections.abc import Iterator

from bpy.types import FCurve, Object


# アクションにあるチャンネルにステップ補間モディファイアを設定する
def _add_step_modifier(channel: FCurve, step: int, offset: int):
    stepped = channel.modifiers.new("STEPPED")
    stepped.frame_step = step
    stepped.frame_offset = offset


# アクションにあるチャンネルのステップ補間モディファイアを削除する
def _remove_step_modifier(channel: FCurve):
    for modifier in list(channel.modifiers):
        if modifier.type == "STEPPED":
            channel.modifiers.remove(modifier)

    # そのままだとグラフエディタが更新されないのでupdateを呼ぶ
    # ref: https://blender.stackexchange.com/questions/157435
    channel.modifiers.update()


# オブジェクトのアクションにあるチャンネルのイテレーターを返す
def _iter_action_channel(obj: Object) -> Iterator[FCurve]:
    if obj.animation_data is not None:
        if obj.animation_data.action is not None:
            for group in obj.animation_data.action.groups:
                for channel in group.channels:
                    yield channel

        for track in obj.animation_data.nla_tracks:
            for strip in track.strips:
                if strip.action is not None:
                    for group in strip.action.groups:
                        for channel in group.channels:
                            yield channel


# アクションにあるチャンネルにステップ補間モディファイアを設定する
def add_step_modifier(obj: Object, step: int, offset: int):
    for channel in _iter_action_channel(obj):
        _remove_step_modifier(channel)
        _add_step_modifier(channel, step, offset)


# アクションにあるチャンネルのステップ補間モディファイアを削除する
def remove_step_modifier(obj: Object):
    for channel in _iter_action_channel(obj):
        _remove_step_modifier(channel)
