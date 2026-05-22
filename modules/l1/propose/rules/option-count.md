# Option Count Rules — Propose

## Bounds

- **Minimum:** 2 options
- **Maximum:** 4 options

## Why these bounds

Fewer than 2 options is not a decision — it is a recommendation. If only one option exists, Propose does not activate; route directly to Specify.

More than 4 options cause decision paralysis without improving decision quality. If more than 4 candidates exist, consolidate by merging options that differ only in degree (not in kind), or exclude options that do not fit scope.

## Consolidation rules

When more than 4 candidates exist:
1. Exclude any option rated `No` on Fits scope
2. Merge options that differ only in implementation detail, not in approach
3. If still more than 4: exclude the highest-complexity option with the lowest fit-to-scope rating
4. If still more than 4: escalate to Reviewer to select which to present

## Minimum distinctness test

Two options are distinct if choosing one meaningfully changes the implementation path, the interfaces exposed, or the risks carried. If two options converge to the same implementation after the first step, they are not distinct — merge them.
