from __future__ import annotations

import shutil
from pathlib import Path

from .types import ConverterOptions


def copy_jpeg(input_path: Path, output_path: Path, options: ConverterOptions) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, output_path)


def convert_with_pillow(input_path: Path, output_path: Path, options: ConverterOptions) -> None:
    from PIL import Image, ImageOps

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        image = ImageOps.exif_transpose(image)
        save_kwargs = _metadata_kwargs(image, options)
        image = _jpeg_ready(image)
        image.save(output_path, "JPEG", quality=options.quality, optimize=True, **save_kwargs)


def convert_heic(input_path: Path, output_path: Path, options: ConverterOptions) -> None:
    try:
        from pillow_heif import register_heif_opener
    except ImportError as exc:
        raise RuntimeError("pillow-heif is required for HEIC/HEIF conversion") from exc

    register_heif_opener()
    convert_with_pillow(input_path, output_path, options)


def convert_raw(input_path: Path, output_path: Path, options: ConverterOptions) -> None:
    try:
        import rawpy
    except ImportError as exc:
        raise RuntimeError("rawpy is required for RAW conversion") from exc

    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rawpy.imread(str(input_path)) as raw:
        if options.fast_preview:
            try:
                thumb = raw.extract_thumb()
            except rawpy.LibRawNoThumbnailError:
                thumb = None
            if thumb is not None and thumb.format == rawpy.ThumbFormat.JPEG:
                output_path.write_bytes(thumb.data)
                return
        rgb = raw.postprocess()
    Image.fromarray(rgb).save(output_path, "JPEG", quality=options.quality, optimize=True)


def _jpeg_ready(image):
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        from PIL import Image

        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        background.alpha_composite(rgba)
        return background.convert("RGB")
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def _metadata_kwargs(image, options: ConverterOptions) -> dict[str, bytes]:
    if not options.preserve_metadata:
        return {}
    kwargs: dict[str, bytes] = {}
    if "icc_profile" in image.info:
        kwargs["icc_profile"] = image.info["icc_profile"]
    exif = image.getexif()
    if exif:
        kwargs["exif"] = exif.tobytes()
    return kwargs
