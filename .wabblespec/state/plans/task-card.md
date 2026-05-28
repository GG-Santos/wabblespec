# Task Card

**goal:** A wabblespec-doctor.py drift detector exists and is wired as an on_archive daemon and an advisory Guard layer, all five schema gaps are closed, and findings C1-C4 plus the high-tier drift items are fixed and verified.
**target:** Framework
**complexity:** High
**change_class:** ADDITIVE
**locked_at:** 2026-05-28T13:02:20Z
**session_id:** foundation-hardening-20260528

## Non-Goals

- Exhaustive resolution of all medium and low tier findings (left for the doctor to surface)
- Full unit-test harness for the 42 shared scripts (deferred to a fast-follow task card)
- Promoting the doctor Guard layer to blocking (stays advisory until clean across several Archives)
- Any product-space changes (framework self-build only, I11)

## Assumptions

- Brainstorm and Propose artifacts are the source of the 28 findings and Option 2 was human-selected
- Python 3.8+ with pyyaml and duckdb available
- Reviewer gates the Plan stage before Executor since Guard is invariant-enforcing
- H1 confidence unification is additive with a deprecation window, keeping the overall delta ADDITIVE

## Acceptance Criteria

### AC1 — doctor exists and runs

Given wabblespec-doctor.py does not exist today
When the doctor is built and invoked with a full run
Then command exits 0, executes all 28 finding checks, and emits a structured report

### AC2 — schema gaps closed

Given recipe.json wave-queue.json delivery brainstorm and propose lack schemas or builders
When schemas are added under engine/shared/schemas and receipt-writer gains brainstorm options_path and a propose builder
Then receipt-writer --validate passes for recipe wave-queue delivery brainstorm and propose receipts

### AC3 — confidence field unified

Given receipts use confidence confidence_score and score interchangeably
When writers are normalized to emit confidence with back-compat reads of legacy names
Then all receipt builders emit a single confidence field in 0 to 1 and validation passes

### AC4 — receipt-index paths resolve

Given 43 of 64 indexed delivery receipt paths point to .wabblespec/receipts/
When the index is regenerated against .wabblespec/state/receipts/
Then every delivery_receipt_path in receipt-index.json resolves to an existing file

### AC5 — platform skill IDs aligned

Given registry full IDs differ from .claude/skills short forms
When the sync process is corrected and re-run
Then registry IDs and .claude/skills directory names match for platform-iot platform-extension and platform-library

### AC6 — critical path and doc fixes

Given archive.py references a nonexistent _shared path and CLAUDE.md states version 0.39.0 and 100 or 99 modules
When archive.py path is corrected and CLAUDE.md is updated
Then archive.py resolves wabble-sound.py and CLAUDE.md states version 0.45.0 and 103 modules

### AC7 — doctor wired as gate

Given no automated drift detection exists
When doctor is added to daemon-config on_archive and as an advisory Guard layer
Then an Archive run triggers the doctor and Guard surfaces its findings without blocking
