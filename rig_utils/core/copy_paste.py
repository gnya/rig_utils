import json
from json.decoder import JSONDecodeError

import bpy
from bpy.types import Constraint, FCurve, Object
from mathutils import Matrix

from .visibility import is_internal_bones


# ボーンのトランスフォームをワールド座標系でコピーする
def copy_bone_transform(obj: Object):
    matrices: dict[str, list[list[float]]] = {}
    bones = obj.pose.bones

    for bone in bones:
        if bone.bone.select and not is_internal_bones(bone.name):
            matrix = obj.convert_space(
                pose_bone=bone,
                matrix=bone.matrix,
                from_space="POSE",
                to_space="WORLD",
            )
            matrices[bone.name] = [list(r) for r in matrix.row]

    wm = bpy.context.window_manager
    wm.clipboard = json.dumps(matrices)


# コンストレイントが依存しているボーンを取得する
def _get_constraint_dependencies(obj: Object, constraint: Constraint) -> set[str]:
    dependencies = set()

    if (
        (constraint.owner_space == "CUSTOM" or constraint.target_space == "CUSTOM")
        and constraint.space_object == obj
        and constraint.space_subtarget
    ):
        dependencies.add(constraint.space_subtarget)

    match constraint.type:
        case "ARMATURE":
            for target in constraint.targets:
                if target.target == obj and target.subtarget:
                    dependencies.add(target.subtarget)
        case "IK":
            if constraint.pole_target == obj and constraint.pole_subtarget:
                dependencies.add(constraint.pole_subtarget)

            if constraint.target == obj and constraint.subtarget:
                dependencies.add(constraint.subtarget)
        case (
            "ACTION"
            | "CHILD_OF"
            | "COPY_LOCATION"
            | "COPY_ROTATION"
            | "COPY_SCALE"
            | "COPY_TRANSFORMS"
            | "DAMPED_TRACK"
            | "FLOOR"
            | "LIMIT_DISTANCE"
            | "LOCKED_TRACK"
            | "PIVOT"
            | "STRETCH_TO"
            | "TRACK_TO"
            | "TRANSFORM"
        ):
            if constraint.target == obj and constraint.subtarget:
                dependencies.add(constraint.subtarget)
        case (
            "CAMERA_SOLVER"
            | "CLAMP_TO"
            | "FOLLOW_PATH"
            | "FOLLOW_TRACK"
            | "LIMIT_LOCATION"
            | "LIMIT_ROTATION"
            | "LIMIT_SCALE"
            | "MAINTAIN_VOLUME"
            | "OBJECT_SOLVER"
            | "SHRINKWRAP"
            | "SPLINE_IK"
            | "TRANSFORM_CACHE"
        ):
            pass

    return dependencies


# 与えられたデータパスがボーンのトランスフォームのものかを判別する
def _is_transform_path(data_path: str) -> bool:
    if not data_path.startswith('pose.bones["'):
        return False

    splited = data_path.split('"')

    if splited[2] == "][":
        return False

    return splited[2][2:].startswith(("location", "rotation", "scale", "matrix"))


# ドライバーが依存しているボーンを取得する
def _get_driver_dependencies(obj: Object, fcurve: FCurve) -> set[str]:
    dependencies = set()

    for variable in fcurve.driver.variables:
        for target in variable.targets:
            if target.id == obj:
                if target.bone_target:
                    dependencies.add(target.bone_target)
                if _is_transform_path(target.data_path):
                    dependencies.add(target.data_path.split('"')[1])

    return dependencies


# あるボーンが依存しているボーンの一覧を格納した辞書を計算する
def _calc_dependencies_by_bone(obj: Object):
    dependencies_by_bone: dict[str, set[str]] = {}
    bones = obj.pose.bones

    for bone in bones:
        dependencies_by_bone[bone.name] = set()

        if bone.parent:
            dependencies_by_bone[bone.name].add(bone.parent.name)

        for constraint in bone.constraints:
            dependencies_by_bone[bone.name] |= _get_constraint_dependencies(
                obj,
                constraint,
            )

    if obj.animation_data is not None:
        for fcurve in obj.animation_data.drivers:
            if _is_transform_path(fcurve.data_path):
                bone_name = fcurve.data_path.split('"')[1]
                dependencies_by_bone[bone_name] |= _get_driver_dependencies(
                    obj,
                    fcurve,
                )

    # 単一のボーン内で循環参照している場合は無視する
    # TODO 処理の方針と矛盾するので将来的にオプションにする
    for bone_name, dependencies in dependencies_by_bone.items():
        if bone_name in dependencies:
            dependencies.remove(bone_name)

    return dependencies_by_bone


# あるボーンに対する深さを格納した辞書を計算する
def _calc_depth_by_bone(obj: Object) -> dict[str, int]:
    dependencies_by_bone = _calc_dependencies_by_bone(obj)
    depth_by_bone: dict[str, int] = {}

    # みているボーンが依存しているボーンの一覧を計算する
    def _calc_depth(dependencies: set[str]) -> int | None:
        if len(dependencies) == 0:
            # ボーンが何にも依存していないならdepthは0
            return 0

        max_depth = 0

        # みているボーンが依存しているボーンが依存しているボーンをみて一番深いdepthを探す
        for dependency in dependencies:
            if dependency not in depth_by_bone:
                return None

            max_depth = max(max_depth, depth_by_bone[dependency])

        # dependencyがすべてdepth_by_boneに含まれるならmax_depth+1がボーンのdepthとなる
        return max_depth + 1

    while dependencies_by_bone:
        resolved = False

        for bone_name, dependencies in list(dependencies_by_bone.items()):
            if (depth := _calc_depth(dependencies)) is not None:
                depth_by_bone[bone_name] = depth
                dependencies_by_bone.pop(bone_name)
                resolved = True

        if not resolved:
            # 依存関係が循環している場合は例外を送出する
            raise RuntimeError(
                f"Dependency cycle detected. : {len(dependencies_by_bone)}"
            )

    return depth_by_bone


# ボーンのトランスフォームをワールド座標系でペーストする
def paste_bone_transform(obj: Object) -> bool:
    try:
        wm = bpy.context.window_manager
        matrices: dict[str, list[list[float]]] = json.loads(wm.clipboard)
    except JSONDecodeError:
        return False

    bones = obj.pose.bones
    depth_by_bone = _calc_depth_by_bone(obj)

    # ある深さに対するボーンの一覧を格納した辞書を計算する
    # ただし、ボーンはmatricesに存在するもののみ
    bones_by_depth: dict[int, list[str]] = {}

    for bone_name in matrices:
        if (depth := depth_by_bone.get(bone_name)) is not None:
            bones_by_depth.setdefault(depth, []).append(bone_name)

    # 深さが浅いものから順番にトランスフォームを適用する
    for depth in sorted(bones_by_depth):
        for bone_name in bones_by_depth[depth]:
            bone = bones[bone_name]
            bone.matrix = obj.convert_space(
                pose_bone=bone,
                matrix=Matrix(matrices[bone_name]),
                from_space="WORLD",
                to_space="POSE",
            )

        bpy.context.view_layer.update()

    # TODO 自動キーイングを利用している場合には自動でキーを打つ

    return True
