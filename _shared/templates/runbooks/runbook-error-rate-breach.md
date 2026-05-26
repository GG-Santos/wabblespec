# Runbook: Error Rate Breach

**Alert:** `ErrorRateBreach`  
**Severity:** critical  
**SLO:** Error rate < ___ % over 5 min window — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  

---

## Symptoms

- Dashboard panel showing error rate (5xx / total) above declared threshold
- `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])` sustained above SLO
- Users receiving error responses, blank pages, or "Something went wrong" messages
- Alerts may co-fire with LatencyBreach if errors are due to timeouts

---

## Immediate triage

1. Confirm alert is sustained (≥ 1 min) — not a one-off restart artifact.
2. Check error type breakdown: are these 500 (server error), 502 (gateway), 503 (unavailable), or 504 (timeout)?
3. Check deployment log — was a deploy within the last 30 min?
4. Check infrastructure health: are pods/containers crashing and restarting?
5. Check downstream dependencies: database, cache, external APIs.
6. Is this a partial outage (some routes/regions) or total?

---

## Diagnosis

**PromQL — error rate by status code:**
```
sum by (status_code) (
  rate(http_requests_total{status=~"5.."}[5m])
)
```

**PromQL — error rate by route:**
```
sum by (route) (
  rate(http_requests_total{status=~"5.."}[5m])
) / sum by (route) (
  rate(http_requests_total[5m])
)
```

**Log query for errors:** `___ UNDECLARED` (insert log search for ERROR/CRITICAL level with stack traces)

**Dashboard:** `___ UNDECLARED`

**Common causes:**
- Unhandled exception introduced in recent deploy
- Database connection exhaustion (all connections in pool failing)
- External dependency returning errors (propagating upstream)
- Configuration mismatch after deploy (wrong env var, missing secret)
- Memory exhaustion causing OOM kills
- Rate limiting by downstream service
- Misconfigured load balancer or health check probe

---

## Remediation

1. If a recent deploy correlates: initiate rollback via `___ UNDECLARED`.
2. Capture a sample of error logs and identify the exception class and stack trace.
3. If database connection exhaustion: check connection pool metrics; scale if needed or restart connection pool via `___ UNDECLARED`.
4. If external dependency error: check dependency status page at `___ UNDECLARED`; route traffic away or degrade gracefully.
5. If configuration mismatch: verify environment variables against `___ UNDECLARED` (secrets manager / config store).
6. If OOM: check memory metrics, increase memory limit in `___ UNDECLARED`, redeploy.

---

## Escalation

- Unresolved after ___ UNDECLARED min: page ___ UNDECLARED
- Error rate > ___ % (full outage threshold): page ___ UNDECLARED immediately + open incident bridge
- External dependency confirmed down: contact ___ UNDECLARED

---

## Post-incident

- [ ] Incident report filed
- [ ] Root cause documented
- [ ] Exception handling improved / defensive code added
- [ ] Performance-budgets.md or error budget policy reviewed
- [ ] Runbook updated with new learnings
- [ ] Follow-up tickets for permanent fix

---

*Generated from `_shared/templates/runbooks/runbook-error-rate-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
