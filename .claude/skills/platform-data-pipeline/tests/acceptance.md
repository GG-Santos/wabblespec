# Platform Data/Pipeline — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Data/Pipeline as the primary target,
When platform-data-pipeline is invoked,
Then it surfaces: "platform-data-pipeline requires Recipe to have identified Data/Pipeline as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Data/Pipeline as the primary target,
When platform-data-pipeline activates,
Then the activation sequence completes in order: spec-template load → pipeline type detection → engineering load → security load → Verifier gate registration → receipt write.

## Pipeline type routing: orchestrated batch

Given Airflow DAGs, Prefect flows, or Dagster assets are detected,
When platform-data-pipeline detects the pipeline type,
Then `.wabblespec/engine/shared/dev/frameworks/data/airflow.md` is loaded.
Then orchestrated batch concerns are activated.

## Pipeline type routing: dbt

Given dbt models are detected,
When platform-data-pipeline detects the pipeline type,
Then `.wabblespec/engine/shared/dev/frameworks/data/dbt.md` is loaded.
Then SQL transformation concerns are activated.

## Pipeline type routing: Spark

Given Spark batch jobs are detected,
When platform-data-pipeline detects the pipeline type,
Then `.wabblespec/engine/shared/dev/frameworks/data/spark.md` is loaded.

## Data/Pipeline-specific concerns injected into spec

Given platform-data-pipeline is active,
When spec context is assembled,
Then idempotency is declared: pipelines must handle replay on failure without duplicating records.
Then schema evolution strategy is declared: breaking schema changes must not break downstream consumers silently.
Then backfill design is addressed: historical reprocessing path is designed explicitly.
Then data quality assertion gates are declared (row counts, schema validity, DQ assertions).
Then latency class is declared: batch (minutes-hours) or streaming (ms-seconds).
Then delivery guarantee is declared: exactly-once or at-least-once semantics.
Then operational runbook for pipeline failure is required.
Then PII handling in data stores is addressed.

## Silent bad data is the primary failure mode

Given platform-data-pipeline is active,
When spec context is assembled,
Then the spec acknowledges that silent bad data is worse than a crash.
Then data quality assertions are required — pipeline success is not defined by exit code alone.

## Observability declared (not HTTP status codes)

Given platform-data-pipeline is active,
When spec context is assembled,
Then observability is declared as: row counts, lag metrics, DQ assertion results — not HTTP status codes.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-data-pipeline attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-data-pipeline run,
Then platform-data-pipeline does not treat success as exit code 0 alone — data quality assertions are required.
Then platform-data-pipeline does not omit idempotency design.
Then platform-data-pipeline does not omit schema evolution strategy.

## Receipt fields

Given any successful platform-data-pipeline activation,
Then a receipt is written to `.wabblespec/state/receipts/platform-data-pipeline-<timestamp>.json`.
Then the receipt contains: platform, pipeline_type_detected, idempotency_declared, schema_evolution_declared, backfill_designed, dq_gates_declared, delivery_guarantee, gates_registered, capability_handoff.
