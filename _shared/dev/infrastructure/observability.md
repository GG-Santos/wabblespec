# Observability Engineering Standards

Loaded by Apply when gateway-engineering is active. Covers structured logging, metrics, tracing, and alerting.

## The three pillars

| Pillar | Answers | Tool examples |
|---|---|---|
| Logs | What happened? | Loki, Elasticsearch, CloudWatch, Datadog |
| Metrics | How is the system behaving? | Prometheus, Datadog, CloudWatch Metrics |
| Traces | Where did time go? | Jaeger, Zipkin, Datadog APM, OpenTelemetry |

Spec must declare: which tools are used for each pillar; how they are correlated (request_id linking logs, metrics, and traces).

## Structured logging requirements

Every service must emit structured logs (JSON). Do not use free-form string log lines.

```json
{
  "timestamp": "2026-05-24T10:00:00.000Z",
  "level": "info",
  "message": "Request processed",
  "service": "user-service",
  "version": "1.2.3",
  "request_id": "req_abc123",
  "user_id": "usr_456",
  "method": "GET",
  "path": "/users/456",
  "status": 200,
  "duration_ms": 45,
  "trace_id": "trace_789"
}
```

### Required fields on every log line

| Field | Value |
|---|---|
| `timestamp` | ISO 8601 UTC |
| `level` | debug / info / warn / error / fatal |
| `message` | Human-readable summary |
| `service` | Service name |
| `request_id` | Per-request unique ID |
| `trace_id` | Distributed trace ID (if using tracing) |

### Log levels

| Level | When |
|---|---|
| debug | Development only; verbose internal state |
| info | Normal operations: request start/end, state changes |
| warn | Unexpected but handled: retried request, rate limit approaching |
| error | Operation failed; requires attention but service continues |
| fatal | Service cannot continue; process exits |

Do not log at debug in production by default. Make level configurable via environment variable.

### PII in logs

Never log: passwords, tokens, full credit card numbers, SSNs, full email addresses (use first 3 chars + domain if needed for debugging).

## Metrics requirements

Spec must declare the metrics for each service:

### Standard service metrics (every service)

```
http_requests_total{method, path, status}     — counter
http_request_duration_seconds{method, path}   — histogram (p50, p95, p99)
http_request_in_flight                         — gauge (current requests being processed)
```

### Application-specific metrics

Declare in spec: what does "success" look like for this service? What metric measures it?

Examples:
- `orders_created_total` — counter
- `payment_processing_duration_seconds` — histogram
- `queue_depth` — gauge
- `cache_hit_rate` — gauge

### Prometheus format

```go
// Go example
import "github.com/prometheus/client_golang/prometheus"

var requestDuration = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Help:    "HTTP request latency",
        Buckets: prometheus.DefBuckets,
    },
    []string{"method", "path", "status"},
)
```

Expose metrics on `/metrics` endpoint (not publicly accessible).

## Distributed tracing

Use OpenTelemetry for vendor-neutral tracing:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer("my-service")

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # ... work ...
        span.set_attribute("order.status", "completed")
```

Propagate trace context across service boundaries via `traceparent` header (W3C Trace Context standard).

## SLI / SLO requirements

Spec must declare Service Level Indicators and Objectives:

```yaml
slos:
  - name: "API Availability"
    sli: "percentage of requests returning 2xx or 3xx"
    target: 99.9%
    window: 30d
    
  - name: "API Latency"
    sli: "percentage of requests completing in < 200ms"
    target: 95%
    window: 30d
```

Error budgets: `100% - SLO target` = budget for failures. When budget is exhausted, freeze non-critical deployments.

## Alerting requirements

Spec must declare alerts:

| Condition | Severity | Action |
|---|---|---|
| Error rate > 5% for 5 minutes | CRITICAL | Page on-call |
| p99 latency > 2x SLO threshold for 10 minutes | WARNING | Notify team |
| Service down (all instances unhealthy) | CRITICAL | Page on-call immediately |
| Error budget < 10% | WARNING | Freeze non-critical deploys |
| Disk usage > 80% | WARNING | Plan capacity increase |

Alert on symptoms (error rate, latency), not causes (CPU, memory) — causes are for debugging after symptom alert fires.
