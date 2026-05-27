# Performance Budgets — API-Service

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/api-service`.
> Reference: `.wabblespec/engine/shared/references/performance-budgets.md`.

---

## Latency

### p50 latency (median)

**Target:** ≤ 50ms for synchronous read endpoints; ≤ 100ms for write endpoints
**Rationale:** p50 reflects the typical user experience; above 50ms on reads indicates query or serialization inefficiency
**Measurement:** server-side request duration histogram, p50 bucket
**PII impact:** none — do not log request bodies in latency traces

### p95 latency

**Target:** ≤ 200ms for all endpoints
**Rationale:** Tier 2 standard; p95 above 200ms means 1 in 20 users is having a bad experience
**Measurement:** server-side histogram, p95 bucket
**PII impact:** none

### p99 latency

**Target:** ≤ 500ms for all endpoints; ≤ 200ms for auth and health check endpoints
**Rationale:** p99 tail latency sets client timeout floors; auth latency above 200ms degrades perceived app speed
**Measurement:** server-side histogram, p99 bucket; alert on 5-minute p99 breach
**PII impact:** none

### Timeout declaration (required per endpoint)

Each endpoint must declare its client-side timeout. Undeclared timeouts default to infinity — a correctness failure, not a performance issue.

```
GET  /health:      client timeout 1s
GET  /resource:    client timeout 5s
POST /resource:    client timeout 10s
POST /batch:       client timeout 30s
```

___ UNDECLARED — populate per endpoint before running Monitor

---

## Error rate

### HTTP 5xx error rate

**Target:** < 0.1% of requests over 5-minute window (Tier 1) or < 1% (Tier 2)
**Rationale:** APIs serving other services should have tighter error budgets than user-facing web; a 1% error rate propagates through dependent services
**Measurement:** `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])`
**PII impact:** none — do not log request bodies in error responses

### HTTP 4xx error rate (client errors)

**Target:** Monitor only (no SLO) — high 4xx rates indicate client misuse or breaking API changes
**Rationale:** 4xx errors are client errors; spike detection reveals integration breaks
**Measurement:** `rate(http_requests_total{status=~"4.."}[5m])`
**PII impact:** none

---

## Throughput

### Requests per second

**Target:** ___ RPS steady state; ___ RPS peak (burst capacity)
**Rationale:** Declare based on expected load; Monitor uses this to size throughput panels
**Measurement:** `rate(http_requests_total[1m])`
**PII impact:** none

---

## Availability

**Target:** 99.9% uptime measured monthly
**Rationale:** Tier 2 for standard APIs; services consumed by other services often require tighter SLAs — adjust to 99.95% for critical dependencies
**Measurement:** health check endpoint (`GET /healthz`) polled every 30s from at least 2 regions
**PII impact:** health check response must not include internal system details

---

## Resource ceilings

### Memory

**Target:** ≤ ___ MB resident memory under steady-state load (p95)
**Rationale:** Memory above ceiling triggers OOM in container environments; set based on container memory limit × 0.8
**Measurement:** container memory metric; alert at 80% of declared limit
**PII impact:** none

### CPU

**Target:** ≤ ___ % CPU utilization at p95 load
**Rationale:** CPU saturation above 80% causes latency spikes under burst load
**Measurement:** container CPU metric over 1-minute window
**PII impact:** none

---

## gRPC (if applicable)

### gRPC deadline propagation

**Target:** All gRPC calls declare deadline; no undeadlined calls
**Rationale:** Missing deadlines cause cascading hangs in downstream services
**Measurement:** gRPC interceptor audit; flag calls with no deadline context
**PII impact:** none

---

## PII fields (excluded from log schema)

<!-- Declare any PII-bearing fields that must not appear in request logs or traces -->
<!-- Example:
- Authorization header value
- user_id (if PII under GDPR)
- request body fields: email, phone, address
-->
___ UNDECLARED — populate before running Monitor
