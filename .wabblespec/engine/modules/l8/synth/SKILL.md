---
name: synth
description: Converts a human-validated Instinct observation into a structured improvement hypothesis. One pattern in, one candidate.json out. Writes to .wabblespec/state/experiments/candidates/. Requires 3 validated patterns before first activation.
layer: L8
---

# Synth

You turn one observation into one hypothesis. No more, no less.

## What this skill does

Synth reads a single human-validated pattern from `instinct-observations.md`, reads the current SKILL.md of the affected module, and produces one `candidate.json` in `.wabblespec/state/experiments/candidates/`. The candidate is a structured claim: what the module currently does, what it should do differently, why, what the risk is, and when to roll back.

Synth does not write code. It does not propose implementations. It states the hypothesis clearly enough that Blueprint can define benchmark gates without asking Synth again.

## When to use

Do not activate unless ALL of the following are true:

1. `instinct-observations.md` contains ≥ 3 entries with `Human-validated: true`
2. Each validated entry has `Confidence: medium` or `high`
3. Human explicitly invokes Synth and names the specific pattern to process

Process one pattern per invocation. Do not batch.

## Inputs

| Input | Path | Required |
|---|---|---|
| Validated pattern | `.wabblespec/state/memory/instinct-observations.md` | Yes — must have `Human-validated: true` |
| Module SKILL.md | `modules/{layer}/{module}/SKILL.md` | Yes — read fully before writing |
| Instinct receipt | `.wabblespec/state/receipts/instinct-*.json` | Yes — confirms corpus was current |

Read the module's SKILL.md before writing anything. A hypothesis about behavior you have not read is invalid.

When multiple runs have produced overlapping observations for the same pattern, merge them deterministically per `.wabblespec/engine/shared/templates/observation-merge-guide.md` before synthesizing — one merged pattern in, one hypothesis out.

## Decision logic

Before writing, answer three questions:

1. **Is the pattern real?** Do the evidence receipts named in `instinct-observations.md` exist and confirm the described failure?
2. **Is the change bounded?** Can the behavior change be stated in one sentence? If multiple changes are implied, stop and surface the decomposition need to the human.
3. **Is the risk nameable?** Can you state a specific, measurable condition that would indicate rollback is needed? "Quality degrades" is not nameable. "False-completion rate rises above 15%" is.

If any answer is no: stop, write a one-paragraph note to the user explaining what is missing. Do not write `candidate.json`.

## Reference Routing

| Situation | Reference |
|---|---|
| Synth receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type synth` |

## Output contract

**One file:** `.wabblespec/state/experiments/candidates/{candidate-id}.candidate.json`

```json
{
  "candidate_id": "kebab-case-unique-id",
  "source_pattern": "Pattern N name from instinct-observations.md",
  "affected_module": "module-id matching framework.yaml",
  "behavior_change": "One sentence: what the module currently does vs what it should do instead.",
  "evidence": ["path/to/receipt1.json", "path/to/receipt2.json"],
  "risk": "What breaks or degrades if this change is applied incorrectly.",
  "rollback_condition": "Specific measurable condition that triggers rollback.",
  "created_at": "ISO-8601",
  "status": "pending"
}
```

All fields are required. Missing fields = invalid candidate, do not write.

**Good output:** `behavior_change` is specific enough that Blueprint can determine before/after states without asking Synth again.

**Bad output:** `behavior_change: "improve the module's detection accuracy"` — no specific before/after, not actionable.

## Failure modes

**Hypothesis inflation** — candidate describes multiple behavior changes. Fix: split into separate invocations.

**Evidence laundering** — candidate cites receipts that show failure but the failure count does not meet Instinct's thresholds. Fix: confirm pattern occurrence count before citing as evidence.

**Rollback drift** — rollback condition is aspirational ("if quality suffers"). Fix: rollback condition must name a metric and threshold from an existing receipt field or measurable output.

## Not tested

Synth cannot verify that its hypothesis, if implemented, will improve the module. Synth produces a structured claim. Blueprint defines the benchmark gate. Benchmark validates it.
