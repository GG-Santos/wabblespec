# Module Plan — ReferenceLoad (L0)

**Tier:** 2 — CORE
**Layer:** L0 Intake
**v5.3 origin:** Partial — reference loading was implicit in v5.3 module references/. Formalized as standalone module in v6.1.

---

## Purpose

Fetch external evidence during the Research phase. Writes evidence to Memory as FRESH drawers with provenance. Validates staleness of previously loaded references before reuse. ReferenceLoad is the entry point for all external knowledge into the framework.

---

## Activation

`skill-rules.json` triggers:
- Research phase start (Gate 3: Phase fires)
- Explicit reference request from any module
- Staleness check request on existing drawer (AGING or STALE state)

---

## Source Types

| Source Type | Examples | Trust Level |
|---|---|---|
| Framework references | `_shared/references/`, module `references/` | HIGH — controlled |
| Project files | Spec artifacts, AGENT.md, existing docs | HIGH — local |
| External docs (user-provided path) | File path provided by user | MEDIUM — verify staleness |
| External docs (fetched) | URL, API doc, standard spec | MEDIUM — timestamp required |
| Instinct tracker | `.wabblespec/memory/tracker.json` | HIGH — internal |

ReferenceLoad does not fetch arbitrary URLs without user declaration. No silent external calls.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Memory drawers | `.wabblespec/memory/drawers/` | Evidence stored for session |
| ReferenceLoad receipt | `.wabblespec/receipts/referenceload-receipt.md` | Lists all loaded references + staleness states |

---

## Workflow

```
1. Identify required references for current phase + stage
   -> Framework references: auto-load from module references/ directories
   -> Project references: read from project file tree
   -> External references: require explicit declaration

2. For each reference:
   a. Check Memory index for existing drawer on this topic
      -> IF exists: check staleness state
         -> FRESH/AGING: skip load, use existing, note in receipt
         -> STALE: reload, update drawer, reset to FRESH
         -> EXPIRED: reload required, old drawer archived
         -> NEEDS_REVERIFICATION: reload, flag in receipt
      -> IF not exists: load fresh

   b. Load reference content

   c. Write to Memory drawer with:
      -> staleness: FRESH
      -> source: reference path/URL
      -> confidence: based on source trust level
      -> timestamp: now

   d. Notify Provenance (lineage record)

3. Write ReferenceLoad receipt listing:
   -> All loaded references
   -> Staleness state at load time
   -> What was skipped (already FRESH)
   -> What was reloaded (was STALE/EXPIRED)
   -> Confidence per reference
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over reference drawer writes |
| `rules/source-trust.md` | Rules | Trust level assignment per source type |
| `rules/load-policy.md` | Rules | When to reload vs. reuse; external call policy |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | ReferenceLoad writes all loaded evidence as drawers |
| Provenance | Notified on every write for lineage tracking |
| MemorySearch | Searches drawers that ReferenceLoad populated |
| Recipe | ReferenceLoad reads target from recipe.json to select relevant references |
| Dream | May re-evaluate staleness of drawers ReferenceLoad created |

---

## Verification Mode

**Observation** — receipt lists all loaded references, every reference has a drawer in Memory, staleness states are set, Provenance notified for each.

---

## Receipt Extension Fields

```json
{
  "references_loaded": "integer",
  "references_reused": "integer",
  "references_reloaded": "integer",
  "references_expired_archived": "integer",
  "external_sources": "array of strings",
  "lowest_confidence": "number"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| External fetch policy | User-declared path only vs. allow WebFetch with confirmation | Per-module planning |
| Staleness recheck trigger | Every Research phase vs. only when AGING/STALE detected | Per-module planning |
| Framework reference auto-load scope | All module references/ vs. only active platform + active gateways | Per-module planning |
