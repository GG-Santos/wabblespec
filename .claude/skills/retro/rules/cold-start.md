# Cold-Start Behavior — Retro

Defines what Retro does when its session history or receipt data are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Retro requires L8 corpus gate (100+ PASS receipts)."

## Absent: completed sessions to retrospect

Condition: No completed receipt chains in `.wabblespec/state/receipts/`.
Detection: No delivery receipts with PASS status.
Action: Surface: "No completed sessions to retrospect. Retro requires at least one completed delivery receipt."

## Absent: retro period declaration

Condition: Retro invoked without specifying what time period or runs to cover.
Action: Default to last 10 completed runs. Surface: "No period declared — retrospecting last 10 completed runs."

## Absent: prior Retro receipt (for tracking recurring patterns)

Condition: No prior `retro-receipt.json`.
Action: Treat as first retro. No recurring patterns identified yet — establish baseline observations.

## Absent: memory store (for context about sessions)

Condition: Memory store empty when Retro tries to enrich retrospective with session context.
Detection: Memory search returns empty.
Action: Proceed with receipts only — no memory enrichment. Log: "Memory store empty — retro based on receipts only."

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate |
| `default_period` | Last 10 completed runs |
| `analysis_type` | What worked, what didn't, recurring patterns, actionable improvements |
| `recurring_threshold` | 3+ occurrences across sessions to declare a recurring pattern |
| `output` | Retrospective report — human reviews before actioning recommendations |
