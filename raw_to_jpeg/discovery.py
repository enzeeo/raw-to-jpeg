from __future__ import annotations

from pathlib import Path

from .formats import classify_path, output_name_for
from .types import ConverterOptions, ImageTask


OUTPUT_DIR_NAME = "raw-to-jpeg"


def output_root_for(input_path: Path) -> Path:
    base = input_path if input_path.is_dir() else input_path.parent
    return base / OUTPUT_DIR_NAME


def discover_images(input_path: str | Path, options: ConverterOptions | None = None) -> list[ImageTask]:
    options = options or ConverterOptions()
    root = Path(input_path).expanduser().resolve()
    output_root = output_root_for(root)

    if root.is_file():
        return [_task_for_file(root, root.parent, output_root)]
    if not root.is_dir():
        raise FileNotFoundError(root)

    candidates = root.rglob("*") if options.recursive else root.glob("*")
    tasks: list[ImageTask] = []
    for candidate in candidates:
        if candidate.is_dir():
            continue
        if OUTPUT_DIR_NAME in candidate.relative_to(root).parts:
            continue
        tasks.append(_task_for_file(candidate, root, output_root))
    return tasks


def _task_for_file(path: Path, base: Path, output_root: Path) -> ImageTask:
    kind = classify_path(path)
    relative_path = path.relative_to(base)
    if kind is None:
        return ImageTask(path, None, relative_path, "unsupported", "unsupported_format")
    output_path = output_root / relative_path.with_name(output_name_for(path))
    return ImageTask(path, output_path, relative_path, kind)

