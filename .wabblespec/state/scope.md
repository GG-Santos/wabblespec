# Session Scope

**target:** Library-Package
**complexity:** Low
**locked_at:** 2026-05-28T03:49:55Z
**session_id:** phase1-root-cleanup-20260528

## In Scope

- Delete `scope.md` from `.wabblespec/` root (canonical path is `.wabblespec/state/scope.md`; root copy is stale duplication)
- Delete `recipe.json` from `.wabblespec/` root (canonical path is `.wabblespec/state/recipe.json`; root copy is stale duplication)
- Move `options-framework-script-delegation-20260528T110016Z.md` from `.wabblespec/` root to `.wabblespec/state/working/`
- Move `brainstorm/` directory from `.wabblespec/` root to `.wabblespec/state/brainstorm/`
- Move `enhance/` directory from `.wabblespec/` root to `.wabblespec/state/enhance/`
- Delete stale T3 checkpoint files from `.wabblespec/state/session/checkpoints/` (T3 archived — checkpoints are orphaned)
- Add canonical path declarations to `CLAUDE.md` under framework state paths section

## Out of Scope

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

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
