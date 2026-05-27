#!/usr/bin/env python3
"""
WabbleSpec Nexus — blast-radius.py

Reads graph.json. Given --entity <eid>, computes forward reachability
(all entities reachable via co-occurrence/dependency edges).
Outputs a ranked list with hop distance.

Usage:
  python modules/l5/nexus/scripts/blast-radius.py --entity "module::executor"
  python modules/l5/nexus/scripts/blast-radius.py --entity "concept::guard" --max-hops 4
"""
import argparse
import json
import sys
from collections import deque
from pathlib import Path


def find_ws_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / ".wabblespec").is_dir():
            return p / ".wabblespec"
    raise FileNotFoundError("No .wabblespec directory found from cwd")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def build_adjacency(edges: list[dict]) -> dict[str, list[str]]:
    """Build an undirected adjacency list from edge list."""
    adj: dict[str, list[str]] = {}
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if not src or not tgt:
            continue
        adj.setdefault(src, []).append(tgt)
        adj.setdefault(tgt, []).append(src)
    return adj


def bfs_reachability(
    start: str,
    adj: dict[str, list[str]],
    max_hops: int,
) -> list[dict]:
    """BFS from start node. Returns entities in hop order."""
    visited = {start}
    queue = deque([(start, 0)])
    results = []

    while queue:
        current, hop = queue.popleft()
        if hop >= max_hops:
            continue
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                next_hop = hop + 1
                results.append({"entity_id": neighbor, "hop_distance": next_hop})
                queue.append((neighbor, next_hop))

    return sorted(results, key=lambda r: (r["hop_distance"], r["entity_id"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Nexus blast-radius")
    parser.add_argument("--entity", required=True,
                        help="Entity ID to compute blast radius from. e.g. 'module::executor'")
    parser.add_argument("--max-hops", type=int, default=3,
                        help="Maximum hop distance to traverse (default: 3)")
    args = parser.parse_args()

    try:
        ws_root = find_ws_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    graph_path = ws_root / "nexus" / "graph.json"
    graph = load_json(graph_path)
    if graph is None:
        print("ERROR: nexus/graph.json not found — run graph-builder.py first", file=sys.stderr)
        sys.exit(1)

    nodes_by_id = {n["id"]: n for n in graph.get("nodes", [])}
    edges = graph.get("edges", [])
    adj = build_adjacency(edges)

    entity_id = args.entity
    if entity_id not in nodes_by_id:
        # Try partial match
        matches = [eid for eid in nodes_by_id if args.entity.lower() in eid.lower()]
        if not matches:
            print(f"ERROR: entity '{entity_id}' not found in graph", file=sys.stderr)
            sys.exit(1)
        if len(matches) > 1:
            print(f"Ambiguous entity '{entity_id}'. Matches:", file=sys.stderr)
            for m in matches:
                print(f"  {m}", file=sys.stderr)
            sys.exit(1)
        entity_id = matches[0]

    reachable = bfs_reachability(entity_id, adj, args.max_hops)

    print(f"Blast radius for: {entity_id}")
    print(f"Max hops: {args.max_hops}")
    print(f"Affected entities: {len(reachable)}")
    print()

    if not reachable:
        print("No entities reachable within hop limit.")
        sys.exit(0)

    print(f"{'Hop':<5} {'Entity ID':<50} {'Type':<10} {'Drawers'}")
    print("-" * 80)
    for r in reachable:
        node = nodes_by_id.get(r["entity_id"], {})
        drawer_count = len(node.get("drawer_ids", node.get("drawer_count", [])))
        if isinstance(drawer_count, list):
            drawer_count = len(drawer_count)
        print(f"{r['hop_distance']:<5} {r['entity_id']:<50} {node.get('type', '-'):<10} {drawer_count}")


if __name__ == "__main__":
    main()
