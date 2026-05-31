---
name: wave-refine
description: Iterative wave review-fix loop. Reviews the current wave output via /wave-review (3 parallel agents), fixes findings, re-reviews the full scope to confirm no regressions, repeats until all reviews pass or the iteration cap (3, matching the REVISE cap) is reached. Use when the user wants automated fix-verify cycles, asks to refine until clean, or needs the full review-fix loop without stopping.
---

# wave-refine

Iterative review-fix loop: `/wave-review` → fix → full-scope re-review → repeat.

Unlike `/wave-fix` (single-pass, no re-review), this skill re-runs the full parallel
review after each fix to confirm no regressions were introduced.

## Usage

```
/wave-refine [--type standard|security|design|multi] [--max-iterations N]
```

- `--max-iterations`: default 3 (matches WabbleSpec REVISE cycle cap)

## When NOT to use

- Review only, no fix (use `/wave-review`)
- Single-pass fix without re-review (use `/wave-fix`)
- Findings already in conversation — fix directly, do not start a new review loop

## Instructions

### 1. Initial review

Run `/wave-review` (3 parallel agents + Grader synthesis). If PASS: stop, inform user.

### 2. Fix-review loop (up to max-iterations)

#### 2a. Fix findings
Sort CRITICAL → HIGH → MEDIUM → LOW, grouped by file.

#### 2b. Verify
```bash
python .wabblespec/engine/shared/scripts/quality-floor-check.py
```
Fix regressions before re-reviewing.

#### 2c. Full-scope re-review

**SCOPE RULE:** Re-run `/wave-review` on the full wave output — not just the failing
criterion. A fix can introduce a regression in a previously-passing area. The full
parallel review must re-pass before reporting success.

```bash
python .wabblespec/engine/shared/scripts/wave-review.py --ref HEAD
```

Then invoke `/wave-review` on the new pending file.

- PASS → inform user, stop
- FAIL → next iteration (back to 2a)

### 3. Iteration limit

If max iterations exhausted and still FAIL: report iterations run, remaining findings,
suggest `/wave-fix` for targeted pass.

## See also

- `/wave-review` — review only
- `/wave-fix` — single-pass fix without re-review
