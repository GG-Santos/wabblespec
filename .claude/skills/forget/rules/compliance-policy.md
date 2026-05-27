# Forget Compliance Policy

Rules governing compliance deletions (Type 3). Applied in addition to deletion-types.md.

---

## Legal Basis Values

| Value | Trigger |
|---|---|
| `GDPR_17` | EU GDPR Article 17 — right to erasure request |
| `CCPA` | California Consumer Privacy Act erasure request |
| `court_order` | Court order requiring data destruction |
| `internal_policy` | Internal retention policy expiry |
| `other` | Other documented legal basis — compliance_reference must be more specific |

Reject requests with undocumented or invalid `legal_basis`. Do not attempt to infer legal basis from context.

---

## Provenance Record is Permanent

Compliance deletion removes drawer content. It does NOT remove the Provenance deletion record.

The Provenance record retains:
- `content_hash` (SHA-256 of deleted content) — allows verification that correct content was deleted
- `deleted_at`, `actor`, `legal_basis`, `compliance_reference`, `subject_id`
- No content text — hash only

This audit trail survives the deleted data permanently.

---

## FRESH/AGING Drawer Protection

FRESH and AGING drawers represent recently verified, active evidence. Compliance deletion of active drawers is high-risk.

**Required before deleting FRESH/AGING drawers:**
1. `dry_run: true` output reviewed by human
2. Explicit human Attestation via Verifier Attestation mode
3. `compliance_reference` documented with specific legal instrument

No automated path exists to delete FRESH/AGING drawers in compliance type. Human decision is mandatory.

---

## Bulk Compliance Purge (multiple subjects)

When a single compliance request covers multiple subjects (e.g., data breach purge):

1. Enumerate all matching `subject_id` values in advance
2. Run `dry_run: true` for each subject and aggregate candidate list
3. Present full candidate list to human for confirmation
4. Execute one subject at a time — one Provenance record per drawer
5. Write one Forget receipt per subject_id (not one combined receipt)

Do not execute bulk compliance deletion in a single pass without per-subject confirmation.

---

## EntityGraph Notification After Compliance Deletion

After every compliance deletion, notify EntityGraph with:
- `drawer_id`
- `topic`
- `event: "COMPLIANCE_DELETION"`

EntityGraph removes all references to the deleted drawer from KG triples. This prevents stale cross-references pointing to deleted evidence.

If EntityGraph notification fails, record the failure in the Forget receipt under `entity_graph_notification_failed: true` and surface for manual re-sync.

---

## What Compliance Deletion Cannot Remove

- Provenance records (permanent by design)
- Receipts referencing the deleted drawer (receipt chain integrity preserved)
- Snapshots or checkpoints that may contain drawer content (Rollback must be consulted separately)

If regulatory obligation requires purging from snapshots, escalate to human — Forget scope is limited to the active memory store.
