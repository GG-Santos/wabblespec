# Cold-Start Behavior — Product

Defines what Product does when its expected upstream artifacts are absent.

## Absent: PRD or product spec

Condition: No `PRD.md`, `GDD.md`, `FDS.md`, or equivalent product document in the project.
Detection: File scans return empty for known product document patterns.
Action: Ask the user for the product description or goal before proceeding. Do not synthesize a PRD from thin air.
Output: None until user provides product intent.

## Absent: prior receipts

Condition: No receipts from upstream modules.
Detection: `.wabblespec/receipts/` is empty.
Action: Surface DEPENDENCY error naming Recipe — Product requires a declared build target before it can structure requirements.
Do NOT: Proceed without recipe.json confirmed.

## Default state on cold start

| Field | Default |
|---|---|
| `requirements` | empty list — must be populated from user input |
| `priority` | P2 (product-level requirements) |
| `status` | `draft` |
