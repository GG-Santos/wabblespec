#!/usr/bin/env python3
"""Run the shared memory CLI from this checkout without installing it."""

from __future__ import annotations

import sys
from pathlib import Path


def _dependency_error() -> None:
    print(
        "memory needs the shared package dependencies in this Python environment.",
        file=sys.stderr,
    )
    print(
        "Install this checkout with `python -m pip install -e packages/memory`, "
        "or run the launcher from an environment that already has them.",
        file=sys.stderr,
    )


# Minimal primer: find repo root and add to sys.path so _shared is importable.
def _primer() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")


_primer()

from _shared.repo_root import inject_package_src  # noqa: E402


def main() -> None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            root = parent
            break
    else:
        raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")

    inject_package_src(root)

    from memory.runtime import configure_project

    configure_project(root)

    from memory.cli import main as cli_main

    try:
        cli_main()
    except ModuleNotFoundError as exc:
        if exc.name == "chromadb":
            _dependency_error()
            raise SystemExit(2) from exc
        raise


if __name__ == "__main__":
    main()
