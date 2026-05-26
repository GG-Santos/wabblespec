# Cold-Start Behavior — Monitor

Defines what Monitor does when its SLO declarations or observability infrastructure are absent.

## Absent: SLO declaration

Condition: Monitor invoked but no SLO is declared in spec or `monitoring.yaml`.
Detection: File scan finds no SLO entries.
Action: Surface: "Monitor requires declared SLOs. Add SLO declarations to spec or monitoring.yaml before monitoring can evaluate compliance."
Do NOT: Invent SLO targets. Only evaluate against declared targets.

## Absent: metrics endpoint

Condition: Application is not exposing a Prometheus or compatible metrics endpoint.
Detection: Scrape attempt returns 404 or connection refused.
Action: Log: "Metrics endpoint unavailable at [url]. Monitor cannot evaluate metrics-based SLOs." Surface to user. Evaluate log-based SLOs if logs are available.

## Absent: wabble-health.py

Condition: `_shared/scripts/wabble-health.py` (or `modules/l7/monitor/rules/wabble-health.md`) missing.
Detection: File read returns 404.
Action: Apply SKILL.md health check rules. Log: "wabble-health.md missing — using SKILL.md defaults."

## Absent: observability stack (logs/metrics/traces)

Condition: No structured logging, no metrics, no tracing configured.
Detection: All three observability signals unavailable.
Action: BLOCK ongoing monitoring. Surface: "No observability signals available. Configure structured logging (minimum) before Monitor can operate. See `_shared/dev/infrastructure/observability.md`."

## Default state on cold start

| Field | Default |
|---|---|
| `evaluation_frequency` | Not declared — must be specified (real-time / periodic / on-demand) |
| `alert_threshold` | Per declared SLO — no default |
| `slo_window` | 30-day rolling window (default; configurable) |
| `error_budget_burn_rate` | Alert at 2x burn rate for 1-hour window |
| `pager_policy` | Not declared — must be specified for production |
