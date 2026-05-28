from __future__ import annotations

from pathlib import Path

from PIL import Image

from raw_to_jpeg import ConverterOptions, convert_file, convert_path

from conftest import make_image


def test_existing_output_is_skipped_by_default(tmp_path):
    source = make_image(tmp_path / "photo.png", color=(10, 20, 30))
    output = tmp_path / "out.jpg"
    make_image(output, color=(200, 200, 200))
    original_bytes = output.read_bytes()

    result = convert_file(source, output)

    assert result.status == "skipped"
    assert result.reason == "output_exists"
    assert output.read_bytes() == original_bytes


def test_overwrite_allows_replacement(tmp_path):
    source = make_image(tmp_path / "photo.png", color=(10, 20, 30))
    output = tmp_path / "out.jpg"
    make_image(output, color=(200, 200, 200))

    result = convert_file(source, output, ConverterOptions(overwrite=True))

    assert result.status == "converted"
    assert output.read_bytes() != source.read_bytes()
    assert Image.open(output).format == "JPEG"


def test_jpeg_files_are_copied_unchanged(tmp_path):
    source = make_image(tmp_path / "photo.jpg", color=(12, 34, 56))
    output = tmp_path / "copy.jpg"

    result = convert_file(source, output)

    assert result.status == "copied"
    assert output.read_bytes() == source.read_bytes()


def test_png_is_converted_to_jpeg(tmp_path):
    source = make_image(tmp_path / "photo.png", color=(12, 34, 56))
    output = tmp_path / "photo.jpg"

    result = convert_file(source, output)

    assert result.status == "converted"
    with Image.open(output) as saved:
        assert saved.format == "JPEG"
        assert saved.mode == "RGB"


def test_alpha_images_are_composited_on_white_background(tmp_path):
    source = make_image(tmp_path / "transparent.png", mode="RGBA", color=(255, 0, 0, 128))
    output = tmp_path / "transparent.jpg"

    result = convert_file(source, output)

    assert result.status == "converted"
    with Image.open(output) as saved:
        r, g, b = saved.getpixel((0, 0))
        assert r > 240
        assert 120 <= g <= 140
        assert 120 <= b <= 140


def test_convert_path_skips_unsupported_files_in_summary(tmp_path):
    make_image(tmp_path / "photo.png")
    (tmp_path / "notes.txt").write_text("not an image")

    batch = convert_path(tmp_path)

    statuses = [result.status for result in batch.results]
    assert statuses.count("converted") == 1
    assert statuses.count("skipped") == 1
    assert any(result.reason == "unsupported_format" for result in batch.results)
