#!/usr/bin/env python3
"""
WabbleSpec Nexus — pattern-matcher.py

Reads graph.json. Given --domain <term>, finds co-occurrence clusters
with frequency counts. Outputs top patterns ranked by frequency.

Usage:
  python modules/l5/nexus/scripts/pattern-matcher.py --domain "authentication"
  python modules/l5/nexus/scripts/pattern-matcher.py --domain "guard" --top 10
"""
import argparse
import json
import sys
from collections import defaultdict
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


def find_domain_nodes(domain: str, nodes: list[dict]) -> list[str]:
    """Return entity IDs whose label contains the domain term."""
    domain_lower = domain.lower()
    return [n["id"] for n in nodes if domain_lower in n.get("label", "").lower()]


def find_co_occurrence_clusters(
    domain_ids: set[str],
    edges: list[dict],
    nodes_by_id: dict,
) -> list[dict]:
    """
    Find all nodes that co-occur (share an edge) with any domain node.
    Group by co-occurring node, sum edge weights as frequency.
    """
    cluster_freq: dict[str, int] = defaultdict(int)
    cluster_domain_nodes: dict[str, list[str]] = defaultdict(list)

    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        weight = edge.get("weight", 1)

        if src in domain_ids and tgt not in domain_ids:
            cluster_freq[tgt] += weight
            cluster_domain_nodes[tgt].append(src)
        elif tgt in domain_ids and src not in domain_ids:
            cluster_freq[src] += weight
            cluster_domain_nodes[src].append(tgt)
        elif src in domain_ids and tgt in domain_ids:
            # Both domain — cross-cluster within domain
            cluster_freq[src] += weight
            cluster_domain_nodes[src].append(tgt)

    patterns = []
    for entity_id, freq in cluster_freq.items():
        node = nodes_by_id.get(entity_id, {})
        patterns.append({
            "entity_id": entity_id,
            "label": node.get("label", entity_id),
            "type": node.get("type", "unknown"),
            "frequency": freq,
            "co_occurs_with": list(set(cluster_domain_nodes[entity_id])),
            "drawer_ids": node.get("drawer_ids", []),
        })

    return sorted(patterns, key=lambda p: -p["frequency"])


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Nexus pattern-matcher")
    parser.add_argument("--domain", required=True,
                        help="Domain term to find patterns for. e.g. 'guard', 'authentication'")
    parser.add_argument("--top", type=int, default=15,
                        help="Number of top patterns to return (default: 15)")
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

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    nodes_by_id = {n["id"]: n for n in nodes}

    domain_ids = set(find_domain_nodes(args.domain, nodes))
    if not domain_ids:
        print(f"No entities found matching domain '{args.domain}'")
        sys.exit(0)

    patterns = find_co_occurrence_clusters(domain_ids, edges, nodes_by_id)
    top_patterns = patterns[:args.top]

    print(f"Pattern discovery for domain: '{args.domain}'")
    print(f"Domain entities found: {len(domain_ids)}")
    print(f"  {', '.join(sorted(domain_ids))}")
    print(f"Top {len(top_patterns)} co-occurrence patterns:")
    print()

    if not top_patterns:
        print("No co-occurrence patterns found.")
        sys.exit(0)

    print(f"{'Rank':<5} {'Frequency':<10} {'Type':<10} {'Entity'}")
    print("-" * 70)
    for i, p in enumerate(top_patterns, 1):
        print(f"{i:<5} {p['frequency']:<10} {p['type']:<10} {p['label']}")
        if p["co_occurs_with"]:
            co_labels = [nodes_by_id.get(c, {}).get("label", c) for c in p["co_occurs_with"][:3]]
            print(f"      co-occurs with: {', '.join(co_labels)}")
        if p["drawer_ids"]:
            print(f"      evidence drawers: {len(p['drawer_ids'])}")
        print()


if __name__ == "__main__":
    main()
