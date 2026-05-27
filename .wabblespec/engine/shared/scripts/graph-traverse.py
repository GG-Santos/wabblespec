"""
graph-traverse.py — Shared BFS/DFS traversal over WabbleSpec graph JSON files.
Consumers: nexus, shift, memory

Usage:
    python graph-traverse.py --graph <path> --start <node_id> [options]

Options:
    --graph     Path to graph JSON (nexus/graph.json or entity-graph.json)
    --start     Starting node ID
    --mode      bfs | dfs (default: bfs)
    --max-hops  Maximum edge depth (default: 3)
    --direction outbound | inbound | both (default: outbound)
    --filter-type  Only traverse edges of this type
    --output    Path to write result JSON (default: stdout)
"""

import argparse
import json
import sys
from collections import deque
from pathlib import Path


def load_graph(graph_path: str) -> dict:
    p = Path(graph_path)
    if not p.exists():
        print(f"ERROR: graph file not found: {graph_path}", file=sys.stderr)
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build_adjacency(nodes: list, edges: list, direction: str, filter_type: str | None) -> dict:
    adj: dict[str, list[dict]] = {n["id"]: [] for n in nodes}
    for edge in edges:
        etype = edge.get("type", "")
        if filter_type and etype != filter_type:
            continue
        src = edge.get("source") or edge.get("from")
        tgt = edge.get("target") or edge.get("to")
        if src is None or tgt is None:
            continue
        if direction in ("outbound", "both"):
            if src in adj:
                adj[src].append({"neighbor": tgt, "edge": edge})
        if direction in ("inbound", "both"):
            if tgt in adj:
                adj[tgt].append({"neighbor": src, "edge": edge})
    return adj


def bfs(start: str, adj: dict, max_hops: int) -> list[dict]:
    visited: set[str] = set()
    queue: deque[tuple[str, int, list]] = deque()
    queue.append((start, 0, []))
    result: list[dict] = []

    while queue:
        node_id, depth, path = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        result.append({"node_id": node_id, "depth": depth, "path": path})
        if depth >= max_hops:
            continue
        for entry in adj.get(node_id, []):
            neighbor = entry["neighbor"]
            if neighbor not in visited:
                edge_label = entry["edge"].get("type", "unknown")
                queue.append((neighbor, depth + 1, path + [f"{node_id}-[{edge_label}]->{neighbor}"]))

    return result


def dfs(start: str, adj: dict, max_hops: int) -> list[dict]:
    visited: set[str] = set()
    result: list[dict] = []

    def _dfs(node_id: str, depth: int, path: list[str]) -> None:
        if node_id in visited or depth > max_hops:
            return
        visited.add(node_id)
        result.append({"node_id": node_id, "depth": depth, "path": path})
        for entry in adj.get(node_id, []):
            neighbor = entry["neighbor"]
            edge_label = entry["edge"].get("type", "unknown")
            _dfs(neighbor, depth + 1, path + [f"{node_id}-[{edge_label}]->{neighbor}"])

    _dfs(start, 0, [])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Shared BFS/DFS graph traversal")
    parser.add_argument("--graph", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--mode", choices=["bfs", "dfs"], default="bfs")
    parser.add_argument("--max-hops", type=int, default=3)
    parser.add_argument("--direction", choices=["outbound", "inbound", "both"], default="outbound")
    parser.add_argument("--filter-type", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    graph = load_graph(args.graph)
    nodes: list = graph.get("nodes", [])
    edges: list = graph.get("edges", [])

    node_ids = {n["id"] for n in nodes}
    if args.start not in node_ids:
        print(f"ERROR: start node '{args.start}' not in graph", file=sys.stderr)
        sys.exit(1)

    adj = build_adjacency(nodes, edges, args.direction, args.filter_type)

    if args.mode == "bfs":
        traversal = bfs(args.start, adj, args.max_hops)
    else:
        traversal = dfs(args.start, adj, args.max_hops)

    output = {
        "start": args.start,
        "mode": args.mode,
        "max_hops": args.max_hops,
        "direction": args.direction,
        "filter_type": args.filter_type,
        "node_count": len(traversal),
        "nodes": traversal,
    }

    out_json = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(out_json, encoding="utf-8")
        print(f"Traversal written: {args.output} ({len(traversal)} nodes)")
    else:
        print(out_json)


if __name__ == "__main__":
    main()
