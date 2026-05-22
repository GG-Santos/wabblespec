# WabbleSpec v6.1 — Engineering

**Gateway:** Engineering
**Layer:** L4 Capability
**Tier:** 1 — CRITICAL ROUTING
**Document scope:** Engineering gateway — cross-cutting CI/CD, architecture review, reliability, systems design standards

---

## Overview

The Engineering gateway owns cross-cutting technical standards that apply regardless of build target: architecture review, ADR policy, CI/CD pipeline declaration, reliability principles, and systems design patterns. It does not own target-specific build toolchains or performance budgets — those live in L3 platform packages.

**In scope (cross-cutting):**
- Architecture review (ADR, C4 model, coupling/cohesion analysis)
- CI/CD pipeline declaration (branch strategy, deployment strategy, rollback)
- Reliability principles (SLO, error budget, circuit breaker, chaos engineering scope)
- Systems design standards (CAP theorem, idempotency, backpressure, data contracts)
- Test coverage policy (coverage floors, integration, E2E, contract tests)

**Explicitly not in scope (owned by L3 platform packages):**
- Build toolchain configuration (platform engineering directories)
- Target-specific performance budgets
- Hardware integration (IoT platform)
- Platform-specific build pipeline implementation

---

## Gateway Structure

```
.wabblespec/gateways/engineering/
  SKILL.md
  skill-rules.json
  references/
    architecture-review.md
    ci-cd.md
    reliability.md
    systems-design.md
  rules/
    adr-policy.md
    test-coverage-policy.md
  evaluations/
  schemas/
    receipt.schema.json
```

---

## Activation

`skill-rules.json` triggers Engineering gateway on:
- P2 Systems Design stage — architecture review always runs
- P3 Technical Spec — cross-cutting engineering standards applied
- BREAKING spec changes — Engineering review required before Executor proceeds
- Explicit `/engineering` command

---

## Architecture Review

**Reference:** `references/architecture-review.md`

### ADR (Architecture Decision Record)

Required for any decision with implications beyond 6 months or affecting multiple modules/services.

Required triggers:
- Framework or language selection
- Database selection (type and product)
- Auth mechanism selection
- Deployment strategy selection
- Any decision that is hard to reverse

ADR format:

```markdown
# ADR-<NNN> — <title>

**status:** proposed|accepted|deprecated|superseded
**date:** YYYY-MM-DD
**supersedes:** ADR-<NNN> (if applicable)

## Context

<the situation that makes this decision necessary>

## Decision

<the decision made>

## Consequences

<what becomes easier, what becomes harder, what is now required>
```

Supersession: new ADR references old ADR, old ADR marked `superseded`. Document reads ADRs for decision log generation.

### C4 Model

Architecture documented using C4 model at appropriate level per spec stage:

| Level | What | When required |
|---|---|---|
| Context (L1) | System, external actors, system relationships | P2 Systems Design — all targets |
| Container (L2) | Applications, data stores, major components | P2 Systems Design — all targets |
| Component (L3) | Internals of key containers | P3 Technical Spec — complex targets |
| Code (L4) | Implementation level | Not required — live code is the source of truth |

### Coupling and Cohesion

**Coupling:** Loose coupling between services declared and measured. Tight coupling requires justification in an ADR.

**Cohesion:** Module boundaries must justify their grouping on domain or responsibility grounds. Convenience grouping (modules grouped because they were written at the same time or by the same person) is not accepted.

---

## CI/CD Pipeline

**Reference:** `references/ci-cd.md`

### Pipeline Stages

Declared order required in spec:

```
lint → test → build → security scan → deploy
```

Each stage is a gate. Failure in any stage blocks subsequent stages. No deploy without preceding security scan. No build without preceding tests.

### Branch Strategy

Declared in spec — one of:
- **Trunk-based:** all developers integrate to main frequently (feature flags for in-progress work)
- **GitHub Flow:** feature branches, PR to main, deploy from main
- **GitFlow:** main + develop + feature/release/hotfix branches

Not declared = trunk-based as default. Explicit declaration required if team deviates.

### Deployment Strategy

Declared per environment:

| Strategy | Definition | When preferred |
|---|---|---|
| Blue-green | Two identical environments, traffic switches | Zero-downtime required |
| Canary | Gradual traffic shift to new version | Risk mitigation for large changes |
| Rolling | Instances updated progressively | Simple deployments, acceptable brief mixed versions |

Rollback trigger declared: threshold (error rate, latency) that automatically surfaces rollback prompt. Deploy module enforces this declaration.

### Branch Protection

