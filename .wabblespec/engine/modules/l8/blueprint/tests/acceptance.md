# Blueprint — Acceptance Criteria

## Activation gate

Given no candidate.json with status: pending exists,
When Blueprint is invoked,
Then Blueprint refuses and names the missing candidate.

Given candidate.json exists but affected module SKILL.md is not readable,
When Blueprint is invoked,
Then Blueprint stops and surfaces the missing SKILL.md path.

## Blueprint production

Given a valid candidate.json,
When Blueprint produces blueprint.json,
Then all required fields are present: blueprint_id, candidate_ref, change_type, affected_module, before_behavior, after_behavior, benchmark_gates, affected_targets, verification_mode, attestation_required, created_at, status.

Given change_type is AUGMENT,
Then before_behavior quotes or closely paraphrases current SKILL.md text.
Then after_behavior states exact replacement text.

## Benchmark gate requirement

Given any blueprint.json,
Then benchmark_gates contains at least one entry.
Then each gate entry has: metric, threshold, direction, developer_outcome, rationale.
Then developer_outcome is one of: false_completion, missed_test, stale_evidence, rework.

## Attestation requirement

Given blueprint.json is written,
Then status is "awaiting-attestation" until human signs off.
Then Augment and Factory must not start while status is "awaiting-attestation".

## Self-modification rule

Given affected_module is an L8 module,
Then verification_mode in blueprint.json is "Attestation".
Then attestation_required is true.

## Scope constraint

Given a candidate that implies multiple distinct behavior changes,
When Blueprint evaluates it,
Then Blueprint surfaces a scoping note to the human instead of writing a multi-behavior blueprint.

## Boundary enforcement

Given any Blueprint invocation,
Then no file is written under modules/.
Then no candidate.json is modified.
Then exactly one blueprint.json is written per invocation.
