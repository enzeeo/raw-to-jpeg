# Design: raw-to-jpeg

Generated on 2026-05-28
Status: Approved design, pending written-spec review

## Problem Statement

Build a reusable Python package and local CLI that converts folders of mixed image files into JPEGs. The package must be easy to plug into other Python codebases, while the CLI must support local one-off use, including an optional macOS Finder picker.

The tool should accept a file or folder, recursively discover supported images, and write JPEG outputs into a `raw-to-jpeg/` subfolder in the input directory. It should ignore unrelated files, preserve relative folder structure, process hundreds of photos efficiently, and return structured results for library consumers.

## Goals

- Convert PNG, TIFF, HEIC, WebP, camera RAW, and existing JPEG files into a normalized `raw-to-jpeg/` output tree.
- Preserve relative folder paths under the output folder to avoid filename collisions.
- Copy existing `.jpg` and `.jpeg` files unchanged into the output tree.
- Use quality-first conversion defaults, with optional fast RAW preview mode.
- Skip existing outputs by default and require explicit overwrite.
- Provide a reusable Python API and a thin CLI entrypoint named `raw-to-jpeg`.
- Support parallel batch conversion with bounded worker count.
- Produce structured per-file results: converted, copied, skipped, or failed.

## Non-Goals

- No GUI app in v1.
- No remote service or web app in v1.
- No image editing controls beyond JPEG quality and fast RAW preview mode.
- No destructive changes to source images.
- No re-encoding of existing JPEGs in v1. They are copied unchanged.

## Key Decisions

- Package shape: Python library plus thin CLI.
- Distribution: installable with `pip` or `pipx`.
- Backend stack: Pillow, `pillow-heif`, and `rawpy`.
- Folder scan: recursive by default.
- Output behavior: `raw-to-jpeg/` subfolder, preserving relative paths.
- Existing outputs: skipped by default, overwritten only with `--overwrite`.
- Finder picker: macOS-only optional flag, not default CLI behavior.

## Architecture

Core package: `raw_to_jpeg`

Public API:

```python
convert_path(input_path: PathLike, options: ConverterOptions | None = None) -> BatchResult
convert_file(input_path: PathLike, output_path: PathLike, options: ConverterOptions | None = None) -> ConversionResult
discover_images(input_path: PathLike, options: ConverterOptions | None = None) -> list[ImageTask]
```

Core types:

```python
@dataclass(frozen=True)
class ConverterOptions:
    quality: int = 90
    overwrite: bool = False
    recursive: bool = True
    workers: int | None = None
    fast_preview: bool = False
    preserve_metadata: bool = True

@dataclass(frozen=True)
class ConversionResult:
    status: Literal["converted", "copied", "skipped", "failed"]
    input_path: Path
    output_path: Path | None
    reason: str | None
    duration_s: float
    error: str | None = None

@dataclass(frozen=True)
class BatchResult:
    input_path: Path
    output_root: Path
    results: list[ConversionResult]
```

Internal modules:

- `formats.py`: extension classification and supported format constants.
- `discovery.py`: file and folder scan, excluding generated `raw-to-jpeg/` folders.
- `converter.py`: batch orchestration and worker pool.
- `backends.py`: conversion functions for Pillow images, RAW images, and JPEG copying.
- `cli.py`: argument parsing, progress, summary output, and macOS picker integration.

## Format Handling

Supported source formats:

- JPEG copy: `.jpg`, `.jpeg`
- Pillow conversion: `.png`, `.tif`, `.tiff`, `.webp`
- HEIC conversion through `pillow-heif`: `.heic`, `.heif`
- RAW conversion through `rawpy`: `.arw`, `.cr2`, `.cr3`, `.dng`, `.nef`, `.nrw`, `.orf`, `.raf`, `.raw`, `.rw2`, `.sr2`

Behavior:

- Unsupported files are skipped with reason `unsupported_format`.
- Existing outputs are skipped with reason `output_exists` unless overwrite is enabled.
- Source JPEG files are copied byte-for-byte.
- Converted images are saved as `.jpg`.
- Alpha channels are composited onto a white background before JPEG save.
- Orientation is applied before saving when metadata provides it.
- ICC and EXIF metadata are preserved where the backend exposes them cleanly.

## Output Layout

For a folder input:

```text
Photos/
  IMG_001.CR3
  exports/logo.png
  old/photo.jpg
  raw-to-jpeg/
    IMG_001.jpg
    exports/logo.jpg
    old/photo.jpg
```

For a single file input:

```text
Photos/
  logo.png
  raw-to-jpeg/
    logo.jpg
```

If the scan encounters an existing `raw-to-jpeg/` folder, it is excluded to avoid converting generated outputs again.

## CLI

Command examples:

```bash
raw-to-jpeg ./Photos
raw-to-jpeg ./Photos --workers 8
raw-to-jpeg ./Photos --overwrite
raw-to-jpeg ./Photos --fast-preview
raw-to-jpeg --pick
```

CLI flags:

