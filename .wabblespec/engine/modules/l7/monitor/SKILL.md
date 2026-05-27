---
name: monitor
description: Generates observability config from Engineering SLO declarations. Produces metric definitions, alert rules, log schema, health check config, and dashboard template. Config is generated — not hand-written. SLOs in engineering specs are the source of truth.
---

# Monitor

You generate observability configuration. You do not write observability config by hand — you derive it from SLO declarations in the Engineering specs. Your output is ready to apply to the observability stack (Prometheus, Datadog, CloudWatch, etc.). You do not invent SLOs — you codify the ones declared.

## What this skill does

Reads SLO declarations from engineering specs and performance budgets. Generates five config artifacts: metric definitions, alert rules, log schema, health check config, and dashboard template. All are derived from declared requirements — nothing invented.

## When to use

After Executor wave completes and engineering specs contain SLO declarations, with performance budgets and platform specs finalized.

## Inputs

- `engineering/performance-budgets.md` — latency, error rate, throughput targets
- `engineering/build-toolchain.md` — platform context
- Platform SLOs (from L3 platform engineering specs)
- Deployment target (Kubernetes, ECS, Lambda, bare metal, etc.)
- Observability stack selection: Prometheus+Grafana | Datadog | CloudWatch | OpenTelemetry

## How to do it

### Step 1 — Extract SLO declarations

Read all engineering files. Collect:
- Latency targets: P50, P95, P99 values
- Error rate targets: % threshold over time window
- Throughput targets: requests/sec or events/sec
- Availability targets: uptime % or nines
- Resource budgets: CPU %, memory %, disk I/O
- Platform-specific: flash %, frame rate, battery current (IoT/Game)

If no SLO declared for a dimension: note as `UNDECLARED` — do not invent a target.

### Step 1b — Guard log signal monitoring

In addition to SLO-based monitoring, Monitor subscribes to Guard operation logs as a signal source via PostToolUse hook.

Read all `guard-*-receipt.json` files in `.wabblespec/receipts/` for the current session. Evaluate:

- **Repeated blocks:** Same operation type blocked ≥ 3 times in one session → systemic policy issue
- **Risk-tier escalations:** Any CRITICAL tier trigger in Guard logs
- **Freeze violations:** Any `violation_type: scope-freeze` in Guard blocked operations

When any of the above conditions are met, auto-emit a typed DEPENDENCY error event routed to Triage. Schema: `.wabblespec/engine/shared/schemas/error-event.schema.json`.

Error event fields:
```json
{
  "error_type": "DEPENDENCY",
  "source": "guard-log-monitor",
  "pattern": "string — description of the detected pattern",
  "occurrence_count": "integer — how many times the pattern was observed",
  "session_id": "string — current session identifier"
}
```

This step is additive — does not change existing SLO-monitoring behavior. SLO monitoring runs regardless of Guard log findings. Guard log monitoring runs regardless of SLO declarations.

### Step 2 — Generate metric definitions

```yaml
# metrics.yml
metrics:
  - name: http_request_duration_seconds
    type: histogram
    description: "HTTP request latency"
    buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
    labels: [method, route, status_code]
    slo_target: p95 < 200ms          # from performance-budgets.md

  - name: http_error_rate
    type: gauge
    description: "5xx error rate over 5m window"
    slo_target: < 1%                 # from performance-budgets.md

  - name: active_connections
    type: gauge
    description: "Current active connections"
```

### Step 3 — Generate alert rules

One alert per SLO breach condition:

```yaml
# alerts.yml (Prometheus AlertManager format)
groups:
  - name: slo-alerts
    rules:
      - alert: LatencyP95Breach
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])) > 0.200
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency {{ $value }}s exceeds SLO 200ms"
          runbook: "docs/runbooks/latency-breach.md"

      - alert: ErrorRateBreach
        expr: |
          rate(http_requests_total{status=~"5.."}[5m]) /
          rate(http_requests_total[5m]) > 0.01
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Error rate {{ $value | humanizePercentage }} exceeds SLO 1%"
```

### Step 4 — Generate log schema

```json
// log-schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "required": ["timestamp", "level", "message", "service", "trace_id"],
  "properties": {
    "timestamp": { "type": "string", "format": "date-time" },
    "level": { "enum": ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"] },
    "message": { "type": "string" },
    "service": { "type": "string" },
    "trace_id": { "type": "string" },
    "span_id": { "type": "string" },
    "duration_ms": { "type": "number" },
    "error": { "type": "object" }
  }
}
```

**No PII in logs.** If platform engineering spec declares PII fields: log schema explicitly excludes those fields.

### Step 5 — Generate health check config

```yaml
# healthcheck.yml
checks:
  - name: liveness
    endpoint: /healthz
    method: GET
    expected_status: 200
    timeout_ms: 1000
    interval_s: 10

  - name: readiness
    endpoint: /readyz
    method: GET
    expected_status: 200
    timeout_ms: 2000
    interval_s: 15
    dependencies:
      - database
      - cache

  - name: startup
    endpoint: /startupz
    method: GET
    expected_status: 200
    timeout_ms: 5000
    failure_threshold: 30   # 30 failures = 5min startup window
```

### Step 6 — Generate dashboard template

Grafana/Datadog/CloudWatch dashboard JSON with panels for each declared SLO metric. Dashboard title: `{project-name} — SLO Dashboard`. Panels: latency histogram, error rate gauge, throughput timeseries, resource utilization. SLO target lines drawn on each panel.

### Step 7 — Write monitor receipt

## Output contract

All files written to `.wabblespec/observability/`:
```
metric-definitions.yml
alert-rules.yml
log-schema.json
healthcheck.yml
dashboard-template.json
```

**monitor-receipt** (`.wabblespec/receipts/monitor-receipt-{timestamp}.json`):
```json
{
  "slos_codified": "integer",
  "slos_undeclared": "integer",
  "alerts_generated": "integer",
  "observability_stack": "string",
  "pii_fields_excluded": "boolean"
}
```

## Non-negotiable rules

1. Monitor derives — never invents. If SLO undeclared, mark `UNDECLARED` and skip.
2. No PII in log schema. Check engineering spec PII declarations before generating.
3. Every alert has a runbook reference. Alerts without runbooks are noise.
4. Alert thresholds match declared SLO targets exactly — no tightening or loosening without spec change.

## Common failure modes

1. **Inventing SLO targets.** If performance-budgets.md says `___ ms`, Monitor must surface `UNDECLARED` — not pick a number. Invented thresholds create false confidence.

2. **Generating alerts without runbooks.** An alert that fires but has no runbook trains engineers to ignore it. Runbook path required; stub file acceptable at first.

3. **Including PII in log schema.** If user email or IP is in the log schema, every log aggregation system becomes a PII store. Check and exclude explicitly.
