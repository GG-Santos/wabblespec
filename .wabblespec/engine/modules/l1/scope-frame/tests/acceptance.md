# ScopeFrame — Acceptance Criteria

## BLOCK: absent recipe.json

Given `recipe.json` does not exist or is stale,
When ScopeFrame is invoked,
Then ScopeFrame surfaces a DEPENDENCY error naming Recipe.
Then ScopeFrame does not infer scope from the user message alone.
Then no scope.md is written.

## BLOCK: absent recipe receipt

Given `recipe-receipt.json` is absent,
When ScopeFrame is invoked,
Then ScopeFrame surfaces a DEPENDENCY error: Recipe must complete before ScopeFrame runs.
Then ScopeFrame does not proceed without recipe-receipt confirmed.

## Happy path: scope declared and confirmed

Given `recipe.json` is present and the user has provided a task description,
When ScopeFrame runs,
Then scope is derived from the recipe target and user request.
Then In Scope items use action language ("implement X", "define Y").
Then Out of Scope contains at least one explicitly excluded item (never empty).
Then Assumptions contains at least one entry (every task has at least one assumption).
Then the drafted scope is presented to the user for confirmation.
Then scope.md is NOT written until the user explicitly confirms.
Then scope.md is written to `.wabblespec/scope.md` after confirmation.
Then a receipt is written with `user_confirmed: true`.

## user_confirmed must be true

Given any ScopeFrame invocation,
Then the receipt is never written with `user_confirmed: false`.
Then scope.md is not a locked scope without user confirmation.

## Project standards: loaded before drafting

Given `category: project-standard` drawers exist in Memory,
When ScopeFrame runs,
Then `critical` standard drawers are loaded into context before drafting scope.
Then `high` standard drawers are loaded if the recipe target or task description overlaps their category.
Then each loaded standard's evidence path is spot-checked to confirm the pattern still exists.
Then confirmed standards are cited by drawer ID in the Assumptions section.
Then standards whose evidence path is missing are marked NEEDS_REVERIFICATION and not cited.

## No project standards: proceed without block

Given no `category: project-standard` drawers exist in Memory,
When ScopeFrame runs,
Then ScopeFrame notes "no project standards discovered" in Assumptions and proceeds.
Then no error is raised.

## cold-start: scope.md absent

Given `scope.md` does not exist,
When ScopeFrame runs,
Then this is the expected cold-start condition — ScopeFrame creates scope.md.
Then scope is derived from recipe.json target and task card input from first principles.

## scope.md already locked with no expansion

Given `scope.md` is already locked and no scope expansion has been detected,
Then ScopeFrame does not re-trigger.

## Out of Scope invariant

Given the drafted scope.md,
Then the Out of Scope section contains at least one explicitly named exclusion.
Then "everything else" is not a valid Out of Scope entry.

## Receipt fields

Given any successful ScopeFrame run,
Then the receipt contains: `in_scope_count`, `out_of_scope_count`, `assumptions_count`, `user_confirmed`.
Then `user_confirmed` is always `true` for a PASS receipt.
