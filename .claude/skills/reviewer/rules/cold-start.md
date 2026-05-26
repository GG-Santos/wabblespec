# Cold-Start Behavior — Reviewer

Defines what Reviewer does when its expected upstream artifacts are absent.

## Absent: wave output to review

Condition: No completed wave output or executor receipt when Reviewer is called.
Detection: No `wave-*-receipt.json` or no changed files from a wave.
Action: Surface DEPENDENCY error — Reviewer reviews wave output. Without a completed wave, there is nothing to review.
Do NOT: Review speculative or hypothetical output.

## Absent: spec artifacts (no acceptance criteria)

Condition: No files under `specs/` when Reviewer runs.
Detection: Directory empty or 404.
Action: Surface DEPENDENCY error naming Specify. Reviewer needs acceptance criteria to evaluate against.
Do NOT: Review wave output without declared criteria — produces arbitrary feedback.

## Absent: defect-patterns reference

Condition: `_shared/references/defect-patterns.md` absent.
Detection: File read returns 404.
Action: Proceed with built-in review heuristics only. Log SOFT warning: `defect_patterns_reference: absent`.
Do NOT: Block review — defect-patterns is a reference aid.

## Default state on cold start

| Field | Default |
|---|---|
| `review_scope` | all files changed by the current wave |
| `criteria_source` | spec acceptance criteria (required) |
| `finding_threshold` | MEDIUM and above surface to human; LOW logged to receipt only |
