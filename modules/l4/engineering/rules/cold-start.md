# Cold-Start Behavior — Gateway Engineering

Defines how gateway-engineering behaves when expected upstream artifacts are absent.

## Absent: gateway-spec-receipt (Phase A not yet run)

Condition: `gateway-engineering-spec-receipt.json` absent when Phase B is triggered.
Detection: Phase B checks for spec receipt.
Action: Block Phase B — surface DEPENDENCY error: "Phase A (architecture + quality analysis) must complete before Phase B verdict."
Do NOT: Issue verdict without Phase A context.

## Absent: spec to evaluate

Condition: No spec.md when Phase A is triggered.
Action: Produce minimal Phase A INFORM output. List required spec sections: architecture decision record (ADR), test strategy, breaking change policy.

## Absent: reference files

Condition: `references/quality-patterns.md` or `references/architecture.md` absent.
Detection: File read returns 404 during Phase A.
Action: Log absent files. Proceed with available files. Note in Phase A receipt.

## Absent: infrastructure reference files

Condition: `_shared/dev/infrastructure/cicd.md`, `containers.md`, `iac.md`, or `observability.md` absent when gateway-engineering is active.
Detection: Apply checks for infrastructure files during routing.
Action: Log warning: "Infrastructure reference file missing: [path]." Apply continues without that file's rules. Executor may produce output that misses infrastructure requirements.

## Absent: spec-declared ADR

Condition: Phase A triggered but no ADR present in spec when architecture decision is required.
Action: Phase A flags: "No ADR found. An ADR is required when the spec involves: new third-party service, new database, microservices split, or cross-cutting infrastructure pattern." Issue recommendation, not BLOCK at Phase A.

## Default state on cold start

| Field | Default |
|---|---|
| `phase_a_status` | `pending` |
| `verdict` | `pending` |
| `adr_required` | Evaluated at Phase A — depends on spec content |
| `infrastructure_loaded` | false — until Apply confirms files loaded |
| `test_strategy_declared` | false — Specify must elicit |

No engineering verdict defaults. Every verdict requires explicit Phase B execution.
