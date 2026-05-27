# Acceptance Tests — Research Log (L6)

## AT-RLOG-01: Research Log delegates storage to Memory

**Given** a Research Log invocation
**When** a drawer is to be written
**Then** Research Log formats the entry and passes it to Memory for storage; it does not write directly to ChromaDB

---

## AT-RLOG-02: spec_binding enables Provenance citation

**Given** a Research Log entry with `spec_binding` present
**When** the drawer write succeeds
**Then** Research Log notifies Provenance with a citation-record linking the drawer to the spec artifact; future BREAKING changes to that spec will trigger NEEDS_REVERIFICATION on this drawer

---

## AT-RLOG-03: spec_binding absent skips Provenance notification

**Given** a Research Log entry with no `spec_binding`
**When** the drawer write succeeds
**Then** no Provenance citation is sent; the finding is session-scoped only

---

## AT-RLOG-04: Feature-scoped research artifact written when spec_binding present

**Given** a Research Log entry with `spec_binding.spec_artifact_path` set
**When** the finding is logged
**Then** a `research/{feature-slug}/research.md` file is written (or updated) where feature-slug is derived from the final path segment of `spec_artifact_path`

---

## AT-RLOG-05: Observed-behavior findings get confidence <= 0.7 and AGING state

**Given** a finding from observed behavior with no version anchor
**When** Research Log processes the confidence and staleness
**Then** `confidence <= 0.7` and `staleness_state: AGING`

---

## AT-RLOG-06: Do not activate for pre-existing FRESH drawers

**Given** a finding that matches a topic already in a FRESH drawer
**When** Research Log is invoked
**Then** Research Log does not write a duplicate drawer — it directs the caller to use MemorySearch to verify before logging

---

## AT-RLOG-07: Receipt confirms drawer count and confidence range

**Given** a completed Research Log run
**Then** the receipt at `.wabblespec/state/receipts/research-log-{timestamp}.json` contains:
- `drawers_written`
- `topics`
- `confidence_range`
- `feature_scoped_path`
