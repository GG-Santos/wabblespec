---
name: entity-graph
description: Temporal entity relationship graph from drawer data. Extracts typed entities, builds co-occurrence graph with min threshold, assigns confidence tiers, tracks valid_from/valid_to temporal validity. Zero LLM involvement — script only.
---

# EntityGraph

You run the EntityGraph script. You do not interpret its output — you surface it.

## What this skill does

Invokes `modules/l5/entity-graph/scripts/entity-graph.py`. The script reads all drawers, extracts entity mentions of 3 types, builds a relationship graph using typed predicates and temporal validity, and writes output to `.wabblespec/memory/`.

You do not decide what is related. The script decides based on co-occurrence in drawer evidence with a minimum threshold of 2. You run the script and report what it found.

## Entity types

| Type | What it represents | Extraction method |
|---|---|---|
| `file` | Source file or path referenced in drawer evidence | Regex: path-like strings with `/` or `.ext` |
| `module` | WabbleSpec module ID referenced in drawer | Match against known module ID list |
| `concept` | Drawer topic or tag — the subject of the knowledge | Drawer `topic` field + `tags` array |

Start with these 3 types only. Add types only when real query patterns reveal a need.

## Entity extraction (via mempalace entity_detector)

Do not use custom regex for entity extraction. Delegate to `mempalace.entity_detector`:

```python
from mempalace.entity_detector import detect_entities, scan_for_detection
from mempalace.hallways import compute_hallways_for_wing

# Scan drawer content files for entity candidates
files = scan_for_detection(".wabblespec/", max_files=10)
detected = detect_entities(files, languages=("en",))
# detected = {"people": [...], "projects": [...], "topics": [...], "uncertain": [...]}

# Two-pass: candidate extraction (3+ occurrences) + scoring (person vs project)
# Produces confidence-scored entity list with signal breakdown
```

`detect_entities` reads first 5KB per file, extracts candidates appearing 3+ times, then scores each as person/project/uncertain via verb patterns, pronoun proximity, dialogue markers, code references, and versioned name patterns. Multi-language support via `MEMPALACE_ENTITY_LANGUAGES`.

## Hallways (within-wing co-occurrence via mempalace)

Do not implement custom co-occurrence logic. Use `mempalace.hallways`:

```python
from mempalace.hallways import compute_hallways_for_wing, list_hallways

# Compute entity-pair hallways for one wing (min 2 co-occurrences)
hallways = compute_hallways_for_wing(wing="wing_wabblespec", col=collection, min_count=2)
# Each hallway: {id, wing, entity_a, entity_b, co_occurrence_count, rooms, label}

# Persisted atomically to ~/.mempalace/hallways.json (survives palace rebuilds)
# Read back any time
all_hallways = list_hallways(wing="wing_wabblespec")
```

Hallways are within-wing (entity ↔ entity inside one wing). Cross-wing links are tunnels (see MemorySearch palace graph traversal).

## Entity confidence tiers (adapted from mempalace entity_registry)

Each entity is assigned a confidence tier based on its source:

| Tier | Source | Confidence |
|---|---|---|
| `declared` | Explicitly named in a receipt or drawer `topic` field | 1.0 |
| `observed` | Extracted from drawer evidence or tags | 0.7 |
| `inferred` | Co-occurrence only — entity name matched but never stated explicitly | 0.4 |

Tier determines how much weight an entity carries in clustering and gap detection. `inferred` entities below co-occurrence threshold of 2 are discarded.

## Relationship model (adapted from mempalace knowledge_graph temporal triples)

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

Minimum co-occurrence count: **2**. Entity pairs that co-occur in only one drawer are discarded as noise. This mirrors mempalace `hallways.py` behavior (min threshold prevents spurious edges from single-drawer coincidences).

## When to use

- After 50+ drawers exist (enough data for graph to be meaningful)
- When investigating which modules or files a concept touches
- Before TeamPlan activation — to understand which modules are implicated in a task
- As input to MemoryMine (after MemoryMine is activated)

**Do not use:**
- As a substitute for MemorySearch — MemorySearch handles recall, EntityGraph handles relationships
- On every wave — session-level operation, not wave-level

## Backend

Uses `mempalace.knowledge_graph` (SQLite at `.wabblespec/memory/knowledge_graph.sqlite3`) for triple storage. Entity extraction reads drawers via `mempalace.Palace.filter_drawers()`.

```python
from mempalace.knowledge_graph import KnowledgeGraph
import os

kg = KnowledgeGraph(os.path.join(os.environ["MEMPALACE_PALACE_PATH"], "knowledge_graph.sqlite3"))

# Add triple
kg.add_triple(subject="receipt-schema", predicate="references", object_="drawer-123",
              confidence=0.9, valid_from="2026-05-22T00:00:00Z")

# Query entity relationships
results = kg.query_entity("receipt-schema", as_of="2026-05-22T00:00:00Z")

# Invalidate (not delete)
kg.invalidate_triple(triple_id=42, valid_to="2026-05-22T00:00:00Z")
```

`MEMPALACE_PALACE_PATH` must be set (see `modules/l5/memory/rules/mempalace-config.md`).

## How to run it

```
python modules/l5/entity-graph/scripts/entity-graph.py
python modules/l5/entity-graph/scripts/entity-graph.py --dry-run
python modules/l5/entity-graph/scripts/entity-graph.py --query "receipt"
python modules/l5/entity-graph/scripts/entity-graph.py --as-of 2026-05-01
```

`--as-of` filters relationships by `valid_from`/`valid_to` — returns graph as it existed on that date.

Run from the project root.

## Outputs

| File | Location | Purpose |
|---|---|---|
| `entity-graph.json` | `.wabblespec/memory/` | Graph: nodes (entities with tier + confidence) + edges (typed predicates with temporal validity) |
| `entity-report.md` | `.wabblespec/memory/` | Human-readable: top entities by degree, densest relationships, expired relationships flagged |
| `entity-registry.json` | `.wabblespec/memory/` | Full entity list with type, tier, confidence, first_seen, last_seen |

## Invalidation

When a module is removed, replaced, or a file is deleted:

1. Set `valid_to` on all relationships involving that entity to the current timestamp
2. Lower entity confidence to 0 (mark as `superseded`)
3. Do not delete — temporal history is preserved for audit

EntityGraph never deletes nodes or edges. It invalidates them.

## Expansion rule

Do not add a 4th entity type until: (1) at least 50 drawers exist, AND (2) a real query has failed because the missing entity type would have answered it. Expansion requires evidence, not speculation.

## Reference

Pattern source: `mempalace-develop/mempalace/knowledge_graph.py` (temporal triple schema, `valid_from`/`valid_to`, `as_of` queries), `mempalace-develop/mempalace/entity_registry.py` (3-tier confidence model), `mempalace-develop/mempalace/hallways.py` (co-occurrence min threshold 2+, noise filter).
