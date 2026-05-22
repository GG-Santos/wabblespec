---
name: provenance
description: Evidence lineage recorder. Append-only log for every Memory write, deletion, and cascade event. Enables NEEDS_REVERIFICATION propagation when upstream sources change.
---

# Provenance

You are the trust infrastructure. Every drawer written to Memory has a provenance record — source, confidence, what cites it, and its full event history. You never overwrite or delete records. You only append. When an upstream spec changes with BREAKING classification, you compute the cascade: which drawers are affected, which specs cite those drawers.

## What this skill does

Maintains `.wabblespec/memory/provenance/`. Three operations: **Record** (on Memory write), **Cascade** (on BREAKING spec change), **Delete-record** (on Forget archiving a drawer). Writes an append-only `ledger.md` and a machine-readable `index.json`.

## When to use / when not to use

**Use when:**
- Memory notifies you of a write or update
- A spec change arrives with BREAKING classification
- Forget notifies you of a drawer deletion
- Any module queries lineage for a drawer

**Do not use when:**
- Reading drawers for evidence — that is Memory / MemorySearch
- Applying staleness transitions — that is Memory

## Storage

```
.wabblespec/memory/provenance/
  ledger.md          <- append-only human-readable log (never edit existing entries)
  index.json         <- drawer_id -> provenance record map
  contradictions.md  <- active contradiction list (Dream resolves these)
```

Schema: `modules/l5/provenance/schemas/provenance-record.schema.json`
Rules: `modules/l5/provenance/rules/contradiction-policy.md`, `rules/cascade-policy.md`

## Inputs

- **Record (from Memory):** `{drawer_id, topic, source, source_module, confidence, timestamp}`
- **Cascade (from spec change event):** `{spec_path, change_classification}`
- **Delete-record (from Forget):** `{drawer_id, reason, requesting_module}`
- **Citation-record (from Specify):** `{drawer_id, spec_artifact_path}`

## How to do it

### Record path (Memory write notification)

```
1. Receive: {drawer_id, topic, source, source_module, confidence, timestamp}
2. Check index.json for existing record on this drawer_id:
   IF exists: update fields, preserve all prior event history
   IF not exists: create new provenance record
3. Check for existing FRESH/AGING drawer on same topic:
   IF found AND different drawer_id: flag contradiction
     -> append to contradictions.md: {drawer_a, drawer_b, topic, flagged_at}
     -> set contradicts field on both provenance records
4. Append to ledger.md:
   "| {timestamp} | WRITTEN | {drawer_id} | {source_module} | {source} |"
5. Update index.json
6. Confirm to Memory (write proceeds)
```

### Cascade path (BREAKING spec change)

```
1. Receive: {spec_path, change_classification: "BREAKING"}
2. Query index.json: all records where cited_by contains spec_path
3. For each affected drawer:
   a. Notify Memory to transition drawer to NEEDS_REVERIFICATION
   b. Find all other spec artifacts in drawer's cited_by list
   c. Flag those specs NEEDS_REVERIFICATION (record in their receipts)
   d. Append cascade entry to ledger.md
4. Write cascade summary to provenance receipt
```

Cascade depth limit: 2 hops. See `rules/cascade-policy.md`.

### Delete-record path (Forget)

```
1. Receive: {drawer_id, reason, requesting_module, archived_to}
2. Update provenance record: deletion fields
3. Trigger NEEDS_REVERIFICATION for all specs in cited_by
4. Append to ledger.md:
   "| {timestamp} | DELETED | {drawer_id} | {requesting_module} | {reason} |"
```

### Citation-record path

```
1. Receive: {drawer_id, spec_artifact_path}
2. Add spec_artifact_path to cited_by list in provenance record
3. Update index.json
```

## Output contract

**Provenance receipt** (`.wabblespec/receipts/provenance-{timestamp}.json`):

Base receipt schema with extensions:
```json
{
  "records_created": 0,
  "records_updated": 0,
  "cascade_triggered": false,
  "cascade_depth": 0,
  "contradictions_flagged": 0,
  "deletions_recorded": 0
}
```

**ledger.md format** (append-only table):

```
| timestamp | event | drawer_id | actor | detail |
```

Never edit existing rows. New rows appended at bottom only.

## Common failure modes

1. **Editing ledger.md.** Ledger is append-only. Past entries are never modified. Corrections are new entries with event type CORRECTION referencing the original.

2. **Not cascading on BREAKING.** A BREAKING spec change must trigger Provenance cascade computation. Non-BREAKING changes do not cascade — check the classification before computing.

3. **Cascade beyond 2 hops.** Default cascade depth is 2. Beyond that, log the gap in ledger.md and surface for human decision. Do not run unlimited cascades.

4. **Missing cited_by population.** Provenance can only cascade if cited_by is populated. Ensure Specify and other spec-writing modules notify Provenance when they reference a drawer.
