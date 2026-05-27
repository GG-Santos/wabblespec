# Runbook: Latency Breach

**Alert:** `LatencyP95Breach` (or `LatencyP99Breach` — update to match your alerts.yml)  
**Severity:** warning (P95) | critical (P99)  
**SLO:** P95 latency < ___ ms — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  

---

## Symptoms

- Dashboard panel showing P95 or P99 latency exceeds declared threshold
- `histogram_quantile` metric sustained above SLO target for ≥ 2 min
- Users may report slow responses or timeouts
- Downstream services may show elevated latency if this service is a dependency

---

## Immediate triage

1. Confirm alert is sustained (≥ 2 min) — not a transient spike from a single slow request.
2. Check scope: is latency elevated for all routes or a specific endpoint?
3. Check deployment log — was a deploy within the last 30 min?
4. Check infrastructure: CPU, memory, and connection pool saturation.
5. Check upstream/downstream dependencies for health degradation.

---

## Diagnosis

**PromQL — identify affected route (adapt to your stack):**
```
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket{route="___ UNDECLARED"}[5m]))
```

**PromQL — compare route-level breakdown:**
```
histogram_quantile(0.95,
  sum by (route) (rate(http_request_duration_seconds_bucket[5m])))
```

**Log query:** `___ UNDECLARED` (insert your log aggregation query for slow requests)

**Dashboard:** `___ UNDECLARED` — link to SLO dashboard

**Common causes:**
- Database query regression (N+1, missing index, lock contention)
- Downstream dependency slowdown (external API, cache miss storm)
- Insufficient connection pool size under load
- Memory pressure causing GC pauses
- Cold start after deploy (especially serverless/container)
- Thundering herd after traffic spike or wake-from-sleep

---

## Remediation

1. If a recent deploy correlates: initiate rollback via `___ UNDECLARED`.
2. If database query regression: identify slow queries via `___ UNDECLARED`, consider adding index or caching layer.
3. If downstream dependency: check dependency runbook at `___ UNDECLARED`; if unresponsive, implement circuit breaker or return degraded response.
4. If connection pool saturation: increase pool size in `___ UNDECLARED` config, redeploy.
5. If GC pressure: increase heap allocation in `___ UNDECLARED`, monitor GC pause metrics.
6. If cold-start spike: verify pre-warming configuration at `___ UNDECLARED`.

---

## Escalation

- Unresolved after ___ UNDECLARED min: page ___ UNDECLARED
- P99 breach + customer-facing impact confirmed: page ___ UNDECLARED immediately
- Database infrastructure issue: contact ___ UNDECLARED (DBA / infra team)

---

## Post-incident

- [ ] Incident report filed
- [ ] Root cause documented (query regression / dependency / infra / deploy)
- [ ] Performance-budgets.md updated if SLO target needs revision
- [ ] Runbook updated with new learnings
- [ ] Follow-up tickets created for permanent fix

---

*Generated from `.wabblespec/engine/shared/templates/runbooks/runbook-latency-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
