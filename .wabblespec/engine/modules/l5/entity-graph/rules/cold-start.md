# Cold-Start Behavior — Entity Graph

Defines what Entity Graph does when its expected inputs or output artifacts are absent.

## Absent: memory store to build from

Condition: `memory/` is empty or has fewer than 3 drawers.
Detection: Index read returns fewer than 3 drawers.
Action: Build an empty graph — `entity-graph.json` with `{"nodes": [], "edges": []}`. Log: "Fewer than 3 drawers found — entity graph will be empty until more memory exists."
Do NOT: Block the run. An empty graph is valid.

## Absent: prior entity-graph.json

Condition: `entity-graph.json` does not exist.
Detection: File read returns 404.
Action: Treat as first run. Build graph from scratch from all current drawers. No incremental update — full build.

## Absent: entity-report.md output target

Condition: `entity-report.md` does not exist when Entity Graph attempts to write it.
Detection: File absent.
Action: Create the file. This is normal on first run.

## Absent: graph-traverse.py (dependency check)

Condition: `.wabblespec/engine/shared/scripts/graph-traverse.py` missing.
Detection: File read returns 404.
Action: Log: "graph-traverse.py unavailable — entity-graph.json will be built but graph traversal by Nexus will fall back to linear scan."
Do NOT: Block entity graph build. The graph output is still valid.

## Default state on cold start

| Field | Default |
|---|---|
| `entity_types` | file, module, concept (3 types — no 4th type until 50+ drawers + failed query need) |
| `edge_weight` | 1 per co-occurrence in same drawer |
| `min_degree` | 1 (all nodes included regardless of connection count) |
| `build_mode` | full (first run); incremental (subsequent runs if prior graph exists) |
| `dry_run` | false (writes output files) |
