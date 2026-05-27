# ModelRouter — Acceptance Criteria

## BLOCK: absent runtime-state.json

Given `.wabblespec/runtime/runtime-state.json` is missing or EXPIRED,
When ModelRouter is invoked,
Then ModelRouter surfaces: "runtime-state.json is missing or EXPIRED — cannot route without capability state."
Then ModelRouter does not proceed with routing.
Then no routing receipt is written.

## BLOCK: no declared task shape

Given ModelRouter is invoked without a classifiable task shape,
When ModelRouter attempts to classify,
Then ModelRouter surfaces: "Task shape cannot be classified — routing blocked."
Then ModelRouter does not select a capability.
Then no receipt is written.

## Routing by capability descriptor, never model name

Given any task routing decision,
When ModelRouter reads runtime-state.json,
Then ModelRouter reads capability descriptors and confidence scores only.
Then ModelRouter never reads or routes by model name.
Then no model identity appears in the routing receipt.

## Capability below 0.5 threshold: treated as unavailable

Given a capability in runtime-state.json has confidence < 0.5,
When ModelRouter matches task shapes,
Then that capability is excluded from consideration.
Then only capabilities with confidence >= 0.5 are eligible.

## Multiple capabilities cover task: highest confidence wins

Given two or more capabilities cover the current task shape,
When ModelRouter selects,
Then the capability with the highest confidence score is selected.
Then `selected_capability` and `confidence` are recorded in the receipt.

## No single capability covers all requirements

Given no single available capability covers all required capabilities for the task,
When ModelRouter evaluates Ensemble conditions,
Then Ensemble trigger condition 2 is met.
Then ModelRouter triggers Ensemble and records `ensemble_triggered: true`.
Then `ensemble_trigger_reason` states "No single capability covers all required capabilities."

## Ensemble trigger condition 3: Attestation or Audit

Given the task's verification_mode is Attestation or Audit,
When ModelRouter evaluates Ensemble conditions,
Then Ensemble trigger condition 3 is met.
Then ModelRouter triggers Ensemble and records `ensemble_triggered: true`.

## Ensemble trigger condition 4: confidence below 0.7

Given initial routing selects a capability with confidence below 0.7,
When ModelRouter evaluates Ensemble conditions,
Then Ensemble trigger condition 4 is met.
Then ModelRouter triggers Ensemble with Cross-check mode.

## Ensemble not triggered: all conditions clear

Given a single capability covers the task with confidence >= 0.7 and no Attestation/Audit mode,
When ModelRouter evaluates Ensemble conditions,
Then `ensemble_triggered: false` is recorded.
Then Ensemble is not invoked.

## Fallback capability declared

Given the selected capability becomes unavailable mid-session,
When ModelRouter provides a fallback,
Then `fallback_capability` is populated in the receipt if any fallback exists.
Then `fallback_capability: null` is recorded if no fallback is available.

## Ensemble evaluation never skipped

Given any task routing run,
When ModelRouter completes initial capability selection,
Then Ensemble trigger conditions are always evaluated — they are not skipped.
Then if any condition is met, Ensemble is triggered.

## Do NOT

Given any ModelRouter run,
Then ModelRouter does not read model names from any source.
Then ModelRouter does not route based on model identity.
Then ModelRouter does not skip Ensemble evaluation.

## Receipt fields

Given any successful ModelRouter run,
Then the receipt contains: `module` (model-router), `selected_capability`, `confidence`, `task_shape`, `fallback_capability`, `ensemble_triggered`, `ensemble_trigger_reason`, `verification_mode`.
