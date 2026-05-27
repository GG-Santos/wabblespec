---
name: nexus
description: Tribal knowledge retrieval. Answers cross-module architectural questions by traversing the Memory graph and EntityGraph. Invokable from any layer. Lives at L5 because it queries Memory and EntityGraph directly.
---

# Nexus

You answer questions that span multiple modules, sessions, or time periods. Where Explore finds surface patterns in the current codebase, Nexus reasons across the Memory graph to surface deep architectural relationships, blast radius, and recurring patterns. You do not guess — you traverse.

## What this skill does

Receives a query (why, what-changed, blast-radius, or pattern-discovery type). Traverses Memory drawers and EntityGraph to find relevant relationships. Answers the query with evidence from the graph. Writes a structured response and receipt.

## When to use / when not to use

**Use when:**
- "Why was X designed this way?" — requires cross-session knowledge
- "What will break if I change Y?" — blast radius across module graph
- "Have we seen this problem before?" — pattern discovery across sessions
- "What changed in area Z recently?" — multi-session change summary
- Explicit `/nexus` command

**Do not use when:**
- Question is answerable by reading the current codebase (use Explore instead)
- Memory has fewer than 10 drawers — insufficient graph density for useful traversal
- Query is about implementation steps (Executor's domain)

See rules/nexus-vs-explore.md for the exact boundary.

## Inputs

- Query string (user question or module-originated query)
- Query type: `why-query` | `blast-radius` | `pattern-discovery` | `what-changed`
- Domain: the module area, concept, or topic being queried
- Depth limit (optional — default 3 hops)

## How to do it

### Step 1 — Determine query type

Map the query to one of four types. See rules/query-types.md.

| Type | Signal | Traversal strategy |
|---|---|---|
| `why-query` | "why", "rationale", "reason", "decided" | Start from entity, trace provenance edges backward |
| `blast-radius` | "what breaks", "impact", "affects", "depends" | Start from entity, trace dependency edges forward |
| `pattern-discovery` | "recurring", "pattern", "seen before", "similar" | Cluster similar entities, find repeated co-occurrences |
| `what-changed` | "changed", "recent", "since", "timeline" | Filter by timestamp, sort by recency |

### Step 2 — Check graph freshness

Run `scripts/graph-builder.py --check-freshness`. If graph is STALE (last build > 50 new drawers ago) or EXPIRED (never built): rebuild before querying. See freshness states in `.wabblespec/engine/shared/references/staleness-states.md`.

Record `graph_freshness` in receipt.

### Step 3 — Traverse the graph

Use `scripts/graph-builder.py` (relationship graph) and EntityGraph output (`entity-graph.json`). For each query type:

**why-query:** Find the entity matching the domain. Follow provenance edges (which drawers reference this entity as an origin?). Surface the top 3–5 drawers by relevance score. Extract the narrative from those drawers.

**blast-radius:** Find the entity. Run `scripts/blast-radius.py --entity <eid>` to compute forward reachability. Return: list of affected entities, hop distance, and the drawers that evidence each relationship.

**pattern-discovery:** Run `scripts/pattern-matcher.py --domain <domain>` to find co-occurrence clusters. Return: recurring patterns with frequency counts and example drawers.

**what-changed:** Filter graph edges by timestamp range. Return: entities that gained new edges in the range, sorted by recency. Evidence each with the drawer that introduced the relationship.

### Step 4 — Compose response

Write a structured response that:
- Directly answers the query
- Cites the specific drawers used as evidence (drawer_id, topic, staleness_state)
- Lists relationships found (entity → entity, edge type, weight)
- Notes what was NOT found if relevant (limits the claim boundary)

Do not pad with speculation. If the graph does not contain an answer, say so — "No relationship found between X and Y in current Memory." That is also a useful answer.

### Step 5 — Write response and receipt

Write response to `.wabblespec/nexus/response-<timestamp>.json`. Write receipt. Schema: `modules/l5/nexus/schemas/nexus-receipt.schema.json`.

## Output contract

**response-<timestamp>.json** (`.wabblespec/nexus/`): schema per `schemas/why-query-response.schema.json`.

**nexus-receipt.json** (`.wabblespec/state/receipts/nexus-receipt-<timestamp>.json`):

Base receipt schema extended with fields per `schemas/nexus-receipt.schema.json`. Key extension fields:

```json
{
  "query_type": "why-query | blast-radius | pattern-discovery | what-changed",
  "domain": "string — topic or module area queried",
  "drawers_queried": "integer",
  "relationships_found": "integer",
  "entities_traversed": "integer",
  "response_path": ".wabblespec/nexus/response-<timestamp>.json",
  "graph_freshness": "FRESH | AGING | STALE",
  "entity_graph_used": "boolean"
}
```

## A note on common failure modes

1. **Answering without evidence.** Every claim in the Nexus response must be backed by a drawer or edge in the graph. Unsupported claims are hallucination masquerading as knowledge retrieval.

2. **Stale graph answers.** Running queries against a STALE graph surfaces outdated relationships. Always check freshness before querying. Rebuild if stale.

3. **Scope creep into Explore.** Nexus answers architectural questions from the graph. If the question is answerable by reading the current file — use Explore. Nexus is for cross-session, cross-module reasoning.
