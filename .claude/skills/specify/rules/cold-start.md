# Cold-Start Behavior — Specify

Defines what Specify does when its expected upstream artifacts are absent.

## Absent: specs/ directory

Condition: `specs/` directory does not exist or is empty.
Detection: Directory read returns empty or 404.
Action: Start a fresh spec hierarchy beginning at P1. Derive the first capability from the recipe.json target and the user's opening statement.
Output: `specs/<first-capability>/spec.md` at P1 priority.

## Absent: prior receipts

Condition: No `recipe-receipt.json` or `scopeframe-receipt.json` in `.wabblespec/state/receipts/`.
Detection: Required receipt stems missing from `required_receipts` in state.json, or files absent.
Action: Surface DEPENDENCY error naming the missing upstream module (Recipe or ScopeFrame).
Do NOT: Proceed without recipe.json and scope.md confirmed. Specify writes specs against a declared target — without Recipe, the target is unknown.

## Absent: scope.md

Condition: `.wabblespec/state/scope.md` does not exist.
Detection: File read returns 404.
Action: Surface DEPENDENCY error: ScopeFrame must run before Specify. Do not infer scope from the user message alone.
Do NOT: Write specs without declared scope boundaries.

## Default state on cold start

| Field | Default |
|---|---|
| `priority` | P1 (highest, first capability) |
| `status` | `draft` |
| `patch_mode` | false (full spec, not patch) |
| `scope_class` | `LOCAL` until integration points confirmed |

Fresh hierarchy starts at P1. Specify does not assign P0 — that is reserved for invariant-level requirements set by framework governance.
