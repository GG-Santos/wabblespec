# Cold-Start Behavior — Explore

Defines what Explore does when its expected upstream artifacts are absent.

## Absent: recipe.json

Condition: No declared build target when Explore runs.
Detection: `.wabblespec/state/recipe.json` absent or stale.
Action: Surface DEPENDENCY error naming Recipe. Explore needs a target to bound its search space.
Do NOT: Explore the entire project without a target — produces unbounded, low-signal output.

## Absent: prior receipts

Condition: `recipe-receipt.json` absent.
Detection: Stem missing.
Action: Surface DEPENDENCY error naming Recipe.
Do NOT: Proceed without receipt chain started.

## Default state on cold start

| Field | Default |
|---|---|
| `search_depth` | `medium` (balanced; deep requires explicit declaration) |
| `scope_constraint` | bounded by recipe target type |
| `output_format` | file list + summary (never raw dumps) |
