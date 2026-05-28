---
name: provenance
description: Evidence lineage recorder. Append-only log for every Memory write, deletion, and cascade event. Enables NEEDS_REVERIFICATION propagation when upstream sources change.
---

# Provenance

You are the trust infrastructure. Every drawer written to Memory has a provenance record — source, confidence, what cites it, and its full event history. You never overwrite or delete records. You only append. When an upstream spec changes with BREAKING classification, you compute the cascade: which drawers are affected, which specs cite those drawers.

## What this skill does

Maintains `.wabblespec/state/memory/provenance/`. Three operations: **Record** (on Memory write), **Cascade** (on BREAKING spec change), **Delete-record** (on Forget archiving a drawer). Delegates ledger append and index update to `provenance-append.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| Record, cascade, delete, or contradiction ledger writes | `engine/shared/references/script-delegation-contract.md` → `provenance-append.py` |

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
.wabblespec/state/memory/provenance/
  ledger.md          <- append-only human-readable log (never edit existing entries)
  index.json         <- drawer_id -> provenance record map
  contradictions.md  <- active contradiction list (Dream resolves these)
```

Schema: `modules/l5/provenance/schemas/provenance-record.schema.json`
Rules: `modules/l5/provenance/rules/contradiction-policy.md`, `rules/cascade-policy.md`

## Inputs

- **Record (from Memory):** `{drawer_id, topic, source, source_module, confidence, timestamp}` — source must include `path` and `type`
- **Cascade (from spec change event):** `{spec_path, change_class, source_hash_current}` — `change_class` is BREAKING|NON_BREAKING|ADDITIVE
- **Delete-record (from Forget):** `{drawer_id, reason, requesting_module}`
- **Citation-record (from Specify):** `{drawer_id, spec_artifact_path}`

## How to do it

### Record path (Memory write notification)

```
1. Receive: {drawer_id, topic, source, source_module, confidence, timestamp}
2. Compute source_hash:
   IF source.type in ["project-file", "framework-reference"]:
     SHA-256 the file at source.path -> store as source_hash (64-char hex)
   ELSE (internal-computation or external-doc):
     source_hash = null
3. Check index.json for existing record on this drawer_id:
   IF exists: update fields, preserve all prior event history, preserve cascade_events[]
   IF not exists: create new provenance record with source_hash and empty cascade_events[]
4. Check for existing FRESH/AGING drawer on same topic:
   IF found AND different drawer_id: flag contradiction
     -> append to contradictions.md: {drawer_a, drawer_b, topic, flagged_at}
     -> set contradicts field on both provenance records
5-6. Delegate ledger append and index update:
```bash
python .wabblespec/engine/shared/scripts/provenance-append.py record \
  --drawer-id <drawer_id> \
  --topic "<topic>" \
  --source-path <source.path> \
  --source-type <source.type> \
  --written-by <source_module> \
  --confidence <confidence>
```
7. Confirm to Memory (write proceeds)
```

### Cascade path (spec change event)

```
1. Receive: {spec_path, change_class, source_hash_current}
2. Check change_class:
   IF change_class is NON_BREAKING or ADDITIVE:
     -> log to ledger.md: "| {timestamp} | CHANGE | change_class={change_class} | source={spec_path} | no cascade |"
     -> exit (no cascade)
   IF change_class absent: default to BREAKING, log warning
3. Check source_hash_current vs stored source_hash on provenance record for spec_path:
   IF hashes differ AND change_class != BREAKING: log warning (hash mismatch vs declared class)
4. Query index.json: all records where cited_by contains spec_path (hop 1 drawers)
5. For each hop-1 drawer:
   a. Notify Memory to transition drawer to NEEDS_REVERIFICATION
   b. Collect all spec artifacts in drawer's cited_by list -> hop-2 affected_specs
6. For each path in affected_specs (hop 2):
   a. Flag spec NEEDS_REVERIFICATION (record in its receipt)
7. Append cascade_event to each affected drawer's cascade_events[]:
   {triggered_at, change_class: "BREAKING", source_spec: spec_path, hop_depth: 1, affected_specs: []}
   And to hop-2 specs' owning drawers:
   {triggered_at, change_class: "BREAKING", source_spec: spec_path, hop_depth: 2, affected_specs: [spec paths]}
8-9. Delegate cascade ledger append:
```bash
python .wabblespec/engine/shared/scripts/provenance-append.py cascade \
  --spec-path <spec_path> \
  --change-class BREAKING \
  --affected-drawers "<drawer_id_1>" "<drawer_id_2>"
```
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

**Provenance receipt** (`.wabblespec/state/receipts/provenance-{timestamp}.json`):

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
