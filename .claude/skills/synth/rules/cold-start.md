# Cold-Start Behavior — Synth

Defines what Synth does when its corpus gate or validated patterns are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Synth requires L8 corpus gate (100+ PASS receipts). Current: [n]."

## Absent: validated Instinct patterns

Condition: No human-validated patterns from Instinct.
Detection: Instinct receipts exist but `validated: false` on all patterns, or no instinct receipts.
Action: BLOCK Synth. Surface: "Synth requires at least 1 human-validated Instinct pattern to synthesize from."
Do NOT: Synthesize from unvalidated observations.

## Absent: prior Synth receipt

Condition: No prior `synth-receipt.json`.
Action: Treat as first synthesis run. Build synthesis from all available validated patterns.

## Absent: target module or domain for synthesis

Condition: Synth invoked without declaring what to synthesize (which module, which pattern domain).
Action: Surface: "Synth requires a target: module ID, layer, or pattern domain."

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate + at least 1 validated Instinct pattern |
| `synthesis_source` | Validated Instinct patterns only |
| `output` | Synthesis proposal — requires human review before framework incorporation |
| `auto_apply` | false — Synth proposes; human approves; Blueprint applies |
| `min_patterns` | 1 validated pattern (minimum to run) |
