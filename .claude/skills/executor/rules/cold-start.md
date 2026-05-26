# Cold-Start Behavior — Executor

Defines what Executor does when its expected upstream artifacts are absent.

## Absent: decompose receipt

Condition: No `decompose-receipt.json` in `.wabblespec/receipts/`.
Detection: Receipt stem missing from `required_receipts` in state.json, or file absent.
Action: DEPENDENCY error — Decompose must complete before Executor begins. Executor cannot derive a wave plan from scratch.
Do NOT: Infer wave structure from the task description alone.

## Absent: prior wave receipts (Wave N > 0)

Condition: Wave N is about to begin but Wave N-1 receipt is absent.
Detection: Expected `wave-{N-1}-receipt.json` missing from `.wabblespec/receipts/`.
Action: Treat as wave 0 only if N=0. For N>0, surface I10 DEPENDENCY error — prior wave receipt must exist.
Do NOT: Skip a wave or merge two waves because a receipt is missing.

## Absent: guard receipt for current wave

Condition: Guard has not returned PASS for Wave N yet.
Detection: `guard-wave-{N}-receipt.json` absent when Executor attempts to begin Wave N execution.
Action: Block execution — wait for Guard PASS. I4 violation if Executor proceeds without it.
Do NOT: Proceed on the assumption that Guard "would have passed."

## Absent: state.json

Condition: `.wabblespec/session/state.json` does not exist when Executor begins.
Detection: File read returns 404.
Action: Write the pre-execution prologue immediately (see state-protocol.md). Do not proceed without writing state first.
Do NOT: Execute any wave before state.json has `enforcement_active: true` and the planning receipt stems.

## Default state on cold start

| Field | Default |
|---|---|
| `current_wave` | 0 |
| `wave_plan` | null — must come from decompose receipt |
| `enforcement_active` | true (always set before Wave 1) |
| `active_module` | `executor` |
| Required receipts at start | All four planning-phase stems from decompose |
