---
name: benchmark-loop
description: Autonomously optimize a measurable metric by iterating one atomic git-committed change at a time, reverting on regression, and surfacing findings when stuck.
---

# benchmark-loop

Runs an autonomous metric optimization loop: one atomic change per iteration, committed before verify, reverted on regression. Does not generate or propose changes on its own -- the user or a prior skill identifies the optimization target; this skill runs the iteration loop.

## When to use

- `/benchmark-loop` is invoked with a verify command and an optimization target
- The working tree is clean and the project is a git repository
- A measurable quality score (number to stdout) can be obtained in under 30 seconds

## When NOT to use

- No verify command exists that outputs a single number -- use `/benchmark` (static measurement) instead
- The working tree has uncommitted changes -- commit or stash first
- The user wants a one-shot quality measurement without iteration -- use `quality-floor-check.py` directly

## How to do it

### Step 0 -- Declare Hypothesis (Required)

Before any iteration begins, write a structured hypothesis. This is not optional — a loop without a declared hypothesis produces descriptive results, not confirmatory ones.

**Template:**
```
IF we [change to framework artifact X]
THEN [quality metric Y] will [increase/decrease] by [estimated delta, e.g. "+3 points"]
BECAUSE [evidence: drawer ID, receipt, or prior observation]
```

**Quality checklist (all five must be satisfied before proceeding to Step 1):**
- [ ] Single variable being tested (one change at a time, describable in one sentence without "and")
- [ ] Specific metric defined (not "quality" — name the exact metric the verify command outputs)
- [ ] Estimated effect size stated (the expected delta — needed to classify the outcome)
- [ ] Timeframe defined (maximum iteration count or stop condition)
- [ ] Success/failure criteria clear before launch (what delta counts as Confirmed vs Inconclusive)

**Outcome classification (applied per iteration and at loop end):**
- `Confirmed` — delta >= declared estimate and in the correct direction
- `Refuted` — delta is negative or opposite direction
- `Inconclusive` — delta within noise floor (< 5% of baseline metric or < 0.5 absolute)

Add a `hypothesis_confirmed` column to the TSV log with value `Confirmed`, `Refuted`, or `Inconclusive` for each iteration.

### Step 1 -- Validate preconditions

1. Confirm working tree is clean (`git status --short` returns empty)
2. Confirm verify command outputs a single number: `<verify_cmd> | python -c "import sys; float(sys.stdin.read().strip())"`
3. Record baseline metric value

### Step 2 -- Iteration loop

For each iteration:
1. Make exactly ONE atomic change (describable in one sentence without "and")
2. `git commit -m "<change description>"` BEFORE verifying
3. Run verify command; capture metric value
4. If metric improved: advance (keep commit)
5. If metric regressed or unchanged: `git revert HEAD --no-edit` (discard)
6. Append to TSV log: `iteration\tcommit\tmetric\tdelta\tstatus`

### Step 3 -- Stuck detection

- After 5 consecutive discards: analyze discard patterns → shift strategy (different files, different approach)
- After 10 consecutive discards: STOP. Surface findings to user:
  - What was tried
  - What the discard pattern suggests
  - Recommended next approach

### Step 4 -- Completion

Stop when:
- Metric reaches target (if provided)
- 10 consecutive discards (stuck)
- User interrupts

Before declaring a final verdict, confirm all four conditions hold:
- [ ] Reached the iteration count or target declared in Step 0 (not stopped early on a single good result)
- [ ] Effect size is meaningful — net delta exceeds the noise floor (< 5% of baseline or < 0.5 absolute counts as inconclusive)
- [ ] Results are consistent across the last 3 iterations (a single spike does not count as convergence)
- [ ] Hypothesis outcome is classified: `Confirmed`, `Refuted`, or `Inconclusive` per the Step 0 criteria

Present final TSV log and net delta from baseline.

## Pitfalls

- Guard files are read-only -- never modify files in Guard command scope
- Prefer `git revert` over `git reset` -- preserve history
- The verify command must complete in under 30 seconds; longer commands will cause timing issues
- Never skip the commit step -- git is the rollback mechanism, not a safety net
- A "shift strategy" at 5 discards means genuinely different files or approach, not minor variations on the same change

## Experiment receipt

When a benchmark-loop run concludes, write an experiment receipt to record the full hypothesis-to-outcome trail:

```
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type experiment \
  --task-id <task-id> --session-id <session-id> \
  --experiment-hypothesis "We believe [change] will [metric] because [reasoning]" \
  --experiment-variants "<variant-a-path>" "<variant-b-path>" \
  --experiment-primary-metric "<metric-name>" \
  --experiment-winner "<winning-variant-or-inconclusive>" \
  --experiment-outcome <CONFIRMED|REFUTED|INCONCLUSIVE> \
  --experiment-learnings "<what was learned regardless of outcome>" \
  --status COMPLETE --confidence <0.0-1.0> \
  --out .wabblespec/state/receipts/experiment-<timestamp>.json
```

The `--experiment-outcome` field must match the Step 0 hypothesis outcome classification. The `--experiment-learnings` field is required even for REFUTED outcomes — a refuted hypothesis is still learning.

## Verify command contract

The verify command MUST:
- Output exactly one number to stdout
- Complete in under 30 seconds
- Return exit 0 on success
- Be deterministic (same code state → same metric)
