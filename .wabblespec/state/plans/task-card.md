# Task Card

**goal:** The `.wabblespec/` root contains only VERSION, CHANGELOG.md, INDEX.md, wabblespec.yaml, state/, and engine/, with all stray session artifacts relocated to canonical paths under `state/` and CLAUDE.md updated to declare the canonical locations for scope and recipe state files.
**target:** Library-Package
**complexity:** Low
**change_class:** COSMETIC
**locked_at:** 2026-05-28T03:50:30Z
**session_id:** phase1-root-cleanup-20260528

## Non-Goals

- Updating any SKILL.md files to reference new canonical paths (Phase 2 work)
- Updating any script path resolution logic (Phase 2 work)
- Moving or renaming anything inside `state/` or `engine/` subdirectories
- `brainstorm-receipt` and `propose-receipt` in `state/receipts/` — correctly placed, not moving

## Assumptions

- No skill or script reads `.wabblespec/scope.md` (root) or `.wabblespec/recipe.json` (root) at runtime in a way that breaks if absent — root files are stale session artifacts
- `.wabblespec/state/scope.md` and `.wabblespec/state/recipe.json` already exist and are up to date
- `enhance/enhanced-*.md` files have no downstream consumers — working artifacts from brainstorm session
- T3 checkpoint files are safe to delete — `delivery-receipt-toprank-integration-phase2-T3.json` exists with `status: PASS`
- No project-standard drawers discovered — none cited

## Acceptance Criteria

### AC1 — Root contains only canonical items

Given the `.wabblespec/` root directory,
When cleanup completes,
Then the root contains no items other than: `VERSION`, `CHANGELOG.md`, `INDEX.md`, `wabblespec.yaml`, `state/`, `engine/` — specifically `scope.md`, `brainstorm/`, `enhance/`, and `options-framework-script-delegation-20260528T110016Z.md` SHALL NOT be present.

### AC2 — Moved artifacts exist at new paths

Given the stray items previously at `.wabblespec/` root,
When cleanup completes,
Then `options-framework-script-delegation-20260528T110016Z.md` exists at `.wabblespec/state/working/options-framework-script-delegation-20260528T110016Z.md`, brainstorm output files exist under `.wabblespec/state/brainstorm/`, and enhanced working files exist under `.wabblespec/state/enhance/`.

### AC3 — Orphaned checkpoints cleared

Given `.wabblespec/state/session/checkpoints/` containing `checkpoint-wave-1.json` and `checkpoint-wave-2.json` from the archived T3 session,
When cleanup completes,
Then neither file exists in that directory.

### AC4 — CLAUDE.md declares canonical paths

Given the `CLAUDE.md` "Framework State" section listing key paths,
When cleanup completes,
Then CLAUDE.md contains a note stating that `.wabblespec/state/scope.md` and `.wabblespec/state/recipe.json` are the canonical session state paths (not the root-level copies).
