# Data/Pipeline Engineering — Build Toolchain

## Python Pipelines (Airflow, Prefect, Dagster, PySpark)

**Package management:** `uv` (preferred) or `pip` with pinned `requirements.txt`.

**Project structure:**
```
pipeline/
  src/
    <pipeline_name>/
      __init__.py
      extract.py
      transform.py
      load.py
      quality.py
  tests/
    unit/
    integration/
  dags/          (Airflow) or flows/ (Prefect) or assets/ (Dagster)
  requirements.txt
  pyproject.toml
```

**Testing:**
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (require test data and test destination)
pytest tests/integration/ -v --tb=short

# Type check
mypy src/ --strict

# Lint
ruff check src/
```

---

## dbt

**Version:** Pin dbt-core and adapter versions in `requirements.txt`.

**Project structure:**
```
dbt_project.yml
models/
  staging/        # raw → clean
  intermediate/   # clean → joined
  marts/          # joined → business metrics
tests/            # data quality tests
seeds/            # reference data CSVs
snapshots/        # slowly changing dimensions
macros/
```

**Key commands:**
```bash
dbt run              # run all models
dbt test             # run all data quality tests
dbt run --select staging.+  # run staging + all downstream
dbt test --select staging   # test only staging models
dbt source freshness        # check source staleness
dbt docs generate && dbt docs serve  # generate + serve docs
```

**CI pipeline:**
```bash
dbt run --target ci --full-refresh
dbt test --target ci
```

---

## Spark (PySpark / Scala)

**Build tool:** Maven (Scala) or poetry/uv (PySpark).

**Submit:**
```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 10 \
  --executor-memory 4g \
  --executor-cores 2 \
  jobs/transform_job.py \
  --date 2024-01-15
```

**Docker image for Spark:**
```dockerfile
FROM apache/spark:3.5.0-python3
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/
```

---

## Streaming (Kafka / Flink)

**Kafka consumer:**
```python
from confluent_kafka import Consumer, KafkaError

consumer = Consumer({
    'bootstrap.servers': os.environ['KAFKA_BROKERS'],
    'group.id': '<pipeline-name>',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,  # manual commit after processing
})
```

**Flink:**
```bash
flink run \
  --jobmanager yarn-cluster \
  --parallelism 8 \
  target/<job>.jar \
  --kafka-brokers $KAFKA_BROKERS \
  --output-path s3://$OUTPUT_BUCKET/
```

---

## CI/CD Pipeline

```yaml
# CI: validate
test:
  script:
    - pip install -r requirements-dev.txt
    - pytest tests/unit/ -v
    - mypy src/ --strict
    - ruff check src/
    - dbt parse  # validate dbt project structure

# CI: integration (on main branch only)
integration-test:
  script:
    - pytest tests/integration/ -v
    - dbt run --target ci --full-refresh
    - dbt test --target ci

# Deploy: promote to production environment
deploy:
  script:
    - dbt run --target prod
    # or: upload DAG files to Airflow
    # or: submit Spark job to cluster
```

---

## Environment Management

| Environment | Purpose | Data | Trigger |
|---|---|---|---|
| development | Local dev + unit tests | Synthetic or sampled | Manual |
| CI | Automated validation | Sampled or synthetic | PR + main |
| staging | Integration test | Copy of prod (anonymized) | Before release |
| production | Live | Real data | Scheduled or event |

**Never run production pipelines with development credentials.** Environment-specific credentials in secrets manager.
