# Benchmark — Acceptance Criteria

## Gate validation

Given a blueprint benchmark_gate with no developer_outcome field,
When Benchmark evaluates it,
Then Benchmark rejects the gate before running and surfaces the missing field to human.

Given Augment receipt with structural_check_passed: false,
When Benchmark is invoked,
Then Benchmark refuses and names the incomplete Augment.

Given fixture set path in blueprint does not exist on disk,
When Benchmark is invoked,
Then Benchmark refuses and names the missing fixture path.

## Threshold enforcement

Given AUGMENT change_type and experimental module scores 85% parity on held-out set,
When threshold is 80%,
Then verdict is PASS and blueprint status is updated to benchmark-passed.

Given AUGMENT change_type and experimental module scores 75% parity on held-out set,
When threshold is 80%,
Then verdict is FAIL, failure_note is written to tracker.json, blueprint status unchanged.

Given NEW change_type and experimental module scores 65% improvement over baseline,
When threshold is 60%,
Then verdict is PASS.

## tracker.json integrity

Given any Benchmark run,
Then result is appended to tracker.json — existing entries unmodified.
Then held-out value recorded, not tuning-set value.

Given FAIL verdict,
Then failure_note is non-empty.
Then requeue_decision is null (no auto-requeue).

## Promotion gating

Given FAIL verdict,
Then Forge is blocked for this blueprint ID.
Then blueprint status remains approved (not benchmark-passed).

Given PASS verdict,
Then blueprint status is updated to benchmark-passed.
Then tracker.json entry has verdict: PASS.

## Control arm validation

Given a benchmark fixture for a candidate that modifies probabilistic behavior (output style, phrase detection, heuristic classification, confidence thresholds),
And the fixture has no `control_arm` field,
When Benchmark evaluates the fixture,
Then Benchmark surfaces MISSING_CONTROL_ARM to the human.
Then Benchmark does not run the gate until the human either provides the arm or explicitly confirms it is inapplicable.
Then the warning is recorded in tracker.json with `verdict: "WARN"`.

Given a benchmark fixture for a candidate that adds a deterministic structural gate (file existence check, schema field presence),
And the fixture has no `control_arm` field,
When Benchmark evaluates the fixture,
Then Benchmark does not surface MISSING_CONTROL_ARM.
Then the gate runs without a control arm.

Given a benchmark fixture with a valid `control_arm` object,
When Benchmark records the tracker.json entry,
Then `honest_delta` is recorded alongside `held_out_value`.
Then `honest_delta` equals `held_out_value` minus `arm_held_out_value`.

## Boundary enforcement

Given any Benchmark run,
Then no file in modules/ is created or modified.
Then Augment output files are not modified.
Then only tracker.json and blueprint status field are mutated.
