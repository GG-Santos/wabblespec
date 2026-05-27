# Platform: Data Pipeline

ETL, data processing, and workflow orchestration target. Activates when Recipe identifies a data pipeline, batch job, or stream processing system as the primary build target.

**Skill:** `modules/l3/data-pipeline/SKILL.md`

## What makes Data Pipeline different

| Concern | Data Pipeline approach |
|---------|----------------------|
| Idempotency | Every pipeline stage declares idempotency strategy — re-running must be safe |
| Backpressure | Stream stages declare backpressure handling — no unbounded queues |
| Schema evolution | Input and output schemas versioned; breaking schema changes declared |
| Observability | Metrics, logging, and alerting declared per stage |
| Checkpointing | Long-running pipelines declare checkpoint strategy for resume-on-failure |
| Data quality | Validation rules declared per input field — what happens on invalid data |
| Ordering | Event ordering guarantees declared (at-least-once, exactly-once, ordered) |

## Platform-specific spec sections

- Pipeline topology: source → transform stages → sink, with data shapes at each boundary
- Idempotency strategy: how re-runs are detected and handled safely
- Error handling: what happens to malformed records (dead-letter queue, skip, fail)
- Checkpoint and resume: how progress is saved and recovered
- SLA and latency targets: declared per pipeline
- Data lineage: which upstream sources feed each output artifact

## Security controls loaded

- PII handling: PII fields identified and redaction/masking strategy declared
- Secrets: source credentials in secrets manager — not in pipeline config files
- Data access control: which systems can read pipeline outputs declared
- Audit logging: data access events logged for PII-containing pipelines

## Gateway interaction

Data pipeline targets typically activate:
- `gateway-security` — always if handling PII or sensitive data
- `gateway-engineering` — always (schema contracts, idempotency surface)
- `gateway-ai` — if pipeline includes LLM inference stages
