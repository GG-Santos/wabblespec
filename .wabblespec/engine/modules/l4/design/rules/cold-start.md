# Cold-Start Behavior — Gateway Design

Defines how gateway-design behaves when expected upstream artifacts are absent.

## Absent: gateway-spec-receipt (Phase A not yet run)

Condition: `gateway-design-spec-receipt.json` absent when Phase B is triggered.
Detection: Phase B checks for spec receipt.
Action: Block Phase B — "Phase A (flow / component / system analysis) must complete before Phase B verdict."

## Absent: spec to evaluate

Condition: No spec.md when Phase A is triggered.
Action: Produce minimal Phase A INFORM output. List required spec sections: flow states (loading/empty/error/success), component inventory, navigation model.

## Absent: reference files

Condition: `references/flows.md`, `references/components.md`, or `references/systems.md` absent.
Detection: File read returns 404 during Phase A.
Action: Log absent files. Proceed with available files. Note in Phase A receipt.

## Absent: error state declaration

Condition: Spec describes flows but no error state handling is declared.
Detection: Phase A flow scan finds no error state, no offline state, or no empty state.
Action: Phase A issues FLAG per missing state type: "Flow '[name]' missing error state declaration." Error and empty states are required for all flows.

## Absent: loading state declaration

Condition: Spec includes async operations but no loading state design.
Detection: Phase A finds API calls, data fetching, or async operations with no loading treatment.
Action: Phase A issues FLAG: "Async operation in '[flow]' has no loading state. Skeleton screen or spinner required."

## Default state on cold start

| Field | Default |
|---|---|
| `phase_a_status` | `pending` |
| `verdict` | `pending` |
| `required_states` | loading, empty, error, partial, success, offline — all must be addressed per flow |
| `error_message_tone` | User-directed (no blame), actionable, specific — enforced per writing rules |
| `navigation_model` | Not declared — Specify must elicit |
| `component_system` | Not declared — token consumption required (no raw px/hex in component specs) |

All six flow states (loading/empty/error/partial/success/offline) are required per flow — enforced as design invariants.
