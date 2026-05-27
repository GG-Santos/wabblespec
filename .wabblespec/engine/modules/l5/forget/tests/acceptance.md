# Acceptance Tests — Forget (L5)

## AT-FORGET-01: Provenance recorded before deletion

**Given** any Forget deletion operation
**When** Forget executes
**Then** Provenance is notified and records the deletion event BEFORE the drawer is deleted; if Provenance call fails, deletion does not proceed

---

## AT-FORGET-02: FRESH and AGING drawers require force and compliance_reference

**Given** a drawer with staleness state FRESH or AGING
**When** Forget is invoked without `force: true` and a `compliance_reference`
**Then** Forget FAILS and does not delete the drawer

---

## AT-FORGET-03: Provenance records and receipts are never deleted

**Given** any Forget invocation including compliance deletion
**When** deletion executes
**Then** Provenance ledger records and task receipts are never removed — only drawer content is deleted

---

## AT-FORGET-04: Content hash recorded in Provenance

**Given** a drawer being deleted
**When** the Provenance deletion record is written
**Then** it contains the SHA hash of the drawer's content at time of deletion

---

## AT-FORGET-05: Bulk-expired deletion type

**Given** a bulk-expired Forget invocation
**When** Forget selects drawers for deletion
**Then** only drawers with `staleness_state: EXPIRED` are included; no FRESH/AGING/STALE drawer is deleted in a bulk-expired pass

---

## AT-FORGET-06: Entity graph notified of deletions

**Given** a successful drawer deletion
**When** Forget completes
**Then** `entity_graph_notified: true` is in the receipt and EntityGraph has been informed to invalidate affected edges

---

## AT-FORGET-07: Forget receipt contains required fields

**Given** a completed Forget operation
**Then** the receipt at `.wabblespec/receipts/forget-receipt-{timestamp}.json` contains:
- `deletion_type`
- `drawers_deleted`
- `provenance_records_written`
- `entity_graph_notified`
- `dry_run`
- `compliance_reference`

---

## AT-FORGET-08: Dry-run mode performs no deletions

**Given** a Forget invocation with `dry_run: true`
**When** execution completes
**Then** no drawers are deleted, no Provenance records are written, and the receipt shows `dry_run: true` with the count of drawers that would have been deleted
