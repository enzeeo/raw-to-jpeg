from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeAlias


ConversionStatus: TypeAlias = Literal["converted", "copied", "skipped", "failed"]


@dataclass(frozen=True)
class ConverterOptions:
    quality: int = 90
    overwrite: bool = False
    recursive: bool = True
    workers: int | None = None
    fast_preview: bool = False
    preserve_metadata: bool = True


@dataclass(frozen=True)
class ImageTask:
    input_path: Path
    output_path: Path | None
    relative_path: Path
    kind: str
    reason: str | None = None


@dataclass(frozen=True)
class ConversionResult:
    status: ConversionStatus
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

