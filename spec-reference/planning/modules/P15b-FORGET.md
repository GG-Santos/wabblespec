# Module Plan — Forget (L5)

**Tier:** 3 — SUPPORTING
**Layer:** L5 Memory
**v5.3 origin:** Forget module — controlled evidence deletion with Provenance audit trail

---

## Purpose

Controlled deletion of Memory drawers. Forget is the only module authorized to delete drawers. Dream decays staleness — Forget removes. Every deletion is recorded in Provenance (append-only ledger.md). Deleted drawers are not purged silently — a deletion record persists even after the drawer content is gone. Forget requires explicit scope declaration and human confirmation for bulk deletions.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/forget <drawer-id>` command (single drawer)
- Explicit `/forget --scope <filter>` command (bulk — requires Attestation)
- Dream flags EXPIRED drawers for Forget (Dream suggests, Forget executes)
- Archive --sweep mode: Archive delegates EXPIRED drawer removal to Forget
- Legal/compliance request (GDPR right to erasure — documented in spec)

Forget cannot activate without explicit command or authorized delegation. No automatic deletion without human-authorized trigger.

---

## Deletion Types

| Type | Trigger | Confirmation required |
|---|---|---|
| Single drawer | Explicit command | Confirmation prompt (show drawer summary before delete) |
| Bulk (EXPIRED) | Dream suggestion or Archive --sweep | Attestation required |
| Bulk (topic scope) | Explicit --scope filter | Attestation required |
| Compliance deletion | Legal request + explicit command | Attestation + documented reason |

---

## Deletion Process

Forget does NOT hard-delete without trace. Process for every deletion:

1. Write Provenance deletion record (drawer ID, reason, timestamp, authorized by)
2. Remove drawer content (file deleted)
3. Remove drawer from Memory index.md
4. Notify EntityGraph: remove drawer_refs for deleted drawer, trigger orphan check
5. Notify Provenance: cascade — any drawer citing deleted drawer flagged NEEDS_REVERIFICATION

Deletion record in Provenance ledger.md is permanent — append-only, never removed.

---

## Deletion Record Format (Provenance)

```markdown
## Deletion — <drawer-id>

**deleted_at:** ISO 8601
**reason:** expired|superseded|compliance|explicit|sweep
**authorized_by:** human|dream|archive
**attestation_id:** string (if Attestation required)
**cascaded_to:** [drawer IDs that cited this drawer — now flagged NEEDS_REVERIFICATION]
```

---

## Bulk Deletion Guard

Before bulk deletion executes:

1. Display: count of drawers to be deleted, staleness breakdown, topic distribution
2. Require Attestation
3. Write Provenance deletion record for each drawer
4. Execute deletion
5. Write Forget receipt with full list of deleted drawer IDs

No bulk deletion proceeds without showing scope summary first.

---

## Compliance Deletion (GDPR / Right to Erasure)

When compliance deletion requested:
- Reason declared: `compliance` with legal basis noted
- Scope: all drawers referencing the data subject
- EntityGraph: all nodes referencing deleted drawers removed
- Provenance: deletion record notes legal basis (not the deleted content)
- Receipt: compliance deletion flagged for audit trail

---

## Workflow

```
1. Receive deletion request (single, bulk, or compliance)

2. Identify scope:
   -> Single: one drawer ID
   -> Bulk: apply filter, show count + summary
   -> Compliance: identify all drawers referencing data subject

3. Require confirmation:
   -> Single: confirmation prompt
   -> Bulk/Compliance: Attestation

4. For each drawer in scope:
   a. Write Provenance deletion record
   b. Delete drawer file
   c. Remove from Memory index.md
   d. Notify EntityGraph (drawer_ref removal)
   e. Cascade: flag citing drawers NEEDS_REVERIFICATION

5. Write Forget receipt (list of all deleted drawer IDs)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — explicit only, exclusive write authority over deletion |
| `rules/no-silent-delete.md` | Rules | Every deletion recorded in Provenance before file removed |
| `rules/bulk-attestation.md` | Rules | Bulk deletion requires Attestation |
| `rules/compliance-policy.md` | Rules | Legal deletion procedure |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | Forget is sole authorized deleter of Memory drawers |
| Provenance | Forget writes deletion record to Provenance ledger.md before every delete |
| EntityGraph | Forget notifies EntityGraph to remove drawer_refs and check orphans |
| Dream | Dream flags EXPIRED drawers as Forget candidates (suggestion only) |
| Archive | Archive --sweep delegates EXPIRED drawer removal to Forget |
| MemoryMine | MemoryMine identifies EXPIRED orphan risks — Forget executes removal |

---

## Verification Mode

**Attestation** — Attestation required for bulk deletions, Provenance deletion record written before file removed, EntityGraph notified, receipt written with full deletion list.

---

## Receipt Extension Fields

```json
{
  "deletion_type": "single|bulk|compliance",
  "drawers_deleted": "integer",
  "deleted_ids": ["string"],
  "provenance_records_written": "integer",
  "entitygraph_notified": "boolean",
  "cascaded_reverification": "integer",
  "attestation_received": "boolean",
  "compliance_reason": "string"
}
```
