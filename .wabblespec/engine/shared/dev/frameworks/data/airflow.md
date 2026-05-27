# Apache Airflow

Loaded by Apply when Airflow DAGs or Prefect flows are detected.

## Version baseline

Airflow 2.8+. Declare: deployment (Composer, MWAA, Astronomer, self-hosted); executor type (Kubernetes, Celery, Local).

## DAG structure

```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(
    schedule="0 6 * * *",          # 6am UTC daily
    start_date=datetime(2026, 1, 1),
    catchup=False,                  # do not backfill past runs
    max_active_runs=1,              # prevent concurrent runs
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(hours=2),
    },
    tags=["domain", "frequency"],
)
def my_pipeline():
    
    @task
    def extract() -> dict:
        # Extract data; return serializable result
        return {"records": [...]}

    @task
    def transform(data: dict) -> dict:
        # Transform; XCom passes data between tasks
        return {"processed": [...]}

    @task
    def load(data: dict) -> None:
        # Load to destination
        pass
    
    # Dependency declaration
    raw = extract()
    transformed = transform(raw)
    load(transformed)

my_pipeline()
```

## Scheduling

| Pattern | Cron |
|---|---|
| Daily at midnight UTC | `"0 0 * * *"` |
| Hourly | `"@hourly"` or `"0 * * * *"` |
| Weekly on Sunday | `"0 0 * * 0"` |
| No schedule (trigger only) | `None` |

`catchup=False`: do not create historical runs for dates before start_date. Always declare this unless backfill is intended.

## XCom — data passing between tasks

XCom (cross-communication) passes data between tasks via Airflow's metadata database.

Limits:
- Max XCom value: 48KB (SQLite/MySQL) — avoid for large data
- For large data: write to S3/GCS/database and pass the path/key via XCom

```python
@task
def extract() -> str:
    # Write large data to S3, return path
    s3_path = upload_to_s3(data)
    return s3_path  # pass path, not data

@task
def transform(s3_path: str) -> str:
    data = read_from_s3(s3_path)
    # process...
    return output_path
```

## Connections and variables

```python
# Connection: configured in Airflow UI or environment variable
from airflow.hooks.base import BaseHook

conn = BaseHook.get_connection("my_postgres_conn")
# conn.host, conn.login, conn.password

# Variable: key-value store in Airflow metadata DB
from airflow.models import Variable

bucket = Variable.get("data_bucket", default_var="default-bucket")
```

Do not hardcode credentials in DAG files. Always use connections and variables.

## Error handling and alerting

```python
from airflow.utils.email import send_email

def on_failure_callback(context):
    send_email(
        to="team@example.com",
        subject=f"DAG Failed: {context['dag'].dag_id}",
        html_content=f"Task {context['task_instance_key_str']} failed."
    )

@dag(
    on_failure_callback=on_failure_callback,
    ...
)
```

Spec must declare: alert recipients, which failures page, which auto-retry.

## Backfill and reprocessing

```bash
# Trigger backfill for a date range
airflow dags backfill --start-date 2026-01-01 --end-date 2026-01-31 my_pipeline
```

Spec must declare: how to safely backfill without double-counting; whether the pipeline is idempotent for a given execution_date.

## Testing

```python
# Unit test tasks without running the DAG
from airflow.models import DagBag

def test_dag_loads_without_errors():
    dagbag = DagBag()
    dag = dagbag.get_dag("my_pipeline")
    assert dag is not None
    assert len(dagbag.import_errors) == 0

def test_extract_task(mocker):
    # Mock external calls
    mocker.patch("my_dag.upload_to_s3", return_value="s3://bucket/key")
    result = extract.function()
    assert result.startswith("s3://")
```

Pytest + mocks for task logic. Integration tests in a local or CI Airflow environment.
