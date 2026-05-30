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

Present final TSV log and net delta from baseline.

## Pitfalls

- Guard files are read-only -- never modify files in Guard command scope
- Prefer `git revert` over `git reset` -- preserve history
- The verify command must complete in under 30 seconds; longer commands will cause timing issues
- Never skip the commit step -- git is the rollback mechanism, not a safety net
- A "shift strategy" at 5 discards means genuinely different files or approach, not minor variations on the same change

## Verify command contract

The verify command MUST:
- Output exactly one number to stdout
- Complete in under 30 seconds
- Return exit 0 on success
- Be deterministic (same code state → same metric)
