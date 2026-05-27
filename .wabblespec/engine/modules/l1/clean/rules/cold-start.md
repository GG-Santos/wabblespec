# Cold-Start Behavior — Clean

Defines what Clean does when its expected upstream artifacts are absent.

## Absent: wave receipts

Condition: No wave receipts exist when Clean runs.
Detection: No `wave-*-receipt.json` in `.wabblespec/state/receipts/`.
Action: Surface DEPENDENCY error — Clean operates on completed wave output. Without a completed wave, there is nothing to clean.
Do NOT: Run cleanup passes against in-progress or uncommitted code.

## Absent: prior receipts

Condition: `decompose-receipt.json` absent.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Decompose. Clean needs to know the wave plan structure to scope its cleanup correctly.
Do NOT: Run unbounded cleanup without declared scope.

## Default state on cold start

| Field | Default |
|---|---|
| `cleanup_scope` | bounded to files touched by the most recent completed wave |
| `cleanup_types` | whitespace, dead imports, formatting (non-semantic only by default) |
| `semantic_changes` | blocked — Clean does not make semantic changes without explicit authorization |
