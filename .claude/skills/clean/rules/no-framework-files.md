# No Framework Files Rule — Clean

## Hard boundary

Clean operates exclusively on product space — project root excluding `.wabblespec/`, `.claude/`, and `.git/`. It never reads, modifies, or writes to any of those dot-prefixed framework directories.

This boundary is absolute. No exception exists. If a clean operation would require touching a file in `.wabblespec/`, that operation is not a Clean operation — it belongs to the module that owns that file.

## Framework files that are never Clean targets

- `.wabblespec/state/receipts/` — owned by each module that writes receipts
- `.wabblespec/state/plans/` — owned by planning modules (Specify, Decompose, etc.)
- `.wabblespec/state/` — all runtime state; framework-owned
- `.wabblespec/engine/` — all framework source; framework-owned
- `.claude/` — harness configuration; never touched from product tasks
- Any file under `.wabblespec/` or `.claude/` regardless of content

## Product files that are Clean targets

- `src/` — application source
- `tests/` — test files (formatting and dead code only — Clean does not modify test assertions)
- `scripts/` — build and utility scripts
- Root-level configuration files within declared scope

## If scope declaration includes a .wabblespec/ or .claude/ path

Reject the scope and prompt for a corrected declaration. Do not silently exclude the path and proceed with the rest — make the boundary explicit.
