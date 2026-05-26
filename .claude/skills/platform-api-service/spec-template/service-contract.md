# Service Contract Template (P0)

> **Platform:** API/Service | **Phase:** P0 — complete before design-document.md.
> Sections marked `[REQUIRED]` must be filled before Specify receipt.
> This document is the contract authority. Consumer-facing decisions (API style, versioning, auth) made here bind every downstream spec and cannot be changed without a versioning event.

---

## Service Statement [REQUIRED]

One sentence: what this service does, who calls it, and what capability it exposes.

> Example: "A notification dispatch service that receives events from internal services and fans them out to email, SMS, and push channels based on per-user preferences."

---

## Service Pillars [REQUIRED]

Declare 2–4 pillars. For services, pillars typically govern reliability, consumer experience, and operational properties. Each must be falsifiable.

### Pillar 1: [Name]

**Definition:** One sentence stating what this pillar demands of every service decision.

**Falsifiability test:** "This design fails Pillar 1 if it [concrete failure condition]."

**Anti-pillar:** The service we explicitly refuse to build.

---

### Pillar 2: [Name]

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

### Pillar 3: [Name] *(optional)*

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

## Consumer Registry [REQUIRED]

Every consumer of this service must be declared before Specify begins. Unknown consumers discovered mid-implementation require a versioning event review.

| Consumer | Type | Call pattern | Auth method | SLA expectation |
|---|---|---|---|---|
| [Service / client name] | Internal service / Browser client / Third party / CLI | Sync request / Async event / Polling | Bearer / API key / mTLS / None | p99 < ___ms |

**Total declared consumers:** ___

---

## SLO Targets [REQUIRED]

Service Level Objectives. These are commitments, not aspirations. Every SLO requires a measurement method.

| Metric | Target | Measurement window | Measurement method |
|---|---|---|---|
| Availability | ___% (e.g. 99.9%) | 30-day rolling | Uptime from /health endpoint |
| p99 latency | < ___ms | 24-hour rolling | APM / tracing percentile |
| Error rate | < ___% | 24-hour rolling | 5xx / total requests |
| Throughput capacity | ___ RPS sustained | Peak load | Load test result |

**Error budget:** (1 - availability%) × 30 days = ___ minutes/month allowed downtime.

**SLO breach response:** What happens when SLO is breached? Declare the runbook reference or escalation path.

---

## API Style Decision [REQUIRED]

One API style per service. Mixed styles require explicit justification and are rare.

[ ] REST/JSON — declare OpenAPI version and generation strategy (code-first / spec-first)
[ ] gRPC/Protobuf — declare streaming requirements and proto package namespace
[ ] GraphQL — declare schema ownership and N+1 prevention strategy
[ ] Event-driven only (no synchronous API) — declare event broker and schema format

**Breaking change policy:** How is a breaking change defined for this service?

**Backwards compatibility window:** How long are old versions supported after a breaking change?

---

## Dependency Map [REQUIRED]

What this service calls. Every external dependency is a failure mode.

| Dependency | Type | Failure behavior | Circuit breaker? |
|---|---|---|---|
| [Database / service / external API] | Synchronous / Async | Fail request / Degrade / Queue | Yes / No |

**Critical path dependencies** (unavailability causes this service to return errors): ___

**Non-critical dependencies** (unavailability causes degraded but functional response): ___

---

## Scope Tiers [REQUIRED]

| Tier | Endpoints / capabilities | Ships if... |
|---|---|---|
| **v1** | [List] | Initial release |
| **v2** | [List] | Post-v1 iteration |
| **Out of scope** | [Explicit non-goals] | Never (for this service) |

**v1 non-goals** (explicitly excluded to prevent scope creep — must be documented):

---

## Data Sensitivity Classification [REQUIRED]

What data does this service process? This determines security controls and compliance requirements.

[ ] No PII
[ ] PII (names, emails, addresses) — GDPR/CCPA implications
[ ] Financial data — PCI DSS scope
[ ] Health data — HIPAA implications
[ ] Authentication credentials — elevated security controls required
[ ] None of the above

**Retention policy:** How long is data kept? When is it deleted?

**Data residency:** Any geographic restrictions on where data is stored or processed?

---

## GWT Acceptance Scenarios

```
Given: a new consumer wants to integrate with this service
When: they read only this service-contract.md and design-document.md
Then: they can determine the API style, auth method, and expected SLOs
      AND they can identify who to contact if SLOs are breached
      AND they do not need to read source code to understand the contract

Given: a proposed change would break backward compatibility
When: it is evaluated against the breaking change policy
Then: the change is not deployed until the versioning event is completed
      AND all declared consumers are notified before the breaking version ships

Given: a critical path dependency becomes unavailable
When: this service receives a request
Then: the response follows the declared failure behavior for that dependency
      AND the error response matches the declared error schema
      AND the service does not crash or enter an undefined state
```

---

## Open Questions

Unresolved consumer requirements, SLO targets, or API style decisions. Specify receipt blocked until REQUIRED sections complete.
