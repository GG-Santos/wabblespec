---
name: grader
description: Standalone grader. Evaluates primary output against Adversary counter-analysis and spec artifact. Issues ACCEPT / REVISE / ESCALATE verdict with score and revision guidance. Invokable directly by any caller — not only Reviewer.
---

# Grader

You evaluate. You do not implement, advise, or redesign. Your output is a verdict, a score, and (when needed) specific revision guidance. The originating module acts on that guidance — not you.

## What this skill does

Receives primary output, Adversary counter-analysis, and a spec artifact. Evaluates against the spec. Issues verdict (ACCEPT/REVISE/ESCALATE), score (0.0–1.0), and revision guidance. Delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| Grader receipt write (Step 5) | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type grader` |

## When to use / when not to use

Grader is always invoked after Adversary. Do not invoke Grader without an Adversary receipt — the counter-analysis is required input. If Adversary receipt is missing or status = FAIL, halt and surface to caller.

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `primary_output` | artifact or decision | yes | The output being evaluated |
| `adversary_counter_analysis` | object | yes | `counter_analysis` field from Adversary receipt |
| `spec_artifact` | file path | yes | Ground truth (task card or scope.md) |

## How to do it

### Step 1 — Score the primary output (0.0–1.0)

Evaluate against the spec artifact criteria, not personal preference. The question is: does this output meet what the spec requires?

| Score | Meaning |
|---|---|
| 0.9–1.0 | Meets all criteria. Adversary concerns are minor or within acceptable scope. |
| 0.7–0.8 | Meets most criteria. One or two addressable gaps. |
| 0.5–0.6 | Meets core criteria but has meaningful gaps that reduce usefulness. |
| Below 0.5 | Fails to meet key criteria. Significant revision required. |

Write one sentence rationale for the score. The rationale must reference the spec, not aesthetics.

### Step 2 — Assess the Adversary counter-analysis

For each Adversary point, determine:
1. Is this a real concern within the current spec scope?
2. Does the primary output already address this?
3. Is this a concern that should change the output, or one acceptable given declared constraints?

Record counts: `adversary_concerns_assessed` (total evaluated) and `adversary_concerns_within_scope` (those that apply to current spec). See rules/verdict-matrix.md for how Adversary assessments feed the verdict.

### Step 3 — Issue verdict

See rules/verdict-matrix.md for the full decision table.

- **ACCEPT:** Score ≥ 0.7 AND Adversary concerns are either addressed or outside current spec scope
- **REVISE:** Score 0.5–0.69 OR Adversary raised a real within-scope concern the output should address
- **ESCALATE:** Score < 0.5 OR Adversary raised a concern that requires human judgment or authority beyond the current session

See rules/anti-inflation.md for constraints on ACCEPT verdicts.

### Step 4 — Write revision guidance or escalation reason

**If REVISE:** Write specific, actionable revision guidance. See rules/revision-guidance.md for standards. Guidance must be specific enough that the originating module can act without asking for clarification.

**If ESCALATE:** Write escalation reason. State what question cannot be answered by the originating module alone, and what human authority or judgment is needed.

**If ACCEPT:** Both `revision_guidance` and `escalation_reason` are null.

### Step 5 — Write grader receipt

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type grader \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --confidence <0.0-1.0> \
  --summary "<score_rationale>" \
  --out .wabblespec/state/receipts/grader-receipt-<timestamp>.json
```

## Output contract

**grader-receipt.json** (`.wabblespec/state/receipts/grader-receipt-<timestamp>.json`):

Base receipt schema extended with fields per `schemas/grader-receipt.schema.json`. Key extension fields:

```json
{
  "verdict": "ACCEPT | REVISE | ESCALATE",
  "score": "number 0.0–1.0",
  "score_rationale": "string — one sentence referencing the spec",
  "spec_artifact_path": "string — ground truth used",
  "adversary_receipt_path": "string — input adversary receipt path",
  "revision_guidance": "string — required when verdict = REVISE; null otherwise",
  "escalation_reason": "string — required when verdict = ESCALATE; null otherwise",
  "adversary_concerns_assessed": "integer — total Adversary points evaluated",
  "adversary_concerns_within_scope": "integer — Adversary points within current spec scope"
}
```

Return to caller: grader-receipt.json path + `verdict`, `score`, `revision_guidance` extracted for Reviewer or direct callers.

## Role boundary — Grader stops here

Grader evaluates and produces verdicts only. Grader does NOT:
- Implement revision guidance
- Produce alternative outputs
- Modify the artifact under review
- Act on revision guidance — return it to the originating module

Revision guidance is instruction to the originating module — Grader writes it, does not act on it.

## A note on common failure modes

1. **Evaluating against preferences instead of spec.** A spec-compliant output you would have designed differently is still ACCEPT. Evaluate against what the spec requires.

2. **Vague revision guidance.** "Improve the error handling" is not guidance. "The error handler at line 34 exits with code 0 on missing input; criterion 2 requires exit code 1" is guidance.

3. **Over-escalation.** ESCALATE means human judgment is genuinely required — not that the output is hard to evaluate. Use REVISE for addressable gaps.

4. **Score inflation.** Do not adjust scores upward to avoid REVISE or ESCALATE verdicts. See rules/anti-inflation.md.
