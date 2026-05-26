# Build Toolchain — Data Pipeline

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Language and runtime

**Language:** [ ] Python  [ ] SQL (dbt)  [ ] Scala (Spark)  [ ] Java  [ ] Other: ___
**Runtime version:** `___ UNDECLARED` _(pin exact version — data pipelines run on scheduled infra, not dev machines)_

---

## Orchestration

**Orchestrator:** [ ] Apache Airflow  [ ] Prefect  [ ] Dagster  [ ] AWS Step Functions  [ ] dbt Cloud  [ ] Cron  [ ] Other: ___
**DAG/flow location:** `___ UNDECLARED` (e.g., `dags/`, `flows/`)
**Schedule cadence:** `___ UNDECLARED` (e.g., `0 2 * * *` — nightly at 02:00 UTC)

---

## Build / packaging

**Build tool:** [ ] Poetry  [ ] pip + requirements.txt  [ ] Docker image  [ ] Maven  [ ] Other: ___
**Dependency lock file:** [ ] poetry.lock  [ ] requirements.txt pinned  [ ] Other: ___

---

## Test runner

**Unit:** [ ] pytest  [ ] unittest  [ ] Other: ___
**Data quality tests:** [ ] dbt test  [ ] Great Expectations  [ ] Soda  [ ] Custom DQ assertions  [ ] Other: ___
**Coverage threshold:** 80% statement (pipeline logic); DQ tests run on every execution

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] CircleCI  [ ] Databricks CI  [ ] Other: ___

**Required CI gates:**
- [ ] Lint (Ruff / flake8)
- [ ] Type check (mypy)
- [ ] Unit tests
- [ ] DQ schema validation tests
- [ ] Idempotency test (run-twice-same-output check)
- [ ] Dependency audit (pip-audit)
- [ ] DAG parse check (no import errors at load time)

---

## Data infrastructure

**Source systems:** `___ UNDECLARED` _(list data sources: Postgres, S3, Kafka, Snowflake, etc.)_
**Sink systems:** `___ UNDECLARED` _(list data sinks: data warehouse, S3, API, etc.)_
**Transformation layer:** [ ] dbt  [ ] Spark SQL  [ ] pandas  [ ] PySpark  [ ] Other: ___
**Storage:** [ ] Snowflake  [ ] BigQuery  [ ] Redshift  [ ] Delta Lake  [ ] Iceberg  [ ] Other: ___

---

## Deployment

**Deployment target:** [ ] Managed Airflow (MWAA/Cloud Composer)  [ ] Self-hosted Airflow  [ ] Databricks  [ ] Prefect Cloud  [ ] Other: ___
**Environment promotion:** [ ] dev → staging → production  [ ] dev → production (declare if no staging)
**Deploy trigger:** [ ] merge to main  [ ] tag push  [ ] manual  [ ] Other: ___

---

## Observability

**Metrics:** [ ] Airflow metrics → Prometheus  [ ] Datadog  [ ] CloudWatch  [ ] Other: ___
**Logs:** [ ] CloudWatch Logs  [ ] Datadog Logs  [ ] Elastic  [ ] Other: ___
**Alerting on:** [ ] SLA breach  [ ] DLQ count threshold  [ ] job failure  [ ] data freshness  [ ] Other: ___

_(Monitor generates batch-SLA, DLQ-rate, and throughput alerts — not request-latency configs.)_

---

## Notes

_Data classification, PII handling procedures, retention policies:_
