---
name: decompose
description: Breaks a locked task card into an ordered wave plan. Each wave is independently verifiable with a declared checkpoint and rollback target.
---

# Decompose

You are the architect of execution order. Given a locked task card, you decide how to break the work into waves — discrete, verifiable units where each wave leaves the project in a defined state. Decompose produces the contract that Executor follows. Executor does not modify the wave plan.

## What this skill does

Reads the locked task card. Confirms complexity (Low/Medium/High). Produces a wave plan where each wave declares: inputs, expected outputs, checkpoint condition, rollback target, and verification mode. Routes wave plan through Reviewer before Executor starts. Writes a receipt.

## When to use / when not to use

**Use when:**
- task-card.md is locked (Specify receipt exists)
- Explicit `/decompose` command
- A BREAKING deviation mid-execution requires re-decompose for affected stages

**Do not use when:**
- task-card.md is not locked (specify-receipt.json missing)
- Recipe declared `collapse_eligible: true` and complexity is Low — wave plan may collapse to single wave

## Inputs

- `.wabblespec/state/plans/task-card.md` (locked task card)
- `.wabblespec/scope.md` (boundary enforcement)
- `.wabblespec/recipe.json` (target, collapse_eligible)
- `.wabblespec/engine/shared/references/invariants.md`

## How to do it

### Step 1 — Confirm task card is locked

Read `specify-receipt.json`. If missing or status FAIL: stop, surface to user, route back to Specify.

### Step 2 — Confirm complexity

Recipe scored complexity at intake. Re-confirm against the full task card now. Use Low/Medium/High criteria from Recipe. If revised upward, note the reason in the wave plan.

### Step 3 — Sequence waves

Rules:
- Each wave produces at least one artifact that can be independently verified
- No wave depends on partial output of another wave
- Foundation before integration: schema before implementation, data model before API, storage before business logic
- Wave 1 always has `rollback_to: null`
- Each subsequent wave's rollback target is the previous wave's checkpoint

**Rollback target selection per wave:**

| Rollback type | When to assign |
|---|---|
| `null` | Wave 1 only |
| `wave-checkpoint` | Default for all other waves — Executor writes file copies to `.wabblespec/state/checkpoints/<wave-id>/` |
| `worktree` | High complexity AND wave contains irreversible operations (migrations, breaking schema changes, framework file edits). Target project must be a git repo. Fallback to `wave-checkpoint` if git worktree unavailable. |

Assign `worktree` only when all three conditions hold: (1) complexity is High, (2) the wave's outputs include at least one irreversible operation, (3) target project has a git repository. If uncertain, default to `wave-checkpoint` — do not assign `worktree` speculatively.

Wave count guidelines:
- Low: 1–2 waves
- Medium: 2–4 waves
- High: 4–8 waves (more than 8 requires user confirmation before writing plan)

### Step 3b — Declare verification command per wave

Every wave must include a `verification_command`: the exact shell command that proves the checkpoint condition is satisfied when run. No pseudocode. No descriptions. A command that can be copied and executed as-is.

If no runnable command exists for a wave (human judgment required, visual inspection, live environment), set `verification_mode` to Attestation — not Observation. Defaulting to Observation when no command is available silently removes the verification gate.

### Step 4 — Assign verification mode per wave

For each wave, declare the mode Verifier will use. Pick the strongest mode that applies:

| Mode | When to use |
|---|---|
| Test | Automated assertion is possible (unit tests, CLI output, file content check) |
| Observation | Artifact existence and state are the criteria (config generated, file written) |
| Audit | Compliance check against task card criteria |
| Review | Output requires judgment (spec quality, design decisions) |
| Attestation | Irreversible action requiring explicit human sign-off |
| Demonstration | Working proof must run against real conditions |

### Step 5 — Write wave plan

Write to `.wabblespec/state/plans/current-wave-plan.md`. See output contract.

### Step 6 — Route to Reviewer

Wave plan is a HIGH-impact decision (execution contract). Route to Reviewer. Reviewer checks: wave sequence is logical, each wave is independently verifiable, rollback targets declared.

### Step 7 — Write receipt

Write to `.wabblespec/state/receipts/decompose-receipt.json`.

## Output contract

**current-wave-plan.md** (`.wabblespec/state/plans/current-wave-plan.md`):

```markdown
# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** <from recipe.json>
**complexity:** Low|Medium|High
**collapse_eligible:** true|false
**generated_at:** ISO-8601-timestamp

## Waves

### Wave 1: <name>

**inputs:** [task-card sections, context files]
**outputs:** [expected artifacts — specific paths or named artifacts]
**checkpoint:** <condition that must be true before Wave 2 begins>
**rollback_to:** null
**verification_mode:** Test|Review|Audit|Measurement|Observation|Attestation|Demonstration

---

### Wave 2: <name>

**inputs:** [Wave 1 outputs + task-card sections]
**outputs:** [expected artifacts]
**checkpoint:** <condition that must be true before Wave 3 begins>
**rollback_to:** Wave 1 checkpoint
**verification_mode:** <mode>

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 2 fails | Wave 1 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |
```

**receipt** (`.wabblespec/state/receipts/decompose-receipt.json`): base receipt. Extension: `wave_count` (integer), `complexity_confirmed` (Low|Medium|High), `reviewer_triggered` (boolean), `rollback_checkpoints` (integer), `waves_with_verification_command` (integer — must equal `wave_count`; a mismatch indicates a wave was left without a runnable verification command).

## A note on common failure modes

1. **Wave with no verification command defaults silently to Observation.** Observation mode passes any wave where the artifact exists, regardless of functional correctness. If you cannot write a runnable verification command, the mode must be Attestation — not Observation. Never leave `verification_command` blank and keep the mode as Observation.

2. **Waves that depend on each other's partial output.** Each wave must be a complete unit. If Wave 2 needs Wave 1 "half done," re-sequence: either merge them or split Wave 1 into a clean prerequisite.

3. **Verification mode too weak.** "Observation" for a wave that produces runnable code misses functional correctness. Pick the strongest mode that applies — Verifier uses what you declare.

4. **Too many waves for Low complexity.** A single Low-complexity feature with 5 waves has been over-engineered. Merge or collapse.
