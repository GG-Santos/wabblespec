---
name: brainstorm
description: Divergent idea generation before convergent planning. Produces a ranked option set for downstream evaluation. Invoked on-demand before Specify or Propose when the solution space is genuinely open.
---

# Brainstorm

You generate options. You do not evaluate them. The moment you begin comparing options during generation, you have left Brainstorm's territory and entered Propose's. Keep them separate.

## What this skill does

Receives a problem or opportunity statement. Generates ideas across the full solution space without evaluation or filtering. Stops when a convergence signal is reached. Writes a ranked option list and delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| Brainstorm receipt write (Step 4) | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type brainstorm` |

## When to use / when not to use

**Use when:**
- Solution space is genuinely open: multiple viable approaches exist and the best is not obvious
- Explicit `/brainstorm` command
- Propose signals that it lacks sufficient options to recommend
- ScopeFrame or Specify surfaces a design decision where no prior art applies

**Do not use when:**
- The solution is already clear — go directly to Propose or Specify
- Brainstorm was already run this session for this problem with no new information
- The task is implementation (Executor) or debugging (Triage) — these are not option-generation problems

## Inputs

- Problem or opportunity statement (from user, ScopeFrame, or Propose)
- Any known constraints (from scope.md if available)

## How to do it

### Step 1 — Set generation mode

**Divergent mode:** No evaluation during generation. Every idea gets written down. Ideas that seem poor at this stage sometimes reveal constraints others don't. Quantity over quality. Do not prune.

Read rules/divergence-rules.md before generating. The most common failure mode is premature convergence — evaluating during generation.

### Step 2 — Generate options

Generate ideas across the full solution space. Aim for breadth across these dimensions (not all will apply to every problem):
- Different architectural approaches (centralized vs distributed, synchronous vs async)
- Different technology choices (if relevant)
- Different trade-off profiles (speed vs reliability, simplicity vs power)
- Different scope assumptions (solve the narrow problem, solve the broader problem)
- Reuse of existing components vs building new

Do not limit to "good" ideas. An idea that turns out to be impractical still helps bound the space.

Continue until a convergence signal fires. See rules/convergence-gate.md.

### Step 3 — Surface top options

After convergence: review the full generated set. Select the 3–5 options most worth evaluating. Surface them in a ranked list. Ranking at this stage is by potential, not recommendation — Propose evaluates and recommends.

This is the only evaluation step in Brainstorm. Do not score, compare, or argue for any option. Just select which ones have enough merit to pass to evaluation.

### Step 4 — Write receipt

Write top options to `.wabblespec/state/brainstorm/options-<timestamp>.md`. Then write receipt:

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type brainstorm \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --requirements "<option-1>" "<option-2>" \
  --out .wabblespec/state/receipts/brainstorm-receipt-<timestamp>.json
```

Pass options file path to Propose (or Specify) for evaluation.

## Output contract

**brainstorm-receipt.json** (`.wabblespec/state/receipts/brainstorm-receipt-<timestamp>.json`):

Base receipt schema extended with fields per `schemas/brainstorm-receipt.schema.json`. Key extension fields:

```json
{
  "options_generated": "integer — total ideas generated before convergence",
  "convergence_trigger": "volume_cap | diminishing_returns | user_signal | time_budget",
  "options": ["array of option summary strings — one per option in top set"],
  "evaluation_deferred": "boolean — must be true; false = invariant violation",
  "top_options_path": ".wabblespec/state/brainstorm/options-<timestamp>.md"
}
```

`evaluation_deferred: true` is a hard invariant. If Brainstorm evaluated options during generation — ranking, comparing, arguing for — this is a process failure. Record `false` and surface it.

## A note on common failure modes

1. **Evaluation during generation.** The most common failure. The moment you write "this approach is better because..." you have stopped generating and started evaluating. The antidote: write options as neutral descriptions, not arguments.

2. **Too few options.** Stopping at 3 ideas because the first 3 seem good misses the value of divergent thinking. Push into the uncomfortable part of the space where good ideas often hide.

3. **All options within one paradigm.** If every option is a variation on the same approach, Brainstorm has not been divergent. Ask: what would a developer from a completely different background propose here?

4. **Generating noise.** The convergence gate exists to prevent endless generation. When ideas stop being genuinely new (diminishing returns), stop. Surfacing 50 options defeats the purpose.
