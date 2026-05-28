from pathlib import Path

from raw_to_jpeg import ConverterOptions, discover_images


def test_discovers_single_file(tmp_path):
    image = tmp_path / "logo.png"
    image.write_bytes(b"not used")

    tasks = discover_images(image)

    assert len(tasks) == 1
    assert tasks[0].output_path == tmp_path / "raw-to-jpeg" / "logo.jpg"


def test_recursive_discovery_excludes_generated_outputs(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "a.png").write_bytes(b"")
    (tmp_path / "raw-to-jpeg").mkdir()
    (tmp_path / "raw-to-jpeg" / "a.jpg").write_bytes(b"")

    tasks = discover_images(tmp_path)

    assert [task.relative_path for task in tasks] == [Path("nested/a.png")]
    assert tasks[0].output_path == tmp_path / "raw-to-jpeg" / "nested" / "a.jpg"


def test_non_recursive_scan_only_top_level(tmp_path):
    (tmp_path / "top.png").write_bytes(b"")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "a.png").write_bytes(b"")

    tasks = discover_images(tmp_path, ConverterOptions(recursive=False))

    assert [task.relative_path for task in tasks] == [Path("top.png")]

