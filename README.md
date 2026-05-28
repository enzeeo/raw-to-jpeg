# raw-to-jpeg

Convert folders of mixed image files into JPEGs.

`raw-to-jpeg` is both a Python package and a local CLI. It accepts a file or
folder, finds image files, and writes JPEG outputs into a `raw-to-jpeg/`
subfolder beside the input. Source files are never modified.

## Features

- Converts PNG, TIFF, WebP, HEIC/HEIF, and common camera RAW files to JPEG.
- Copies existing `.jpg` and `.jpeg` files byte-for-byte.
- Preserves relative folder paths under the output folder.
- Skips existing outputs by default.
- Supports bounded parallel conversion for larger folders.
- Returns structured per-file results for Python callers.
- Includes an optional macOS Finder picker with `--pick`.

## Install

From this checkout:

```bash
uv sync
uv run raw-to-jpeg ./Photos
```

As an installed command:

```bash
pipx install raw-to-jpeg
raw-to-jpeg ./Photos
```

## CLI

```bash
raw-to-jpeg ./Photos
raw-to-jpeg ./Photos --workers 8
raw-to-jpeg ./Photos --overwrite
raw-to-jpeg ./Photos --fast-preview
raw-to-jpeg ./Photos --quality 95
raw-to-jpeg ./Photos --json
raw-to-jpeg --pick
```

Outputs are written to a `raw-to-jpeg/` folder inside the input folder, preserving relative paths. Existing JPEG files are copied unchanged.

### Flags

- `path`: input file or folder. Optional only when using `--pick`.
- `--workers N`: set the number of conversion workers.
- `--overwrite`: replace existing JPEG outputs.
- `--quality N`: set JPEG quality. Default: `90`.
- `--fast-preview`: for RAW files, prefer an embedded preview JPEG when available.
- `--no-recursive`: only scan the top level of a folder.
- `--json`: print machine-readable results.
- `--pick`: choose a file or folder with Finder on macOS.

### Output layout

Input:

```text
Photos/
  IMG_001.CR3
  exports/logo.png
  old/photo.jpg
```

Output:

```text
Photos/
  raw-to-jpeg/
    IMG_001.jpg
    exports/logo.jpg
    old/photo.jpg
```

Existing `raw-to-jpeg/` folders are excluded during discovery so generated
outputs are not converted again.

### Summary output

```text
Converted: 143
Copied JPEGs: 18
Skipped existing: 7
Skipped unsupported: 42
Failed: 2
Output: /Users/me/Photos/raw-to-jpeg
```

## Python API

```python
from raw_to_jpeg import ConverterOptions, convert_path

result = convert_path("Photos", ConverterOptions(workers=8))

for item in result.results:
    print(item.status, item.input_path, item.output_path, item.reason, item.error)
```

Convert one file to a specific output path:

```python
from raw_to_jpeg import ConverterOptions, convert_file

result = convert_file("logo.png", "logo.jpg", ConverterOptions(overwrite=True))
```

Discover planned work without converting:

```python
from raw_to_jpeg import discover_images

tasks = discover_images("Photos")
```

## Supported formats

- JPEG copy: `.jpg`, `.jpeg`
- Pillow conversion: `.png`, `.tif`, `.tiff`, `.webp`
- HEIC conversion: `.heic`, `.heif`
- RAW conversion: `.arw`, `.cr2`, `.cr3`, `.dng`, `.nef`, `.nrw`, `.orf`, `.raf`, `.raw`, `.rw2`, `.sr2`

HEIC/HEIF support depends on `pillow-heif`. RAW support depends on `rawpy` and
the underlying LibRaw version.

## Behavior

- Unsupported files are skipped with reason `unsupported_format`.
- Existing outputs are skipped with reason `output_exists` unless `--overwrite`
  or `ConverterOptions(overwrite=True)` is used.
- Alpha channels are composited onto a white background before JPEG save.
- EXIF orientation is applied before saving.
- ICC and EXIF metadata preservation is best effort.
- Batch conversion continues after per-file failures.

## Development

```bash
uv sync --extra test
uv run --extra test python -m pytest -q
```
