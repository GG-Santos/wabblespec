# Forget Deletion Types

Three deletion types. Each has different input requirements, guard conditions, and Provenance record fields.

---

## Type 1: Single Deletion

Remove one specific drawer by ID.

**Required input:**
```json
{
  "drawer_id": "string",
  "reason": "string — human-readable reason for deletion",
  "actor": "string — who triggered this deletion"
}
```

**Optional input:**
- `compliance_reference` — if deletion is compliance-driven, include here (triggers compliance record even for single type)
- `force: true` — required when drawer is FRESH or AGING (see guard conditions)

**Guard conditions:**
- FRESH or AGING drawers: requires `force: true`. If not set, abort with message: "Drawer is FRESH/AGING — set force:true to confirm intentional deletion."
- EXPIRED or STALE drawers: no force required.

**Provenance record fields:**
- `event: "DELETION"`
- `deletion_type: "single"`
- `drawer_id`, `topic`, `reason`, `actor`, `content_hash`, `deleted_at`

---

## Type 2: Bulk EXPIRED Deletion

Remove all drawers currently in EXPIRED staleness state.

**Required input:**
```json
{
  "type": "bulk-expired",
  "actor": "string"
}
```

**Optional input:**
- `dry_run: true` — lists candidates without deleting. Default: false.

**Guard conditions:**
- Always run `dry_run: true` first to confirm candidates before executing.
- Bulk deletion BLOCKED if any candidate is in FRESH or AGING state. (staleness-checker should have transitioned them — check for misconfiguration.)
- Candidates must have `wabblespec_staleness_state == "EXPIRED"` in ChromaDB metadata.

**Provenance record:** One record per deleted drawer. `deletion_type: "bulk-expired"` on each.

**DRY_RUN output:**
```json
{
  "dry_run": true,
  "candidates": [{ "drawer_id": "...", "topic": "...", "expired_at": "..." }],
  "count": 0
}
```

---

## Type 3: Compliance Deletion

Remove drawers containing PII or regulated data. May target FRESH, AGING, STALE, or EXPIRED drawers. Highest-privilege deletion type.

**Required input:**
```json
{
  "type": "compliance",
  "subject_id": "string — user or entity whose data must be purged",
  "legal_basis": "GDPR_17 | CCPA | court_order | internal_policy | other",
  "actor": "string",
  "compliance_reference": "string — ticket ID, case number, or legal instrument"
}
```

**Guard conditions:**
- `compliance_reference` is mandatory. Reject if absent: "compliance_reference required for Type 3 deletion — include ticket ID, case number, or legal instrument."
- `legal_basis` must be one of the declared enum values. Reject unknown values.
- FRESH/AGING drawers: always require explicit human Attestation before deletion (Verifier Attestation mode). No `force:true` shortcut for compliance type.
- Run `dry_run: true` first to list all matching drawers — present to human for confirmation before executing.

**Provenance record fields:**
- All standard fields plus: `subject_id`, `legal_basis`, `compliance_reference`
- `event: "COMPLIANCE_DELETION"`

**Content hash:** SHA-256 of drawer content written to Provenance record before deletion. Hash only — no content retained in Provenance.

---

## Execution Order (all types)

1. Write Provenance deletion record(s)
2. Delete drawer from memory store (`col.delete(ids=[drawer_id])` via `get_collection()`)
3. Notify EntityGraph
4. Write Forget receipt

**If step 1 fails:** abort. Do not proceed to deletion.
**If step 3 fails:** log notification failure in receipt. Deletion stands — EntityGraph must be manually re-synced.
