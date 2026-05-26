# Cold-Start Behavior — Model Router

Defines what Model Router does when its expected upstream artifacts are absent.

## Absent: runtime-state.json

Condition: `.wabblespec/runtime-state.json` does not exist when Model Router needs to route a task.
Detection: File read returns 404.
Action: Use capability defaults (same as Runtime Probe's cold-start defaults). Log SOFT warning to receipt: `runtime_state: absent — using defaults`.
Do NOT: Block routing because runtime-state.json is missing — conservative defaults are always safe.

## Absent: task shape declaration

Condition: The incoming task has no declared capability requirement (no `requires_capability` field).
Detection: Task input lacks capability descriptor.
Action: Default to `standard-reasoning` tier. Log SOFT warning: `capability_undeclared — routed to standard`.
Do NOT: Route to high-reasoning tier without explicit declaration.

## Absent: prior receipts

Condition: `runtime-probe-receipt.json` absent.
Detection: Stem missing.
Action: Surface SOFT warning — Runtime Probe should run first. Proceed with defaults.
Do NOT: Surface DEPENDENCY error — Model Router can proceed with defaults safely.

## Default state on cold start

| Capability tier | Default routing |
|---|---|
| `high-reasoning` | reserved for tasks that explicitly declare it |
| `standard-reasoning` | default for all undeclared tasks |
| `fast-response` | only when task declares `latency_sensitive: true` |
| `vision` | only when task declares `requires_vision: true` |
