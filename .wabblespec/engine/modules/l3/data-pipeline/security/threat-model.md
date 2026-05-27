# Data/Pipeline Security — Threat Model

## Threat Surface

Data pipelines process potentially sensitive data at scale, often with broad read access to production databases and broad write access to data warehouses. A compromised pipeline can exfiltrate large volumes of data or corrupt downstream analytics silently.

1. **Credential exposure in code or logs** — database passwords, API keys, or cloud credentials hardcoded or logged
2. **SQL injection via pipeline parameters** — user-supplied values interpolated into SQL queries
3. **PII in pipeline logs or intermediate storage** — personal data exposed in log files, error messages, or temp storage
4. **Overprivileged service accounts** — pipeline runs with admin credentials when read-only would suffice
5. **Insecure intermediate storage** — temp files or S3 buckets with sensitive data publicly accessible
6. **Data exfiltration via misconfigured destination** — data written to wrong destination due to environment misconfiguration
7. **Supply chain in pipeline dependencies** — malicious PyPI package in pipeline environment

---

## Threat 1: Credential Exposure

**Description:** Database passwords, API tokens, or cloud credentials appear in pipeline code (hardcoded), environment variable dumps in logs, or error messages.

**Attack scenarios:**
```python
# Hardcoded in code — visible in git history:
conn = psycopg2.connect("postgresql://user:PASSWORD@host/db")

# Logged accidentally:
logger.debug(f"Connection string: {conn_string}")  # exposes password
```

**Mitigations:**
- All credentials from secrets manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager)
- Never in environment variables directly on servers (use secrets manager injection)
- Never in code — not even in "config" files committed to repo
- Logging: scrub connection strings, credential patterns before log output
- `.gitignore` and pre-commit hooks block credential patterns from commits

---

## Threat 2: SQL Injection via Pipeline Parameters

**Description:** Pipeline accepts run parameters (date range, entity IDs, filter values) that are interpolated into SQL queries without parameterization.

**Attack scenario:**
```python
# Vulnerable:
date_param = request.args.get('date')
query = f"SELECT * FROM events WHERE date = '{date_param}'"
# date_param = "2024-01-01' UNION SELECT password FROM users --"
```

**Mitigations:**
- All pipeline parameters validated and typed before use
- SQL queries use parameterized queries, never string interpolation
- Date parameters parsed and validated: `datetime.strptime(date_param, '%Y-%m-%d')`
- Allowlist validation for enum parameters (`if status not in VALID_STATUSES: raise`)

---

## Threat 3: PII in Logs and Intermediate Storage

**Description:** Pipeline logs contain personal data (emails, names, IPs) in debug output. Intermediate S3 files or temp tables contain unmasked PII accessible to anyone with bucket access.

**Mitigations:**
- Identify all PII fields in design-document.md
- PII masked/hashed before logging at any level
- Intermediate storage (temp S3 paths, staging tables) has same access controls as final destination
- Temp files cleaned up in `finally` block — not only on success
- Log sampling: never log full records in production (they may contain PII)

---

## Threat 4: Overprivileged Service Accounts

**Description:** Pipeline service account has admin database access when it only needs to read specific tables. A compromised pipeline can access all tables, not just the ones it needs.

**Mitigations:**
- Source credentials: read-only access to specific tables/schemas only
- Destination credentials: write access to specific schema/dataset only
- Separate service accounts for each pipeline (not a shared data-team account)
- IAM policies follow least privilege: specific S3 paths, specific Kafka topics, specific BigQuery datasets
- Audit credentials quarterly: remove access not actively used

---

## Threat 5: Insecure Intermediate Storage

**Description:** Pipeline writes data to S3 temp path that is publicly accessible or accessible to unintended teams. Sensitive intermediate data is exposed.

**Mitigations:**
- S3 bucket blocks public access (`BlockPublicAcls: true`, `BlockPublicPolicy: true`)
- Temp paths under pipeline-specific prefix with IAM-controlled access
- Intermediate data encrypted at rest (S3 SSE-S3 or SSE-KMS)
- Temp files have TTL — lifecycle policy deletes after ___ days
- Verify bucket policy before first use in production

---

## Threat 6: Environment Misconfiguration → Wrong Destination

**Description:** Pipeline configured for staging accidentally runs against production destination (or vice versa), corrupting data or exposing production data to staging environment.

**Mitigations:**
- Destination URL always constructed from environment-specific config, not hardcoded
- `PIPELINE_ENV` environment variable required at startup — pipeline fails without it
- Production credentials never available in staging environment
- Dry-run mode: `--dry-run` flag prints destination without writing; use in CI
- Destination validation: before any write, print destination and log at INFO level

---

## Threat 7: Supply Chain in Pipeline Dependencies

**Description:** PyPI package used by pipeline is compromised and exfiltrates data or credentials from the pipeline environment.

**Mitigations:**
- `requirements.txt` pins exact versions (`==`) not ranges
- `pip-audit` or `safety` run in CI — zero critical/high findings gate
- Dependency review before adding new packages
- Private PyPI mirror for regulated environments (only audited packages available)
- Minimize dependency count — each dep is an attack surface on a machine with broad data access
