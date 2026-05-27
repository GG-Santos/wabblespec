# Graph Intelligence Gate

Status: Deferred — gate not yet met
Source pattern: `graphify-7` (extract/query/path/analyze)
Modules implicated: EntityGraph, Dream, MemoryMine

This document defines:

1. What full-text failure cases look like — and how to collect them
2. What the graph MVP would add to EntityGraph, Dream, and MemoryMine
3. The activation gate — criteria that must be met before implementing

---

## Why a gate exists

The EntityGraph module already has a KG backend (`WabbleSpec Memory.knowledge_graph`, SQLite). What it does NOT have is traversal operations: BFS discovery, shortest path, community detection, and god-node analysis. These come from graphify-7's `analyze.py`, `query`, and `path` patterns.

The gate rule from the master plan is:

> "What Not To Borrow: graph before corpus."

Graph traversal is only valuable when the corpus is large enough to produce non-trivial path structure. Full-text search (MemorySearch) is cheaper and often sufficient. Graph pays off only when full-text demonstrably fails on real queries.

---

## Full-text failure taxonomy

These are the case types where full-text (MemorySearch / ChromaDB semantic search) fails and graph traversal wins.

| Case type | Full-text result | Graph result |
|---|---|---|
| Multi-hop dependency | Returns drawers similar to query — misses transitive chain | BFS from entity follows edges: A → B → C |
| Path existence | Cannot confirm "does a dependency chain exist between X and Y" | Shortest path query returns YES/NO + edge list |
| Blast radius | Cannot enumerate "all modules affected if X changes" | BFS traversal from X, depth-limited, returns all co-occurring modules |
| Community membership | Returns similar drawers but not structural cluster | Community detection via `cluster.py` pattern |
| Orphan detection | Cannot identify entities with no edges (isolated facts) | God-node inverse: find degree-0 nodes |

### How to log a failure case

When MemorySearch returns results that feel incomplete or misleading, record:

```json
{
  "query": "the query string used",
  "expected": "what the answer should have been",
  "memorysearch_result": "what full-text returned",
  "failure_type": "multi-hop | path-existence | blast-radius | community | orphan",
  "drawer_count_at_time": 0,
  "date": "ISO-8601"
}
```

File at: `.wabblespec/state/memory/graph-failure-cases.jsonl` (append-only, one JSON object per line).

Dream should surface any entries in this file in its gap-map when `failure_type` count ≥ 3.

---

## Graph MVP — what to add to EntityGraph

Adapted from graphify-7 `analyze.py`, `query` (BFS/DFS), `path` (shortest path). Only add these when the activation gate is met.

### Operation 1: BFS query

Graphify-7 pattern: `graphify query "<question>"` — BFS traversal from matching nodes, returns neighbors in breadth order.

WabbleSpec adaptation:

```bash
python modules/l5/entity-graph/scripts/entity-graph.py --query "receipt-schema" --mode bfs --depth 3
```

Implementation: read KG triples from SQLite. Starting from entity matching the query term, walk outbound edges (`predicate` in [depends-on, references, co-occurs-with]) up to `--depth` hops. Return entity list with edge path.

Do NOT return INFERRED edges (confidence < 0.5) in BFS results by default. Add `--include-inferred` flag for explicit opt-in.

### Operation 2: Shortest path

Graphify-7 pattern: `graphify path "AuthModule" "Database"` — BFS between two named nodes.

WabbleSpec adaptation:

```bash
python modules/l5/entity-graph/scripts/entity-graph.py --path "receipt-schema" "executor"
```

Implementation: bidirectional BFS on the KG. Returns path as edge list with predicates, or "NO PATH" if disconnected. Respect `valid_to` — only traverse active (non-expired) edges.

### Operation 3: God-node detection

Graphify-7 pattern: `god_nodes(G)` — nodes with unusually high degree, structural importance.

WabbleSpec adaptation: entities with the highest co-occurrence count across the KG. High-degree entities are "load-bearing" — changes to them have wide blast radius.

```bash
python modules/l5/entity-graph/scripts/entity-graph.py --god-nodes --top 10
```

