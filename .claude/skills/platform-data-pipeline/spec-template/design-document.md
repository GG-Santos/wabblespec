# Data/Pipeline Design Document Template (P1)

> **Platform:** Data/Pipeline
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-data-pipeline activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this pipeline does, what data it moves/transforms/validates, who consumes the output, and what breaks if it fails.

---

## Pipeline Type [REQUIRED]

[ ] Batch ETL — scheduled extraction, transformation, load
[ ] Streaming — continuous event processing (Kafka, Kinesis, Pub/Sub)
[ ] SQL Transformation — dbt models, Spark SQL, BigQuery views
[ ] Orchestrated DAG — Airflow/Prefect/Dagster multi-step workflow
[ ] Data Quality — assertion/monitoring pipeline
[ ] Hybrid — combination (describe: ___)

**Latency class:**
[ ] Batch (runs every ___ minutes/hours/days)
[ ] Near-real-time (lag target: ___ seconds)
[ ] Real-time (lag target: ___ milliseconds)

---

## Data Sources [REQUIRED]

| Source | Type | Format | Volume (rows/day or GB/day) | Schema owner |
|---|---|---|---|---|
| [source name] | DB / S3 / Kafka / API | JSON / Parquet / CSV / Avro | ___ | [team] |

**Source trust level:** Each source classified as: [ ] Authoritative [ ] Derived [ ] External (untrusted)

---

## Data Destinations [REQUIRED]

| Destination | Type | Format | SLA | Downstream consumers |
|---|---|---|---|---|
| [dest name] | DB / S3 / Kafka / Data warehouse | Parquet / JSON / table | ___ | [list consumers] |

**Downstream SLA:** If this pipeline fails, how long until a downstream consumer is affected?

---

## Idempotency Strategy [REQUIRED]

**Is this pipeline idempotent?** [ ] Yes [ ] No — explain why not and document risk.

**Idempotency method:**
[ ] Insert/replace by primary key (upsert)
[ ] Partition overwrite (write to date partition, overwrite entire partition on retry)
[ ] Deduplication by event ID before write
[ ] Exactly-once guarantee from framework (Flink, Kafka Transactions)
[ ] Write-once to append-only store (idempotent by design)

**Why idempotency matters:** Pipelines fail and retry. Without idempotency, retries produce duplicate data. Downstream consumers get double-counted metrics, users see duplicate records, financial aggregations are wrong.

---

## Schema Evolution Strategy [REQUIRED]

How will schema changes be handled without breaking downstream consumers?

| Change type | Strategy |
|---|---|
| Add new column | Backward-compatible — allowed at any time |
| Rename column | Breaking — requires versioned migration (dual-write period) |
| Remove column | Breaking — deprecation period declared: ___ |
| Change data type | Breaking — requires versioned migration |
| Reorder columns | Breaking for positional formats (CSV) — avoid |

**Schema registry:** [ ] Confluent Schema Registry [ ] AWS Glue Data Catalog [ ] dbt schema.yml [ ] None — document why

**Breaking change process:**
1. Announce to downstream consumers ___ days before
2. Dual-write old + new schema for ___ days
3. Migrate consumers
4. Remove old schema

---

## Data Quality Assertions [REQUIRED]

Declare assertions that must pass before data is considered valid. Pipeline halts on assertion failure — bad data does not reach consumers.

| Assertion | Field/Table | Rule | Threshold | On failure |
|---|---|---|---|---|
| Not null | `user_id` | `user_id IS NOT NULL` | 100% | Halt pipeline |
| Row count | output table | `> 0` rows after transform | 100% | Halt pipeline |
| Freshness | `event_time` | Max age < ___ hours | 95% | Alert + halt |
| Uniqueness | `order_id` | No duplicates in output | 100% | Halt pipeline |
| Referential integrity | `product_id` | Exists in products table | 99% (allow _% unknown) | Alert |
| Value range | `price` | `> 0 AND < 1000000` | 99.9% | Alert |

---

## Backfill Strategy [REQUIRED]

**Can this pipeline be backfilled?** [ ] Yes [ ] No — explain why not.

**Backfill method:**
- Trigger: `pipeline run --start-date 2024-01-01 --end-date 2024-01-31`
- Parallelism: ___ days in parallel
- Order: [ ] Chronological [ ] Reverse chronological [ ] Any order
- Effect on existing data: [ ] Overwrites [ ] Skips existing [ ] Appends (deduplicated)

**Cost of backfill:** Estimated compute + storage cost for 1-year backfill: ___

---

## PII and Sensitive Data [REQUIRED]

| Field | PII type | Handling |
|---|---|---|
| `email` | PII | Hashed (SHA-256 + salt) before storage |
| `ip_address` | PII | Masked (last octet removed) |
| `user_id` | Internal ID | Stored as-is |
| [list all] | | |

**Retention policy:** Data deleted after ___ days. Deletion method: ___

**Regulatory scope:** [ ] GDPR [ ] CCPA [ ] HIPAA [ ] None declared

---

## GWT Acceptance Scenarios (Data/Pipeline-specific)

```
Given: the pipeline runs on a dataset with 10% null user_ids
When: the data quality assertion runs
Then: the pipeline halts before writing to the destination
      AND an alert is sent to the declared on-call channel
      AND no partial data is written to the destination

Given: the pipeline fails mid-run and is restarted
When: the pipeline runs again on the same input data
Then: the output contains no duplicate rows
      AND the row count matches a single successful run
      AND downstream consumers see correct data

Given: a new column is added to the source schema
When: the pipeline processes the new schema
Then: the pipeline does not fail due to the new column
      AND the new column is either passed through or explicitly dropped
      AND downstream schema is updated according to the evolution strategy

Given: the pipeline is run in backfill mode for 30 days of history
When: it completes
Then: each day's partition contains the same data as a fresh run would produce
      AND no day is missing
      AND running backfill again produces identical output (idempotent)
```

---

## Operational Runbook Summary

| Failure scenario | Symptoms | First response | Escalation |
|---|---|---|---|
| Pipeline timeout | No completion alert | Check logs, restart with smaller chunk | Page on-call |
| DQ assertion failure | Alert from DQ tool | Do NOT replay — investigate source | Page data owner |
| Source schema change | Schema parse error | Halt downstream, investigate | Page schema owner |
| Destination write failure | Write error in logs | Check destination health | Page infra on-call |

**Full runbook location:** `docs/runbooks/<pipeline-name>.md`

---

## Open Questions

List unresolved design decisions. Specify blocks receipt until REQUIRED sections complete.
