from pathlib import Path

import bpy
from bpy.types import Context, Scene, SpaceView3D


# ユニークなファイル名を取得します
def _get_unique_path(path: Path) -> Path:
    i = 0
    stem = path.stem
    suffix = path.suffix

    while True:
        i += 1
        unique_path = path.with_name(f"{stem}_{i}{suffix}")

        if not unique_path.exists():
            return unique_path


# プレビューを書き出します（動画）
def _render_preview_video(scene: Scene, output_path: Path) -> bool:
    tmp_path = output_path.with_name(f"_tmp_{output_path.stem}")
    scene.render.filepath = str(tmp_path)

    # 一時ファイルが存在していたら削除する
    tmp_files = set(tmp_path.parent.glob(f"{tmp_path.name}*"))

    for tmp_file in tmp_files:
        tmp_file.unlink()

    # 書き出しを行う
    bpy.ops.render.opengl(animation=True)

    # 書き出したファイルの一覧を取得する
    tmp_files = set(tmp_path.parent.glob(f"{tmp_path.name}*"))

    if len(tmp_files) != 1:
        raise RuntimeError(f"Could not identify the generated file: {tmp_files}")

    tmp_file = tmp_files.pop()
    file_path = tmp_file.with_name(f"{output_path.stem}{tmp_file.suffix}")

    result = True

    # 既に存在する場合は削除する
    if file_path.exists():
        try:
            file_path.unlink()
        except PermissionError:
            result = False
            file_path = _get_unique_path(file_path)

    tmp_file.rename(file_path)

    return result


# プレビューを書き出します（連番画像）
def _render_preview_sequence(scene: Scene, output_path: Path) -> bool:
    scene.render.filepath = str(output_path)

    if not scene.render.filepath.endswith(("_")):
        scene.render.filepath += "_"

    # 書き出しを行う
    bpy.ops.render.opengl(animation=True)

    return True


# プレビューを書き出します
def render_preview(context: Context) -> bool:
    space: SpaceView3D = context.space_data  # type: ignore
    scene = context.scene
    image_settings = scene.render.image_settings

    original_shading = space.shading.type
    original_overlay = space.overlay.show_overlays
    space.shading.type = "MATERIAL"
    space.overlay.show_overlays = False

    original_path = scene.render.filepath
    original_frame = scene.frame_current
    output_path = Path(bpy.path.abspath(original_path))
    output_path = output_path.with_name(Path(bpy.data.filepath).stem)

    if image_settings.file_format in ["AVI_JPEG", "AVI_RAW", "FFMPEG"]:
        result = _render_preview_video(scene, output_path)
    else:
        result = _render_preview_sequence(scene, output_path)

    scene.render.filepath = original_path
    scene.frame_current = original_frame

    space.shading.type = original_shading
    space.overlay.show_overlays = original_overlay

    return result
