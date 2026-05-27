# Cold-Start Behavior — Platform Data Pipeline

Defines how the data pipeline platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/data/core.md` missing.
Detection: File read returns 404.
Action: Log warning. Apply continues without delivery semantics, idempotency patterns, and PII handling rules. Decompose proceeds.
Do NOT: Fail the session.

## Absent: conditional framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/data/dbt.md` (or spark/airflow) absent when framework is detected.
Detection: Detected via `dbt_project.yml` / `pyspark` in requirements / Airflow DAG imports but file not found.
Action: Proceed without file. Log: "Data framework file not found: [path]."

## Absent: security reference files

Condition: `modules/l3/data-pipeline/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic controls. PII masking requirement is still enforced as a platform invariant.

## Absent: spec-template files

Condition: `modules/l3/data-pipeline/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `framework` | Not declared — Apply detects from repo signals |
| `delivery_semantics` | Not declared — Specify must elicit (at-least-once / exactly-once) |
| `idempotency` | Required — Specify must declare idempotency strategy before Executor writes pipeline code |
| `pii_fields` | Not declared — Specify must enumerate PII fields and masking strategy |
| `schema_evolution` | Not declared — Specify must declare migration strategy |
| `data_quality_gates` | Not declared — Specify must declare; pipeline without quality gates is a FLAG |
| `backfill_strategy` | Not declared — Specify must elicit for historical data processing |

Idempotency is a pipeline platform invariant — enforced even without framework files.
