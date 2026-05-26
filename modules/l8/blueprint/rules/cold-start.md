# Cold-Start Behavior — Blueprint

Defines what Blueprint does when its Synth input or framework targets are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Blueprint requires L8 corpus gate (100+ PASS receipts)."

## Absent: Synth receipt

Condition: No `synth-receipt.json` with approved synthesis proposal.
Detection: Synth receipt absent or status is not `approved`.
Action: BLOCK Blueprint. Surface: "Blueprint requires an approved Synth proposal. Complete Synth → human approval first."
Do NOT: Design framework changes without an approved synthesis.

## Absent: target file to modify

Condition: Blueprint has a synthesis proposal but cannot identify which framework files to change.
Detection: Synth proposal does not map to specific files.
Action: Surface: "Blueprint cannot identify target files from the synthesis proposal. Specify which modules or files this change applies to."

## Absent: prior Blueprint receipt

Condition: No prior `blueprint-receipt.json`.
Action: Treat as first design run.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate + approved Synth receipt |
| `source` | Approved Synth proposal only |
| `scope` | Declared in synthesis — do not expand scope during design |
| `output` | Design specification — requires Forge to apply |
| `auto_apply` | false — Blueprint designs; Forge applies |
