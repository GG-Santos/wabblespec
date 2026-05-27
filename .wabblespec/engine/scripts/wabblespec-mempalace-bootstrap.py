#!/usr/bin/env python3
"""Compatibility shim for the retired bootstrap filename."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_new_bootstrap() -> Path:
    target = Path(__file__).with_name("memory-bootstrap.py")
    spec = importlib.util.spec_from_file_location("memory_bootstrap", target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load WabbleSpec Memory bootstrap: {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.MEMORY_PATH


MEMORY_PATH = _load_new_bootstrap()


if __name__ == "__main__":
    print(f"WABBLESPEC_MEMORY_PATH={MEMORY_PATH}")
