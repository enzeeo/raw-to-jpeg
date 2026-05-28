from __future__ import annotations

from pathlib import Path

from PIL import Image


def make_image(path: Path, mode: str = "RGB", color=(20, 40, 60, 255)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new(mode, (4, 4), color)
    image.save(path)
    return path
