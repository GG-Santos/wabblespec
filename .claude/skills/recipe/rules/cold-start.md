# Cold-Start Behavior — Recipe

Defines what Recipe does when its expected upstream artifacts are absent.

## Absent: recipe.json

Condition: `.wabblespec/recipe.json` does not exist, or `session_id` does not match the current session.
Detection: File read returns 404, or `session_id` field mismatches.
Action: Run detection scan from scratch (Step 2 in SKILL.md). Do not error — Recipe is the entry gate, not a consumer.
Output: Fresh `recipe.json` with detection_method reflecting how target was found.

## Absent: prior receipts

Condition: No receipts from upstream modules.
Detection: `.wabblespec/receipts/` is empty or missing expected stems.
Action: Recipe has no upstream dependencies — proceed normally. Recipe produces the first receipt.
Do NOT: Pause or surface DEPENDENCY errors. Recipe is always first.

## Default state on cold start

| Field | Default |
|---|---|
| `target` | null — must be detected, never defaulted |
| `confidence` | 0.0 until detection completes |
| `complexity` | null — must be scored, never defaulted |
| `collapse_eligible` | false |
| `detection_method` | `file-signals` (first scan attempt) |
| `session_id` | generated fresh at cold start |

If no detection signal reaches confidence ≥ 0.8, ask user directly. Do not write recipe.json with confidence < 0.8.
