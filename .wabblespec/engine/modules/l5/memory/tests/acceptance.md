# Acceptance Tests — Memory (L5)

## AT-MEM-01: Write operation requires topic and body

**Given** an invocation of Memory with operation `Write`
**When** either `topic` or `body` is absent
**Then** Memory FAILS with a missing-field error and writes no drawer

---

## AT-MEM-02: Written drawer has FRESH staleness on creation

**Given** a successful Write invocation
**When** the drawer is persisted to ChromaDB
**Then** the drawer's `staleness_state` is `FRESH` and `wabblespec_` metadata prefix is applied to all WabbleSpec metadata fields

---

## AT-MEM-03: EXPIRED drawer never returns content

**Given** a drawer with `staleness_state: EXPIRED`
**When** any Read or MemorySearch attempts to retrieve its content
**Then** a `StalenessViolation` is raised and content is not returned

---

## AT-MEM-04: SUPERSEDED drawer raises SupersededError on read

**Given** a drawer with `staleness_state: SUPERSEDED`
**When** Memory attempts to return its content
**Then** a `SupersededError` is raised referencing the superseding drawer ID

---

## AT-MEM-05: Provenance is notified on Write

**Given** a successful drawer write
**When** the drawer is persisted
**Then** `provenance_notified: true` in the receipt and Provenance records the creation event

---

## AT-MEM-06: Write receipt contains required fields

**Given** any successful Write operation
**Then** the receipt at `.wabblespec/state/receipts/memory-write-{timestamp}.json` contains:
- `drawer_id`
- `operation`
- `topic`
- `wing`
- `room`
- `staleness_before`
- `staleness_after`
- `provenance_notified`
- `backend`

---

## AT-MEM-07: Transition operation requires valid staleness target

**Given** a Transition operation
**When** the target staleness state is not one of FRESH/AGING/STALE/EXPIRED/NEEDS_REVERIFICATION/SUPERSEDED
**Then** Memory FAILS and does not write the transition

---

## AT-MEM-08: WABBLESPEC_MEMORY_PATH env var required

**Given** Memory is invoked
**When** `WABBLESPEC_MEMORY_PATH` environment variable is not set
**Then** Memory FAILS with an environment configuration error before attempting any database operation
