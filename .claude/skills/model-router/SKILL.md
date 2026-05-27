---
name: model-router
description: Routes tasks to runtime lanes by capability descriptor. Reads runtime-state.json and task shape to select the best available capability. Evaluates Ensemble trigger conditions after initial routing. Writes routing receipt with selected capability, reason, task shape, fallback, and verification_mode.
---

# ModelRouter

You read capability descriptors — never model names. You route by what the runtime can do, not what it is called.

## What this skill does

Routes tasks to runtime lanes by capability descriptor. Reads runtime-state.json and task shape to select the best available capability. Evaluates Ensemble trigger conditions after initial routing. Writes routing receipt with selected capability, reason, task shape, fallback, and verification_mode.

## When to use

- Start of every Executor wave (called by Executor before Apply)
- When Ensemble conditions need evaluation

## Routing process

1. Read `.wabblespec/state/runtime/runtime-state.json` — get available capabilities with confidence scores
2. Classify current task shape (see `rules/task-shapes.md`)
3. Match task shape to required capability descriptors
4. Select capability with highest confidence that covers the task shape
5. Evaluate Ensemble trigger conditions
6. Write routing receipt

## Capability selection

Capabilities with confidence < 0.5 treated as unavailable. If multiple capabilities cover the task, select highest confidence. If no single capability covers all requirements: Ensemble trigger condition 2 is met.

## Ensemble trigger conditions

Any one activates Ensemble:
1. Task spans multiple build targets simultaneously
2. No single available capability covers all required capabilities
3. Verification mode is Attestation or Audit
4. Confidence below 0.7 after initial routing

If any condition met: activate Ensemble with routing decision and reason.

## ContextTuner integration

Before writing the routing receipt, run context classification via `.wabblespec/engine/shared/scripts/context-tuner.py`. Classification uses the current message (3x weight) and last four history messages (1x each). If confidence >= 0.6: use detected type's parameter profile. If confidence < 0.6: blend with `planning` baseline.

### Six WabbleSpec context types and sampling parameters

| Type | temp | top_p | top_k | freq | pres | rep |
|---|---|---|---|---|---|---|
| `spec-authoring` | 0.30 | 0.85 | 30 | 0.20 | 0.10 | 1.05 |
| `code-generation` | 0.20 | 0.80 | 25 | 0.20 | 0.00 | 1.05 |
| `security-review` | 0.50 | 0.90 | 50 | 0.20 | 0.20 | 1.08 |
| `planning` | 0.60 | 0.90 | 50 | 0.15 | 0.15 | 1.05 |
| `synthesis` | 0.80 | 0.92 | 60 | 0.30 | 0.30 | 1.10 |
| `administrative` | 0.20 | 0.85 | 25 | 0.10 | 0.00 | 1.05 |

No chaotic type. G0DM0D3's chaotic type has 66.7% precision and systematically misclassifies code tasks containing words like "delete" or "break".

### Learned parameter adjustment

If `.wabblespec/state/memory/learned-params/learned-params-{context_type}.json` exists with `sample_count >= 3` and `freshness: FRESH | AGING`: apply adjustments from the `adjustments` field to the base parameters. Never exceed MAX_WEIGHT (50% of base profile) regardless of sample count.

Read learned params as input only. ParamLearner (Feedback module) owns all writes.

### ContextTuner benchmark gate

Fixture set: 90 labeled inputs (15 per type), stratified. Threshold: >= 80% accuracy on held-out set.
Run: `python modules/l2/model-router/scripts/context-tuner-eval.py`

## InferenceGuard eligibility

After routing, set `inference_guard_eligible` based on:
- True when: selected task shape is `security-review` OR gateway-security receipt present in session
- False otherwise

This field flows to InferenceGuard activation check. InferenceGuard reads this field from the routing receipt.

## Output contract

```json
{
  "module": "model-router",
  "selected_capability": "string",
  "confidence": 0.0,
  "task_shape": "string",
  "fallback_capability": "string|null",
  "ensemble_triggered": false,
  "ensemble_trigger_reason": "string|null",
  "verification_mode": "string",
  "inference_guard_eligible": false,
  "context_classification": {
    "detected_type": "string",
    "confidence": 0.0,
    "context_scores": [],
    "pattern_matches": [],
    "parameters_selected": { "temperature": 0.0, "top_p": 0.0, "top_k": 0 },
    "blended": false
  }
}
```

## Empirical calibration notes

These findings come from the WabbleSpec Memory benchmark evaluation (2026-05-10). They inform confidence values for `runtime-state.json` capability entries — not model identity.

| Task shape | Winning capability profile | Measured accuracy | Notes |
|---|---|---|---|
| Room classification (closed-set) | Compact quantized LLM, 4-8B params | 0.62 accuracy | Beats cloud models on this narrow task |
| Room classification (open-set) | Same compact profile | 0.65 accuracy | Open-set harder; same winner |
| General extraction | Mid-size quantized LLM, ~4B, 100-600ms p50 | Best balance | 7.5 GB resident footprint |
| Memory extraction coverage | Micro LLM, 3B params | 0.99 coverage | Weak classifier; use for ingestion only |

**How to use this table:**
- For `classification` task shapes: set capability confidence >= 0.75 only for compact/local LLMs that have been validated on room classification. Do not assume cloud-scale models win on closed-vocabulary classification.
- For `extraction` task shapes: mid-size local LLMs (4B range) outperform both micro and large on the extraction-speed tradeoff.
- For `coverage-critical` tasks (high recall required): micro LLM profiles achieve 0.99 coverage but require a downstream classifier for precision.
- These are measured baselines for the task shapes above. Other task shapes have not been empirically evaluated — use default capability matching rules.

Source: WabbleSpec Memory benchmark harness, fixture set 2026-05-10. Raw numbers are held-out results, not tuning-set results.

## What not to do

- Do not read model names from any source
- Do not route based on model identity
- Do not proceed if runtime-state.json is missing or EXPIRED — surface error
- Do not skip Ensemble evaluation
