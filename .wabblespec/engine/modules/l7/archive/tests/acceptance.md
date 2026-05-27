# Acceptance Tests — Archive (L7)

## AT-ARCH-01: Missing required receipt causes FAIL, not partial delivery

**Given** an Archive run where any required receipt is absent from the chain
**When** Archive checks the receipt chain
**Then** Archive FAILs, records which receipt is absent in the delivery receipt failure reason, and does not compose a delivery receipt with gaps

---

## AT-ARCH-02: not_tested items are verbatim — not summarized

**Given** receipts with `not_tested` fields
**When** Archive compiles the not-tested list
**Then** all items are aggregated verbatim, exact duplicates are removed but distinct items are preserved; no item is minimized, summarized, or hidden

---

## AT-ARCH-03: Version bump rules

**Given** receipts containing change classifications
**When** Archive determines version bump
**Then**:
- Any BREAKING deviation -> major version bump (x.0.0)
- Only ADDITIVE deviations -> minor version bump (0.x.0)
- Only COSMETIC deviations or none -> patch bump (0.0.x)

---

## AT-ARCH-04: CHANGELOG entry is append-only

**Given** an Archive run
**When** CHANGELOG.md is updated
**Then** the new entry is appended (prepended at top per existing format); no existing entry is modified

---

## AT-ARCH-05: Receipt index maintained across executions

**Given** Archive runs for multiple executions
**When** receipt-index.json is updated
**Then** all entries persist; FAIL entries are never deleted — they are audit evidence

---

## AT-ARCH-06: Shift trigger fires on BREAKING or ADDITIVE spec artifact change

**Given** an Archive run where any receipt shows `delta_class: BREAKING` or `delta_class: ADDITIVE` with a SKILL.md, schema, or rules file touched
**When** Archive writes the delivery receipt
**Then** `shift_triggered: true` and Shift is invoked; archiving is not blocked on Shift completion

---

## AT-ARCH-07: Nexus refresh hook — conditional on framework files (post-elimination behavior)

**Given** an Archive run where files_written across all wave receipts contains at least one framework-graph-relevant file (path starts with `modules/` and ends with `SKILL.md` or `skill-rules.json`; or starts with `.wabblespec/engine/shared/schemas/` and ends with `.json`; or exactly equals `framework.yaml`)
**When** post-archive hooks execute
**Then** `graph-builder.py --scope {matched-files}` is invoked; `nexus_refreshed: true`, `nexus_skip_reason: null` in delivery receipt

---

## AT-ARCH-07b: Nexus refresh hook — correctly skipped for non-framework tasks

**Given** an Archive run where files_written contains no framework-graph-relevant files (documentation only, product source, receipts, or other non-module paths)
**When** post-archive hooks execute
**Then** `graph-builder.py` is NOT invoked; `nexus_refreshed: false`, `nexus_skip_reason: "no-framework-files-modified"` in delivery receipt; no graph drift occurs

---

## AT-ARCH-07c: Nexus refresh hook — skipped when Nexus not initialized

**Given** an Archive run on a project where the Nexus graph has not yet been initialized
**When** post-archive hooks execute
**Then** graph-builder.py is not invoked regardless of files_written content; `nexus_refreshed: false`, `nexus_skip_reason: "nexus-not-initialized"` in delivery receipt; archiving continues without error

---

## AT-ARCH-07d: Path-match is prefix-anchored — product-space modules/ paths do not trigger

**Given** files_written contains `src/modules/feature.py` or `tests/modules/test_feature.py`
**When** the Nexus refresh pre-check runs
**Then** these paths do NOT match the framework pattern; Nexus refresh is not triggered; `nexus_skip_reason: "no-framework-files-modified"` recorded

---

## AT-ARCH-08: Delivery receipt contains required extension fields

**Given** a completed Archive run
**Then** the delivery receipt contains:
- `receipts_aggregated`
- `not_tested_items`
- `version_previous`
- `version_new`
- `version_bump_reason`
- `waves_completed`
- `all_waves_passed`
