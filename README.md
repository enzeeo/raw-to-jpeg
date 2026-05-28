# raw-to-jpeg

Convert folders of mixed image files into JPEGs.

## CLI

```bash
raw-to-jpeg ./Photos
raw-to-jpeg ./Photos --workers 8
raw-to-jpeg ./Photos --overwrite
raw-to-jpeg ./Photos --fast-preview
raw-to-jpeg --pick
```

Outputs are written to a `raw-to-jpeg/` folder inside the input folder, preserving relative paths. Existing JPEG files are copied unchanged.

## Python API

```python
from raw_to_jpeg import ConverterOptions, convert_path

result = convert_path("Photos", ConverterOptions(workers=8))
```

