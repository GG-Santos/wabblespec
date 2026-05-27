#!/usr/bin/env python3
"""
WabbleSpec MemorySearch — query interface for the WabbleSpec Memory evidence store.

Semantic, topic, staleness, recency, graph-traverse, and tunnel queries.
All queries go through ChromaDB via the WabbleSpec Memory facade.

Exit 0 = success (results printed as JSON). Exit 1 = error.

Usage:
  python modules/l5/memory-search/scripts/search-index.py --query "staleness decay" --type semantic
  python modules/l5/memory-search/scripts/search-index.py --query "guard" --type topic
  python modules/l5/memory-search/scripts/search-index.py --type staleness --state NEEDS_REVERIFICATION
  python modules/l5/memory-search/scripts/search-index.py --type recency --max 10
  python modules/l5/memory-search/scripts/search-index.py --query "decisions" --type traverse --max-hops 2
  python modules/l5/memory-search/scripts/search-index.py --query "problems->decisions" --type tunnels
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Bootstrap — must run before any backend import ──────────────────────────

def _add_repo_root():
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return
    print(json.dumps({"error": "WabbleSpec repo root not found."}))
    sys.exit(1)


_add_repo_root()


# ── Imports (after bootstrap) ──────────────────────────────────────────────────

try:
    from _shared.memory_backend import (
        BACKEND_NAME,
        find_memory_tunnels,
        get_collection,
        memory_path,
        traverse_memory_graph,
    )
except ImportError:
    print(json.dumps({"error": "WabbleSpec Memory backend unavailable"}))
    sys.exit(1)


# ── Constants ──────────────────────────────────────────────────────────────────

STALENESS_RANK = {
    "FRESH": 3,
    "AGING": 2,
    "STALE": 1,
    "NEEDS_REVERIFICATION": 0,
    "EXPIRED": -1,
    "SUPERSEDED": -2,
}

# Staleness penalty applied to similarity score (lower similarity = worse rank)
STALENESS_PENALTY = {
    "STALE": 0.3,
    "NEEDS_REVERIFICATION": 0.5,
}

DEFAULT_EXCLUDE = {"EXPIRED", "SUPERSEDED"}

# Name/concept boost: 40% effective_distance reduction for module/tool/phase names
_WABBLESPEC_NAMES = {
    "memory", "guard", "verifier", "executor", "archive", "reviewer",
    "dream", "provenance", "entity-graph", "nexus", "instinct",
    "recipe", "specify", "scopeframe", "decompose", "blueprint",
    "benchmark", "synth", "factory", "feedback", "polish",
    "autopilot", "model-router", "runtime-probe", "ensemble",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _store_path() -> str:
    path = memory_path()
    if not path:
        print(json.dumps({"error": "WABBLESPEC_MEMORY_PATH not set"}))
        sys.exit(1)
    return path


def _get_col():
    _store_path()
    return get_collection()


def _meta(m: dict, key: str, default=None):
    return m.get(key, default)


def _staleness(m: dict) -> str:
    return m.get("wabblespec_staleness_state", "FRESH")


def _confidence(m: dict) -> float:
    try:
        return float(m.get("wabblespec_confidence", 0.5))
    except (TypeError, ValueError):
        return 0.5


def _name_boost(query: str, distance: float) -> float:
    """Return effective_distance after 40% reduction if a WabbleSpec module
    name appears in the query. Mirrors the backend hybrid v4 person-name boost."""
    q_lower = query.lower()
    for name in _WABBLESPEC_NAMES:
        if name in q_lower:
            return distance * 0.6
    return distance


def _staleness_filter(rows: list[dict], exclude: set, include_expired: bool):
    """Filter and annotate rows by staleness. Returns (filtered, expired_ct, flagged_ct)."""
    filtered = []
    expired_ct = 0
    flagged_ct = 0
    for r in rows:
        state = _staleness(r["meta"])
        if state == "EXPIRED":
            expired_ct += 1
            if include_expired:
                r["_staleness_violation"] = True
                filtered.append(r)
        elif state == "SUPERSEDED":
            pass  # always exclude
        else:
            if state in ("STALE", "NEEDS_REVERIFICATION"):
                r["_flagged"] = True
                flagged_ct += 1
            filtered.append(r)
    return filtered, expired_ct, flagged_ct


def _build_row(r: dict, rank: int) -> dict:
    m = r["meta"]
    text = r.get("text", "")
    snippet = text[:120].replace("\n", " ").strip()
    flags = []
    if r.get("_staleness_violation"):
        flags.append("STALENESS_VIOLATION")
    if r.get("_flagged"):
        flags.append(_staleness(m))

    return {
        "rank": rank,
        "drawer_id": m.get("wabblespec_drawer_id", r.get("id", "")),
        "topic": m.get("wabblespec_topic", m.get("room", "")),
        "wing": m.get("wing", ""),
        "room": m.get("room", ""),
        "staleness": _staleness(m),
        "confidence": _confidence(m),
        "similarity": round(r.get("similarity", 0.0), 4),
        "matched_via": r.get("matched_via", "drawer"),
        "snippet": snippet,
        "flags": flags,
    }


# ── Query implementations ──────────────────────────────────────────────────────

def query_semantic(query: str, max_results: int, wing: str, exclude: set, include_expired: bool):
    """Vector + BM25 hybrid via col.query(). Full metadata returned directly."""
    col = _get_col()

    # Over-fetch to allow for post-filter headroom
    fetch = min(max_results * 3, col.count())
    where = {"wing": wing} if wing else None

    qr = col.query(query_texts=[query], n_results=fetch, where=where)
    ids = qr.ids[0] if qr.ids else []
    metas = qr.metadatas[0] if qr.metadatas else []
    docs = qr.documents[0] if qr.documents else []
    distances = qr.distances[0] if qr.distances else []

    rows = []
    for i, doc_id in enumerate(ids):
        m = metas[i] if i < len(metas) else {}
        dist = distances[i] if i < len(distances) else 1.0
        effective_dist = _name_boost(query, dist)
        similarity = max(0.0, 1.0 - effective_dist)

        # Staleness penalty applied to similarity score
        state = _staleness(m)
        penalty = STALENESS_PENALTY.get(state, 0.0)
        confidence_boost = _confidence(m) * 0.1
        final_score = similarity - penalty + confidence_boost

        rows.append({
            "id": doc_id,
            "text": docs[i] if i < len(docs) else "",
            "meta": m,
            "similarity": final_score,
            "matched_via": "drawer",
        })

    filtered, expired_ct, flagged_ct = _staleness_filter(rows, exclude, include_expired)
    ranked = sorted(filtered, key=lambda r: r["similarity"], reverse=True)

    # Deduplicate by drawer_id — keep highest-scoring entry per drawer.
    # Synthetic docs (id ends __synth_*) share drawer_id with their source;
    # they boost ranking but should not appear as separate results.
    seen_drawer_ids: set = set()
    deduped = []
    for r in ranked:
        did = r["meta"].get("wabblespec_drawer_id", r.get("id", ""))
        if did not in seen_drawer_ids:
            seen_drawer_ids.add(did)
            deduped.append(r)

    return deduped, expired_ct, flagged_ct, True


def query_topic(query: str, max_results: int, wing: str, exclude: set, include_expired: bool):
    """Metadata filter on room or wing field. Falls back to text search on topic."""
    col = _get_col()

    # Try room filter first, then wing filter
    where: dict = {"room": query}
    if wing:
        where["wing"] = wing

    r = col.get(where=where, limit=max_results * 2)
    ids = r.ids or []
    metas = r.metadatas or []
    docs = r.documents or []

    # If no room match, try wing match alone
    if not ids and not wing:
        r2 = col.get(where={"wing": query}, limit=max_results * 2)
        ids = r2.ids or []
        metas = r2.metadatas or []
        docs = r2.documents or []

    rows = [
        {"id": ids[i], "text": docs[i] if docs else "", "meta": metas[i], "similarity": 0.0}
        for i in range(len(ids))
    ]
    filtered, expired_ct, flagged_ct = _staleness_filter(rows, exclude, include_expired)
    # Rank by confidence desc, staleness rank desc, recency desc
    ranked = sorted(filtered, key=lambda r: (
        _confidence(r["meta"]),
        STALENESS_RANK.get(_staleness(r["meta"]), -1),
        r["meta"].get("filed_at", ""),
    ), reverse=True)
    return ranked, expired_ct, flagged_ct, False


def query_staleness(state: str, max_results: int):
    """Return all drawers in a specific staleness state."""
    col = _get_col()
    r = col.get(where={"wabblespec_staleness_state": state}, limit=max_results)
    ids = r.ids or []
    metas = r.metadatas or []
    docs = r.documents or []
    rows = [
        {"id": ids[i], "text": docs[i] if docs else "", "meta": metas[i], "similarity": 0.0}
        for i in range(len(ids))
    ]
    return rows, 0, 0, False


def query_recency(max_results: int, exclude: set, include_expired: bool):
    """Return drawers sorted by filed_at descending."""
    col = _get_col()
    fetch = min(max_results * 2, col.count())
    r = col.get(limit=fetch)
    ids = r.ids or []
    metas = r.metadatas or []
    docs = r.documents or []
    rows = [
        {"id": ids[i], "text": docs[i] if docs else "", "meta": metas[i], "similarity": 0.0}
        for i in range(len(ids))
    ]
    filtered, expired_ct, flagged_ct = _staleness_filter(rows, exclude, include_expired)
    ranked = sorted(filtered, key=lambda r: r["meta"].get("filed_at", ""), reverse=True)
    return ranked, expired_ct, flagged_ct, False


def query_traverse(start_room: str, max_hops: int):
    """BFS graph traversal across wings from a starting room."""
    try:
        from _shared.memory_backend import traverse_memory_graph
        results = traverse_memory_graph(start_room=start_room, max_hops=max_hops)
        if not isinstance(results, list):
            results = []
    except Exception:
        results = []
    return results, 0, 0, False


def query_tunnels(query: str):
    """Find cross-wing connectors."""
    try:
        from _shared.memory_backend import find_memory_tunnels
        wing_a, wing_b = None, None
        if "->" in query:
            parts = query.split("->", 1)
            wing_a = parts[0].strip() or None
            wing_b = parts[1].strip() or None
        else:
            wing_a = query.strip() or None
        results = find_memory_tunnels(wing_a=wing_a, wing_b=wing_b)
        if not isinstance(results, list):
            results = []
    except Exception:
        results = []
    return results, 0, 0, False


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec MemorySearch")
    parser.add_argument("--query", default="", help="Search query string")
    parser.add_argument(
        "--type",
        choices=["semantic", "topic", "staleness", "recency", "traverse", "tunnels"],
        default="semantic",
        dest="query_type",
    )
    parser.add_argument("--state", default=None, help="Staleness state (for --type staleness)")
    parser.add_argument("--max", type=int, default=10, dest="max_results")
    parser.add_argument("--max-hops", type=int, default=2)
    parser.add_argument("--wing", default=None, help="Filter by wing")
    parser.add_argument("--include-expired", action="store_true")
    args = parser.parse_args()

    exclude = set() if args.include_expired else DEFAULT_EXCLUDE
    semantic_used = False
    graph_traversed = False
    expired_ct = 0
    flagged_ct = 0
    results = []

    if args.query_type == "semantic":
        if not args.query:
            print(json.dumps({"error": "--query required for semantic search"}))
            sys.exit(1)
        results, expired_ct, flagged_ct, semantic_used = query_semantic(
            args.query, args.max_results, args.wing, exclude, args.include_expired
        )

    elif args.query_type == "topic":
        if not args.query:
            print(json.dumps({"error": "--query required for topic search"}))
            sys.exit(1)
        results, expired_ct, flagged_ct, semantic_used = query_topic(
            args.query, args.max_results, args.wing, exclude, args.include_expired
        )

    elif args.query_type == "staleness":
        if not args.state:
            print(json.dumps({"error": "--state required for staleness query"}))
            sys.exit(1)
        results, expired_ct, flagged_ct, semantic_used = query_staleness(
            args.state, args.max_results
        )

    elif args.query_type == "recency":
        results, expired_ct, flagged_ct, semantic_used = query_recency(
            args.max_results, exclude, args.include_expired
        )

    elif args.query_type == "traverse":
        if not args.query:
            print(json.dumps({"error": "--query (start room) required for traverse"}))
            sys.exit(1)
        results, expired_ct, flagged_ct, semantic_used = query_traverse(
            args.query, args.max_hops
        )
        graph_traversed = True

    elif args.query_type == "tunnels":
        results, expired_ct, flagged_ct, semantic_used = query_tunnels(args.query)
        graph_traversed = True

    trimmed = results[: args.max_results]

    # Graph results have a different structure — pass through raw
    if args.query_type in ("traverse", "tunnels"):
        formatted = trimmed
    else:
        formatted = [_build_row(r, i + 1) for i, r in enumerate(trimmed)]

    output = {
        "query": args.query,
        "query_type": args.query_type,
        "backend": BACKEND_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results_returned": len(formatted),
        "results_excluded_expired": expired_ct,
        "results_flagged": flagged_ct,
        "semantic_search_used": semantic_used,
        "entity_graph_traversed": graph_traversed,
        "results": formatted,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