Already partially supported — `entity-report.md` contains "top entities by degree." Formalize this as a named operation.

### Operation 4: Surprising connections

Graphify-7 pattern: `surprising_connections(G, communities)` — edges that cross community boundaries.

WabbleSpec adaptation: entity pairs with `co-occurs-with` predicates that belong to different drawer wings. Surfaces unexpected cross-domain dependencies.

Add to `entity-report.md` as a new section: "Cross-wing connections."

---

## Dream integration

Dream currently: EMA decay, gap-map, staleness-map.

Graph adds to Dream (when activated):

- Append a **connectivity section** to `gap-map.md`: entities that appear in drawers but have no KG edges (degree 0). These are isolated facts with no relationship context — high-value targets for follow-up.
- Surface failure cases from `.wabblespec/state/memory/graph-failure-cases.jsonl` in gap-map when count ≥ 3. Label as: `GRAPH_GATE: N full-text failures logged — graph MVP may be warranted`.

Dream does NOT run graph traversal itself. It reads `entity-graph.json` (already produced by EntityGraph) and appends to its gap-map.

---

## MemoryMine integration

MemoryMine currently: gap detection, cluster detection, pattern analysis.

Graph adds to MemoryMine (when activated):

- After cluster detection, cross-reference drawer clusters with EntityGraph communities. Flag mismatches: drawers that cluster together semantically but have no KG edges between their entities.
- These mismatches are the highest-value graph integration candidates — they show where the KG lacks edges that the semantic layer already implies.

MemoryMine does NOT implement the KG itself. It reads `entity-graph.json` as a second input layer alongside its drawer cluster results.

---

## Activation gate

Do NOT implement any of the above MVP operations until ALL of the following are true:

1. **Corpus gate**: 100+ verified receipts exist in `.wabblespec/state/receipts/`
2. **Failure case gate**: 3+ entries in `.wabblespec/state/memory/graph-failure-cases.jsonl` with distinct `failure_type` values
3. **Evidence gate**: At least one logged failure case where the expected answer is verifiably correct AND full-text returned something provably wrong or incomplete
4. **Drawer gate**: 50+ drawers exist (MemoryMine activation threshold — graph requires the same data density)

The drawer and corpus gates are necessary but not sufficient. The failure case gate is the deciding condition. If 100 receipts and 50 drawers exist but no logged failure cases, do not implement.

---

## What was not taken from graphify-7

- **AST extraction** (`extract.py`, tree-sitter): graphify-7 builds a code structure graph. WabbleSpec's EntityGraph operates on drawer evidence, not source code. The extraction machinery is irrelevant.
- **Community detection clustering** (`cluster.py`, networkx): graphify-7 uses Louvain community detection on in-memory networkx graphs. WabbleSpec KG lives in SQLite — clustering would require loading the entire graph into memory. Too heavy until corpus is large enough to justify it.
- **HTML visualization** (`callflow_html.py`, `tree_html.py`): no visualization layer in WabbleSpec. Entity report is the output.
- **Semantic extraction subagents**: graphify-7 dispatches parallel LLM subagents to extract semantic edges from docs. WabbleSpec's KG is built from deterministic co-occurrence in receipts — no LLM extraction in the KG layer.
- **MCP server** (`serve.py`): out of scope until EntityGraph is activated and query traffic warrants it.
- **Incremental update / watch mode**: no real-time graph update in WabbleSpec. EntityGraph runs as a session-level operation, not a background watcher.

---

## Confidence scores adapted from graphify-7

Graphify-7 uses EXTRACTED/INFERRED/AMBIGUOUS confidence labels with numeric scores. WabbleSpec EntityGraph already uses a 3-tier model (declared/observed/inferred). Mapping:

| graphify-7 | WabbleSpec EntityGraph |
|---|---|
| EXTRACTED (1.0) | declared (1.0) |
| INFERRED (0.75–0.95) | observed (0.7) |
| AMBIGUOUS (0.1–0.3) | inferred (0.4) |

When graph MVP is implemented: path traversal should surface the minimum confidence score along the path (weakest link). A path through a `declared` → `observed` → `inferred` chain reports `inferred` as the path confidence.
