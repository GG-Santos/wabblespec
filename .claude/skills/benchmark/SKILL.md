---
name: benchmark
description: Quality gate before any module promotion. Runs experimental implementation against fixture set, computes held-out metric, compares against blueprint threshold. AUGMENT type requires >= 80% parity. NEW type requires >= 60% improvement over baseline. Failure halts promotion and appends to tracker.json.
layer: L8
---

# Benchmark

You measure whether the experiment earned promotion. Not whether it looks good — whether it passes the gate.

## What this skill does

Benchmark reads an Augment output and a blueprint.json benchmark_gate definition, then runs the experimental module against a committed fixture set. It computes the held-out metric only (never the tuning-set metric), compares against the blueprint threshold, and records the result in `.wabblespec/state/experiments/tracker.json`. Pass: promotion proceeds. Fail: promotion halts, failure note appended to tracker.json, no requeue without human decision.

See `rules/benchmark-discipline.md` for integrity rules. Load it before running any benchmark.

## When to use

Benchmark activates when:
1. Augment receipt exists for the blueprint ID with `structural_check_passed: true`
2. `blueprint.json` status is `approved`
3. Fixture set exists at the path declared in blueprint benchmark_gates
4. Human explicitly invokes Benchmark with the blueprint ID

## Inputs

| Input | Path | Required |
|---|---|---|
| Augment output | `.wabblespec/state/experiments/augments/{blueprint-id}/` | Yes |
| Blueprint | `.wabblespec/state/experiments/blueprints/{id}.blueprint.json` | Yes |
| Augment receipt | `.wabblespec/state/receipts/augment-*.json` | Yes |
| Fixture set | Path from blueprint benchmark_gates[].reproducible.fixtures_path | Yes — must be committed |

## Thresholds (from I8)

| Change type | Gate |
|---|---|
| AUGMENT (modifying existing) | Held-out metric >= 80% parity with current production module |
| NEW (net-new module) | Held-out metric >= 60% improvement signal over baseline |

Parity means: on the same fixture set, the experimental module scores within 80% of the production module's score (or better). Improvement means: the experimental module scores at least 60% above the documented baseline value.

Read `benchmark_gates[].developer_outcome` to confirm the metric is tied to a real failure mode before accepting the gate as valid. A gate without a developer_outcome link is rejected before running.

## Workflow

1. Load `rules/benchmark-discipline.md`.
2. Read blueprint benchmark_gates. Reject any gate without `developer_outcome`.
3. Confirm fixture set exists and is committed (not fetched at runtime).
4. Determine split: `held_out_cases` from blueprint held_out_split.
5. Run experimental module against held-out fixtures only.
6. Compute metric. Compare to threshold.
7. Write result to tracker.json.
8. If PASS: update blueprint status to `benchmark-passed`. Forge may proceed.
9. If FAIL: append failure note to tracker.json. Do not update blueprint status. Halt.

## Control Arm Requirement

For evolution candidates that modify probabilistic or stylistic behavior — phrasing, verbosity, heuristic detection, confidence thresholds — a `control_arm` is required in the benchmark fixture.

**Why:** Comparing a candidate against a verbose baseline conflates "the candidate works" with "any brevity instruction would work." The honest delta is candidate vs a minimal control condition, not candidate vs no instruction at all.

**When `control_arm` is required:** Candidates modifying output style, phrase detection, confidence thresholds, or any heuristic classification.

**When `control_arm` is NOT required:** Candidates adding deterministic structural gates (file existence check, schema field presence, path detection). These are pass/fail on specific conditions — a control arm has no meaning.

**How to set it:**
1. Choose `arm_type`: `terse_instruction` (most common — compare against "be brief"), `system_prompt`, or `minimal_spec`.
2. Run the control arm against the same held-out fixture set.
3. Record `arm_held_out_value` and compute `honest_delta = candidate_held_out_value - arm_held_out_value`.
4. A delta of 0.0 means the candidate adds no value beyond a generic instruction. A delta ≥ 0.1 (in the right direction) suggests real candidate contribution.

**Missing control arm:** When a candidate modifies probabilistic behavior and `control_arm` is absent from the fixture, Benchmark surfaces `MISSING_CONTROL_ARM` and requests the arm before proceeding with the gate run. This is a WARN — not a hard block — to allow humans to explicitly decide that a control arm is inapplicable.

## tracker.json structure

```json
{
  "entries": [
    {
      "blueprint_id": "string",
      "run_at": "ISO-8601",
      "metric_name": "string",
      "held_out_value": 0.0,
      "threshold": 0.0,
      "verdict": "PASS | FAIL | WARN",
      "failure_note": "Required when verdict is FAIL",
      "requeue_decision": null
    }
  ]
}
```

`tracker.json` is append-only. Entries are never removed or edited.

## Output contract

**Mutates:** `.wabblespec/state/experiments/tracker.json` (append only)
**Mutates:** `.wabblespec/state/experiments/blueprints/{id}.blueprint.json` status field (PASS only)

**Good outcome:** held-out metric meets threshold, verdict PASS, blueprint status updated, Forge unblocked.
**Bad outcome:** held-out metric below threshold, verdict FAIL, failure_note written, blueprint status unchanged, Forge blocked.

## Failure modes

**Tuning contamination** — benchmark computed on tuning set, not held-out set. Fix: held-out split must be defined in blueprint before Augment runs. Benchmark reads only held-out cases.

**Gate without developer outcome** — benchmark_gate has no `developer_outcome` field. Fix: reject gate before running, surface to human, return to Blueprint for correction.

**Silent WARN** — benchmark produces WARN verdict without surfacing to human. Fix: WARN verdict is surfaced immediately. Human decides whether to proceed or return to Augment.

## Dev / held-out split protocol

Every fixture set must define a `split.json` before Augment runs. No split = no benchmark.

**Split ratios:**
- Dev set (tuning-safe): 20% of fixtures
- Held-out set (touch once): 80% of fixtures

**`split.json` structure:**
```json
{
  "version": "1.0",
  "fixture_set": "path/to/fixtures/",
  "created_at": "ISO-8601",
  "dev_cases": ["fixture-id-1", "fixture-id-2"],
  "held_out_cases": ["fixture-id-3", "fixture-id-4"]
}
```

**Integrity rules:**
1. Dev cases may be used during iterative Augment tuning.
2. Held-out cases are touched exactly once — at final gate evaluation.
3. If you look at a held-out case's output during tuning, that case is contaminated and must be removed from the held-out set before the final gate run.
4. Benchmark reads `split.json` to determine which cases to run. If `split.json` is absent, Benchmark rejects the run before executing any fixture.
5. New fixtures added after the split was created go to dev by default; a human must explicitly promote any to held-out.

**Creating a split:**
Run `scripts/create-fixture-split.py --fixtures-dir {path} --held-out-ratio 0.8` to generate the initial `split.json`. The split is random but reproducible via a fixed seed (fixture directory name).

## Not tested

Benchmark cannot test the module on real production traffic — only on committed fixtures. Fixtures represent known cases; novel edge cases are not covered until the module accumulates receipts post-promotion.
