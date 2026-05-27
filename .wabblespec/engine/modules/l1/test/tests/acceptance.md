# Test — Acceptance Criteria

## BLOCK: absent spec artifacts

Given `specs/` is empty or returns 404,
When Test is invoked in test-plan mode,
Then Test surfaces a DEPENDENCY error naming Specify.
Then Test does not infer test cases from code structure alone.
Then no test plan is written.

## BLOCK: absent specify receipt (test-plan mode)

Given `specify-receipt.json` is absent and Test is called in test-plan mode,
When Test runs,
Then Test surfaces a DEPENDENCY error naming Specify.
Then Test does not write test cases without confirmed acceptance criteria.

## Happy path: EARS requirement mapping

Given a P4 spec with EARS requirements,
When Test runs,
Then every WHEN/THEN requirement maps to at least one positive case and one boundary case.
Then every IF/WHEN/THEN requirement maps to a positive case and a condition-not-met case.
Then every WHILE requirement maps to a state-entry test and a state-exit test.
Then a test plan is written to `.wabblespec/plans/test-plan-<spec-id>.md`.
Then test stubs are written to `tests/`.
Then a receipt is written to `.wabblespec/receipts/`.

## Untestable requirements: flag, never skip

Given a requirement cannot be mapped to a test case (e.g., it is too vague or describes a subjective property),
When Test processes it,
Then the requirement is flagged with `<!-- UNTESTABLE: <reason> -->`.
Then the requirement is added to the "Untestable Requirements" section of the test plan.
Then the requirement is not silently omitted.

## Test framework: read from platform package

Given the active L3 platform package declares testing conventions,
When Test selects a framework,
Then the framework is read from the platform package testing conventions.
Then Test does not infer the test framework from the file structure alone.

## Pre-execution mode: plan only

Given no wave receipts exist (Executor has not yet run),
When Test is invoked,
Then Test operates in test-plan mode (writing stubs and plans, not running tests).
Then no DEPENDENCY error is surfaced for absent wave receipts in pre-execution mode.
Then no attempt is made to run tests against code that has not been written yet.

## Test stubs: written to tests/ only

Given any Test run,
Then test stubs are written to `tests/` only.
Then Test does not write stubs outside that path.
Then Test does not execute tests — stub generation only.

## Coverage target: 100% of acceptance criteria

Given any Test run in test-plan mode,
Then a test case is generated for every acceptance criterion in the spec.
Then partial coverage (skipping criteria) is not permitted.
Then the Coverage Matrix in the test plan lists every requirement ID with its test case count.

## Test plan required fields

Given any written test plan,
Then the plan contains: `generated_from`, `generated_at`, `requirements_covered`, `requirements_untestable`, Coverage Matrix table, Untestable Requirements table, Test Framework section.
