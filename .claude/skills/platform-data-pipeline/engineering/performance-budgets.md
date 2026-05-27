# Data/Pipeline Engineering — Performance Budgets

## Latency Budgets

Declare based on pipeline type. These are defaults — override in design-document if justified.

| Pipeline type | End-to-end latency budget | Measurement |
|---|---|---|
| Real-time streaming | < 5 seconds (event time to destination) | Kafka consumer lag + processing time |
| Near-real-time | < 60 seconds | Consumer group lag metrics |
| Micro-batch | < 5 minutes | Job completion time |
| Hourly batch | < 30 minutes | Airflow task duration |
| Daily batch | < 2 hours | Airflow DAG duration |

**Measurement:** Kafka consumer lag (`kafka-consumer-groups.sh --describe`) + output row freshness (max `event_at` in destination vs wall clock).

---

## Throughput Budgets

| Metric | Budget | Notes |
|---|---|---|
| Records per second (streaming) | ___ RPS | Declare based on peak load |
| Records per hour (batch) | ___ M records/hour | Size cluster accordingly |
| Data volume per run | ___ GB/day | Cost + storage planning |

**Headroom:** Size for 2× current peak. Data volume grows; pipelines that are right-sized today are bottlenecked tomorrow.

---

## Compute Cost Budgets

| Run type | Budget | Cluster size |
|---|---|---|
| Daily batch | < $___ per run | ___ nodes × ___ cores |
| Streaming (monthly) | < $___ / month | ___ CUs or stream units |
| Backfill (1 year) | < $___ total | Document before triggering |

**Cost monitoring:** Alert when actual compute cost exceeds 150% of budget for a given run.

**Spot/preemptible instances:** Batch jobs should use spot instances where retry-safe. Streaming jobs require on-demand for stability.

---

## Data Freshness SLA

| Output table/topic | Max acceptable age | Alert at |
|---|---|---|
| `daily_metrics` | 2 hours after midnight UTC | 3 hours after midnight |
| `user_events` (streaming) | 60 seconds | 120 seconds |

**Freshness check:** `SELECT MAX(event_at) FROM output_table WHERE date = current_date`. Alert if behind SLA.

---

## Resource Limits

**Memory:**
| Component | Memory limit | OOM behavior |
|---|---|---|
| Spark executor | ___ GB | Spark kills task, retries on another executor |
| Flink task manager | ___ GB | Checkpoint + restart |
| Python worker | ___ GB | OOM kill — declares batch size limit |

**State size (streaming):**
- Deduplication window: < ___ GB in state backend
- Join state: < ___ GB in RocksDB
- Alert when state size approaches 80% of limit

**Partition size:**
- Target: 128–512 MB per Spark partition
- Too small (< 10 MB): shuffle overhead dominates
- Too large (> 1 GB): executor memory pressure, slow GC

---

## Pipeline Duration Alerting

| Pipeline | Expected duration | Alert at |
|---|---|---|
| `<pipeline-name>` daily | ___ minutes | ___ minutes (1.5× expected) |

**SLA breach:** If pipeline does not complete within ___ minutes of scheduled start, page on-call.

**Long-running guard:** Every batch job must have a maximum runtime declared (`execution_timeout` in Airflow, `timeout` in Prefect). No infinite-running pipelines.