Required for main/production branches:
- PR required (no direct push)
- CI must pass before merge
- At least one review (team size 1+ = self-review explicitly declared)

---

## Reliability

**Reference:** `references/reliability.md`

### SLO (Service Level Objective)

Availability and latency targets declared in spec — not implied. No default SLO. Undeclared = no SLO, which must be an explicit decision.

SLO declaration format:

```markdown
## SLO Declarations

**availability:** 99.9% over 30-day rolling window
**latency p50:** < 100ms
**latency p99:** < 500ms
**throughput floor:** 100 RPS sustained
```

### Error Budget

Derived from SLO. Used to gate risky changes:
- 99.9% availability = 43.8 minutes downtime budget per month
- When error budget exhausted: no new risky deployments until budget replenishes
- Error budget consumption tracked by Monitor — reported to Engineering gateway

### Circuit Breaker

Required for all synchronous external calls. No direct blocking calls to external services without a circuit breaker pattern declared. Open/half-open/closed states declared. Fallback behavior for open state declared.

### Chaos Engineering

Scope declared in spec — not required, but must be explicitly stated:
- `none`: no chaos engineering
- `limited`: specific failure scenarios tested (database outage, service unavailability)
- `continuous`: steady-state hypothesis tested in production (Netflix-style)

Undeclared = `none`. Must be active decision.

---

## Systems Design Standards

**Reference:** `references/systems-design.md`

### CAP Theorem

For distributed components: consistency/availability trade-off declared. No implicit assumption of both consistency and availability. AP systems: eventual consistency handling declared. CP systems: availability degradation declared.

### Idempotency

Declared for all state-mutating operations. HTTP methods: POST operations that are not idempotent by design declare retry behavior. Queue-based systems: consumer idempotency declared (deduplication key).

### Backpressure

Declared for all async processing paths. Queue depth limits declared. Consumer lag alerting declared (Monitor generates this from Engineering SLO). No unbounded queue growth without declared overflow strategy.

### Data Contracts

Versioned data contracts — not implicit. Internal service contracts: versioned schemas (JSON Schema, Protobuf, Avro). API contracts: OpenAPI spec versioned and committed. Breaking data contract changes = BREAKING per semver — require Engineering review.

---

## Test Coverage Policy

**Reference:** `rules/test-coverage-policy.md`

Coverage floors are declared per project — not universal. No default 80% rule. The project declares its floor at P1 based on risk profile and team context.

| Test type | Requirement |
|---|---|
| Unit tests | Coverage floor declared per project at P1 |
| Integration tests | Required for all external integrations (database, external APIs, message queues) |
| E2E tests | Required for all critical user journeys (declared at P1) |
| Contract tests | Required for all API consumers (both sides of the contract tested) |

Coverage floor justification: declared in spec with rationale. A data pipeline processing medical records and a CLI dev tool have different appropriate floors.

---

## Integration Points

| Module | Relationship |
|---|---|
| Apply | Apply reads Engineering gateway for cross-cutting standards during execution |
| Verifier | Verifier Review mode consults Engineering gateway for architecture and standards checks |
| Platform packages (L3) | Platform engineering directories implement platform-specific toolchain; Engineering gateway owns cross-cutting standards they inherit |
| Reviewer | Reviewer consults Engineering gateway for BREAKING change review |
| Specify | Specify consults Engineering gateway when classifying architectural changes |
| Monitor (L7) | Monitor reads Engineering gateway SLO declarations for alert rule generation |
| Deploy (L7) | Deploy reads CI/CD and deployment strategy from Engineering gateway declarations |
| Document (L6) | Document reads ADRs from Engineering gateway for decision log generation |

---

## Verification Mode

**Review** — architecture review completed at P2, ADRs present for all major decisions, CI pipeline declared, reliability targets documented, test coverage floor declared.

---

## Receipt Extension Fields

```json
{
  "adr_count": 0,
  "architecture_reviewed": true,
  "ci_pipeline_declared": true,
  "slo_declared": true,
  "breaking_changes_reviewed": 0
}
```

---

## Cross-References

- L3 Platform packages (platform-specific build toolchain): `WabbleSpec v6.1 — Platform.md`
- Security gateway (SAST integration into CI): `WabbleSpec v6.1 — Security.md`
- L7 Monitor (SLO → alert binding): `WabbleSpec v6.1 — Delivery.md` § Monitor
- L7 Deploy (deployment strategy, rollback): `WabbleSpec v6.1 — Delivery.md` § Deploy
- L6 Document (ADR → decision log): `WabbleSpec v6.1 — Expression.md` § Document
- Verification modes: `WabbleSpec v6.1 — Core.md` § Verification Modes
