from __future__ import annotations

from pathlib import Path


JPEG_EXTENSIONS = frozenset({".jpg", ".jpeg"})
PILLOW_EXTENSIONS = frozenset({".png", ".tif", ".tiff", ".webp"})
HEIC_EXTENSIONS = frozenset({".heic", ".heif"})
RAW_EXTENSIONS = frozenset(
    {".arw", ".cr2", ".cr3", ".dng", ".nef", ".nrw", ".orf", ".raf", ".raw", ".rw2", ".sr2"}
)
SUPPORTED_EXTENSIONS = JPEG_EXTENSIONS | PILLOW_EXTENSIONS | HEIC_EXTENSIONS | RAW_EXTENSIONS


def classify_path(path: Path | str) -> str | None:
    suffix = Path(path).suffix.lower()
    if suffix in JPEG_EXTENSIONS:
        return "jpeg"
    if suffix in PILLOW_EXTENSIONS:
        return "pillow"
    if suffix in HEIC_EXTENSIONS:
        return "heic"
    if suffix in RAW_EXTENSIONS:
        return "raw"
    return None


def output_name_for(path: Path) -> str:
    if classify_path(path) == "jpeg":
        return path.name
    return f"{path.stem}.jpg"

