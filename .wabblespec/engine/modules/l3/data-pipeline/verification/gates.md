# Data/Pipeline Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Idempotency Verification

**Check:** Running the pipeline twice on the same input produces identical output (no duplicates).

**Method:**
```bash
# Run 1
python pipeline.py --date 2024-01-15 --env test
COUNT_1=$(query "SELECT COUNT(*) FROM output WHERE date='2024-01-15'")

# Run 2 (same input)
python pipeline.py --date 2024-01-15 --env test
COUNT_2=$(query "SELECT COUNT(*) FROM output WHERE date='2024-01-15'")

[ "$COUNT_1" = "$COUNT_2" ] || echo "FAIL: idempotency violation"
```

**Pass:** Identical row counts on both runs. No duplicates by primary key.
**Fail:** Row count differs between runs, or duplicate primary keys in output.

---

## Gate 2: Data Quality Assertions Pass

**Check:** All declared DQ assertions pass on test data.

**Method:**
```bash
# Great Expectations:
great_expectations checkpoint run test_checkpoint
# dbt:
dbt test --target ci
# Custom:
python run_dq_assertions.py --env test
```

**Pass:** All assertions pass. DLQ is empty after test run.
**Fail:** Any assertion fails. Any records in DLQ from test run (unless DLQ behavior is declared for those records).

---

## Gate 3: Schema Evolution Backward Compatibility

**Check:** Pipeline handles old schema (missing new fields) without error.

**Method:**
```bash
# Run pipeline against old-schema sample data:
python pipeline.py --input test_data/old_schema_sample.json --env test
# Must complete without error
# Output schema must match declared output schema
```

**Pass:** Pipeline completes on old-schema data. No KeyError or AttributeError for new fields.
**Fail:** Pipeline fails or raises exception when processing records missing new fields.

---

## Gate 4: No Credentials in Code or Config

**Check:** No hardcoded credentials, passwords, or API keys in any file.

**Method:**
```bash
detect-secrets scan --baseline .secrets.baseline
# or:
trufflehog filesystem . --only-verified
# Must return zero findings
```

**Pass:** Zero credential patterns found in codebase.
**Fail:** Any hardcoded credential, connection string with password, or API key found.

---

## Gate 5: Parameterized Queries Only

**Check:** No SQL string interpolation or concatenation.

**Method:**
```bash
grep -rn "f\"SELECT\|f'SELECT\|\"SELECT.*%s\".*%.*format\|\"SELECT.*\+.*\"" src/
# Review each match — string-interpolated SQL is a FAIL
grep -rn "\.execute(f\"\|\.execute(\".*\.format\|\.execute(\".*\+" src/
# Must return zero matches (or reviewed matches show safe usage)
```

**Pass:** All SQL uses parameterized placeholders. No string interpolation.
**Fail:** Any SQL query built via string interpolation or concatenation with external data.

---

## Gate 6: PII Handling Verified

**Check:** PII fields declared in design-document.md are masked/hashed before storage and do not appear in logs.

**Method:**
```bash
# Run pipeline on sample data containing PII
python pipeline.py --input test_data/pii_sample.json --env test 2>&1 | tee pipeline.log

# Check logs for PII patterns:
grep -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' pipeline.log
# Must return zero email matches

# Check output for declared masked fields:
query "SELECT email FROM output LIMIT 10"
# emails must be hashed or absent per design-document declaration
```

**Pass:** No PII values in logs. Output PII fields match declared handling (hashed, masked, or absent).
**Fail:** Any PII value in log output. Any PII field stored in clear when design-document declares masking.

---

## Gate 7: Security Controls Verified

**Check:** Credential handling, least-privilege service account, environment guard, and dependency audit.

**Method:**
```bash
# Dependency audit:
pip-audit -r requirements.txt
# Must exit 0 with zero critical/high findings

# Environment guard:
python pipeline.py  # without PIPELINE_ENV
# Must fail with clear error message

# Verify destination logged on startup:
PIPELINE_ENV=test python pipeline.py 2>&1 | grep "Pipeline target"
# Must show test destination, not production
```

**Pass:** pip-audit zero findings. Pipeline fails without PIPELINE_ENV. Destination logged on startup.
**Fail:** Any critical/high dependency finding. Pipeline starts without PIPELINE_ENV. Destination not logged.

---

## Gate 8: Backfill Idempotency

**Check:** Backfill produces same output as incremental run and is idempotent.

**Method:**
```bash
# Backfill 3 days:
python pipeline.py --mode backfill --start 2024-01-01 --end 2024-01-03 --env test

# Record counts per day
for date in 2024-01-01 2024-01-02 2024-01-03; do
  query "SELECT '$date', COUNT(*) FROM output WHERE date='$date'"
done

# Run backfill again:
python pipeline.py --mode backfill --start 2024-01-01 --end 2024-01-03 --env test

# Compare — must be identical
```

**Pass:** Same row counts on second backfill run. No missing days.
**Fail:** Counts differ between runs, or any day missing from output.

---

## Gate 9: Performance Within Budget

**Check:** Pipeline completes within declared latency budget on representative data volume.

**Method:**
```bash
# Time the pipeline on representative sample:
time python pipeline.py --date 2024-01-15 --env staging
# Or for streaming: measure consumer lag after 5 minutes of operation

# Compare to declared budget in performance-budgets.md
```

**Pass:** Completion time within declared budget. Streaming lag within declared target.
**Fail:** Exceeds latency budget on representative data volume.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Idempotency — no duplicates on retry | Yes |
| 2 | Data quality assertions pass | Yes |
| 3 | Schema backward compatibility | Yes |
| 4 | No credentials in code | Yes |
| 5 | Parameterized queries only | Yes |
| 6 | PII handling verified | Yes |
| 7 | Security controls (env guard, audit, least-priv) | Yes |
| 8 | Backfill idempotency | Yes |
| 9 | Performance within budget | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
