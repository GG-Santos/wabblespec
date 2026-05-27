# No Framework Files Rule — Clean

## Hard boundary

Clean operates exclusively on `project/repo/`. It never reads, modifies, or writes to `.wabblespec/`.

This boundary is absolute. No exception exists. If a clean operation would require touching a file in `.wabblespec/`, that operation is not a Clean operation — it belongs to the module that owns that file.

## Framework files that are never Clean targets

- `.wabblespec/receipts/` — owned by each module that writes receipts
- `.wabblespec/plans/` — owned by planning modules (Specify, Decompose, etc.)
- `.wabblespec/options-*.md` — owned by Propose
- `.wabblespec/schemas/` — owned by schema-defining modules
- Any file under `.wabblespec/` regardless of content

## Product files that are Clean targets

- `project/repo/src/` — application source
- `project/repo/tests/` — test files (formatting and dead code only — Clean does not modify test assertions)
- `project/repo/scripts/` — build and utility scripts
- `project/repo/` configuration files within declared scope

## If scope declaration includes a .wabblespec/ path

Reject the scope and prompt for a corrected declaration. Do not silently exclude the path and proceed with the rest — make the boundary explicit.
