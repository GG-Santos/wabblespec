# Cold-Start Behavior — Platform API Service

Defines how the API service platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `_shared/dev/frameworks/api/core.md` or `_shared/dev/frameworks/api/security.md` missing.
Detection: File read returns 404 during Apply routing phase.
Action: Log warning. Apply continues without REST contract, RFC 7807 error format, and idempotency rules. Executor proceeds.
Do NOT: Fail the session.

## Absent: conditional framework files

Condition: `_shared/dev/frameworks/api/grpc.md` or `api/graphql.md` absent when proto files or GraphQL schema detected.
Detection: Signal matched (`.proto` file / `schema.graphql`) but framework file not found.
Action: Proceed without file. Log: "API framework file not found: [path]."

## Absent: security reference files

Condition: `modules/l3/api-service/security/threat-model.md` or `security/platform-controls.md` absent.
Detection: File read returns 404.
Action: Gateway-security uses OWASP API Top 10 from `references/owasp.md` as fallback.

## Absent: spec-template files

Condition: `modules/l3/api-service/spec-template/design-document.md` absent.
Action: Specify uses generic structure. Log: "API spec-template not found."

## Default state on cold start

| Field | Default |
|---|---|
| `auth_strategy` | Not declared — Specify must elicit (Bearer / API key / mTLS) |
| `error_format` | RFC 7807 enforced as default — `application/problem+json` |
| `pagination` | Not declared — Specify must elicit (cursor / offset) |
| `versioning` | Not declared — Specify must elicit (URL path / header) |
| `idempotency` | POST requests must have idempotency key support if writes are retried — Specify must confirm |
| `rate_limiting` | Not declared — Specify must elicit limits and 429 behavior |

RFC 7807 error format is enforced as a default even without framework files — it is an API platform invariant.
