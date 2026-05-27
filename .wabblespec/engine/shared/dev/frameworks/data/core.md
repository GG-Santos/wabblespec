# Data Pipeline Framework Core

Cross-framework knowledge for ETL, streaming, and data orchestration targets. Loaded by Apply for every Data/Pipeline platform task.

## Data pipeline contract requirements

Every data pipeline spec must declare:
- **Delivery semantics**: exactly-once, at-least-once, or at-most-once (and why)
- **Idempotency**: how repeated execution of the same run produces the same result
- **Schema**: source schema, output schema, and version of each
- **Backfill**: how historical data is reprocessed; backfill isolation from live pipeline
- **Failure behavior**: what happens when a record fails; dead letter queue or skip and alert

## Idempotency patterns

```
Run ID:        date + run number (e.g., "2026-05-24-01")
Overwrite key: partition date or output table key
```

A pipeline is idempotent if: running it twice with the same Run ID produces the same output as running it once.

Patterns:
- **Overwrite partition**: write to date-partitioned output; re-running overwrites the partition
- **Upsert**: use a unique key; insert or update on conflict
- **Truncate + insert**: clear the output for this run's scope before writing

Anti-pattern: append-only writes without deduplication — re-runs double-count.

## Data quality gates

Every pipeline must have assertions that run after transformation, before output commit:

```python
# Example assertions
assert row_count > 0, "Output is empty"
assert row_count >= expected_min, f"Row count {row_count} below minimum {expected_min}"
assert null_rate("email") < 0.01, "Null rate on email exceeds 1%"
assert unique_rate("user_id") == 1.0, "Duplicate user_ids found"
```

Spec must declare: which assertions run, what thresholds they check, and what happens on failure (alert, halt, or quarantine).

## Schema evolution

Schema changes break consumers. Rules:
- **Additive changes** (new nullable column): backward compatible; announce to consumers
- **Renaming columns**: not backward compatible; use aliasing during transition period
- **Dropping columns**: not backward compatible; deprecate with 30-day notice
- **Type changes**: never change column types — create a new column

All schemas must be versioned. Spec must declare the versioning strategy and migration path for breaking changes.

## PII in data pipelines

- PII must be identified in the data model (annotate columns in schema)
- PII in transit: encrypted (TLS for network, encrypted storage for files)
- PII in storage: declare retention period; deletion or anonymization at end of retention
- PII masking: mask in dev/staging environments; never copy production PII to non-production without explicit authorization
- Access control: declare which roles/services have access to PII data

## Performance and cost

| Concern | Declaration required |
|---|---|
| Input data volume | Rows per run, GB per run |
| Processing cost | Compute cost per run (spot vs on-demand) |
| Output storage | Row growth rate; retention policy |
| Runtime target | SLA for job completion (e.g., must complete by 6am) |
| Parallelism | Partition count, worker count |

## Operational requirements

Every pipeline spec must include an operational runbook section:
- **What to check first** when the pipeline fails
- **How to rerun** a failed partition or date range
- **How to pause** the pipeline without data loss
- **Alerts**: which conditions page on-call; which conditions auto-retry
- **Dependencies**: upstream pipelines or sources that must succeed first
