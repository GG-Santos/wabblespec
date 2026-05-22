#!/usr/bin/env python3
"""
WabbleSpec MemorySearch — query interface for the mempalace ChromaDB evidence store.

Semantic, topic, staleness, recency, graph-traverse, and tunnel queries.
No flat-file JSON reading. All queries go through the mempalace Palace API.

Exit 0 = success (results printed as JSON). Exit 1 = error.

Usage:
  python modules/l5/memory-search/scripts/search-index.py --query "auth token" --type semantic
  python modules/l5/memory-search/scripts/search-index.py --query "JWT" --type topic
  python modules/l5/memory-search/scripts/search-index.py --type staleness --state NEEDS_REVERIFICATION
  python modules/l5/memory-search/scripts/search-index.py --type recency --max 20
  python modules/l5/memory-search/scripts/search-index.py --query "decisions" --type traverse --max-hops 2
  python modules/l5/memory-search/scripts/search-index.py --query "problems->decisions" --type tunnels
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


STALENESS_RANK = {
    "FRESH": 3,
    "AGING": 2,
    "STALE": 1,
    "NEEDS_REVERIFICATION": 0,
    "EXPIRED": -1,
    "SUPERSEDED": -2,
}

# Staleness penalty applied to ChromaDB similarity score
STALENESS_PENALTY = {
    "STALE": 0.3,
    "NEEDS_REVERIFICATION": 0.5,
}

DEFAULT_EXCLUDE = {"EXPIRED", "SUPERSEDED"}


def get_palace():
    """Return a Palace instance pointed at the WabbleSpec palace path."""
    try:
        from mempalace.palace import Palace
    except ImportError:
        print(json.dumps({"error": "mempalace not installed. Run: pip install mempalace"}))
        sys.exit(1)

    palace_path = os.environ.get("MEMPALACE_PALACE_PATH")
    if not palace_path:
        # Auto-detect
        from pathlib import Path
        for p in [Path.cwd(), *Path.cwd().parents]:
            if (p / ".wabblespec").is_dir():
                palace_path = str(p / ".wabblespec" / "memory")
                break
    if not palace_path:
        print(json.dumps({"error": "MEMPALACE_PALACE_PATH not set and no .wabblespec directory found."}))
        sys.exit(1)

    return Palace(palace_path)


def get_staleness(drawer: dict) -> str:
    meta = drawer.get("metadata", {})
    return meta.get("wabblespec_staleness_state", "FRESH")


def get_confidence(drawer: dict) -> float:
    meta = drawer.get("metadata", {})
    try:
        return float(meta.get("wabblespec_confidence", meta.get("confidence", 0.5)))
    except (TypeError, ValueError):
        return 0.5


def staleness_filter(results: list[dict], exclude: set, include_expired: bool) -> tuple[list[dict], int, int]:
    """
    Apply staleness post-filter.
    Returns (filtered_results, excluded_expired_count, flagged_count).
    """
    filtered = []
    excluded_expired = 0
    flagged = 0

    for r in results:
        state = get_staleness(r)
        if state in exclude:
            if state == "EXPIRED":
                excluded_expired += 1
                if include_expired:
                    r["_staleness_violation"] = True
                    filtered.append(r)
            continue
        if state in ("STALE", "NEEDS_REVERIFICATION"):
            r["_flagged"] = True
            flagged += 1
        filtered.append(r)

    return filtered, excluded_expired, flagged


def rank_semantic(results: list[dict], query: str) -> list[dict]:
    """
    Re-rank semantic results: ChromaDB distance (lower = better) adjusted by staleness.
    """
    def score(r):
        distance = r.get("_chroma_distance", 1.0)
        similarity = 1.0 - min(distance, 1.0)
        state = get_staleness(r)
        penalty = STALENESS_PENALTY.get(state, 0.0)
        confidence_boost = get_confidence(r) * 0.1
        return similarity - penalty + confidence_boost

    return sorted(results, key=score, reverse=True)


def rank_metadata(results: list[dict]) -> list[dict]:
    """
    Rank non-semantic results by confidence, staleness, then recency.
    """
    def key(r):
        state = get_staleness(r)
        rank = STALENESS_RANK.get(state, -1)
        confidence = get_confidence(r)
        filed = r.get("metadata", {}).get("filed_at", "")
        return (confidence, rank, filed)

    return sorted(results, key=key, reverse=True)


def build_result_row(r: dict, rank: int, query: str) -> dict:
    meta = r.get("metadata", {})
    content = r.get("content", r.get("document", ""))
    snippet = content[:120].replace("\n", " ").strip() if content else ""
    flags = []
    if r.get("_staleness_violation"):
        flags.append("STALENESS_VIOLATION")
    if r.get("_flagged"):
        flags.append(get_staleness(r))

    return {
        "rank": rank,
        "drawer_id": r.get("id", ""),
        "topic": meta.get("topic", meta.get("room", "")),
        "wing": meta.get("wing", ""),
        "staleness": get_staleness(r),
        "confidence": get_confidence(r),
        "snippet": snippet,
        "flags": flags,
    }


def query_semantic(palace, query: str, max_results: int, exclude: set, include_expired: bool) -> tuple[list, int, int, bool]:
    raw = palace.search(query=query, n_results=max_results * 3)
    # Attach distance scores
    if isinstance(raw, dict):
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        ids = raw.get("ids", [[]])[0]
        distances = raw.get("distances", [[]])[0]
        results = []
        for i, doc in enumerate(docs):
            results.append({
                "id": ids[i] if i < len(ids) else "",
                "content": doc,
                "metadata": metas[i] if i < len(metas) else {},
                "_chroma_distance": distances[i] if i < len(distances) else 1.0,
            })
    elif isinstance(raw, list):
        results = raw
    else:
        results = []

    filtered, expired_count, flagged_count = staleness_filter(results, exclude, include_expired)
    ranked = rank_semantic(filtered, query)
    return ranked, expired_count, flagged_count, True


def query_topic(palace, query: str, max_results: int, exclude: set, include_expired: bool) -> tuple[list, int, int, bool]:
    raw = palace.filter_drawers(filters={"room": query}, limit=max_results * 2)
    if not isinstance(raw, list):
        raw = []
    filtered, expired_count, flagged_count = staleness_filter(raw, exclude, include_expired)
    ranked = rank_metadata(filtered)
    return ranked, expired_count, flagged_count, False


def query_staleness(palace, state: str, max_results: int) -> tuple[list, int, int, bool]:
    raw = palace.filter_drawers(
        filters={"wabblespec_staleness_state": state},
        limit=max_results
    )
    if not isinstance(raw, list):
        raw = []
    return raw, 0, 0, False


def query_recency(palace, max_results: int, exclude: set, include_expired: bool) -> tuple[list, int, int, bool]:
    raw = palace.filter_drawers(order_by="filed_at", limit=max_results * 2)
    if not isinstance(raw, list):
        raw = []
    filtered, expired_count, flagged_count = staleness_filter(raw, exclude, include_expired)
    ranked = rank_metadata(filtered)
    return ranked, expired_count, flagged_count, False


def query_traverse(palace, start_room: str, max_hops: int) -> tuple[list, int, int, bool]:
    try:
        from mempalace.palace_graph import traverse
        results = traverse(start_room=start_room, max_hops=max_hops)
        if not isinstance(results, list):
            results = []
    except (ImportError, Exception):
        results = []
    return results, 0, 0, False


def query_tunnels(palace, query: str) -> tuple[list, int, int, bool]:
    try:
        from mempalace.palace_graph import find_tunnels
        if "->" in query:
            parts = query.split("->", 1)
            wing_a = parts[0].strip() or None
            wing_b = parts[1].strip() or None
        else:
            wing_a = query.strip() or None
            wing_b = None
        results = find_tunnels(wing_a=wing_a, wing_b=wing_b)
        if not isinstance(results, list):
            results = []
    except (ImportError, Exception):
        results = []
    return results, 0, 0, False


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec MemorySearch")
    parser.add_argument("--query", default="", help="Search query string")
    parser.add_argument("--type", choices=["semantic", "topic", "staleness", "recency", "traverse", "tunnels"],
                        default="semantic", dest="query_type")
    parser.add_argument("--state", default=None, help="Staleness state filter (for --type staleness)")
    parser.add_argument("--max", type=int, default=10, dest="max_results")
    parser.add_argument("--max-hops", type=int, default=2)
    parser.add_argument("--wing", default=None, help="Filter by wing (for topic queries)")
    parser.add_argument("--include-expired", action="store_true")
    args = parser.parse_args()

    palace = get_palace()
    exclude = set() if args.include_expired else DEFAULT_EXCLUDE
    semantic_used = False
    entity_graph_traversed = False
    expired_count = 0
    flagged_count = 0
    results = []

    if args.query_type == "semantic":
        if not args.query:
            print(json.dumps({"error": "--query required for semantic search"}))
            sys.exit(1)
        results, expired_count, flagged_count, semantic_used = query_semantic(
            palace, args.query, args.max_results, exclude, args.include_expired)

    elif args.query_type == "topic":
        if not args.query:
            print(json.dumps({"error": "--query required for topic search"}))
            sys.exit(1)
        results, expired_count, flagged_count, semantic_used = query_topic(
            palace, args.query, args.max_results, exclude, args.include_expired)

    elif args.query_type == "staleness":
        if not args.state:
            print(json.dumps({"error": "--state required for staleness query"}))
            sys.exit(1)
        results, expired_count, flagged_count, semantic_used = query_staleness(
            palace, args.state, args.max_results)

    elif args.query_type == "recency":
        results, expired_count, flagged_count, semantic_used = query_recency(
            palace, args.max_results, exclude, args.include_expired)

    elif args.query_type == "traverse":
        if not args.query:
            print(json.dumps({"error": "--query (start room) required for traverse"}))
            sys.exit(1)
        results, expired_count, flagged_count, semantic_used = query_traverse(
            palace, args.query, args.max_hops)
        entity_graph_traversed = True

    elif args.query_type == "tunnels":
        results, expired_count, flagged_count, semantic_used = query_tunnels(palace, args.query)
        entity_graph_traversed = True

    # Format output
    trimmed = results[:args.max_results]

    if args.query_type in ("traverse", "tunnels"):
        # Graph results have different structure
        formatted = trimmed
    else:
        formatted = [build_result_row(r, i + 1, args.query) for i, r in enumerate(trimmed)]

    output = {
        "query": args.query,
        "query_type": args.query_type,
        "backend": "mempalace/chromadb",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results_returned": len(formatted),
        "results_excluded_expired": expired_count,
        "results_flagged": flagged_count,
        "semantic_search_used": semantic_used,
        "entity_graph_traversed": entity_graph_traversed,
        "results": formatted,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
