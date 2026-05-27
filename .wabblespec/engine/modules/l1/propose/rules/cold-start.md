# Cold-Start Behavior — Propose

Defines what Propose does when its expected upstream artifacts are absent.

## Absent: spec artifacts

Condition: No files under `specs/` when Propose runs.
Detection: Directory empty or 404.
Action: Surface DEPENDENCY error naming Specify. Propose generates design alternatives for a declared spec — without a spec, there is no design problem to propose against.
Do NOT: Generate proposals from the user's raw task description alone.

## Absent: prior receipts

Condition: `specify-receipt.json` absent.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Specify.
Do NOT: Proceed without a confirmed spec.

## Default state on cold start

| Field | Default |
|---|---|
| `proposal_count` | 2 (minimum; 3 if complexity is High) |
| `evaluation_criteria` | derived from spec acceptance criteria — never invented |
| `recommendation` | deferred until user reviews proposals |
