# API/Service Engineering — Performance Budgets

## Latency

**Budget:** p99 response latency < 200ms for standard endpoints under normal load.

Exceptions require explicit declaration in design-document.md:
- Long-running operations (file processing, report generation): use async pattern (accept → 202, poll status endpoint)
- Search with full-text index: declare separate budget (e.g., p99 < 500ms)
- Third-party upstream calls: declare timeout + circuit breaker

**Measurement:**
```bash
# Load test with k6, vegeta, or wrk
k6 run --vus 50 --duration 60s script.js
# Report: p50, p90, p99, p99.9 latency + error rate

# Simple one-liner (vegeta):
echo "GET http://localhost:8080/api/users" | vegeta attack -rate=100 -duration=30s | vegeta report
```

**SLO declaration:** State in design-document:
- p50 target: ___ms
- p99 target: ___ms (default: 200ms)
- Error rate target: < 0.1% under declared RPS

---

## Throughput

**Baseline target:** Service must sustain declared peak RPS without degradation.

**Declare:**
- Expected peak RPS: ___
- Replicas at peak: ___
- RPS per replica: ___

**Throughput test:** Run at 110% of declared peak RPS for 5 minutes. p99 must remain within latency budget.

---

## Startup Time

**Budget:** Service ready to serve traffic within 10 seconds of container start.

"Ready" = /ready endpoint returns 200 (all dependencies connected).

**Why this matters:** Kubernetes restarts slow-starting pods. Deployment rollouts block until new pods are ready. Startup beyond 10s risks deployment timeouts.

**Slow startup causes:**
- Synchronous migration run at startup (run in init container instead)
- Loading large ML models or config files (declare this — budget is different)
- Serial dependency health checks (parallelize)

**Measurement:**
```bash
time docker run --rm <image>  # until /ready returns 200
```

---

## Memory

**Budget:** Declare per service. No universal default.

Suggested starting points:
- Stateless API (no caching): < 256MB RSS at steady state under load
- API with in-memory cache: < 512MB RSS
- Worker processing large payloads: declare O(payload-size) behavior

**Container resource limits (Kubernetes):**
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**OOMKill is a gate failure.** If service OOMKills under declared load, performance budget fails.

---

## Database Query Latency

**Budget:** Individual DB query p99 < 50ms for indexed lookups.

Queries exceeding 100ms must be explained (`EXPLAIN ANALYZE`) and either optimized or declared as expected with justification.

**N+1 prevention:** No N+1 query patterns. Batch-load related data. Verify with query count assertion in integration tests.

**Connection pool exhaustion:** Pool exhaustion under load is a gate failure. Size pool to handle peak RPS × average query time per request.

Pool sizing guide:
```
max_connections = (peak_rps × avg_queries_per_request × avg_query_duration_s) + headroom
```

---

## Response Size

**Budget:** Single-resource response < 100KB. Collection responses paginated.

**Pagination required for all list/collection endpoints.** No unbounded list responses.

Pagination contract:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 1240,
    "next_cursor": "eyJpZCI6MTAwfQ=="
  }
}
```

[ ] Cursor-based (preferred for large / frequently updated collections)
[ ] Offset-based (acceptable for small, stable collections)

**Default page size:** 50. Max page size: 200. Requests for more than max: 400 error.

---

## Health Check Latency

**Budget:** /health returns 200 within 50ms always.

/health must never query the database or call external services. Liveness only — is the process alive?

**Budget:** /ready returns within 2 seconds under normal conditions.

/ready checks real dependencies. If a check takes longer than 2 seconds, it times out and /ready returns 503.
