import json
import platform

from PIL import Image

from raw_to_jpeg import cli
from raw_to_jpeg.types import BatchResult, ConversionResult


def test_cli_json_is_parseable(tmp_path, capsys):
    Image.new("RGB", (1, 1), "red").save(tmp_path / "a.png")

    exit_code = cli.main([str(tmp_path), "--json"])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["results"][0]["status"] == "converted"


def test_cli_human_summary_counts(monkeypatch, tmp_path, capsys):
    result = BatchResult(
        tmp_path,
        tmp_path / "raw-to-jpeg",
        [
            ConversionResult("converted", tmp_path / "a.png", tmp_path / "raw-to-jpeg/a.jpg", None, 0),
            ConversionResult("copied", tmp_path / "b.jpg", tmp_path / "raw-to-jpeg/b.jpg", None, 0),
            ConversionResult("skipped", tmp_path / "c.png", tmp_path / "raw-to-jpeg/c.jpg", "output_exists", 0),
            ConversionResult("skipped", tmp_path / "d.txt", None, "unsupported_format", 0),
        ],
    )
    monkeypatch.setattr(cli, "convert_path", lambda path, options: result)

    exit_code = cli.main([str(tmp_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Converted: 1" in out
    assert "Copied JPEGs: 1" in out
    assert "Skipped existing: 1" in out
    assert "Skipped unsupported: 1" in out


def test_cli_workers_passed_into_options(monkeypatch, tmp_path):
    seen = {}

    def fake_convert(path, options):
        seen["workers"] = options.workers
        return BatchResult(tmp_path, tmp_path / "raw-to-jpeg", [])

    monkeypatch.setattr(cli, "convert_path", fake_convert)

    assert cli.main([str(tmp_path), "--workers", "3"]) == 0
    assert seen["workers"] == 3


def test_pick_unsupported_platform(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")

    try:
        cli.main(["--pick"])
    except SystemExit as exc:
        assert str(exc) == "--pick is only available on macOS"
    else:
        raise AssertionError("expected SystemExit")

