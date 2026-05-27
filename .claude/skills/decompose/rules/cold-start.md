# Cold-Start Behavior — Decompose

Defines what Decompose does when its expected upstream artifacts are absent.

## Absent: specify receipt / spec artifacts

Condition: No `specify-receipt.json` or no files under `specs/` when Decompose runs.
Detection: Receipt stem absent or specs directory empty.
Action: Surface DEPENDENCY error naming Specify. Decompose breaks a locked spec into waves — without a spec, there is nothing to decompose.
Do NOT: Generate a wave plan from the user's raw task description.

## Absent: prior receipts

Condition: `recipe-receipt.json` or `scopeframe-receipt.json` absent.
Detection: Required stems missing from `required_receipts` in state.json.
Action: Surface DEPENDENCY error naming the missing upstream module.
Do NOT: Proceed without the planning chain intact.

## Default state on cold start

| Field | Default |
|---|---|
| `wave_count` | 0 until decomposition completes |
| `wave_plan` | null — must be derived from spec, never defaulted |
| `checkpoint_interval` | every wave (conservative default) |
| `rollback_target` | previous wave receipt (default target) |
