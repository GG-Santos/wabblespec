"""Project-local runtime configuration for the shared memory package."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DRAWERS_COLLECTION = "wabblespec_drawers"
CLOSETS_COLLECTION = "wabblespec_closets"


@dataclass(frozen=True)
class MemoryRuntimeConfig:
    repo_root: Path
    memory_path: Path
    runtime_path: Path
    lock_dir: Path
    wal_dir: Path
    state_dir: Path
    hallways_file: Path
    tunnels_file: Path
    knowledge_graph_path: Path
    drawers_collection: str = DRAWERS_COLLECTION
    closets_collection: str = CLOSETS_COLLECTION


def find_repo_root(start: str | Path | None = None) -> Path:
    """Find the WabbleSpec repo root by walking up to ``.wabblespec``."""

    probe = Path(start or Path.cwd()).resolve()
    candidates = (probe, *probe.parents) if probe.is_dir() else (probe.parent, *probe.parents)
    for parent in candidates:
        if (parent / ".wabblespec").exists():
            return parent
    raise RuntimeError("Cannot find WabbleSpec repo root")


def configure_project(
    repo_root: str | Path | None = None,
    memory_dir: str | Path | None = None,
) -> MemoryRuntimeConfig:
    """Configure env vars and runtime directories for project-local memory state."""

    root = find_repo_root(repo_root) if repo_root is not None else find_repo_root()
    memory_path = Path(memory_dir).expanduser().resolve() if memory_dir else root / ".wabblespec" / "state" / "memory"
    runtime_path = memory_path / ".runtime"
    lock_dir = runtime_path / "locks"
    wal_dir = runtime_path / "wal"
    state_dir = runtime_path / "hook_state"

    for path in (
        memory_path,
        runtime_path,
        lock_dir,
        wal_dir,
        state_dir,
        state_dir / "mine_pids",
    ):
        path.mkdir(parents=True, exist_ok=True)

    os.environ["WABBLESPEC_MEMORY_PATH"] = str(memory_path)
    os.environ["WABBLESPEC_MEMORY_CONFIG_DIR"] = str(runtime_path)
    os.environ["WABBLESPEC_MEMORY_DIR"] = str(memory_path)
    os.environ["WABBLESPEC_MEMORY_LOCK_DIR"] = str(lock_dir)
    os.environ["WABBLESPEC_MEMORY_STATE_DIR"] = str(state_dir)
    os.environ["WABBLESPEC_MEMORY_WAL_DIR"] = str(wal_dir)
    os.environ["WABBLESPEC_MEMORY_COLLECTION"] = DRAWERS_COLLECTION
    os.environ["WABBLESPEC_MEMORY_CLOSETS_COLLECTION"] = CLOSETS_COLLECTION

    return MemoryRuntimeConfig(
        repo_root=root,
        memory_path=memory_path,
        runtime_path=runtime_path,
        lock_dir=lock_dir,
        wal_dir=wal_dir,
        state_dir=state_dir,
        hallways_file=memory_path / "hallways.json",
        tunnels_file=memory_path / "tunnels.json",
        knowledge_graph_path=memory_path / "knowledge_graph.sqlite3",
    )
