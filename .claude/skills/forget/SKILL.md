---
name: forget
description: Controlled deletion of memory drawers. Writes Provenance deletion record before any deletion. Handles single, bulk EXPIRED, and compliance deletion types. Notifies EntityGraph after deletion. Never deletes without a Provenance record.
---

# Forget

You are controlled deletion. You remove drawers that are no longer needed — expired, superseded, or legally required to be purged. You never delete silently. Provenance gets a deletion record before anything is removed. EntityGraph is notified after. The audit trail survives the data.

## What this skill does

Controlled deletion of memory drawers. Writes Provenance deletion record before any deletion. Handles single, bulk EXPIRED, and compliance deletion types. Notifies EntityGraph after deletion. Never deletes without a Provenance record.

## When to use

Invoked per activators declared in `skill-rules.json`.

## Deletion types

### Type 1: Single deletion

Remove one drawer by ID.

```
Input: { drawer_id, reason, actor, compliance_reference? }
```

Use when: one specific drawer is outdated, incorrect, or must be removed for compliance.

### Type 2: Bulk EXPIRED deletion

Remove all drawers in `EXPIRED` staleness state.

```
Input: { type: "bulk-expired", dry_run?: boolean, actor }
```

Use when: routine maintenance — clearing drawers that have already been transitioned to EXPIRED by Memory. `dry_run: true` lists candidates without deleting.

### Type 3: Compliance deletion

Remove drawers containing specified PII or regulated data, regardless of staleness state.

```
Input: {
  type: "compliance",
  subject_id: "string",      // user/entity whose data must be purged
  legal_basis: "GDPR_17|CCPA|court_order|other",
  actor,
  compliance_reference       // ticket ID, case number, or legal instrument
}
```

Use when: right-to-erasure request, legal hold lifted, or regulatory purge required.

## How to do it

**Step 1 — Write Provenance deletion record FIRST.**

Before touching any drawer file:

```json
{
  "event": "DELETION",
  "drawer_id": "<id>",
  "topic": "<topic from drawer>",
  "deleted_at": "<ISO-8601>",
  "actor": "<who triggered>",
  "deletion_type": "single | bulk-expired | compliance",
  "reason": "<human-readable reason>",
  "compliance_reference": "<if compliance type>",
  "content_hash": "<SHA-256 of drawer content before deletion>"
}
```

Write to `.wabblespec/state/memory/provenance/deletions/{drawer-id}-{timestamp}.json`.

**Step 2 — Delete the drawer file.**

Remove from `.wabblespec/state/memory/wings/{wing}/rooms/{room}/drawers/{id}.json`.
If drawer was in closets (EXPIRED archive): remove from `.wabblespec/state/memory/closets/` as well.

**Step 3 — Remove from index.json.**

Remove drawer entry from `.wabblespec/state/memory/index.json`. Drawer becomes invisible to MemorySearch.

**Step 4 — Notify EntityGraph.**

Send deletion event to EntityGraph with drawer_id and topic. EntityGraph removes references from any entity that cited this drawer.

**Step 5 — Write Forget receipt.**

## Compliance deletion: additional rules

- Content hash in Provenance record allows verification that correct content was deleted (hash only — no content retained)
- If drawer is FRESH with recent activity, flag for human review before deletion (unless overridden by `force: true` with compliance_reference)
- Bulk compliance purge: list all drawers matching subject_id in dry_run first, then confirm before executing

## What Forget does NOT do

- Does not delete Provenance records. The deletion audit trail is permanent.
- Does not delete receipts. Receipt chain integrity is preserved.
- Does not delete FRESH or AGING drawers without explicit `force: true` + compliance_reference.
- Does not cascade-delete linked drawers automatically — EntityGraph handles reference cleanup.

## Reference Routing

| Situation | Reference |
|---|---|
| Forget receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type forget` |

## Output contract

**forget-receipt** (`.wabblespec/state/receipts/forget-receipt-{timestamp}.json`):
```json
{
  "deletion_type": "single | bulk-expired | compliance",
  "drawers_deleted": "integer",
  "provenance_records_written": "integer",
  "entity_graph_notified": "boolean",
  "dry_run": "boolean",
  "compliance_reference": "string or null"
}
```

## Common failure modes

1. **Deleting before writing Provenance record.** Order is mandatory: Provenance first, deletion second. If the write fails, abort — do not delete.

2. **Treating Forget as the staleness system.** Forget does not decide when drawers expire. Memory and Dream manage staleness transitions. Forget only executes deletions that have been requested explicitly.

3. **Compliance deletion without compliance_reference.** Type 3 deletion requires a legal instrument reference. Rejecting undocumented compliance deletions is correct behavior — it protects against accidental erasure.
