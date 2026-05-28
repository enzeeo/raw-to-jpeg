from pathlib import Path

from PIL import Image

from raw_to_jpeg import ConverterOptions, convert_path


def test_existing_output_skipped_by_default(tmp_path):
    source = tmp_path / "photo.png"
    Image.new("RGB", (1, 1), "red").save(source)
    output = tmp_path / "raw-to-jpeg" / "photo.jpg"
    output.parent.mkdir()
    output.write_bytes(b"old")

    result = convert_path(tmp_path)

    assert result.results[0].status == "skipped"
    assert result.results[0].reason == "output_exists"
    assert output.read_bytes() == b"old"


def test_overwrite_allows_replacement(tmp_path):
    source = tmp_path / "photo.png"
    Image.new("RGB", (1, 1), "red").save(source)
    output = tmp_path / "raw-to-jpeg" / "photo.jpg"
    output.parent.mkdir()
    output.write_bytes(b"old")

    result = convert_path(tmp_path, ConverterOptions(overwrite=True))

    assert result.results[0].status == "converted"
    assert output.read_bytes() != b"old"


def test_jpeg_copied_unchanged(tmp_path):
    source = tmp_path / "photo.jpg"
    Image.new("RGB", (1, 1), "blue").save(source)
    original = source.read_bytes()

    result = convert_path(tmp_path)

    output = tmp_path / "raw-to-jpeg" / "photo.jpg"
    assert result.results[0].status == "copied"
    assert output.read_bytes() == original


def test_png_alpha_composited_on_white(tmp_path):
    source = tmp_path / "transparent.png"
    Image.new("RGBA", (1, 1), (255, 0, 0, 0)).save(source)

    result = convert_path(tmp_path)

    output = tmp_path / "raw-to-jpeg" / "transparent.jpg"
    assert result.results[0].status == "converted"
    with Image.open(output) as image:
        pixel = image.convert("RGB").getpixel((0, 0))
    assert all(channel >= 250 for channel in pixel)

