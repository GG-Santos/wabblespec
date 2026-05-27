# Augment — Acceptance Criteria

## Activation gate

Given blueprint.json with status: awaiting-attestation,
When Augment is invoked,
Then Augment refuses and names the missing Attestation.

Given change_type: NEW but no Factory stubs exist,
When Augment is invoked,
Then Augment refuses and instructs to run Factory first.

## AUGMENT type behavior

Given change_type: AUGMENT and approved blueprint,
When Augment runs,
Then all source module files except receipts/ are copied to experiments/augments/{blueprint-id}/.
Then the copied SKILL.md reflects after_behavior from the blueprint.
Then no file outside experiments/augments/ is modified.

## NEW type behavior

Given change_type: NEW with Factory stubs,
When Augment completes the stubs,
Then all [FILL] markers are resolved — none remain.
Then SKILL.md has all required sections: purpose, activation, inputs, output contract, failure modes, not-tested.
Then skill-rules.json has activators, anti_activators, authority, verification_mode populated.

## Structural completeness

Given any Augment output,
Then skill-rules.json is valid JSON.
Then receipt schema is valid JSON Schema.
Then SKILL.md not-tested section explicitly names what could not be verified.

## Scope enforcement

Given blueprint specifies one behavior change,
When Augment implements,
Then only that change is applied — no additional improvements, refactors, or scope additions.

## Boundary enforcement (critical)

Given any Augment invocation,
Then no file in modules/ is created or modified.
Then no receipt in .wabblespec/state/receipts/ is modified.
Then no framework.yaml entry is changed.
