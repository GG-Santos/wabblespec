# Cold-Start Behavior — ScopeFrame

Defines what ScopeFrame does when its expected upstream artifacts are absent.

## Absent: recipe.json

Condition: `.wabblespec/recipe.json` does not exist or is stale.
Detection: File read returns 404 or session_id mismatch.
Action: Surface DEPENDENCY error naming Recipe. ScopeFrame cannot declare scope boundaries without a declared build target.
Do NOT: Infer scope from the user message alone.

## Absent: prior receipts

Condition: `recipe-receipt.json` absent.
Detection: Stem missing from receipts directory.
Action: Surface DEPENDENCY error — Recipe must complete before ScopeFrame runs.
Do NOT: Proceed without recipe-receipt confirmed.

## Absent: scope.md

Condition: `.wabblespec/scope.md` does not exist (first run).
Detection: File read returns 404.
Action: This is the expected cold-start condition — ScopeFrame creates scope.md on first run. Derive scope from recipe.json target and task card input.
Output: Fresh `scope.md` with in-scope and out-of-scope sections populated from first principles.

## Default state on cold start

| Field | Default |
|---|---|
| `in_scope` | derived from recipe target and user task — never empty |
| `out_of_scope` | explicit list required; "everything else" is not valid |
| `boundary_type` | `file-list` (conservative default; pattern-match requires explicit declaration) |
