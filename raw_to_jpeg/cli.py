from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from .converter import convert_path
from .types import BatchResult, ConverterOptions


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.pick:
        picked = _pick_path()
        if picked is None:
            return 0
        path = picked
    elif args.path:
        path = Path(args.path)
    else:
        parser.error("path is required unless --pick is used")

    options = ConverterOptions(
        quality=args.quality,
        overwrite=args.overwrite,
        recursive=not args.no_recursive,
        workers=args.workers,
        fast_preview=args.fast_preview,
    )
    result = convert_path(path, options)
    if args.json:
        print(json.dumps(_batch_to_json(result), indent=2))
    else:
        print(_summary(result))
    return 1 if any(item.status == "failed" for item in result.results) else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="raw-to-jpeg")
    parser.add_argument("path", nargs="?")
    parser.add_argument("--pick", action="store_true", help="select a file or folder with Finder on macOS")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--fast-preview", action="store_true")
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json")
    return parser


def _pick_path() -> Path | None:
    if platform.system() != "Darwin":
        raise SystemExit("--pick is only available on macOS")
    script = (
        'try\n'
        'set picked to choose file with prompt "Select an image file or cancel for folder" \n'
        'POSIX path of picked\n'
        'on error number -128\n'
        'try\n'
        'set picked to choose folder with prompt "Select an image folder"\n'
        'POSIX path of picked\n'
        'on error number -128\n'
        'return ""\n'
        'end try\n'
        'end try'
    )
    completed = subprocess.run(["osascript", "-e", script], check=False, capture_output=True, text=True)
    value = completed.stdout.strip()
    return Path(value) if value else None


def _summary(result: BatchResult) -> str:
    converted = _count(result, "converted")
    copied = _count(result, "copied")
    skipped_existing = _count(result, "skipped", "output_exists")
    skipped_unsupported = _count(result, "skipped", "unsupported_format")
    failed = _count(result, "failed")
    return "\n".join(
        [
            f"Converted: {converted}",
            f"Copied JPEGs: {copied}",
            f"Skipped existing: {skipped_existing}",
            f"Skipped unsupported: {skipped_unsupported}",
            f"Failed: {failed}",
            f"Output: {result.output_root}",
        ]
    )


def _count(result: BatchResult, status: str, reason: str | None = None) -> int:
    return sum(1 for item in result.results if item.status == status and (reason is None or item.reason == reason))


def _batch_to_json(result: BatchResult) -> dict:
    data = asdict(result)
    data["input_path"] = str(result.input_path)
    data["output_root"] = str(result.output_root)
    for item in data["results"]:
        item["input_path"] = str(item["input_path"])
        item["output_path"] = str(item["output_path"]) if item["output_path"] is not None else None
    return data


if __name__ == "__main__":
    sys.exit(main())

