---
name: retro
description: Post-execution retrospective. Reads completed wave receipts and produces a structured retro-{timestamp}.md in .wabblespec/state/memory/retro/. Identifies receipt chain health, wave patterns, and unresolved gaps. Does not propose fixes — Synth does that.
layer: L8
---

# Retro

You look back. You record what happened. You do not prescribe what to do next.

## What this skill does

Retro reads all receipts from a completed execution (one task from Recipe through Archive), identifies the receipt chain health, flags any waves where FAIL/PARTIAL occurred, and notes REVISE cycles consumed. It produces one `retro-{timestamp}.md` in `.wabblespec/state/memory/retro/`. The output is structured for human review and as future signal for Instinct.

Retro does not propose module improvements. It does not modify receipts. It does not invoke Synth. It observes and records.

## When to use

Retro activates after an execution completes — Recipe through Archive chain is present in `.wabblespec/state/receipts/`. Invoked manually or by Autopilot post-session.

**Do not run during an active execution.** Check for Executor PID lock before starting.

## Inputs

| Input | Path | What Retro reads |
|---|---|---|
| Execution receipts | `.wabblespec/state/receipts/*.json` | All receipts from the target execution run |
| framework.yaml | `framework.yaml` | Module dependency graph for chain validation |

Retro reads receipts by `timestamp` range or by an execution ID if provided. If no execution ID is given, it reads the most recent complete chain (Recipe → Archive).

## Output contract

**One file:** `.wabblespec/state/memory/retro/retro-{ISO-timestamp}.md`

```markdown
# Retro — {execution summary}

Date: ISO-8601
Execution ID: {id or "inferred"}
Modules in chain: N
Receipt chain health: INTACT | BROKEN | PARTIAL

## Wave Summary

| Wave | Module | Status | REVISE cycles | Notes |
|---|---|---|---|---|
| 1 | recipe | PASS | 0 | |

## Receipt Chain

Chain intact: yes | no
Missing receipts: [list or none]
Broken links: [which module receipt was absent when downstream ran]

## Patterns Observed

[List of patterns — what recurred, what was unusual. No recommendations.]

## Unresolved Gaps

[What finished with PARTIAL status and why. No prescriptions.]

## Not Tested

[What this Retro could not evaluate.]
```

## Failure modes

**Prescriptive drift** — Retro includes "should", "recommend", or "fix" language. Fix: Retro uses "observed", "occurred", "was present". Recommendations belong to Synth.

**Incomplete chain read** — Retro reads only some receipts from the execution, missing intermediate waves. Fix: read all receipts with matching execution context before writing.

**Retro during active execution** — Retro runs while Executor PID lock is active. Fix: check for lock before starting; exit if found.

## Not tested

Retro cannot determine whether the patterns it observes are statistically significant — that requires Instinct with 100+ receipts. Retro's observations are raw material, not conclusions.
