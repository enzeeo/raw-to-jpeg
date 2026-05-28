from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import backends
from .discovery import discover_images, output_root_for
from .types import BatchResult, ConversionResult, ConverterOptions, ImageTask


def convert_path(input_path: str | Path, options: ConverterOptions | None = None) -> BatchResult:
    options = options or ConverterOptions()
    source = Path(input_path).expanduser().resolve()
    tasks = discover_images(source, options)
    output_root = output_root_for(source)
    if not tasks:
        return BatchResult(source, output_root, [])

    workers = options.workers or min(os.cpu_count() or 1, 8)
    workers = max(1, workers)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_convert_task, task, options) for task in tasks]
        results = [future.result() for future in as_completed(futures)]
    return BatchResult(source, output_root, results)


def convert_file(
    input_path: str | Path,
    output_path: str | Path,
    options: ConverterOptions | None = None,
) -> ConversionResult:
    options = options or ConverterOptions()
    source = Path(input_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    task = ImageTask(source, destination, Path(source.name), _kind_for(source))
    return _convert_task(task, options)


def _convert_task(task: ImageTask, options: ConverterOptions) -> ConversionResult:
    start = time.perf_counter()
    try:
        if task.reason == "unsupported_format" or task.output_path is None:
            return _result("skipped", task, start, "unsupported_format")
        if task.output_path.exists() and not options.overwrite:
            return _result("skipped", task, start, "output_exists")
        if task.kind == "jpeg":
            backends.copy_jpeg(task.input_path, task.output_path, options)
            return _result("copied", task, start)
        if task.kind == "heic":
            backends.convert_heic(task.input_path, task.output_path, options)
        elif task.kind == "raw":
            backends.convert_raw(task.input_path, task.output_path, options)
        else:
            backends.convert_with_pillow(task.input_path, task.output_path, options)
        return _result("converted", task, start)
    except Exception as exc:
        return _result("failed", task, start, error=str(exc))


def _kind_for(path: Path) -> str:
    from .formats import classify_path

    return classify_path(path) or "unsupported"


def _result(
    status: str,
    task: ImageTask,
    start: float,
    reason: str | None = None,
    error: str | None = None,
) -> ConversionResult:
    return ConversionResult(
        status=status,  # type: ignore[arg-type]
        input_path=task.input_path,
        output_path=task.output_path,
        reason=reason,
        duration_s=time.perf_counter() - start,
        error=error,
    )
