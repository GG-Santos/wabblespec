#!/usr/bin/env python3
"""
WabbleSpec Nexus — graph-builder.py

Reads entity-graph.json + Memory drawers. Builds/checks a relationship graph
with drawer_id-backed nodes. Writes to .wabblespec/nexus/graph.json.

Freshness states (based on new drawers since last graph build):
  FRESH  < 20 new drawers
  AGING  20-50 new drawers
  STALE  > 50 new drawers

Usage:
  python modules/l5/nexus/scripts/graph-builder.py
  python modules/l5/nexus/scripts/graph-builder.py --check-freshness
  python modules/l5/nexus/scripts/graph-builder.py --scope <file1> <file2> ...
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


FRESH_THRESHOLD = 20
STALE_THRESHOLD = 50


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


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def count_drawers(wings_root: Path) -> int:
    if not wings_root.exists():
        return 0
    return len(list(wings_root.rglob("*.json")))


def get_freshness(graph_data: dict, current_drawer_count: int) -> str:
    last_scanned = graph_data.get("drawers_scanned", 0)
    new_drawers = max(0, current_drawer_count - last_scanned)
    if new_drawers < FRESH_THRESHOLD:
        return "FRESH"
    elif new_drawers <= STALE_THRESHOLD:
        return "AGING"
    return "STALE"


def load_drawers(wings_root: Path) -> list[dict]:
    drawers = []
    for dp in wings_root.rglob("*.json"):
        raw = load_json(dp)
        if isinstance(raw, dict):
            # Attach source path for drawer_id resolution
            raw["_source_path"] = str(dp)
            drawers.append(raw)
    return drawers


def resolve_drawer_id(drawer: dict) -> str:
    """Return the canonical drawer_id for a drawer record."""
    return (
        drawer.get("drawer_id")
        or drawer.get("id")
        or drawer.get("_source_path", "unknown")
    )


def build_nexus_graph(entity_graph: dict, drawers: list[dict]) -> dict:
    """
    Build a Nexus relationship graph from entity-graph.json and Memory drawers.

    Nexus graph nodes extend EntityGraph nodes with drawer_ids — the list of
    drawer_id values that evidence each entity. This backs every entity against
    at least one Memory drawer (architecture requirement A5).
    """
    run_ts = datetime.now(timezone.utc).isoformat()

    # Index entity-graph nodes by id
    eg_nodes = {n["id"]: n for n in entity_graph.get("nodes", [])}
    eg_edges = entity_graph.get("edges", [])

    # Build drawer_id index: entity_id -> [drawer_ids]
    entity_drawer_ids: dict[str, list[str]] = {}

    for drawer in drawers:
        drawer_id = resolve_drawer_id(drawer)
        # Collect all text to match against entity labels
        text_parts = []
        for field in ("topic", "body", "tags"):
            val = drawer.get(field)
            if isinstance(val, list):
                text_parts.extend(str(v) for v in val)
            elif val:
                text_parts.append(str(val))
        evidence = drawer.get("evidence", [])
        if isinstance(evidence, list):
            text_parts.extend(str(e) for e in evidence)
        elif evidence:
            text_parts.append(str(evidence))
        full_text = " ".join(text_parts).lower()

        for eid, node in eg_nodes.items():
            label = node.get("label", "").lower()
            if label and label in full_text:
                entity_drawer_ids.setdefault(eid, [])
                if drawer_id not in entity_drawer_ids[eid]:
                    entity_drawer_ids[eid].append(drawer_id)

    # Build Nexus nodes (EntityGraph nodes + drawer_ids)
    nexus_nodes = []
    for eid, node in eg_nodes.items():
        nexus_node = dict(node)
        nexus_node["drawer_ids"] = entity_drawer_ids.get(eid, [])
        nexus_nodes.append(nexus_node)

    # Nexus edges — same as EntityGraph edges, augmented with relationship type
    nexus_edges = []
    for edge in eg_edges:
        nexus_edges.append({
            "source": edge.get("source"),
            "target": edge.get("target"),
            "weight": edge.get("weight", 1),
            "edge_type": "co-occurrence",
        })

    return {
        "version": "1.0",
        "generated": run_ts,
        "drawers_scanned": len(drawers),
        "node_count": len(nexus_nodes),
        "edge_count": len(nexus_edges),
        "nodes": nexus_nodes,
        "edges": nexus_edges,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Nexus graph-builder")
    parser.add_argument("--check-freshness", action="store_true",
                        help="Report freshness state only, do not rebuild")
    parser.add_argument("--scope", nargs="*", default=[],
                        help="Limit rebuild to edges involving these file paths (targeted update)")
    args = parser.parse_args()

    try:
        ws_root = find_ws_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    wings_root = ws_root / "memory" / "wings"
    entity_graph_path = ws_root / "memory" / "entity-graph.json"
    nexus_dir = ws_root / "nexus"
    graph_path = nexus_dir / "graph.json"

    current_drawer_count = count_drawers(wings_root)

    # Check freshness mode
    if args.check_freshness:
        existing = load_json(graph_path)
        if existing is None:
            print("STALE (no graph built yet)")
            sys.exit(0)
        freshness = get_freshness(existing, current_drawer_count)
        print(freshness)
        sys.exit(0)

    # Load entity-graph
    entity_graph = load_json(entity_graph_path)
    if entity_graph is None:
        print("ERROR: entity-graph.json not found — run entity-graph.py first", file=sys.stderr)
        sys.exit(1)

    # Load drawers
    if not wings_root.exists():
        print("No wings directory — no drawers to process.")
        sys.exit(0)

    drawers = load_drawers(wings_root)
    if not drawers:
        print("No drawers found.")
        sys.exit(0)

    graph = build_nexus_graph(entity_graph, drawers)
    save_json(graph_path, graph)

    freshness = get_freshness(graph, current_drawer_count)
    print(f"graph-builder complete")
    print(f"  nodes        : {graph['node_count']}")
    print(f"  edges        : {graph['edge_count']}")
    print(f"  drawers used : {len(drawers)}")
    print(f"  freshness    : {freshness}")
    print(f"  output       : {graph_path}")


if __name__ == "__main__":
    main()
