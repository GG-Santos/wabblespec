# Cold-Start Behavior — Verifier

Defines what Verifier does when its expected upstream artifacts are absent.

## Absent: wave output to verify

Condition: No completed wave receipt when Verifier runs.
Detection: No `wave-*-receipt.json` in `.wabblespec/receipts/`.
Action: Surface DEPENDENCY error naming Executor. Verifier verifies wave output — it requires a completed wave.
Do NOT: Verify a wave that has not completed.

## Absent: spec artifacts

Condition: No spec files when Verifier runs.
Detection: `specs/` empty or 404.
Action: Surface DEPENDENCY error naming Specify. Verifier checks wave output against acceptance criteria — without specs, criteria are unknown.
Do NOT: Perform verification without declared acceptance criteria.

## Absent: guard receipt for the wave

Condition: `guard-wave-{N}-receipt.json` absent when Verifier checks Wave N.
Detection: Expected receipt stem missing.
Action: Surface DEPENDENCY error — Guard must have PASSed the wave before Verifier can verify it. Verifier trusts Guard's pre-execution check; running Verifier without Guard PASS would bypass I4.
Do NOT: Verify a wave that did not pass Guard.

## Default state on cold start

| Field | Default |
|---|---|
| `verification_mode` | `criteria-match` (checks output against spec acceptance criteria) |
| `pass_threshold` | all criteria must be met — partial pass is FAIL |
| `evidence_required` | yes — Verifier must produce evidence of each criterion check |
