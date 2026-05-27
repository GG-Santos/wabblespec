# Clean — Acceptance Criteria

## BLOCK: absent scope declaration

Given Clean is invoked without a declared scope,
Then Clean surfaces a DEPENDENCY error: "Clean requires a declared scope."
Then Clean does not apply any changes.
Then Clean does not self-scope.

## BLOCK: absent wave receipts

Given no wave receipts exist in `.wabblespec/state/receipts/`,
When Clean is invoked,
Then Clean surfaces a DEPENDENCY error: "Clean operates on completed wave output."
Then Clean does not run cleanup passes against in-progress or uncommitted code.

## BLOCK: absent decompose receipt

Given `decompose-receipt.json` is absent,
When Clean is invoked,
Then Clean surfaces a DEPENDENCY error naming Decompose.
Then Clean does not run unbounded cleanup without declared scope.

## Happy path: COSMETIC cleanup within scope

Given a declared scope and completed wave receipts exist,
When Clean audits the declared scope,
Then dead code confirmed by static analysis is classified COSMETIC and removed.
Then formatting violations (whitespace, indentation, line endings) are classified COSMETIC when a format config exists and normalized.
Then deprecated patterns flagged by Specify are classified COSMETIC and removed.
Then a before/after diff is written to `.wabblespec/state/receipts/clean-diff-<timestamp>.md`.
Then a Clean receipt is written to `.wabblespec/state/receipts/`.

## Delta classification: ADDITIVE rename

Given Clean identifies a rename that matches spec conventions,
When the change is classified,
Then the rename is classified ADDITIVE (minimum).
Then the rename is applied and recorded in the diff.

## BREAKING changes: halt and route

Given Clean identifies a change that would break consumers (e.g., a rename across a public interface),
When the change is classified,
Then Clean halts and classifies it BREAKING.
Then Clean routes it to Executor with a Specify delta.
Then Clean does not apply the BREAKING change.

## Scope invariant:  only

Given any Clean invocation,
Then Clean validates that all targets are within product space (I11 check).
Then Clean never touches `.wabblespec/`.
Then Clean never modifies test assertions.

## Do NOT: introduce abstractions

Given Clean encounters code that could benefit from extraction or refactoring,
Then Clean surfaces the opportunity but does not apply the structural change.
Then structural changes are routed to Specify and Executor.

## Do NOT: rename across package boundaries

Given a rename would cross package or module boundaries,
Then Clean does not apply it.
Then Clean surfaces it and routes to Migrate.

## Scope bounded to last wave

Given Clean is invoked without explicit scope declaration and wave receipts exist,
Then cleanup scope is bounded to files touched by the most recent completed wave.
