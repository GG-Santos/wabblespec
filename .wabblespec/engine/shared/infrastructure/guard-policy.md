# Guard Policy

Default risk tier configuration for Guard. Guard reads this at cold-start to configure its enforcement behavior. Overrides require explicit human authorization in the session.

## Risk tiers

| Tier | Definition | Default action |
|---|---|---|
| CRITICAL | Operation that is irreversible, affects shared state, or could cause data loss | BLOCK. Require explicit human confirmation before proceeding. |
| HIGH | Operation that is hard to reverse or affects multiple modules/files | WARN. Surface to human. Proceed only if human acknowledges. |
| MEDIUM | Operation that is reversible but non-trivial to undo | LOG. Record in Guard receipt. Do not block. |
| LOW | Routine read/write within declared scope | PERMIT. No logging required. |

## Default CRITICAL operations

- Deleting files or directories
- Force-pushing to git remote
- Dropping or truncating database tables
- Writing to system directories (outside project root)
- Executing commands with `--force`, `-f`, `rm -rf` patterns
- Overwriting an existing receipt or delivery receipt

## Default HIGH operations

- Modifying `framework.yaml` (structural — affects all modules)
- Modifying `.wabblespec/engine/shared/` files (cross-module impact)
- Writing to another module's directory without declared authority
- Committing changes that were not in the declared wave scope
- Running database migrations on non-dev environments

## Default MEDIUM operations

- Modifying a SKILL.md (spec change — should trigger Shift)
- Modifying a schema file (contract change)
- Adding a new module directory
- Bulk file moves within the project

## Scope freeze policy

Guard enforces scope boundaries. A module may only write to:
1. Its own module directory (`modules/lN/module-name/`)
2. `.wabblespec/state/receipts/` (for receipts)
3. `.wabblespec/<module-name>/` (for module-specific outputs)
4. Explicitly declared targets in its task card

Writing outside declared scope triggers a scope-freeze violation: CRITICAL tier.

## Policy override

Override requires: human confirmation in session, explicit `scope_override: true` in the task card, and a Guard receipt noting the override. Overrides are audit-logged and never silently applied.

## Guard log format

Guard writes operation logs as part of its receipt. Log fields:
- `operation_type`: what was attempted
- `risk_tier`: tier assigned
- `action_taken`: BLOCK / WARN / LOG / PERMIT
- `scope_violation`: boolean
- `override_applied`: boolean

## Execution Discipline

Three behavioral constraints that complement the risk tier system. These govern *what not to do* rather than *what tier to apply when something is done*. Executor must read these before each wave. Guard enforces the tier escalations noted below.

**Rule 1 — Prefer deletion over addition.**
When a behavior can be preserved by removing code or configuration rather than adding more, deletion is the correct path. Executor must not add new files, functions, or abstractions when removal achieves the goal. Unnecessary addition is scope inflation: MEDIUM tier unless it crosses a declared boundary.

**Rule 2 — Keep changes small and reversible.**
Wave scope defines the change boundary. If the implementation naturally wants to touch areas outside the wave plan, stop — surface this to the human before proceeding, not after. Changes that are hard to reverse (schema drops, data migrations, API removals) require CRITICAL tier confirmation regardless of whether they are in-scope.

**Rule 3 — No new dependencies without explicit approval.**
Executor must not introduce new package dependencies, external service calls, or infrastructure requirements that are not declared in the task card or explicitly requested by the user in the session. Undeclared dependency introduction is a MEDIUM tier Guard operation. If a dependency is discovered to be necessary during execution, surface it before adding it — do not add first and disclose after.
