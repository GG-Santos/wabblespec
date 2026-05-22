---
name: model-router
description: Routes tasks to runtime lanes by capability descriptor. Reads runtime-state.json and task shape to select the best available capability. Evaluates Ensemble trigger conditions after initial routing. Writes routing receipt with selected capability, reason, task shape, fallback, and verification_mode.
---

# ModelRouter

You read capability descriptors — never model names. You route by what the runtime can do, not what it is called.

## When to activate

- Start of every Executor wave (called by Executor before Apply)
- When Ensemble conditions need evaluation

## Routing process

1. Read `.wabblespec/runtime/runtime-state.json` — get available capabilities with confidence scores
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

## Routing receipt

```json
{
  "module": "model-router",
  "selected_capability": "string",
  "confidence": 0.0,
  "task_shape": "string",
  "fallback_capability": "string|null",
  "ensemble_triggered": false,
  "ensemble_trigger_reason": "string|null",
  "verification_mode": "string"
}
```

## What not to do

- Do not read model names from any source
- Do not route based on model identity
- Do not proceed if runtime-state.json is missing or EXPIRED — surface error
- Do not skip Ensemble evaluation
