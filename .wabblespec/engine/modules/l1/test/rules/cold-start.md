# Cold-Start Behavior — Test

Defines what Test does when its expected upstream artifacts are absent.

## Absent: spec artifacts

Condition: No files under `specs/` when Test runs.
Detection: Directory empty or 404.
Action: Surface DEPENDENCY error naming Specify. Test writes test plans against declared requirements — without specs, acceptance criteria are unknown.
Do NOT: Infer test cases from code structure alone.

## Absent: wave receipts (no execution has run)

Condition: No wave receipts exist — Test called before Executor has run.
Detection: No `wave-*-receipt.json` in `.wabblespec/state/receipts/`.
Action: If called pre-execution, Test operates in test-plan mode (writing test plans, not running tests). No DEPENDENCY error for this case — test planning is a valid pre-execution activity.
Do NOT: Attempt to run tests against code that has not been written yet.

## Absent: prior receipts

Condition: `specify-receipt.json` absent when Test is called in test-plan mode.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Specify.
Do NOT: Write test cases without confirmed acceptance criteria.

## Default state on cold start

| Field | Default |
|---|---|
| `mode` | `plan` (pre-execution) or `run` (post-execution) — inferred from presence of wave receipts |
| `coverage_target` | all acceptance criteria in spec (100% — no partial coverage by default) |
| `test_type` | unit + integration (default; E2E requires explicit declaration) |
