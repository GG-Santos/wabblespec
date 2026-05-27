# Data/Pipeline Security — Platform Controls

These controls apply to all Data/Pipeline targets. Enforced by Verifier via `verification/gates.md`.

---

## Control 1: Credentials from Secrets Manager

**Rule:** No credentials, passwords, API keys, or connection strings in code, config files committed to version control, or plain environment variables.

**Acceptable:**
```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/pipeline/db-password')
password = secret['SecretString']
```

**Prohibited:**
- `password = "hardcoded123"` in any file
- `DB_PASSWORD=plaintext` in `.env` committed to repo
- Credentials in Airflow connections stored as plaintext (use Secrets Backend)

**Enforcement:** Pre-commit hook scans for credential patterns. CI runs `detect-secrets` or `trufflehog`.

---

## Control 2: Parameterized Queries Only

**Rule:** All database queries use parameterized queries (placeholders). No string interpolation or concatenation to build SQL.

**Required:**
```python
cursor.execute("SELECT * FROM events WHERE date = %s AND user_id = %s", (date, user_id))
```

**Prohibited:**
```python
cursor.execute(f"SELECT * FROM events WHERE date = '{date}'")  # injection risk
cursor.execute("SELECT * FROM events WHERE date = '" + date + "'")  # injection risk
```

**Applies to:** psycopg2, SQLAlchemy, Spark SQL, BigQuery, Redshift, all SQL interfaces.

---

## Control 3: PII Masking in Logs

**Rule:** No PII values in any log output at any log level.

**Pattern:**
```python
import re

PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]'),
    # add patterns per declared PII fields
]

def safe_log(message: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        message = re.sub(pattern, replacement, message)
    return message
```

**Enforcement:** Code review of all log statements. PII fields from design-document.md reviewed against log output.

---

## Control 4: Least-Privilege Service Account

**Rule:** Each pipeline has its own service account with minimum required permissions. No shared credentials between pipelines.

**Source permissions:** `SELECT` on declared tables only. No `CREATE`, `DROP`, `UPDATE` on source.
**Destination permissions:** `INSERT`, `UPDATE`, `DELETE` on output tables only. No DDL without explicit justification.
**S3/GCS permissions:** `GetObject` + `PutObject` on specific path prefix only. No `ListBucket` on bucket root without justification.

**Enforcement:** IAM policy reviewed as part of Gate 7 (security controls). Principle: if the pipeline doesn't need it, it doesn't have it.

---

## Control 5: Intermediate Storage Security

**Rule:** All intermediate/temp storage has the same access controls and encryption as the final destination.

**S3:**
- No public access (bucket + object level)
- Server-side encryption enabled (SSE-S3 or SSE-KMS)
- Lifecycle policy: temp prefixes deleted after ___ days

**Temp tables (Redshift/BigQuery/Snowflake):**
- In pipeline-owned schema with appropriate grants
- Dropped in `finally` block (not only on success)

---

## Control 6: Environment Guard

**Rule:** Pipeline must validate its target environment at startup and refuse to run if environment is ambiguous.

```python
import os

PIPELINE_ENV = os.environ.get('PIPELINE_ENV')
if not PIPELINE_ENV:
    raise RuntimeError("PIPELINE_ENV not set — refusing to start")
if PIPELINE_ENV not in ('development', 'staging', 'production'):
    raise RuntimeError(f"Unknown PIPELINE_ENV: {PIPELINE_ENV}")

DESTINATIONS = {
    'development': 's3://dev-bucket/pipeline/',
    'staging': 's3://staging-bucket/pipeline/',
    'production': 's3://prod-bucket/pipeline/',
}
destination = DESTINATIONS[PIPELINE_ENV]
logger.info(f"Pipeline target: {destination}")  # always log destination on startup
```

---

## Control 7: DQ Gate is a Hard Stop

**Rule:** Data quality assertion failures must halt the pipeline. Partial or bad data must not reach the destination.

**Implementation:** DQ assertions run before any write to the destination. If any assertion fails:
1. No data written to destination
2. Records routed to DLQ (if streaming) or job fails (if batch)
3. Alert fired
4. Requires manual review before retry

**Prohibited:** Logging DQ failures and continuing ("soft failure" mode). Bad data reaching consumers is the primary failure mode in data pipelines.

---

## Control 8: Dependency Audit Gate

**Rule:** `pip-audit` or equivalent must pass with zero critical/high findings before any pipeline runs in production.

```bash
pip-audit -r requirements.txt --vulnerability-service osv
# Must exit 0 with zero critical/high findings
```

**Waiver:** Critical findings with no available fix must be documented with: CVE ID, impact assessment, and timeline for resolution.
