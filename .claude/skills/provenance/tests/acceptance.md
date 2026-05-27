# Acceptance Tests — Provenance (L5)

## AT-PROV-01: Ledger is append-only

**Given** any Provenance write operation
**When** a record is created or updated
**Then** no existing entry in `ledger.md` is modified or deleted; only new entries are appended

---

## AT-PROV-02: Cascade only on BREAKING change class

**Given** a spec artifact change is recorded with Provenance
**When** the `change_class` is determined
**Then**:
- `BREAKING` -> cascade triggered, affected drawers marked NEEDS_REVERIFICATION
- `NON_BREAKING` -> no cascade
- `ADDITIVE` -> no cascade

---

## AT-PROV-03: Cascade depth limit of 2 hops

**Given** a BREAKING change that triggers cascade
**When** Provenance traverses the dependency graph
**Then** cascade propagation stops at 2 hops from the changed artifact; no drawer beyond 2 hops is marked NEEDS_REVERIFICATION in this cascade

---

## AT-PROV-04: Four operation paths supported

**Given** a Provenance invocation
**When** path is declared
**Then** the following are supported:
- `Record` — log a new provenance event
- `Cascade` — propagate a change through the dependency graph
- `Delete-record` — record a deletion event (append-only)
- `Citation-record` — record a spec-to-drawer citation

---

## AT-PROV-05: Contradictions are flagged, not silently accepted

**Given** a new provenance record that conflicts with an existing record for the same drawer
**When** Provenance processes the record
**Then** it is written to `contradictions.md` and flagged in the receipt

---

## AT-PROV-06: Receipt contains required fields

**Given** a completed Provenance operation
**Then** the receipt at `.wabblespec/state/receipts/provenance-{timestamp}.json` contains:
- `records_created`
- `records_updated`
- `cascade_triggered`
- `cascade_depth`
- `contradictions_flagged`
- `deletions_recorded`

---

## AT-PROV-07: Citation-record binds drawer to spec artifact

**Given** a `Citation-record` operation with a `drawer_id` and `spec_artifact_path`
**When** Provenance writes the record
**Then** the drawer's provenance entry gains a `cited_by` entry referencing the spec artifact path, enabling future cascade when that spec changes with BREAKING classification
