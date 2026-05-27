# Budget Definition

Performance budgets are declared targets. They do not emerge from measurement — they are set before measurement and then measured against.

## Budget sources

Performance budgets come from one of three sources, in priority order:

1. **Platform engineering spec** — declared SLOs in the L3 platform module (web, api-service, mobile, etc.)
2. **Gateway-engineering spec** — build and runtime performance standards
3. **User-declared** — explicit targets provided at Perf invocation time

If no budget exists from any source: Perf must surface this. `platform_budget_applied: "NONE_DECLARED"`. Do not invent a budget.

---

## Budget dimensions

Every platform has at minimum these dimensions:

| Dimension | Web | API | Mobile | CLI | IoT |
|---|---|---|---|---|---|
| Latency (P95) | LCP < 2.5s | P95 < 200ms | App launch < 1s | Command < 500ms | Response < 100ms |
| Error rate | CLS < 0.1 | Error rate < 1% | Crash rate < 0.1% | Exit code 0 | Fault rate < 0.01% |
| Resource | FID < 100ms | CPU < 70% | Memory < 150MB | Memory < 50MB | Flash < 80% |

These are defaults when no platform spec exists. They are conservative starting points, not overrides of declared SLOs.

---

## Budget recording

Record the budget applied in the receipt: `platform_budget_applied: "<name>"`. If using defaults: `"perf-defaults-<platform>"`. If from platform spec: the spec file path.

The budget is the reference frame. Every measurement result is stated relative to it:
- "P95 latency: 180ms against 200ms budget (PASS, 10% headroom)"
- "Memory: 210MB against 150MB budget (FAIL, 40% over)"

---

## Budget changes

If a budget must change during a Perf session (discovered constraint, new requirement), document the change in the receipt and explain why. Do not silently adjust the budget to make measurements pass. Budget adjustments require human confirmation.
