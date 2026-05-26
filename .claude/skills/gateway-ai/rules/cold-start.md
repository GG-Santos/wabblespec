# Cold-Start Behavior — Gateway AI

Defines how gateway-ai behaves when expected upstream artifacts are absent.

## Absent: gateway-spec-receipt (Phase A not yet run)

Condition: `gateway-ai-spec-receipt.json` absent when Phase B is triggered.
Detection: Phase B checks for spec receipt.
Action: Block Phase B — "Phase A (AI safety + eval + cost analysis) must complete before Phase B verdict."
Do NOT: Issue verdict without Phase A context.

## Absent: spec to evaluate

Condition: No spec.md when Phase A is triggered.
Action: Produce minimal Phase A INFORM output. List required spec sections: model declaration (pinned ID), prompt version, eval harness plan, context budget, output schema.

## Absent: reference files

Condition: `references/safety.md`, `references/evals.md`, or `references/cost.md` absent.
Detection: File read returns 404 during Phase A.
Action: Log absent files. Proceed with available files. Note in Phase A receipt which safety/eval/cost context was reduced.
Do NOT: Silently omit the absent context. The spec author must know safety analysis was reduced.

## Absent: model declaration in spec

Condition: Spec exists but no model ID declared (or model declared as "latest" / unpinned).
Detection: Spec scan finds no `model:` field, or finds a floating reference.
Action: Phase A issues FLAG: "Model must be pinned to an exact ID (e.g., claude-sonnet-4-6). Floating references are forbidden."
Do NOT: Accept "latest" or "claude-sonnet" without version suffix as valid model declarations.

## Absent: eval harness declaration

Condition: Spec has AI components but no eval harness declared.
Detection: Phase A scan finds no eval section.
Action: Phase A issues FLAG: "Eval harness required before production deployment. Specify eval dataset size, format, and threshold in spec."

## Default state on cold start

| Field | Default |
|---|---|
| `phase_a_status` | `pending` |
| `verdict` | `pending` |
| `model_pinned` | false — until spec declares exact model ID |
| `eval_declared` | false — until spec includes eval section |
| `pii_in_context` | assumed absent — Specify must declare if present |
| `cost_budget_declared` | false — until spec includes token budget |

Floating model references and absent eval harness are automatic FLAGs in Phase B verdict.
