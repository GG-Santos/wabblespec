"""Canonical WabbleSpec repo-root detection and sys.path injection.

Single source of truth for the sentinel walk used by all scripts and the
_shared facade. Import this AFTER the repo root is already on sys.path
(each entry-point script does a minimal four-line bootstrap first), then
use these helpers everywhere else instead of re-implementing the walk.

No imports from _shared or packages/memory -- this module must be
importable as soon as the repo root is on sys.path and nothing else.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SENTINEL = ".wabblespec"

# Canonical paths — set after find_repo_root() is called via bootstrap().
# Scripts should import these rather than constructing paths manually.
SHARED: Path | None = None   # .wabblespec/engine/shared/
ENGINE: Path | None = None   # .wabblespec/engine/


def find_repo_root(start: Path | str | None = None) -> Path:
    """Walk up from *start* to find the directory containing .wabblespec.

    *start* may be a file path or directory. Defaults to cwd.
    Raises RuntimeError with an actionable message if not found.
    """
    probe = Path(start).resolve() if start else Path.cwd().resolve()
    candidates = (probe, *probe.parents) if probe.is_dir() else (probe.parent, *probe.parents)
    for parent in candidates:
        if (parent / _SENTINEL).exists():
            return parent
    raise RuntimeError(
        f"Cannot find WabbleSpec repo root: no '{_SENTINEL}' directory found "
        f"walking up from {probe}. Run this script from inside the WabbleSpec checkout."
    )


def inject_package_src(root: Path) -> None:
    """Add repo root and packages/memory/src to sys.path (idempotent)."""
    package_src = root / ".wabblespec" / "engine" / "packages" / "memory" / "src"
    for path in (root, package_src):
        s = str(path)
        if s not in sys.path:
            sys.path.insert(0, s)


def bootstrap(start: Path | str | None = None) -> Path:
    """Find repo root, inject both paths, return root. Idempotent.

    Convenience wrapper used by scripts that need the full setup
    (repo root + packages/memory/src) in a single call.
    Also sets module-level SHARED and ENGINE constants.
    """
    global SHARED, ENGINE
    root = find_repo_root(start)
    inject_package_src(root)
    ENGINE = root / ".wabblespec" / "engine"
    SHARED = ENGINE / "shared"
    return root
