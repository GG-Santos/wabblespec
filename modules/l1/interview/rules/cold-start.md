# Cold-Start Behavior — Interview

Defines what Interview does when its expected upstream artifacts are absent.

## Absent: existing spec or task card

Condition: No spec artifacts and no task card when Interview runs.
Detection: `specs/` empty and no task card in `.wabblespec/plans/`.
Action: Start fresh — generate opening questions from the recipe target and complexity level. Interview is designed to run before specs exist for High-complexity tasks.
Output: Structured question list derived from recipe target, complexity, and user opening statement.

## Absent: prior receipts

Condition: `recipe-receipt.json` absent.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Recipe. Interview needs a declared target to ask relevant questions.
Do NOT: Ask generic questions without a target — produces unfocused interview output.

## Default state on cold start

| Field | Default |
|---|---|
| `question_set` | derived from target and complexity; 5–10 questions for High complexity |
| `question_categories` | requirements, constraints, integration points, acceptance criteria |
| `max_rounds` | 2 (default; more requires explicit user approval) |
