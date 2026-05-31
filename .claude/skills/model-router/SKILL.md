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

## Task Capability Classification

Use this table when no runtime-state.json is present or when confidence values are equal across capabilities. Task type determines the minimum required capability tier — route to the highest available tier that meets or exceeds the minimum.

| Task type | Min tier | Rationale |
|---|---|---|
| Architecture decisions (system design, module decomposition, cross-cutting tradeoffs) | Highest | Low-capability routing produces structurally unsound designs that fail at review |
| Security review (threat modeling, vulnerability analysis, access control audit) | Highest | Security false negatives from low capability are not recoverable at review time |
| Code review spanning the entire codebase | Highest | Cross-file reasoning requires full coherence over large context |
| Synthesis of ambiguous requirements (reconciling conflicting specs, gap-map analysis) | Highest | Ambiguity resolution requires judgment; patterns do not transfer from simpler tasks |
| Complex multi-step reasoning (L8 evolution, wave-plan conflict resolution) | High-analysis | Significant context span; quality degrades before token budget is exhausted |
| Multi-file refactors, API design, spec authoring | High-analysis | Structured output with tradeoff awareness required |
| LLM pipeline design, evaluation framework design | High-analysis | Domain requires calibrated reasoning, not just pattern completion |
| Deterministic code generation from a complete spec | Fast-execution | Output shape fully determined by input; reasoning overhead wastes budget |
| Test boilerplate from established patterns | Fast-execution | Pattern-completion task; low novelty |
| Documentation from templates (changelogs, READMEs from existing content) | Fast-execution | Transformation task with high structural constraint |
| Deployment operations, infrastructure commands | Fast-execution | Execution fidelity matters more than reasoning quality |
| Simple content formatting, SEO tasks, commit message generation | Fast-execution | Short output, well-defined rules, reversible if wrong |

When the task is reasoning-heavy (spec-authoring, synthesis, security-review) and both token expansion and capability upgrade are available, route to higher capability rather than allocating more tokens to a weaker capability — capability level provides more leverage on reasoning tasks than additional token budget.

## Reference Routing

| Situation | Reference |
|---|---|
| ModelRouter receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type model-router` |

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

## Token budget vs capability upgrade tradeoff

When performance on a task is insufficient and the options are (a) increase token budget or (b) route to a higher-capability runtime, empirical evidence from agent evaluation shows:

- Token usage explains approximately 80% of agent performance variance on browsing/research tasks
- Capability level explains approximately 5% of variance independently
- Upgrading capability quality provides more leverage than doubling the token budget allocated to a weaker capability — especially for complex reasoning tasks where the weaker capability hits diminishing returns before exhausting its token budget

Apply this as a routing tiebreaker: when both token expansion and capability upgrade are available options and the task is reasoning-heavy (spec-authoring, synthesis, security-review), prefer routing to higher capability over simply allocating more tokens to the current capability.

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

## Capability Tier Selection

When selecting between multiple available capabilities of the same type, use task complexity as a tiebreaker before applying confidence scores.

| Tier | Task complexity signal | Select when |
|---|---|---|
| Lite | Fast, single-source, time-sensitive | Quick lookups, simple questions, format conversions, status checks |
| Standard | Default; moderate reasoning depth | Feature implementation, code review, spec authoring, most research tasks |
| Max | Multi-source synthesis requiring parallel processing | Deep research with multiple information sources, structured report generation, complex multi-step reasoning where quality difference is measurable |

Upgrading capability tier provides more leverage than increasing token budget for reasoning-heavy tasks — a weaker capability hits diminishing returns before exhausting its token budget, while a stronger capability closes the gap earlier. Apply max only when the task genuinely requires multi-source synthesis. For everything else, standard is the correct default.

## What not to do

- Do not read model names from any source
- Do not route based on model identity
- Do not proceed if runtime-state.json is missing or EXPIRED — surface error
- Do not skip Ensemble evaluation
