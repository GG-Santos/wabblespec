# Cold-Start Behavior — Nexus

Defines what Nexus does when its expected graph or memory inputs are absent.

## Absent: entity-graph.json

Condition: `entity-graph.json` does not exist.
Detection: File read returns 404.
Action: Surface to user: "Nexus requires entity-graph.json. Run entity-graph to build it first." Do NOT run Nexus without the graph.
Do NOT: Build the graph inline during a Nexus query — these are separate operations.

## Absent: memory store

Condition: `memory/` is empty or does not exist.
Detection: Index read returns empty.
Action: Nexus returns empty results. Log: "Memory store empty — no nodes or relationships to query." Surface to user: "No memory content exists yet. Run Memory Mine after completing sessions."

## Absent: graph-traverse.py script

Condition: `_shared/scripts/graph-traverse.py` not found.
Detection: Script read returns 404.
Action: Fall back to linear drawer scan without graph traversal. Log: "graph-traverse.py missing — relationship traversal unavailable. Results will be unranked drawer matches."

## Absent: bm25.py script

Condition: `_shared/scripts/bm25.py` not found.
Action: Fall back to keyword matching. Log: "bm25.py unavailable — using keyword fallback."

## Absent: query-types.md

Condition: `rules/query-types.md` missing.
Detection: File read returns 404.
Action: Apply known query types from SKILL.md defaults. Log: "query-types.md missing — using SKILL.md defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `graph_available` | false — requires entity-graph.json |
| `traversal_mode` | graph (if graph-traverse.py available); linear fallback otherwise |
| `result_limit` | 10 nodes per query |
| `min_edge_weight` | 1 (include all edges) |
| `query_scope` | All entity types (file, module, concept) |
