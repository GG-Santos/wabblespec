#!/usr/bin/env python3
"""
WabbleSpec EntityGraph script.

Reads all drawers, extracts 3 entity types (file, module, concept),
builds co-occurrence relationship graph, writes:
  .wabblespec/memory/entity-graph.json   -- nodes + edges
  .wabblespec/memory/entity-report.md   -- human-readable summary

Entity types:
  file    -- path-like strings in drawer evidence/topic
  module  -- known WabbleSpec module IDs mentioned in drawer
  concept -- drawer topic + tags

Edge weight = number of drawers in which two entities co-occur.

Usage:
  python modules/l5/entity-graph/scripts/entity-graph.py
  python modules/l5/entity-graph/scripts/entity-graph.py --dry-run
  python modules/l5/entity-graph/scripts/entity-graph.py --query <term>
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

try:
    for p in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents, Path.cwd(), *Path.cwd().parents]:
        if (p / ".wabblespec").is_dir():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            break
    from _shared.memory_backend import get_knowledge_graph
    _HAS_KG = True
except ImportError:
    _HAS_KG = False

# Minimum co-occurrence weight to write a KG triple
KG_EDGE_WEIGHT_THRESHOLD = 2

# ── Known module IDs ──────────────────────────────────────────────────────────

KNOWN_MODULES = {
    "recipe", "specify", "scope-frame", "decompose", "executor",
    "verifier", "guard", "archive", "reviewer", "apply", "scaffold",
    "rollback", "autopilot", "team-plan", "memory", "memory-search",
    "provenance", "entity-graph", "dream", "memory-mine", "forget",
    "platform-cli", "platform-web", "platform-api-service",
    "gateway-security", "gateway-engineering", "gateway-ai",
    "homowabian", "economy", "document", "polish", "research-log",
    "instinct", "synth", "blueprint", "factory", "augment",
    "benchmark", "forge", "retro", "feedback",
}

# ── Path-like pattern ─────────────────────────────────────────────────────────

# Matches: path/to/file.ext  OR  path/to/directory/
FILE_PATTERN = re.compile(
    r'\b(?:[a-zA-Z0-9_\-]+/){1,}[a-zA-Z0-9_\-]*(?:\.[a-zA-Z]{1,10})?\b'
)

# ── I/O helpers ───────────────────────────────────────────────────────────────

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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


# ── Entity extraction ─────────────────────────────────────────────────────────

def extract_entities(drawer: dict) -> dict[str, set[str]]:
    """Return {'file': set, 'module': set, 'concept': set} from one drawer."""
    entities: dict[str, set[str]] = {"file": set(), "module": set(), "concept": set()}

    # Gather all text fields to scan
    text_parts: list[str] = []
    if drawer.get("topic"):
        text_parts.append(str(drawer["topic"]))
    if drawer.get("body"):
        text_parts.append(str(drawer["body"]))
    evidence = drawer.get("evidence", [])
    if isinstance(evidence, list):
        for e in evidence:
            text_parts.append(str(e))
    elif isinstance(evidence, str):
        text_parts.append(evidence)

    full_text = " ".join(text_parts)

    # file entities
    for match in FILE_PATTERN.finditer(full_text):
        candidate = match.group(0)
        # Skip if it looks like a URL fragment or date
        if re.match(r'\d{4}/\d{2}/\d{2}', candidate):
            continue
        entities["file"].add(candidate)

    # module entities — exact word-boundary match against known set
    for token in re.split(r'[\s,;:()\[\]`"\']+', full_text):
        token = token.strip().lower()
        if token in KNOWN_MODULES:
            entities["module"].add(token)

    # concept entities — topic field + tags
    if drawer.get("topic"):
        topic = str(drawer["topic"]).strip()
        if topic:
            entities["concept"].add(topic.lower())
    tags = drawer.get("tags", [])
    if isinstance(tags, list):
        for tag in tags:
            tag = str(tag).strip().lower()
            if tag:
                entities["concept"].add(tag)

    return entities


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph(drawers: list[dict]) -> tuple[dict, dict]:
    """
    Returns:
      nodes: {entity_id -> {type, label, drawer_count, drawer_ids}}
      edges: {(id_a, id_b) -> weight}  -- id_a < id_b always
    """
    node_drawer_count: dict[str, int] = defaultdict(int)
    node_type: dict[str, str] = {}
    node_drawer_ids: dict[str, list[str]] = defaultdict(list)
    edge_weight: dict[tuple[str, str], int] = defaultdict(int)

    for drawer in drawers:
        # Resolve canonical drawer_id for this drawer record
        drawer_id = (
            drawer.get("drawer_id")
            or drawer.get("id")
            or str(drawer.get("_source_path", "unknown"))
        )
        extracted = extract_entities(drawer)
        # Collect all entity IDs from this drawer
        drawer_entity_ids: list[str] = []

        for etype, labels in extracted.items():
            for label in labels:
                eid = f"{etype}::{label}"
                node_drawer_count[eid] += 1
                node_type[eid] = etype
                drawer_entity_ids.append(eid)
                # Track which drawers contributed to this entity (D6 fix)
                if drawer_id not in node_drawer_ids[eid]:
                    node_drawer_ids[eid].append(drawer_id)

        # Co-occurrence edges within this drawer
        for a, b in combinations(sorted(set(drawer_entity_ids)), 2):
            key = (a, b) if a < b else (b, a)
            edge_weight[key] += 1

    nodes = {
        eid: {
            "id": eid,
            "type": node_type[eid],
            "label": eid.split("::", 1)[1] if "::" in eid else eid,
            "drawer_count": count,
            "drawer_ids": node_drawer_ids[eid],
        }
        for eid, count in node_drawer_count.items()
    }

    edges = {f"{a}|||{b}": w for (a, b), w in edge_weight.items()}

    return nodes, edges


# ── Output builders ───────────────────────────────────────────────────────────

def build_graph_json(nodes: dict, edges: dict, run_ts: str, drawer_count: int) -> dict:
    node_list = sorted(nodes.values(), key=lambda n: (-n["drawer_count"], n["label"]))
    edge_list = []
    for key, weight in sorted(edges.items(), key=lambda kv: -kv[1]):
        a, b = key.split("|||", 1)
        edge_list.append({"source": a, "target": b, "weight": weight})

    return {
        "version": "1.0",
        "generated": run_ts,
        "drawers_scanned": drawer_count,
        "node_count": len(node_list),
        "edge_count": len(edge_list),
        "nodes": node_list,
        "edges": edge_list,
    }


def build_report(nodes: dict, edges: dict, run_ts: str, drawer_count: int) -> str:
    type_counts: dict[str, int] = defaultdict(int)
    for n in nodes.values():
        type_counts[n["type"]] += 1

    # Degree = number of edges a node participates in
    degree: dict[str, int] = defaultdict(int)
    for key in edges:
        a, b = key.split("|||", 1)
        degree[a] += 1
        degree[b] += 1

    top_by_degree = sorted(degree.items(), key=lambda kv: -kv[1])[:20]
    top_edges = sorted(edges.items(), key=lambda kv: -kv[1])[:15]

    lines = [
        "# Entity Graph Report",
        "",
        f"> Generated: {run_ts}",
        f"> Drawers scanned: {drawer_count}",
        f"> Nodes: {len(nodes)}  Edges: {len(edges)}",
        "",
        "## Entity Type Breakdown",
        "",
    ]
    for etype in ("concept", "module", "file"):
        lines.append(f"- {etype}: {type_counts.get(etype, 0)}")

    lines += [
        "",
        "## Top 20 Entities by Degree (most connected)",
        "",
        "| Entity | Type | Degree | Drawer count |",
        "|---|---|---|---|",
    ]
    for eid, deg in top_by_degree:
        n = nodes.get(eid, {})
        lines.append(
            f"| {n.get('label', eid)} | {n.get('type', '-')} "
            f"| {deg} | {n.get('drawer_count', 0)} |"
        )

    lines += [
        "",
        "## Top 15 Relationships (highest co-occurrence weight)",
        "",
        "| Entity A | Entity B | Weight |",
        "|---|---|---|",
    ]
    for key, weight in top_edges:
        a, b = key.split("|||", 1)
        label_a = nodes.get(a, {}).get("label", a)
        label_b = nodes.get(b, {}).get("label", b)
        lines.append(f"| {label_a} | {label_b} | {weight} |")

    lines += [
        "",
        "---",
        "",
        "## Expansion rule",
        "",
        "Do not add a 4th entity type until 50+ drawers exist AND a real query "
        "fails because the missing type would have answered it.",
    ]

    return "\n".join(lines) + "\n"


# ── Knowledge Graph writer ────────────────────────────────────────────────────

def write_kg_triples(
    nodes: dict,
    edges: dict,
    drawers: list[dict],
    kg_path: Path,
    run_ts: str,
    dry_run: bool,
) -> tuple[int, int]:
    """Write co-occurrence triples (weight >= threshold) to SQLite KG.

    Also writes 'supersedes' triples for SUPERSEDED drawers and calls
    invalidate() for EXPIRED / SUPERSEDED drawers' is_active edge.

    Returns (triples_written, invalidations_applied).
    """
    if not _HAS_KG:
        return 0, 0

    triples_written = 0
    invalidations = 0

    if dry_run:
        # Count only — don't open the DB
        for key, weight in edges.items():
            if weight >= KG_EDGE_WEIGHT_THRESHOLD:
                triples_written += 1
        return triples_written, 0

    kg = get_knowledge_graph()

    # KG requires YYYY-MM-DDTHH:MM:SSZ format
    kg_ts = run_ts[:19] + "Z" if "+" in run_ts or run_ts.endswith("Z") else run_ts[:19] + "Z"

    # Co-occurrence triples
    for key, weight in edges.items():
        if weight < KG_EDGE_WEIGHT_THRESHOLD:
            continue
        a, b = key.split("|||", 1)
        label_a = nodes.get(a, {}).get("label", a)
        label_b = nodes.get(b, {}).get("label", b)
        kg.add_triple(
            subject=label_a,
            predicate="co-occurs-with",
            obj=label_b,
            valid_from=kg_ts,
            confidence=min(1.0, weight / 10.0),
            source_drawer_id=key,
        )
        triples_written += 1

    # Supersession + invalidation triples per drawer
    now_iso = kg_ts
    for drawer in drawers:
        state = drawer.get("staleness_state", "FRESH")
        drawer_id = drawer.get("id") or drawer.get("drawer_id") or ""
        if not drawer_id:
            continue

        if state in ("EXPIRED", "SUPERSEDED"):
            try:
                kg.invalidate(
                    subject=drawer_id,
                    predicate="is_active",
                    obj="true",
                    ended=now_iso,
                )
                invalidations += 1
            except Exception:
                pass  # Triple may not exist yet — that's fine

        superseded_by = drawer.get("superseded_by")
        if state == "SUPERSEDED" and superseded_by:
            try:
                kg.add_triple(
                    subject=superseded_by,
                    predicate="supersedes",
                    obj=drawer_id,
                    valid_from=now_iso,
                    confidence=1.0,
                )
            except Exception:
                pass

    kg.close()
    return triples_written, invalidations


# ── Entity registry builder ────────────────────────────────────────────────────

def build_entity_registry(nodes: dict, run_ts: str, drawer_count: int) -> dict:
    """Build a structured entity registry for external consumption."""
    registry: dict[str, list] = {"concept": [], "module": [], "file": []}
    for eid, node in nodes.items():
        etype = node.get("type", "concept")
        if etype in registry:
            registry[etype].append({
                "id": eid,
                "label": node["label"],
                "drawer_count": node["drawer_count"],
                "drawer_ids": node.get("drawer_ids", []),
            })
    for etype in registry:
        registry[etype].sort(key=lambda e: -e["drawer_count"])

    return {
        "version": "1.0",
        "generated": run_ts,
        "drawers_scanned": drawer_count,
        "entity_counts": {k: len(v) for k, v in registry.items()},
        "entities": registry,
    }


# ── Query filter ──────────────────────────────────────────────────────────────

def filter_by_query(nodes: dict, edges: dict, query: str) -> tuple[dict, dict]:
    """Return subgraph containing only nodes whose label contains query."""
    q = query.lower()
    matched_ids = {eid for eid, n in nodes.items() if q in n["label"].lower()}
    # Include all neighbors of matched nodes
    neighbor_ids: set[str] = set(matched_ids)
    for key in edges:
        a, b = key.split("|||", 1)
        if a in matched_ids or b in matched_ids:
            neighbor_ids.add(a)
            neighbor_ids.add(b)

    filtered_nodes = {eid: n for eid, n in nodes.items() if eid in neighbor_ids}
    filtered_edges = {
        key: w for key, w in edges.items()
        if key.split("|||")[0] in neighbor_ids and key.split("|||")[1] in neighbor_ids
    }
    return filtered_nodes, filtered_edges


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec EntityGraph — entity extraction and co-occurrence graph")
    parser.add_argument("--dry-run", action="store_true", help="Compute without writing files")
    parser.add_argument("--query", type=str, default="", help="Filter output to subgraph containing this term")
    args = parser.parse_args()

    try:
        ws_root = find_ws_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    memory_root = ws_root / "memory"
    wings_root = memory_root / "wings"
    graph_path = memory_root / "entity-graph.json"
    report_path = memory_root / "entity-report.md"
    registry_path = memory_root / "entity-registry.json"
    kg_path = memory_root / "knowledge_graph.sqlite3"

    if not wings_root.exists():
        print("No wings directory found — no drawers to process.")
        sys.exit(0)

    run_ts = datetime.now(timezone.utc).isoformat()

    # Load all drawers
    drawer_paths = list(wings_root.rglob("*.json"))
    drawers: list[dict] = []
    errors: list[str] = []

    for dp in drawer_paths:
        d = load_json(dp)
        if isinstance(d, dict):
            d["_source_path"] = str(dp)
            drawers.append(d)
        else:
            errors.append(f"parse error: {dp}")

    if not drawers:
        print("No drawers found — nothing to graph.")
        sys.exit(0)

    # Build graph
    nodes, edges = build_graph(drawers)

    # Apply query filter if requested
    display_nodes, display_edges = nodes, edges
    if args.query:
        display_nodes, display_edges = filter_by_query(nodes, edges, args.query)
        print(f"Query '{args.query}': {len(display_nodes)} nodes, {len(display_edges)} edges in subgraph")

    # Build outputs
    graph_data = build_graph_json(display_nodes, display_edges, run_ts, len(drawers))
    report_content = build_report(display_nodes, display_edges, run_ts, len(drawers))
    registry_data = build_entity_registry(display_nodes, run_ts, len(drawers))

    # KG writes (always use full graph, not query-filtered subgraph)
    triples_written, invalidations = write_kg_triples(
        nodes, edges, drawers, kg_path, run_ts, args.dry_run
    )

    if not args.dry_run:
        try:
            save_json(graph_path, graph_data)
            save_text(report_path, report_content)
            save_json(registry_path, registry_data)
        except OSError as exc:
            print(f"ERROR writing output: {exc}", file=sys.stderr)
            sys.exit(1)

    # Report
    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"entity-graph {prefix}complete")
    print(f"  drawers processed   : {len(drawers)}")
    print(f"  nodes               : {len(display_nodes)}")
    print(f"  edges               : {len(display_edges)}")
    type_counts: dict[str, int] = defaultdict(int)
    for n in display_nodes.values():
        type_counts[n["type"]] += 1
    for etype in ("concept", "module", "file"):
        if type_counts[etype]:
            print(f"    {etype}: {type_counts[etype]}")
    kg_label = "(WabbleSpec Memory KG unavailable)" if not _HAS_KG else ""
    print(f"  KG triples written  : {triples_written} {kg_label}")
    print(f"  KG invalidations    : {invalidations} {kg_label}")
    if not args.dry_run:
        print(f"  entity-graph.json  : {graph_path}")
        print(f"  entity-report.md   : {report_path}")
        print(f"  entity-registry.json: {registry_path}")
        if _HAS_KG:
            print(f"  knowledge_graph.sqlite3: {kg_path}")
    if errors:
        print(f"  errors: {len(errors)}", file=sys.stderr)
        for e in errors:
            print(f"    {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
