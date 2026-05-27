# Engineering Quality Patterns

Architectural decision records, test strategy requirements, and breaking change classification. Used by gateway-engineering during spec review.

## Architecture Decision Records (ADRs)

Every significant architectural decision must be documented before implementation. An ADR captures: what was decided, why, and what alternatives were considered.

### ADR format

```markdown
# ADR-{number}: {short title}

**Date**: {YYYY-MM-DD}  
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-{N}  
**Deciders**: {who was involved in the decision}

## Context

{The situation that requires a decision. What problem are we solving? What constraints exist?}

## Decision

{The decision made. Be direct: "We will use X for Y."}

## Rationale

{Why this option was chosen. What trade-offs were accepted?}

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| {Option A} | {Reason} |
| {Option B} | {Reason} |

## Consequences

**Positive**:
- {benefit}

**Negative / trade-offs**:
- {cost or limitation}

## Review date

{When this decision should be reviewed — usually 6-12 months, or on a specific trigger condition}
```

### When an ADR is required

- Choosing a database or data store
- Choosing a framework or major library
- Defining an API contract that other services will consume
- Choosing an authentication mechanism
- Defining data retention or deletion policy
- Any decision that would be expensive to reverse

### ADR storage

```
docs/decisions/
  ADR-001-database-choice.md
  ADR-002-auth-mechanism.md
  ADR-003-api-versioning.md
```

## Test strategy requirements

Every project spec must declare a test strategy. Required content:

### Test pyramid declaration

```yaml
test_strategy:
  unit:
    coverage_target: 80%          # lines or branches; declare which
    scope: "business logic, use cases, utilities"
    framework: "{Jest / pytest / go test / RSpec / ...}"
    
  integration:
    scope: "database access, external APIs, message queues"
    isolation: "test database; mocked external services"
    framework: "{supertest / httpx / testcontainers / ...}"
    
  e2e:
    scope: "critical user flows only — login, checkout, core feature"
    count: "{N} flows"
    framework: "{Playwright / Cypress / Detox / ...}"
    run_frequency: "on PR and pre-deploy"
    
  contract:
    scope: "API contracts with consumers (if applicable)"
    framework: "{Pact / ...}"
    required: "{yes / no}"
```

### What must be tested

At minimum:
- Happy path: input → expected output
- Error path: invalid input → correct error response / exit code
- Boundary cases: empty input, max length, zero values
- Auth boundary: unauthenticated → 401; wrong user → 403
- Idempotency: repeated operation → same result (for APIs and pipelines)

### What must not be tested

- Implementation internals (private methods, internal state)
- Framework behavior (trust that React renders, that Express routes)
- Third-party library internals

## Breaking change classification

Changes must be classified before implementation. The classification determines review requirements and deployment strategy.

### API breaking changes

| Change | Breaking? | Required action |
|---|---|---|
| Add new optional field to request | No | Safe to deploy |
| Add new field to response | No (for JSON; yes for strict schemas) | Check consumers |
| Remove field from request or response | Yes | Version bump + migration guide |
| Rename field | Yes | Add alias first; deprecate old; remove in next major |
| Change field type | Yes | Version bump + migration guide |
| Change enum values | Yes (remove/rename) / No (add new) | Remove = breaking |
| Change HTTP method | Yes | Version bump |
| Change URL path | Yes | Redirect old → new for grace period |
| Add required field | Yes | Version bump + migration guide |
| Change error format | Yes | Version bump |

### Database breaking changes

| Change | Risk | Required action |
|---|---|---|
| Add nullable column | Low | Safe; add default or make nullable |
| Add non-nullable column | High | Add as nullable → backfill → add constraint |
| Remove column | High | Deprecate first; verify no consumers; then remove |
| Rename column | High | Add alias column → migrate → remove old |
| Change column type (compatible) | Medium | Test type coercion; add check constraint |
| Change column type (incompatible) | High | New column → migrate data → drop old |
| Add index | Low | Concurrent index creation in production |
| Drop index | Medium | Verify index is not in use by queries |
| Add foreign key constraint | High | Verify data integrity first; add with NOT VALID then validate |

### Dependency breaking changes

Before upgrading a major dependency version:
1. Read the changelog for breaking changes
2. Run the full test suite against the new version
3. Benchmark performance-critical paths (major versions often change performance)
4. Test in staging for at least 24 hours before production

## Engineering gate checklist

gateway-engineering Phase B checks:

- [ ] Test strategy declared in spec
- [ ] Coverage target declared and CI-enforced
- [ ] Breaking changes identified and migration plan declared
- [ ] ADRs written for significant architectural decisions
- [ ] Performance budget declared and measured (not assumed)
- [ ] No `TODO:` comments in spec (deferred decisions are breaking)
- [ ] Observability declared (logging, metrics, tracing)
- [ ] Runbook section present for operational concerns
