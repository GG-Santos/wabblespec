#!/usr/bin/env python3
"""Syntax-only Python check that does not write bytecode."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".omc",
    ".omx",
    ".planning",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".svn",
    ".vscode",
    ".venv",
    "skill_benchmarks",
    "venv",
}


def iter_python_files(paths: list[Path]) -> list[Path]:
    """Return Python files under paths, excluding cache/venv dirs."""
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            for file_path in path.rglob("*.py"):
                if any(part in EXCLUDED_DIRS for part in file_path.parts):
                    continue
                files.append(file_path)
    return sorted(files)


def check_python_syntax(paths: list[Path]) -> dict:
    """Compile source strings without writing .pyc files."""
    failures = []
    files = iter_python_files(paths)
    for file_path in files:
        try:
            source = file_path.read_text(encoding="utf-8")
            compile(source, str(file_path), "exec")
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            failures.append({
                "path": str(file_path),
                "error": f"{type(exc).__name__}: {exc}",
            })

    return {
        "status": "pass" if not failures else "fail",
        "files": len(files),
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Syntax-check Python files without writing bytecode.")
    parser.add_argument("paths", nargs="+", type=Path, help="Python files or directories")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    result = check_python_syntax(args.paths)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Syntax check: {result['status']} ({result['files']} files)")
        for failure in result["failures"]:
            print(f"  {failure['path']}: {failure['error']}")

    raise SystemExit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
