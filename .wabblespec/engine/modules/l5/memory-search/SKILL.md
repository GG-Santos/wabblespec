---
name: memory-search
description: Query interface for the WabbleSpec memory store. Semantic search via ChromaDB. Finds evidence by natural language, topic, staleness state, or recency. Returns ranked results with staleness flags. No write authority — reads only.
---

# MemorySearch

You are the query interface for the evidence store. You find drawers, rank them, and return results with accurate staleness state. You never write to drawers. If a result is EXPIRED, you exclude it and report the exclusion. If a result is STALE or NEEDS_REVERIFICATION, you flag it — the caller decides whether to use it.

## Backend

WabbleSpec memory store — ChromaDB vector index at `.wabblespec/memory/`. Semantic queries use vector embeddings; metadata queries use ChromaDB `where` filters.

**Dependency:** shared internal package at `packages/memory/`. `WABBLESPEC_MEMORY_PATH` must point to `.wabblespec/memory/`; import through `_shared.memory_backend` so runtime configuration runs first.

## What this skill does

Queries the memory store at `.wabblespec/memory/`. Supports semantic, topic-filter, staleness-filter, and recency queries. Post-filters results by WabbleSpec staleness metadata. Ranks by confidence + staleness + recency. Writes a MemorySearch receipt.

## When to use / when not to use

**Use when:**
- Research phase begins (run MemorySearch before any Plan phase)
- Any module requests evidence by topic or keyword
- Explicit `/memory-search` command
- Staleness audit needed (query by staleness state)

**Do not use when:**
- Retrieving a specific drawer by known ID — use Memory directly
- Writing or transitioning drawers — Memory only

## Inputs

```json
{
  "query_type": "semantic | topic | staleness | recency | traverse | tunnels",
  "query": "string",
  "staleness_filter": ["FRESH", "AGING", "STALE", "NEEDS_REVERIFICATION"],
  "max_results": 10,
  "wing": null,
  "include_expired": false,
  "max_hops": 2
}
```

Default `staleness_filter` excludes EXPIRED and SUPERSEDED. `include_expired: true` emits STALENESS_VIOLATION warning per returned expired drawer.

## How to do it

### Step 1 — Execute query

The search script is at `modules/l5/memory-search/scripts/search-index.py`. Call it or invoke it directly:

```bash
python modules/l5/memory-search/scripts/search-index.py --query "staleness decay" --type semantic
python modules/l5/memory-search/scripts/search-index.py --query "guard" --type topic
python modules/l5/memory-search/scripts/search-index.py --type staleness --state NEEDS_REVERIFICATION
python modules/l5/memory-search/scripts/search-index.py --type recency --max 10
```

Internally the script uses:

```python
from _shared.memory_backend import get_collection
import os

col = get_collection()

if query_type == "semantic":
    # ChromaDB vector search — returns semantically similar drawers
    qr = col.query(query_texts=[query], n_results=max_results * 3, where=wing_filter)
    # qr.ids[0], qr.metadatas[0], qr.documents[0], qr.distances[0]

elif query_type == "topic":
    # Metadata filter on room field
    r = col.get(where={"room": query}, limit=max_results * 2)
    # r.ids, r.metadatas, r.documents

elif query_type == "staleness":
    # Filter by WabbleSpec staleness metadata
    r = col.get(where={"wabblespec_staleness_state": query}, limit=max_results)

elif query_type == "recency":
    # Fetch all, sort by filed_at descending
    r = col.get(limit=max_results * 2)
    # Sort r by meta["filed_at"] descending

elif query_type == "traverse":
    from _shared.memory_backend import traverse_memory_graph
    results = traverse_memory_graph(start_room=query, max_hops=max_hops)

elif query_type == "tunnels":
    from _shared.memory_backend import find_memory_tunnels
    results = find_memory_tunnels(wing_a=..., wing_b=...)
```

### Step 2 — Apply staleness post-filter

For each result, read `wabblespec_staleness_state` from ChromaDB metadata:

```
EXPIRED     → exclude. If caller set include_expired=true, include with STALENESS_VIOLATION flag.
SUPERSEDED  → exclude, note superseded_by drawer ID in response.
STALE       → include with STALE flag.
NEEDS_REVERIFICATION → include with NEEDS_REVERIFICATION flag.
FRESH/AGING → include, no flag.
```

### Step 3 — Rank results

Semantic queries: ChromaDB distance score is primary. Override with staleness penalty:

```
score = chroma_similarity_score
     - (0.3 if staleness == STALE)
     - (0.5 if staleness == NEEDS_REVERIFICATION)
     + (confidence * 0.1)
```

Non-semantic queries: rank by confidence (desc), then staleness rank (FRESH=3, AGING=2, STALE=1, NEEDS_REVERIFICATION=0), then filed_at (desc).

Deduplicate by `wabblespec_drawer_id` — synthetic pointer docs share a drawer ID with their source; keep only the highest-scoring entry per drawer.

### Step 4 — Format and return

Return top `max_results` after ranking. Write MemorySearch receipt.

## Output format (in-context)

```
## MemorySearch Results

query: <query text>
query_type: <type>
backend: memory/chromadb
timestamp: <ISO 8601>
results_returned: N
results_excluded_expired: N
results_flagged: N

| rank | drawer_id | topic | wing | staleness | confidence | snippet |
|---|---|---|---|---|---|---|
| 1 | <id> | <topic> | <wing> | FRESH | 0.9 | <first 120 chars of content> |
```

## Output contract

**MemorySearch receipt** (`.wabblespec/receipts/memorysearch-{timestamp}.json`):

```json
{
  "query_type": "string",
  "query": "string",
  "backend": "memory/chromadb",
  "results_returned": 0,
  "results_excluded_expired": 0,
  "results_flagged_stale": 0,
  "results_flagged_needs_reverification": 0,
  "semantic_search_used": true,
  "entity_graph_traversed": false
}
```

## Semantic vs full-text

Semantic search (default for `query_type: semantic`) uses ChromaDB vector embeddings — finds conceptually related drawers even when exact keywords don't match. Use for open research questions.

Topic/staleness/recency queries use ChromaDB metadata filters — exact match, no vector scoring. Use when you know the wing, room, or staleness state you want.

Full-text grep over drawer files is not used. ChromaDB handles both semantic and metadata queries.

## Common failure modes

1. **Returning EXPIRED drawers.** Never return EXPIRED content even with a warning unless `include_expired` explicitly set. Emit STALENESS_VIOLATION per expired drawer returned.

2. **Trusting ChromaDB rank alone.** ChromaDB distance ranks by semantic similarity only — it does not know about staleness. Always apply staleness post-filter and penalty before returning results.

3. **Not flagging STALE results.** STALE drawers must carry a flag. Caller must see the staleness state.

4. **Skipping semantic search for keyword queries.** Semantic search finds conceptually related drawers that keyword matching misses. Prefer `query_type: semantic` for research queries; reserve `topic` filter for exact wing/room lookups.

5. **Duplicate results from synthetic docs.** Synthetic pointer documents share `wabblespec_drawer_id` with their source drawer. Deduplicate by `wabblespec_drawer_id` before returning results.

## Reference

`modules/l5/memory-search/scripts/search-index.py` (implementation), `modules/l5/memory/rules/memory-backend-config.md` (setup + env var), `modules/l5/memory/rules/staleness-thresholds.md`.
