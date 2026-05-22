---
name: platform-data-pipeline
description: Data/Pipeline platform. Activates when Recipe detects an ETL pipeline, streaming processor, data orchestration job, or data quality system. Loads pipeline-specific spec templates, engineering rules, security controls, and verification gates. Produces a materially different spec from Web or API targets — focused on schema evolution, idempotency, exactly-once semantics, data quality gates, backfill strategy, and operational runbooks.
---

# Platform: Data/Pipeline

You are the Data/Pipeline platform layer. You activate when Recipe identifies a data pipeline, ETL job, streaming processor, or data orchestration target.

## What this skill does

Loads data pipeline-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to activate

Recipe must have already run and identified Data/Pipeline as the primary target. Activation signals in `skill-rules.json`.

## What makes Data/Pipeline different from other targets

| Concern | Data/Pipeline | Web | API/Service |
|---|---|---|---|
| Failure mode | Silent bad data (worse than crash) | 5xx error | 4xx/5xx error |
| Idempotency | Required — pipelines replay on failure | Nice to have | Depends |
| Success signal | Row counts, data quality assertions, schema validity | HTTP 200 | HTTP 2xx |
| Schema | Evolves over time — breaking changes break downstream consumers | HTML/JSON structure | Endpoint schema |
| Backfill | Historical reprocessing required — design for it | N/A | N/A |
| Latency class | Batch (minutes-hours) or Streaming (ms-seconds) | Real-time | Real-time |
| State | Stateful (checkpoints, watermarks, offsets) or stateless | Stateless | Stateless |
| Volume | Scales to TB/PB — cost is a first-class concern | Scales to users | Scales to RPS |
| Observability | Row counts, lag metrics, DQ assertions — not HTTP status codes | APM traces | APM traces |
| Orchestration | DAGs, cron schedules, event triggers, sensors | Request/response | Request/response |

A spec written without this platform context will miss: idempotency requirements, schema evolution strategy, backfill design, data quality assertion gates, PII handling in data stores, exactly-once vs at-least-once delivery guarantees, and operational runbook for pipeline failure.

## Activation sequence

```
1. Recipe identifies Data/Pipeline target and signals platform-data-pipeline activation
2. Load spec-template variant
3. Detect pipeline type (batch ETL / streaming / orchestration) via skill-rules.json signals
4. Load engineering/build-toolchain.md and engineering/performance-budgets.md
5. Load security/threat-model.md and security/platform-controls.md
6. Register verification/gates.md with Verifier
7. Write platform activation receipt
```

## Pipeline type routing

| Detected signal | Pipeline type |
|---|---|
| Airflow DAGs, Prefect flows, Dagster assets | Orchestrated batch |
| Kafka consumers, Flink jobs, Spark Streaming | Streaming |
| dbt models | SQL transformation |
| Spark batch jobs, pandas ETL scripts | Batch ETL |
| Great Expectations, dbt tests | Data quality |

## Output contract

**Platform activation receipt** (`.wabblespec/receipts/platform-data-pipeline-{timestamp}.json`)

## Files loaded by this module

```
modules/l3/data-pipeline/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
