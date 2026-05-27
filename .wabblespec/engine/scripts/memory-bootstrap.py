#!/usr/bin/env python3
"""Bootstrap the shared internal memory package for this checkout."""

from __future__ import annotations

import sys
from pathlib import Path


# Minimal primer: get repo root on sys.path so _shared is importable.
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


def bootstrap() -> Path:
    """Prepare sys.path, env vars, and runtime directories for WabbleSpec Memory."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            root = parent
            break
    else:
        raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")

    inject_package_src(root)

    from memory.runtime import configure_project

    return configure_project(root).memory_path


MEMORY_PATH = bootstrap()


if __name__ == "__main__":
    runtime = MEMORY_PATH / ".runtime"
    print(f"WABBLESPEC_MEMORY_PATH={MEMORY_PATH}")
    print(f"WABBLESPEC_MEMORY_RUNTIME={runtime}")
