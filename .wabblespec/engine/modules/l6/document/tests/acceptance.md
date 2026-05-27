# Acceptance Tests — Document (L6)

## AT-DOC-01: Post-Archive-receipt gate enforced

**Given** a Document invocation when no Archive receipt exists for the current execution
**When** Document checks its prerequisite
**Then** Document FAILS with a missing-archive-receipt error and produces no documentation output

---

## AT-DOC-02: Only verified facts documented

**Given** a Document run
**When** Document generates content
**Then** only facts confirmed by receipts and verified execution output are written; speculation, assumptions, and unverified claims are not included

---

## AT-DOC-03: Four output types produced

**Given** a successful Document run
**When** execution completes
**Then** Document produces as applicable:
- README section
- Inline comments
- CHANGELOG entry
- API reference

---

## AT-DOC-04: Receipt confirms documentation artifacts

**Given** a completed Document run
**Then** the receipt at `.wabblespec/state/receipts/document-{timestamp}.json` contains:
- `archive_receipt_verified`
- `artifacts_documented`
- `output_paths`
- `cross_link_verified`
- `verdict`

---

## AT-DOC-05: PASS — reference output with cross-references section present

**Given** the task-card declares a `reference`-type deliverable (path in `.wabblespec/engine/shared/references/` or type explicitly `reference`)
**And** the produced file contains a `## Cross-references` or `## See also` section with at least one real entry
**When** Document inspects the output before writing the receipt
**Then** Document proceeds to write the document receipt with `cross_link_verified: true`
**Then** the task is marked complete

---

## AT-DOC-06: BLOCK — reference output with no cross-references section

**Given** the task-card declares a `reference`-type deliverable
**And** the produced file contains neither `## Cross-references` nor `## See also`
**When** Document inspects the output
**Then** Document emits CROSS_LINK_MISSING
**Then** Document does not write the document receipt
**Then** Document surfaces: "Reference document at {path} has no cross-references section. Add a '## Cross-references' or '## See also' section with at least one entry."
**Then** the task loops back to add cross-references before re-running Document

---

## AT-DOC-07: BLOCK — reference output with empty cross-references section

**Given** the task-card declares a `reference`-type deliverable
**And** the produced file contains a `## Cross-references` section header but no real entries beneath it (empty or HTML comments only)
**When** Document inspects the output
**Then** Document emits CROSS_LINK_MISSING
**Then** Document does not write the document receipt

---

## AT-DOC-08: PASS — non-reference output bypasses cross-references check

**Given** the task-card declares a non-reference deliverable (README, inline comments, CHANGELOG, API reference)
**When** Document generates output
**Then** Document does not check for a cross-references section
**Then** Document writes the receipt with `cross_link_verified: null`
**Then** the task completes normally

---

## DO NOT suppress CROSS_LINK_MISSING

**Given** a reference deliverable where the cross-references section is absent, empty, or comment-only
**Then** Document does not write the document receipt regardless of task urgency
**Then** at least one real cross-reference entry must be added before Document can receipt the task complete
