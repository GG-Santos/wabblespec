# Data/Pipeline Systems Design Template (P2)

> **Platform:** Data/Pipeline
> **Template version:** 1.0
> **Prerequisite:** design-document.md `[REQUIRED]` sections complete.

---

## Pipeline Architecture Diagram

```
Source(s)
  └── Extract / Consume
        └── Transform
              ├── Validate (DQ assertions)
              └── Load / Publish
                    └── Destination(s)
                          └── Downstream consumers
```

Annotate with:
- Latency SLA at each stage
- Volume at each stage
- Failure behavior at each stage

---

## Orchestration Design

**Orchestrator:** [ ] Airflow [ ] Prefect [ ] Dagster [ ] cron [ ] event-triggered [ ] none

**DAG/flow structure:**

```
pipeline_dag
  ├── extract_task
  │     └── depends_on: source availability sensor
  ├── validate_source_task
  │     └── depends_on: extract_task
  ├── transform_task
  │     └── depends_on: validate_source_task
  ├── validate_output_task
  │     └── depends_on: transform_task
  └── load_task
        └── depends_on: validate_output_task (must pass)
```

**Schedule:** `cron: "0 2 * * *"` (2am UTC daily) or event-triggered (describe trigger):

**Retry policy:**
```
retries: 3
retry_delay: 5 minutes
retry_exponential_backoff: true
max_retry_delay: 30 minutes
```

**On failure:** [ ] Alert only [ ] Alert + block downstream [ ] Alert + trigger rollback

---

## Partitioning Strategy

| Dimension | Partition key | Reason |
|---|---|---|
| Time | `date` (daily) or `hour` | Enables backfill and retention |
| Region | `region` (if multi-region data) | Query cost reduction |

**Partition overwrite:** On retry, overwrite the full partition — not append. Prevents duplicates.

**Partition pruning:** All queries filter on partition key to avoid full scans.

---

## Checkpointing (Streaming)

**Checkpoint mechanism:** [ ] Kafka consumer group offsets [ ] Flink checkpoints (HDFS/S3) [ ] Spark Structured Streaming checkpoints

**Checkpoint location:** `s3://<bucket>/checkpoints/<pipeline-name>/`

**Checkpoint interval:** Every ___ records or ___ seconds

**Recovery behavior:** On restart, resume from last committed checkpoint. Maximum data loss: 0 (exactly-once) or ___ events (at-least-once with dedup).

---

## State Management

| State type | Storage | TTL | Size estimate |
|---|---|---|---|
| Deduplication window | Redis / RocksDB | ___ hours | ___ MB |
| Aggregation state | In-memory + checkpoint | Session | ___ MB |
| Join state | RocksDB (Flink) | ___ hours | ___ GB |

**State explosion risk:** Unbounded state is a production incident waiting to happen. All state has declared TTL or maximum size.

---

## Transformation Logic

Document each transformation step:

| Step | Input | Output | Business rule | Failure behavior |
|---|---|---|---|---|
| Parse events | Raw JSON string | Structured record | JSON schema validation | Drop + DLQ |
| Normalize timestamps | Mixed timezone timestamps | UTC timestamp | Convert to UTC | Halt if invalid |
| Enrich with reference data | user_id | user segment | Left join — segment = NULL if no match | Pass through NULL |
| Aggregate | Events per user | Daily count | COUNT(*) GROUP BY user_id, date | — |

---

## Dead Letter Queue (DLQ)

**DLQ:** All records that fail parsing, validation, or enrichment go to DLQ instead of being silently dropped.

| Failure type | DLQ destination | Retention | Reprocessing |
|---|---|---|---|
| Parse error | `s3://<bucket>/dlq/parse-errors/` | 30 days | Manual trigger after fix |
| DQ assertion failure | `s3://<bucket>/dlq/dq-failures/` | 30 days | Manual trigger after fix |
| Enrichment failure | `s3://<bucket>/dlq/enrich-errors/` | 30 days | Manual trigger after fix |

**DLQ alert:** Alert when DLQ exceeds ___ records or ___ % of input volume.

---

## Monitoring and Alerting

| Metric | Source | Alert threshold | Alert channel |
|---|---|---|---|
| Pipeline lag | Kafka consumer group lag | > ___ seconds | PagerDuty |
| Row count | Output table count vs expected | < 90% of expected | Slack #data-alerts |
| DQ failure rate | DQ tool | Any assertion failure | PagerDuty |
| Pipeline duration | Orchestrator runtime | > ___ minutes | Slack #data-alerts |
| Error rate | Log aggregator | > 0 errors | Slack #data-alerts |
