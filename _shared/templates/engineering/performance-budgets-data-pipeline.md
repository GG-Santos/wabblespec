# Performance Budgets — Data Pipeline

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/data-pipeline`.
> Reference: `_shared/references/performance-budgets.md`.
> Note: Data pipelines have batch SLAs and stream latency targets, not request latency.

---

## Throughput

### Batch processing throughput

**Target:** ≥ ___ records/second sustained throughput (declare based on peak input volume × 1.5 headroom)
**Rationale:** Throughput ceiling must exceed peak input rate with headroom; if throughput < input rate, the backlog grows unboundedly
**Measurement:** benchmark run on production-equivalent hardware; peak volume replay test
**PII impact:** none

### Stream processing latency (if applicable)

**Target:** ≤ ___ ms end-to-end latency from event ingestion to sink write at p99 (stream pipelines only)
**Rationale:** Stream latency SLA drives buffer sizing, consumer group configuration, and downstream alerting delays
**Measurement:** timestamp injection at source and sink; Kafka lag monitoring / equivalent
**PII impact:** event payloads may contain PII — declare and redact before metrics

---

## Batch SLA

### Batch job completion deadline

**Target:** ___ batch job must complete by ___ (e.g., "nightly ETL must complete by 06:00 local time")
**Rationale:** Downstream systems, reports, and dashboards depend on batch completion; missing deadline cascades
**Measurement:** job completion timestamp logged and alerting set for SLA breach
**PII impact:** none — log job metadata only, not data contents

### Batch job duration ceiling

**Target:** ≤ ___ hours for full batch run; alert at 80% of ceiling
**Rationale:** Runaway jobs consuming full cluster resources block other workloads; ceiling prevents unbounded growth
**Measurement:** job duration histogram; alert on duration regression across releases
**PII impact:** none

---

## Idempotency

### Re-run safety

**Target:** Any batch job run twice on the same input produces identical output with zero duplicate records in the sink
**Rationale:** Re-runs are the primary recovery mechanism; a non-idempotent pipeline cannot be safely recovered (enforced in `l3/data-pipeline` acceptance tests AT-DP-01)
**Measurement:** integration test: run job twice on fixture, assert sink record count == single-run count
**PII impact:** none

---

## Data quality

### Null rate ceiling per critical field

**Target:** ≤ ___ % null values for each declared critical field (define per field)
**Rationale:** Silent null propagation is the most common data quality failure; pipeline must assert floor before writing to sink
**Measurement:** DQ assertion in pipeline code; assert-and-halt on breach (silent bad data is worse than a stopped pipeline — enforced in `l3/data-pipeline` AT-DP-04)
**PII impact:** none

### Schema version compliance

**Target:** 100% of records comply with the declared schema version at ingestion; schema violations logged and routed to dead-letter queue, not silently dropped
**Rationale:** Silent schema drift causes downstream query failures that surface hours or days later
**Measurement:** schema validation step in pipeline; DLQ count alert
**PII impact:** DLQ may contain PII — encrypt at rest; access-controlled

---

## Error rate

### Pipeline error rate

**Target:** < 0.1% of records routed to dead-letter queue in steady state
**Rationale:** Above 0.1% DLQ rate indicates upstream data quality or schema changes that need investigation
**Measurement:** `DLQ_count / total_processed` over each batch run or 1-hour stream window
**PII impact:** DLQ access must be restricted and audited

---

## Recovery

### Backfill throughput

**Target:** Backfill job processes ≥ ___ days of historical data per hour
**Rationale:** Backfill capacity determines maximum outage recovery time; undeclared capacity makes SLA recovery impossible to estimate (enforced in `l3/data-pipeline` AT-DP-03)
**Measurement:** backfill benchmark on production-equivalent cluster
**PII impact:** none

---

## Resource

### Cluster CPU ceiling

**Target:** ≤ 80% cluster CPU utilization at peak batch load
**Rationale:** Sustained >80% CPU causes job queue saturation and cascading latency spikes
**Measurement:** cluster monitoring during peak batch window
**PII impact:** none

### Storage growth rate

**Target:** ≤ ___ GB/day data volume growth; alert at 80% of storage quota
**Rationale:** Unmonitored data growth causes storage exhaustion that halts pipelines
**Measurement:** storage metric with 30-day trend; capacity planning review quarterly
**PII impact:** none

---

## PII fields (excluded from log schema)

<!-- Data pipelines frequently process PII — these must be redacted from operational logs -->
<!-- Example:
- email
- phone_number
- ip_address
- user_id (if regulated as PII under GDPR/CCPA)
- payment_card_number
- health_record_id
-->
___ UNDECLARED — this field is REQUIRED before pipeline goes to production for any dataset containing personal data
