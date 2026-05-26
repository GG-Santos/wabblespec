# Runbook: Throughput Drop

**Alert:** `ThroughputDrop`  
**Severity:** warning (< declared target) | critical (< ___ % of declared target — sustained)  
**SLO:** Throughput ≥ ___ req/s (API) / ≥ ___ records/s (Data Pipeline) — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** API Service, Data Pipeline platforms primarily; also applies to any platform with declared throughput SLO  

---

## Symptoms

- Throughput metric below declared floor for ≥ ___ min
- Queue depth growing (data pipeline: job backlog accumulating; API: request queue depth rising)
- Downstream consumers reporting data lag or timeout waiting for results
- Auto-scaling not keeping up with load (if applicable)
- Database or message broker connection pool at capacity

---

## Immediate triage

1. Is this a demand-side drop (less traffic arriving than expected) or a supply-side drop (system can't keep up with demand)?
2. **Demand-side:** Is upstream sending fewer requests? Check upstream health. Not an incident — but if SLO is measured against declared throughput target regardless of demand, treat as investigation.
3. **Supply-side:** Are requests/records queuing up? Check queue depth and consumer lag metrics.
4. Check infrastructure: are all instances/workers healthy? Any crashed pods/containers?
5. Was a deploy recent? Did it reduce concurrency, add latency to the hot path, or change batch size?

---

## Diagnosis

**PromQL — current throughput:**
```
rate(http_requests_total[5m])        # API Service
# or
rate(records_processed_total[5m])    # Data Pipeline
```

**PromQL — queue depth / consumer lag:**
```
___ UNDECLARED  # insert Kafka consumer lag / SQS queue depth / RabbitMQ backlog query
```

**Worker/pod health:** `___ UNDECLARED` (insert health check for all pipeline workers or API pods)

**Dashboard:** `___ UNDECLARED`

**Common causes (API Service):**
- Insufficient replica count — auto-scaler not triggered fast enough
- Hot path latency increased, reducing effective throughput (tangled with LatencyBreach)
- Database connection pool exhausted — requests waiting on DB connections
- External rate limiting applied by downstream service
- Circuit breaker open — dropping requests to protect dependencies

**Common causes (Data Pipeline):**
- Worker crash causing partition rebalance delay (Kafka, etc.)
- Batch size too large — each record taking too long to process
- DQ (data quality) validation rejecting records at high rate — pipeline processing but not committing
- External API rate limit hit mid-pipeline
- Idempotency deduplication overhead growing with state store size

---

## Remediation

### API Service
1. Scale up replica count immediately: `___ UNDECLARED`.
2. If DB connection pool: increase pool size in `___ UNDECLARED`, redeploy; check DB for lock contention.
3. If latency is the root cause of low throughput: follow `runbook-latency-breach.md`.
4. If circuit breaker open: check downstream health; do not force-close circuit without confirming dependency is healthy.
5. If external rate limit: implement backpressure or queue at the ingress layer; do not overload the limited dependency.

### Data Pipeline
1. Scale worker count: `___ UNDECLARED` (increase Kafka consumers, Airflow workers, etc.).
2. If DQ rejection rate is high: inspect DQ failure logs at `___ UNDECLARED`; fix upstream data issue or adjust DQ rule if rule is wrong.
3. If batch size too large: reduce batch size in `___ UNDECLARED` to bring per-record processing time within budget.
4. If idempotency deduplication slow: check state store size; run compaction at `___ UNDECLARED`.
5. If worker crash loop: see `runbook-crash-rate-breach.md` for the pipeline worker.

---

## Escalation

- Throughput < ___ % of declared floor for > ___ min (backlog growing uncontrollably): page ___ UNDECLARED
- Data pipeline SLA breach imminent (batch will not complete by declared SLA window): page ___ UNDECLARED + notify data consumers
- External rate limit confirmed: contact ___ UNDECLARED (vendor / infra team)

---

## Post-incident

- [ ] Root cause documented (scale / latency / DB / DQ / rate limit / worker crash)
- [ ] Auto-scaling thresholds reviewed — should have scaled sooner
- [ ] Throughput floor in performance-budgets.md confirmed still accurate
- [ ] Runbook updated with pipeline-specific worker and queue details

---

*Generated from `_shared/templates/runbooks/runbook-throughput-drop.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
