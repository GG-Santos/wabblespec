# Cold-Start Behavior — Economy

Defines what Economy does when its expected upstream artifacts are absent.

## Absent: prior session tracking data

Condition: No Economy tracking data from prior sessions when Economy initializes.
Detection: No `economy-*.json` receipts or tracking ledger in `.wabblespec/`.
Action: Start a fresh ledger. Economy is designed to accumulate data over time — absence of prior data is the expected first-run condition.
Output: Fresh tracking ledger with zero baseline. First session establishes the baseline.

## Absent: recipe.json

Condition: No declared build target when Economy is called.
Detection: `.wabblespec/recipe.json` absent or stale.
Action: Surface DEPENDENCY error naming Recipe. Economy tracks costs per target type — without a target, cost attribution is undefined.
Do NOT: Track costs without a target.

## Absent: prior receipts

Condition: No wave receipts to cost when Economy runs.
Detection: No `wave-*-receipt.json` in `.wabblespec/receipts/`.
Action: No error — Economy can initialize and wait. Cost tracking starts when waves complete.
Do NOT: Surface DEPENDENCY error when no waves have run yet.

## Default state on cold start

| Field | Default |
|---|---|
| `session_cost` | 0.00 |
| `wave_costs` | empty list |
| `budget_limit` | null (unlimited unless declared) |
| `alert_threshold` | null (no alerts until budget declared) |
| `currency` | `tokens` (default unit; switch to USD requires explicit config) |
