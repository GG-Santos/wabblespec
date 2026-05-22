# Data/Pipeline Engineering — Platform Verification

How to run and interpret the data pipeline verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# Unit tests
pytest tests/unit/ -v

# Type check
mypy src/ --strict

# Lint
ruff check src/

# dbt validation
dbt parse
dbt run --target ci --full-refresh
dbt test --target ci

# Integration test with sample data
pytest tests/integration/ -v
```

---

## Idempotency Verification

```bash
# Run pipeline twice on same input, compare output row counts:
python pipeline.py --date 2024-01-15 --mode test
ROW_COUNT_1=$(query "SELECT COUNT(*) FROM output WHERE date='2024-01-15'")

python pipeline.py --date 2024-01-15 --mode test  # run again
ROW_COUNT_2=$(query "SELECT COUNT(*) FROM output WHERE date='2024-01-15'")

if [ "$ROW_COUNT_1" != "$ROW_COUNT_2" ]; then
  echo "FAIL: idempotency violation — counts differ"
fi
```

---

## Data Quality Assertion Verification

```bash
# Great Expectations:
great_expectations checkpoint run <checkpoint_name>
# Must return: "Validation succeeded" for all suites

# dbt tests:
dbt test --target ci
# Must return: 0 failures

# Check DLQ is empty after test run:
aws s3 ls s3://<bucket>/dlq/ --recursive | wc -l
# Should be 0 for clean test data
```

---

## Schema Evolution Verification

```bash
# When adding a new column — verify pipeline handles old schema:
python test_backward_compat.py --schema-version old --data test_data/old_schema_sample.json
# Must complete without error

# Verify new schema output is valid:
python test_schema.py --output output/test_run/ --expected-schema schemas/output_v2.json
# Must return: schema valid
```

---

## Backfill Verification

```bash
# Run backfill for 3 days:
python pipeline.py --mode backfill --start 2024-01-01 --end 2024-01-03

# Run again (idempotency check):
python pipeline.py --mode backfill --start 2024-01-01 --end 2024-01-03

# Compare counts for each day:
for date in 2024-01-01 2024-01-02 2024-01-03; do
  query "SELECT COUNT(*) FROM output WHERE date='$date'"
done
# Both runs must produce identical counts for each date
```

---

## Interpreting Gate Failures

**Gate FAIL — idempotency violation:**
- Find all `INSERT` operations — replace with `UPSERT` or partition overwrite
- Check for append-only writes without deduplication
- Add deduplication step before write

**Gate FAIL — DQ assertion fails on test data:**
- Examine DLQ records to understand failure pattern
- Is the test data realistic? If not: fix test data
- Is the assertion too strict? Adjust threshold with justification
- Is there a real data quality problem in source? Fix source

**Gate FAIL — schema backward compatibility:**
- Run old schema sample through new pipeline
- Find the code that fails on missing field
- Add `record.get('new_field', default_value)` pattern
- Never assume fields exist — always use `.get()` with a default

**Gate FAIL — performance (exceeds latency budget):**
- Profile: add timing to each stage, find bottleneck
- Check partition count (too few = slow; too many = overhead)
- Check join strategy (broadcast small tables)
- Check data skew (one partition much larger than others)
