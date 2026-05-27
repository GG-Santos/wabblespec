"""WabbleSpec facade over the shared internal memory backend."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from _shared.repo_root import find_repo_root, inject_package_src

DRAWERS_COLLECTION = "wabblespec_drawers"
CLOSETS_COLLECTION = "wabblespec_closets"
LEGACY_DRAWERS_COLLECTION = "mempalace_drawers"
LEGACY_CLOSETS_COLLECTION = "mempalace_closets"
BACKEND_NAME = "memory/chromadb"


def repo_root() -> Path:
    """Return the WabbleSpec repo root (delegates to shared canonical finder)."""
    return find_repo_root(Path(__file__))


def _configure_backend() -> None:
    """Inject sys.path and configure memory env vars. Idempotent.

    If WABBLESPEC_MEMORY_PATH is already set we were already configured in
    this process (or a parent set the env var). In that case we still ensure
    packages/memory/src is on sys.path (needed for the module-level imports
    below) but skip configure_project to avoid redundant directory creation
    and a second sentinel walk.
    """
    try:
        root = repo_root()
    except RuntimeError as exc:
        raise RuntimeError(
            "WabbleSpec memory backend could not locate the repo root.\n"
            f"  {exc}\n"
            "  Either run from inside the WabbleSpec checkout or set "
            "  WABBLESPEC_MEMORY_PATH before importing this module."
        ) from exc

    inject_package_src(root)

    if os.environ.get("WABBLESPEC_MEMORY_PATH"):
        # Already configured -- just ensure sys.path is correct and return.
        return

    from memory.runtime import configure_project
    configure_project(root)


_configure_backend()

from memory.convo_miner import TOPIC_KEYWORDS, mine_convos  # noqa: E402
from memory.knowledge_graph import KnowledgeGraph  # noqa: E402
from memory.palace import get_closets_collection as _get_closets_collection  # noqa: E402
from memory.palace import get_collection as _get_collection  # noqa: E402
from memory.searcher import search_memories as _search_memories  # noqa: E402

try:  # noqa: E402
    from memory import hallways as _hallways
except Exception:  # pragma: no cover - optional backend capability
    _hallways = None

try:  # noqa: E402
    from memory import palace_graph as _palace_graph
except Exception:  # pragma: no cover - optional backend capability
    _palace_graph = None


def memory_path() -> str:
    path = os.environ.get("WABBLESPEC_MEMORY_PATH")
    if path:
        return path
    return str(repo_root() / ".wabblespec" / "state" / "memory")


def runtime_path() -> str:
    return str(Path(memory_path()) / ".runtime")


def get_collection(
    collection_name: str = DRAWERS_COLLECTION,
    *,
    create: bool = True,
):
    return _get_collection(memory_path(), collection_name=collection_name, create=create)


def get_legacy_collection(collection_name: str, *, create: bool = False):
    return _get_collection(memory_path(), collection_name=collection_name, create=create)


def get_closets_collection(*, create: bool = True):
    return _get_closets_collection(memory_path(), create=create)


def get_knowledge_graph() -> KnowledgeGraph:
    kg_path = Path(memory_path()) / "knowledge_graph.sqlite3"
    return KnowledgeGraph(str(kg_path))


def search_memories(
    query: str,
    *,
    wing: str | None = None,
    room: str | None = None,
    n_results: int = 5,
    max_distance: float = 0.0,
    vector_disabled: bool = False,
    candidate_strategy: str = "vector",
) -> dict[str, Any]:
    return _search_memories(
        query=query,
        palace_path=memory_path(),
        wing=wing,
        room=room,
        n_results=n_results,
        max_distance=max_distance,
        vector_disabled=vector_disabled,
        candidate_strategy=candidate_strategy,
        collection_name=DRAWERS_COLLECTION,
    )


def mine_sessions(
    convo_dir: str,
    *,
    wing: str = "wing_sessions",
    agent: str = "wabblespec",
    limit: int = 0,
    dry_run: bool = False,
    extract_mode: str = "exchange",
):
    return mine_convos(
        convo_dir=convo_dir,
        palace_path=memory_path(),
        wing=wing,
        agent=agent,
        limit=limit,
        dry_run=dry_run,
        extract_mode=extract_mode,
    )


def traverse_memory_graph(start_room: str, *, max_hops: int = 2):
    if _palace_graph is None:
        return []
    return _palace_graph.traverse(start_room=start_room, max_hops=max_hops)


def find_memory_tunnels(wing_a: str | None = None, wing_b: str | None = None):
    if _palace_graph is None:
        return []
    return _palace_graph.find_tunnels(wing_a=wing_a, wing_b=wing_b)


def has_hallways() -> bool:
    return _hallways is not None


def list_hallways(*args, **kwargs):
    if _hallways is None:
        return []
    return _hallways.list_hallways(*args, **kwargs)


def backend_health() -> dict[str, Any]:
    health: dict[str, Any] = {
        "backend": BACKEND_NAME,
        "memory_path": memory_path(),
        "runtime_path": runtime_path(),
        "drawers_collection": DRAWERS_COLLECTION,
        "closets_collection": CLOSETS_COLLECTION,
        "capabilities": {
            "knowledge_graph": True,
            "palace_graph": _palace_graph is not None,
            "hallways": has_hallways(),
            "session_ingest": True,
            "search": True,
        },
    }

    for label, collection_name in (
        ("drawers_count", DRAWERS_COLLECTION),
        ("closets_count", CLOSETS_COLLECTION),
    ):
        try:
            health[label] = get_collection(collection_name, create=False).count()
        except Exception:
            health[label] = 0

    kg_path = Path(memory_path()) / "knowledge_graph.sqlite3"
    health["knowledge_graph_path"] = str(kg_path)
    health["knowledge_graph_exists"] = kg_path.exists()
    return health