- `path`: optional input file or folder unless `--pick` is used.
- `--pick`: macOS Finder picker for selecting a file or folder.
- `--workers N`: override parallel worker count.
- `--overwrite`: replace existing outputs.
- `--quality N`: JPEG quality, default `90`.
- `--fast-preview`: for RAW files, prefer embedded preview JPEG when available.
- `--no-recursive`: scan only the top-level folder.
- `--json`: print machine-readable batch result.

Default human summary:

```text
Converted: 143
Copied JPEGs: 18
Skipped existing: 7
Skipped unsupported: 42
Failed: 2
Output: /Users/me/Photos/raw-to-jpeg
```

## Finder Picker

The `--pick` flag is macOS-only and implemented in the CLI, not the core library.

Rules:

- On macOS, use `osascript` to show a Finder picker for file or folder selection.
- On non-macOS, fail with a clear error explaining that `--pick` is unavailable.
- If the user cancels the picker, exit without converting.

## Performance Model

Each file conversion is independent, so v1 should use a bounded worker pool.

Default worker count:

```python
min(os.cpu_count() or 1, 8)
```

Reasoning:

- Hundreds of small and medium images benefit from parallelism.
- RAW decoding can be CPU and memory heavy, so unbounded workers are risky.
- A user override keeps the default simple while supporting faster machines.

Batch processing should stream results as each task completes so the CLI can show progress without waiting for the full folder to finish.

## Error Handling

Batch conversion should not stop on the first bad file.

Per-file errors:

- unreadable image
- unsupported RAW variant
- output write failure
- malformed image data
- missing optional decoder support

These produce `ConversionResult(status="failed", error=...)`. The CLI exits non-zero if any file failed, but still completes the rest of the batch.

## Testing Plan

Unit tests:

- extension classification for supported and unsupported formats
- discovery of a single file
- recursive folder discovery
- generated `raw-to-jpeg/` folders are excluded
- output path generation preserves relative structure
- existing output is skipped by default
- overwrite allows replacement
- JPEG files are copied unchanged

Conversion tests:

- PNG to JPEG
- TIFF to JPEG
- WebP to JPEG
- HEIC to JPEG when `pillow-heif` support is available
- RAW conversion through a small fixture or mocked `rawpy` call path
- alpha compositing uses a white background

CLI tests:

- summary counts match structured results
- `--json` emits parseable JSON
- `--workers` is passed into options
- `--pick` handles unsupported platforms cleanly

Concurrency tests:

- worker count does not change final result counts
- failures in one worker do not stop unrelated conversions

## Parallel-Agent Build Plan

Use parallel agents only after this spec is accepted and implementation starts. The work splits cleanly because each agent can own a separate domain.

Agent 1: Core API and result model

- Create package skeleton.
- Implement `ConverterOptions`, `ConversionResult`, `BatchResult`, and public API shape.
- Own files: `raw_to_jpeg/__init__.py`, `raw_to_jpeg/types.py`, initial `converter.py`.

Agent 2: Format detection and image backends

- Implement format classification.
- Implement Pillow conversion, HEIC registration, JPEG copy, and RAW conversion path.
- Own files: `raw_to_jpeg/formats.py`, `raw_to_jpeg/backends.py`.

Agent 3: CLI and Finder picker

- Implement `argparse` CLI, human summary, JSON output, and macOS `--pick`.
- Own files: `raw_to_jpeg/cli.py`, README CLI examples.

Agent 4: Tests and fixtures

- Build focused pytest coverage for discovery, output paths, conversion, and CLI.
- Create small generated fixtures where possible.
- Own files: `tests/`.

Coordinator integration:

- Review each agent summary.
- Check for file conflicts.
- Run full test suite.
- Fix integration gaps in one pass.

## Distribution Plan

Package with `pyproject.toml`.

Expected install:

```bash
pipx install raw-to-jpeg
```

Expected library use:

```python
from raw_to_jpeg import ConverterOptions, convert_path

result = convert_path("Photos", ConverterOptions(workers=8))
```

CI should run tests on macOS and Linux. macOS matters because HEIC and Finder behavior are first-class concerns. Linux matters because the package should still be importable and usable without Finder.

## Research Notes

- Pillow documents support for image formats including TIFF and WebP.
- `pillow-heif` registers HEIF/HEIC support as a Pillow plugin.
- `rawpy` exposes LibRaw-backed `postprocess()` and `extract_thumb()` APIs.
- LibRaw publishes supported camera and RAW format coverage, but support varies by LibRaw version and compile options.

Reference links:

- https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
- https://pillow-heif.readthedocs.io/en/stable/pillow-plugin.html
- https://letmaik.github.io/rawpy/api/rawpy.RawPy.html
- https://www.libraw.org/supported-cameras

## Success Criteria

- A user can run `raw-to-jpeg ./Photos` and get JPEGs in `./Photos/raw-to-jpeg/`.
- Mixed folders with images and non-images complete without manual cleanup.
- Existing JPEGs are copied into the output tree.
- Existing outputs are not overwritten unless requested.
- Library consumers can inspect structured per-file results.
- The smallest relevant test suite passes before implementation is considered done.

## Open Questions

- Exact package name availability on PyPI is not checked yet.
- Final RAW fixture strategy depends on keeping the repository small.
- Metadata preservation should be best-effort in v1, not a hard guarantee for every format.
