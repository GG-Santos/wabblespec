# Cold-Start Behavior — Factory

Defines what Factory does when its corpus gate or pattern inputs are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Factory requires L8 corpus gate (100+ PASS receipts)."

## Absent: prompt-patterns.md reference

Condition: `.wabblespec/engine/shared/references/prompt-patterns.md` missing.
Detection: File read returns 404.
Action: BLOCK Factory. Surface: "Factory requires prompt-patterns.md (35 patterns, 6 categories). This file must exist."
Do NOT: Generate new prompt patterns without the reference — Factory refines existing patterns, not invents unconstrained ones.

## Absent: target pattern to refine or instantiate

Condition: Factory invoked without declaring which pattern (DP-XX or named pattern) to work with.
Action: Surface: "Factory requires a target: pattern ID (e.g., DP-03) or pattern name from prompt-patterns.md."

## Absent: test case for pattern validation

Condition: Factory is about to write a new pattern variant but no test case exists.
Detection: No test case declared in the invocation.
Action: FLAG: "Pattern variant requires at least one test case demonstrating correct vs. incorrect behavior."
Do NOT: Block Factory — flag and request test case alongside output.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate |
| `pattern_source` | prompt-patterns.md only — no pattern fabrication |
| `test_required` | Flagged if absent (not blocked) |
| `output` | Pattern variant proposal — requires human review |
| `scope` | Single pattern per run |
