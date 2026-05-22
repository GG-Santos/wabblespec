# Module Plan — Monitor (L7)

**Tier:** 3 — SUPPORTING
**Layer:** L7 Delivery
**v5.3 origin:** Monitor module — post-deployment observability configuration

---

## Purpose

Generate observability configuration for deployed artifacts. Monitor reads Engineering gateway SLO declarations and platform-appropriate monitoring patterns to produce metrics, logging, and alerting configuration. Writes config files to project/repo/ alongside the deployed artifact. Does not operate monitors — generates the config that external monitoring infrastructure consumes.

---

## Activation

`skill-rules.json` triggers:
- Deploy receipt confirmed (Monitor generates config after successful deploy)
- Explicit `/monitor <environment>` command
- Engineering gateway SLO declared in spec (Monitor notified to align alerts)
- Platform targets that require observability by default: API/Service, Data/Pipeline, AI/Agent, Desktop (server components)

---

## What Monitor Generates

| Output | Description | Platform |
|---|---|---|
| Metrics config | Prometheus/StatsD/CloudWatch metric definitions | API/Service, Data/Pipeline |
| Log schema | Structured log format declaration | All server-side targets |
| Alert rules | Threshold-based alerts derived from SLO | All targets with SLO |
| Health check config | Liveness + readiness probe definitions | API/Service, IoT/Embedded |
| Dashboard template | Grafana/CloudWatch dashboard JSON skeleton | API/Service, Data/Pipeline |
| Tracing config | OpenTelemetry/Jaeger trace sampling config | API/Service |

---

## SLO-to-Alert Binding

Monitor reads Engineering gateway SLO declarations and generates alert rules:

| SLO type | Alert rule generated |
|---|---|
| Availability target (e.g. 99.9%) | Alert when error rate exceeds 1 - target over rolling window |
| Latency p99 target | Alert when p99 exceeds target for > 5 minutes |
| Throughput floor | Alert when RPS drops below declared floor |
| Custom metric | Alert rule declared in spec — Monitor implements |

Alert window and evaluation frequency declared in spec — not defaulted.

---

## Log Schema

All server-side targets produce structured JSON logs. Monitor declares the schema:

```json
{
  "timestamp": "ISO 8601",
  "level": "DEBUG|INFO|WARN|ERROR|FATAL",
  "service": "service name",
  "trace_id": "string (optional)",
  "message": "string",
  "context": {}
}
```

No unstructured logs in server-side targets. Monitor enforces this via linting rules in CI config.

---

## Workflow

```
1. Read: Engineering gateway SLO declarations, platform package monitoring patterns, Deploy receipt

2. Select monitoring tooling per platform (from platform package):
   -> API/Service: Prometheus + Grafana (default), CloudWatch (AWS), or declared
   -> Data/Pipeline: Airflow metrics, dbt monitoring, custom
   -> AI/Agent: token usage metrics, latency histograms, refusal rate

3. Generate metric definitions aligned to SLO

4. Generate alert rules from SLO thresholds

5. Generate log schema

6. Generate health check config (API/Service, IoT)

7. Write all config to project/repo/monitoring/ or declared path

8. Write Monitor receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — post-Deploy, SLO-driven |
| `templates/prometheus/` | Template | Prometheus rules and alert templates |
| `templates/cloudwatch/` | Template | CloudWatch alarm templates |
| `templates/opentelemetry/` | Template | OTel config templates |
| `templates/log-schema.json` | Template | Structured log schema |
| `rules/slo-binding.md` | Rules | SLO to alert mapping rules |
| `rules/no-unstructured-logs.md` | Rules | Structured logs required for server targets |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Deploy | Deploy receipt triggers Monitor; Monitor config deployed alongside artifact |
| Engineering gateway | Monitor reads SLO declarations for alert rule generation |
| Platform packages (L3) | Platform monitoring conventions determine tooling selection |
| Instinct | Deploy events observed by Instinct; Monitor alerts feed operational patterns |
| Verifier | Verifier Measurement mode reads Monitor thresholds for quantitative gate |

---

## Verification Mode

**Observation** — metric definitions present, alert rules aligned to SLO declarations, log schema declared, health check config present (if applicable), receipt written.

---

## Receipt Extension Fields

```json
{
  "environment": "string",
  "monitoring_tool": "string",
  "metrics_defined": "integer",
  "alert_rules_generated": "integer",
  "slo_bindings": "integer",
  "log_schema_declared": "boolean",
  "output_path": "string"
}
```
