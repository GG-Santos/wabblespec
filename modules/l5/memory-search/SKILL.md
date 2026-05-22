---
name: memory-search
description: Query interface for Memory. Semantic search via mempalace ChromaDB backend. Finds evidence by natural language, topic, staleness state, or recency. Returns ranked results with staleness flags. No write authority — reads only.
---

# MemorySearch

You are the query interface for the evidence store. You find drawers, rank them, and return results with accurate staleness state. You never write to drawers. If a result is EXPIRED, you exclude it and report the exclusion. If a result is STALE or NEEDS_REVERIFICATION, you flag it — the caller decides whether to use it.

## Backend

mempalace `Palace` semantic search (ChromaDB vector index). Falls back to `filter_drawers` for staleness/recency queries that don't benefit from semantic ranking.

**Dependency:** `pip install mempalace` required. `MEMPALACE_PALACE_PATH` must point to `.wabblespec/memory/`.

## What this skill does

Queries the mempalace palace at `.wabblespec/memory/`. Supports semantic, topic-filter, staleness-filter, and recency queries. Post-filters results by WabbleSpec staleness metadata. Ranks by confidence + staleness + recency. Writes a MemorySearch receipt.

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

```python
from mempalace.palace import Palace
import os

palace = Palace(os.environ["MEMPALACE_PALACE_PATH"])

if query_type == "semantic":
    # ChromaDB vector search — returns semantically similar drawers
    results = palace.search(query=query, n_results=max_results * 2)  # over-fetch for post-filter

elif query_type == "topic":
    # Metadata filter on wing/room/topic fields
    results = palace.filter_drawers(filters={"room": query}, limit=max_results * 2)

elif query_type == "staleness":
    # Filter by WabbleSpec staleness metadata
    results = palace.filter_drawers(
        filters={"wabblespec_staleness_state": query},
        limit=max_results
    )

elif query_type == "recency":
    # Filter by filed_at descending (mempalace native field)
    results = palace.filter_drawers(order_by="filed_at", limit=max_results)

elif query_type == "traverse":
    # BFS graph traversal from a starting room — finds connected rooms across wings
    from mempalace.palace_graph import traverse
    results = traverse(start_room=query, max_hops=max_hops)
    # Returns [{room, wings, halls, count, hop, connected_via}] — no staleness filter needed
    # (graph nodes are structural, not evidence drawers)

elif query_type == "tunnels":
    # Find cross-wing connectors — rooms that appear in multiple wings
    from mempalace.palace_graph import find_tunnels
    wing_parts = query.split("->") if "->" in query else [query, None]
    results = find_tunnels(
        wing_a=wing_parts[0].strip() if wing_parts[0] else None,
        wing_b=wing_parts[1].strip() if len(wing_parts) > 1 and wing_parts[1] else None
    )
    # Returns [{room, wings, halls, count, recent}] sorted by count desc
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

### Step 4 — Format and return

Return top `max_results` after ranking. Write MemorySearch receipt.

## Output format (in-context)

```
## MemorySearch Results

query: <query text>
query_type: <type>
backend: mempalace/chromadb
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
  "backend": "mempalace/chromadb",
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

Full-text grep over drawer files is no longer used. ChromaDB handles both semantic and metadata queries.

## Common failure modes

1. **Returning EXPIRED drawers.** Never return EXPIRED content even with a warning unless `include_expired` explicitly set. Emit STALENESS_VIOLATION per expired drawer returned.

2. **Trusting ChromaDB rank alone.** ChromaDB distance ranks by semantic similarity only — it does not know about staleness. Always apply staleness post-filter and penalty before returning results.

3. **Not flagging STALE results.** STALE drawers must carry a flag. Caller must see the staleness state.

4. **Skipping semantic search for keyword queries.** Semantic search finds conceptually related drawers that keyword matching misses. Prefer `query_type: semantic` for research queries; reserve `topic` filter for exact wing/room lookups.

## Reference

`mempalace-develop/mempalace/palace.py` (Palace.search, Palace.filter_drawers), `mempalace-develop/mempalace/config.py` (MEMPALACE_PALACE_PATH).
