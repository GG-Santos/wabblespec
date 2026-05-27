# Data/Pipeline Technical Spec Template (P3)

> **Platform:** Data/Pipeline
> **Template version:** 1.0
> **Prerequisite:** systems-design.md complete.

---

## Transformation Implementation Specs

Each transformation step from systems-design.md gets one entry.

### Step: `<step_name>`

**Input schema:**
```json
{
  "user_id": "string (UUID)",
  "event_type": "string (enum: click|view|purchase)",
  "timestamp": "string (ISO 8601 UTC)",
  "properties": "object (arbitrary)"
}
```

**Output schema:**
```json
{
  "user_id": "string",
  "event_type": "string",
  "event_at": "timestamp (UTC)",
  "property_count": "integer"
}
```

**Logic:**
```python
def transform(record: dict) -> dict | None:
    # Returns None to send to DLQ
    if not record.get('user_id'):
        return None  # → DLQ
    return {
        'user_id': record['user_id'],
        'event_type': record['event_type'],
        'event_at': parse_utc(record['timestamp']),
        'property_count': len(record.get('properties', {}))
    }
```

**GWT scenarios:**
```
Given: a record with null user_id
When: the transform step processes it
Then: record is routed to DLQ
      AND a DLQ counter metric is incremented
      AND no exception propagates to fail the pipeline run

Given: a record with a timestamp in PST timezone
When: the normalize step processes it
Then: timestamp is converted to UTC
      AND stored in event_at field
      AND original timezone information is not preserved (by design)
```

---

## Data Quality Assertion Implementation

```python
# Using Great Expectations or dbt tests

# Great Expectations example:
suite = context.get_expectation_suite("pipeline_output")
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "user_id", "mostly": 1.0}  # 100%
    )
)
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_table_row_count_to_be_between",
        kwargs={"min_value": 1, "max_value": None}
    )
)

# dbt test example (schema.yml):
# models:
#   - name: pipeline_output
#     columns:
#       - name: user_id
#         tests: [not_null, unique]
#       - name: event_at
#         tests: [not_null]
```

**Assertion failure behavior:** Pipeline stops. No data written to destination. Alert fired. Requires manual investigation before rerun.

---

## Idempotency Implementation

### Partition Overwrite Pattern (Batch)
```python
# Write to temp partition, then atomic rename
df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet(f"s3://{bucket}/output/date={run_date}/")
# Overwrite replaces the full partition — no duplicates on retry
```

### Upsert Pattern (Streaming to OLTP)
```sql
-- PostgreSQL
INSERT INTO output_table (id, value, updated_at)
VALUES (%s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
  value = EXCLUDED.value,
  updated_at = EXCLUDED.updated_at;
```

### Deduplication Pattern (Streaming)
```python
# Deduplicate by event_id within a watermark window
df.withWatermark("event_at", "2 hours") \
  .dropDuplicates(["event_id"])
```

---

## Backfill Implementation

```bash
# Airflow backfill:
airflow dags backfill <dag_id> \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --max-active-runs 4

# Custom runner:
python pipeline.py --mode backfill --start 2024-01-01 --end 2024-01-31 --parallelism 4
```

**Backfill isolation:** Backfill runs must not affect production pipeline scheduling. Use separate worker pool or queue.

**Cost control:** Backfill resource limits declared: max ___ parallel runs, max ___ GB/hour.

---

## Operational Runbook

### Pipeline Failure Response

```
1. Check orchestrator logs for error message
2. Identify failure stage (extract / transform / DQ / load)
3. If DQ failure: DO NOT RETRY before investigating source
4. If transient error (network, timeout): retry manually
5. If schema error: halt, notify schema owner, do not retry
6. After root cause fixed: run in test mode with sample data first
7. Retry production run
8. Verify output row counts match expected
9. Document in incident log
```

### DLQ Review Process

```
1. Alert fires: DLQ has records
2. Sample 10 DLQ records, identify pattern
3. If known good records (bug in transform): fix transform, reprocess DLQ
4. If truly bad source data: notify source team, discard DLQ after investigation
5. Clear DLQ after resolution (do not let it grow unbounded)
```
