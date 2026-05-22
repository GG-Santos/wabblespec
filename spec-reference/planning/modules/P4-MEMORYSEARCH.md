# Module Plan — MemorySearch (L5)

**Tier:** 2 — CORE
**Layer:** L5 Memory
**v5.3 origin:** Memory module search behavior — formalized as standalone module

---

## Purpose

Query interface for Memory. Finds evidence by topic, entity, or relationship. Returns ranked results with staleness states. MemorySearch is how all modules access stored evidence — Memory stores, MemorySearch retrieves.

---

## Activation

`skill-rules.json` triggers:
- Research phase (every Research phase runs MemorySearch)
- Any module requesting evidence by topic or entity
- Explicit `/memory-search` command
- EntityGraph relationship traversal request

---

## Query Types

| Query Type | Input | Returns |
|---|---|---|
| Topic | keyword or phrase | Drawers matching topic, ranked by relevance + confidence |
| Entity | entity name | Drawers referencing that entity, via EntityGraph |
| Relationship | entity A + relationship type + entity B | Drawers confirming or denying relationship |
| Recency | timestamp range | Drawers written/updated in period |
| Staleness | staleness state filter | Drawers in specified state (e.g., all NEEDS_REVERIFICATION) |
| Full-text | arbitrary text | Drawers containing matching content |

---

## Result Format

```markdown
## MemorySearch Results

**query:** <query text>
**query_type:** <type>
**timestamp:** <when queried>

| rank | drawer_id | topic | staleness | confidence | snippet |
|---|---|---|---|---|---|
| 1 | <id> | <topic> | FRESH | 0.9 | <first 100 chars> |
```

Each result includes staleness state. Caller is responsible for handling STALE/EXPIRED per I9 rules.

---

## Staleness Enforcement on Results

| Staleness | MemorySearch behavior |
|---|---|
| FRESH | Return normally |
| AGING | Return with AGING flag |
| STALE | Return with STALE flag — caller must acknowledge |
| EXPIRED | Exclude from results. Emit STALENESS_VIOLATION if caller explicitly requested this drawer. |
| NEEDS_REVERIFICATION | Return with NEEDS_REVERIFICATION flag — surface for human check |
| SUPERSEDED | Redirect to superseding drawer automatically |

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Search results | Returned to calling module (in-context) | Evidence retrieval |
| MemorySearch receipt | `.wabblespec/receipts/memorysearch-receipt.md` | I10 compliance |

---

## Workflow

```
1. Receive query (type + parameters)

2. Read Memory index.md for drawer list + staleness states

3. Apply staleness filter:
   -> Exclude EXPIRED (emit STALENESS_VIOLATION if explicitly requested)
   -> Flag STALE and NEEDS_REVERIFICATION in results

4. Execute query against drawer files:
   -> Topic: keyword match against drawer topics + content
   -> Entity: traverse EntityGraph for entity references
   -> Relationship: EntityGraph relationship query
   -> Recency: filter by last_verified timestamp
   -> Full-text: scan drawer content

5. Rank results:
   -> Primary: confidence score
   -> Secondary: staleness (FRESH > AGING > STALE)
   -> Tertiary: recency (newer = higher)

6. Return ranked result list with staleness flags

7. Write MemorySearch receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over search results (no write authority) |
| `scripts/search-index.py` | Script | Deterministic full-text search across drawer files |
| `schemas/search-result.schema.json` | Schema | Result format validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | MemorySearch reads from Memory drawers. No write authority. |
| EntityGraph | MemorySearch queries EntityGraph for entity and relationship queries |
| ReferenceLoad | ReferenceLoad writes evidence; MemorySearch retrieves it later |
| Research phase | Every Research phase runs MemorySearch before Plan begins |
| Specify | Reads MemorySearch results to populate spec with evidence |
| Provenance | MemorySearch reads provenance records to include trust metadata in results |

---

## Verification Mode

**Observation** — results returned, staleness states present on all results, EXPIRED drawers excluded, receipt written.

---

## Receipt Extension Fields

```json
{
  "query_type": "string",
  "results_returned": "integer",
  "results_excluded_expired": "integer",
  "results_flagged_stale": "integer",
  "results_flagged_needs_reverification": "integer",
  "entity_graph_traversed": "boolean"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Ranking algorithm | Confidence + staleness + recency (current) vs. TF-IDF | Per-module planning |
| Max results returned | Unlimited vs. configurable cap (default 10) | Per-module planning |
| Full-text search implementation | Script-based scan vs. simple index | Per-module planning |
