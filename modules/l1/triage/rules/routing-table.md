# Routing Table — Triage

## Route by type and severity

| Type | Severity | Route | Priority |
|---|---|---|---|
| Bug | Critical | Executor (immediate wave) + Autopilot L3+ | immediate |
| Bug | High | Interview → Specify (delta) → Executor | next-wave |
| Bug | Medium | Specify (delta) → Executor | next scheduled wave |
| Bug | Low | Specify (delta) → Executor | scheduled |
| Feature | Any | Interview → Specify → Propose → Decompose | scheduled |
| Debt | Any (COSMETIC) | Clean | scheduled |
| Debt | Any (structural) | Specify + Executor | scheduled |
| Question | Any | Interview | immediate |
| Security | Any | Security gateway (immediately) + severity-based routing | immediate |

## Security routing detail

Security issues always route to Security gateway first, regardless of severity. After Security gateway assessment:
- If confirmed vulnerability: severity upgraded to Critical minimum → Bug routing applies
- If not a vulnerability: reclassify type and re-route

## Debt routing detail

Classify debt as COSMETIC or structural before routing:
- COSMETIC debt: formatting, dead code, deprecated patterns → Clean
- Structural debt: architectural issues, abstraction violations, cross-cutting concerns → Specify + Executor

## Feature routing detail

All features go through Interview first — features are rarely fully specified at the point of triage. Interview resolves ambiguity before Specify drafts the delta.

## Autopilot escalation

Critical bugs trigger Autopilot at L3+ in addition to the Executor immediate wave. Autopilot monitors the wave and can escalate further if the fix does not resolve within expected time.

## Route is advisory when ambiguous

If type is ambiguous (e.g. "is this a bug or a feature request?"), route to Interview first. Interview resolves the classification and returns to Triage for final routing.
