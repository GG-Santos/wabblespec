---
name: entity-graph
description: Temporal entity relationship graph from drawer data. Extracts typed entities, builds co-occurrence graph with min threshold, assigns confidence tiers, tracks valid_from/valid_to temporal validity. Zero LLM involvement — script only.
---

# EntityGraph

You run the EntityGraph script. You do not interpret its output — you surface it.

## What this skill does

Invokes `modules/l5/entity-graph/scripts/entity-graph.py`. The script reads all curated drawers from `.wabblespec/memory/wings/`, extracts entity mentions of 3 types, builds a relationship graph using typed predicates and temporal validity, writes co-occurrence triples to the knowledge graph, and writes output files to `.wabblespec/memory/`.

You do not decide what is related. The script decides based on co-occurrence in drawer evidence with a minimum threshold of 2. You run the script and report what it found.

## Entity types

| Type | What it represents | Extraction method |
|---|---|---|
| `file` | Source file or path referenced in drawer evidence | Regex: path-like strings with `/` or `.ext` |
| `module` | WabbleSpec module ID referenced in drawer | Match against known module ID list |
| `concept` | Drawer topic or tag — the subject of the knowledge | Drawer `topic` field + `tags` array |

Start with these 3 types only. Add types only when real query patterns reveal a need.

## Entity extraction

The script uses three extraction methods — one per entity type:

**File entities** — regex match against path-like strings in drawer text:
```python
FILE_PATTERN = re.compile(r'\b(?:[a-zA-Z0-9_\-]+/){1,}[a-zA-Z0-9_\-]*(?:\.[a-zA-Z]{1,10})?\b')
```

**Module entities** — exact word-boundary match against the known WabbleSpec module ID list (KNOWN_MODULES set in the script). Covers ~50 module names including all L1-L8 modules, gateways, and shared tools.

**Concept entities** — drawer `topic` field plus any `tags` array entries.

All three feed into a unified co-occurrence graph built per drawer.

## Entity confidence tiers

Each entity is assigned a confidence tier based on its source:

| Tier | Source | Confidence |
|---|---|---|
| `declared` | Explicitly named in a receipt or drawer `topic` field | 1.0 |
| `observed` | Extracted from drawer evidence or tags | 0.7 |
| `inferred` | Co-occurrence only — entity name matched but never stated explicitly | 0.4 |

Tier determines how much weight an entity carries in clustering and gap detection. `inferred` entities below co-occurrence threshold of 2 are discarded.

## Relationship model

Relationships are typed predicates, not bare co-occurrence weights:

```json
{
  "subject": "entity-id",
  "predicate": "co-occurs-with | depends-on | references | supersedes",
  "object": "entity-id",
  "weight": 3,
  "valid_from": "2026-05-21T00:00:00Z",
  "valid_to": null,
  "source_drawers": ["drawer-id-1", "drawer-id-2"]
}
```

- `weight` = number of drawers in which the pair co-occurs (min threshold: 2)
- `valid_from` = date of first co-occurrence
- `valid_to` = set when a relationship is explicitly invalidated (e.g. a module is replaced)
- Relationships with `valid_to < now` are excluded from active queries

## Co-occurrence threshold

Minimum co-occurrence count: **2**. Entity pairs that co-occur in only one drawer are discarded as noise. This threshold prevents spurious edges from single-drawer coincidences.

## When to use

- After 50+ drawers exist (enough data for graph to be meaningful)
- When investigating which modules or files a concept touches
- Before TeamPlan activation — to understand which modules are implicated in a task
- As input to MemoryMine (after MemoryMine is activated)

**Do not use:**
- As a substitute for MemorySearch — MemorySearch handles recall, EntityGraph handles relationships
- On every wave — session-level operation, not wave-level

## Backend

Knowledge graph: SQLite at `.wabblespec/memory/knowledge_graph.sqlite3` through the WabbleSpec Memory facade.

```python
from _shared.memory_backend import get_knowledge_graph

kg = get_knowledge_graph()

# Add co-occurrence triple (weight >= 2 threshold)
kg.add_triple(
    subject="receipt-schema",
    predicate="co-occurs-with",
    obj="guard",
    valid_from="2026-05-22T00:00:00Z",   # must be YYYY-MM-DDTHH:MM:SSZ format
    confidence=0.9,
    source_drawer_id="edge-key",
)

# Query entity relationships
results = kg.query_entity("receipt-schema")

# Invalidate when a relationship ends (e.g. module replaced)
kg.invalidate(subject="old-module", predicate="co-occurs-with", obj="guard", ended="2026-05-22T00:00:00Z")

kg.close()
```

`WABBLESPEC_MEMORY_PATH` must be set (see `modules/l5/memory/rules/memory-backend-config.md`).

## How to run it

```
python modules/l5/entity-graph/scripts/entity-graph.py
python modules/l5/entity-graph/scripts/entity-graph.py --dry-run
python modules/l5/entity-graph/scripts/entity-graph.py --query "receipt"
```

`--query` filters output to the subgraph containing entities whose label matches the query term.

Run from the project root.

## Outputs

| File | Location | Purpose |
|---|---|---|
| `entity-graph.json` | `.wabblespec/memory/` | Graph: nodes (entities with tier + confidence) + edges (typed predicates with temporal validity) |
| `entity-report.md` | `.wabblespec/memory/` | Human-readable: top entities by degree, densest relationships |
| `entity-registry.json` | `.wabblespec/memory/` | Full entity list with type, label, drawer count, drawer IDs |
| `knowledge_graph.sqlite3` | `.wabblespec/memory/` | SQLite KG — co-occurrence triples with temporal validity |

## Invalidation

When a module is removed, replaced, or a file is deleted:

1. Set `valid_to` on all relationships involving that entity to the current timestamp via `kg.invalidate()`
2. Lower entity confidence to 0 (mark as `superseded`)
3. Do not delete — temporal history is preserved for audit

EntityGraph never deletes nodes or edges. It invalidates them.

## Expansion rule

Do not add a 4th entity type until: (1) at least 50 drawers exist, AND (2) a real query has failed because the missing entity type would have answered it. Expansion requires evidence, not speculation.

## Reference

`modules/l5/entity-graph/scripts/entity-graph.py` (implementation), `modules/l5/memory/rules/memory-backend-config.md` (env var setup).
