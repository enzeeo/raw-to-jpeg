# MEMORY.md

## Decisions

### 2026-05-28 - raw-to-jpeg Product Shape
- Decided: Build `raw-to-jpeg` as a Python package with a thin CLI.
- Why: The user wants it to be pluggable into other codebases while still runnable locally.
- Rejected: CLI-only tool and native macOS app as v1 product shapes.

### 2026-05-28 - Conversion Scope
- Decided: v1 converts PNG, TIFF, HEIC, WebP, camera RAW, and existing JPEG/JPG files.
- Why: User said PNG/TIFF/HEIC/WebP are the main focus, but also explicitly chose to require camera RAW support.
- Rejected: Deferring RAW support.

### 2026-05-28 - Output Behavior
- Decided: Recursively scan folders by default, preserve relative folder structure, and write outputs under `raw-to-jpeg/`.
- Why: This handles folders with hundreds of mixed files and avoids filename collisions.
- Rejected: Flattening all outputs into one folder.

### 2026-05-28 - Safety Defaults
- Decided: Skip existing outputs by default and require explicit overwrite.
- Why: Repeat runs should not accidentally destroy prior conversions.
- Rejected: Overwrite-by-default and unique suffix generation.

### 2026-05-28 - JPEG Handling
- Decided: Copy existing `.jpg` and `.jpeg` files unchanged into the `raw-to-jpeg/` output tree.
- Why: User explicitly requested JPEGs from original folders also be copied into the output folder.
- Rejected: Skipping JPEGs or recompressing them.

### 2026-05-28 - Backend Stack
- Decided: Use Pillow, `pillow-heif`, and `rawpy` for v1.
- Why: Best match for a Python package that is easy to install and embed.
- Rejected: libvips-first and external CLI-tool-first backends for v1.
