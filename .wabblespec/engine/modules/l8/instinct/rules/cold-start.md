# Cold-Start Behavior — Instinct

Defines what Instinct does when the L8 corpus gate is not met or patterns are absent.

## Absent: L8 corpus gate (< 100 PASS receipts)

Condition: `.wabblespec/engine/shared/references/l8-corpus-gate.md` reports fewer than 100 PASS receipts.
Detection: Receipt count check at module activation.
Action: BLOCK Instinct activation. Surface: "L8 corpus gate not met. Instinct requires 100+ PASS receipts. Current: [n]."
Do NOT: Operate in observer or any other mode until the gate is met.

## Absent: memory store (no drawers to observe)

Condition: `memory/` is empty or has fewer than 10 drawers.
Detection: Index read returns fewer than 10 drawers.
Action: BLOCK Instinct. Surface: "Instinct requires at least 10 memory drawers to observe patterns from."

## Absent: prior Instinct receipt

Condition: No prior `instinct-receipt.json`.
Detection: Receipt absent.
Action: Treat as first observation run. No prior patterns to compare against — establish baseline.

## Absent: human-validated pattern confirmation

Condition: Instinct has identified a candidate pattern but it has not been human-validated.
Detection: Pattern in receipt has `validated: false`.
Action: Surface for human review. Do NOT action or escalate unvalidated patterns.
Do NOT: Apply patterns to framework changes without human validation. Instinct is observer-only until validation is confirmed.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | 100 PASS receipts + 10 memory drawers |
| `mode` | observer-only (read-only; no writes to framework) |
| `pattern_confidence_threshold` | 3 occurrences across independent sessions before surfacing |
| `human_validation_required` | true — all patterns require human sign-off before actioning |
| `validated_patterns` | 0 (baseline; 3 required for L8 evolution gate) |
