# API/Service Design Document Template (P1)

> **Platform:** API/Service
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-api-service activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this API/service does, who calls it (other services, browser clients, CLI tools, third parties), and the primary business function it exposes.

---

## API Style [REQUIRED]

[ ] REST (HTTP/JSON)
[ ] GraphQL
[ ] gRPC (Protobuf)
[ ] WebSocket (real-time)
[ ] Mixed — declare primary: ___

**API contract format:**
[ ] OpenAPI 3.x spec (`openapi.yaml`) — generated from code or hand-authored (declare which)
[ ] `.proto` files (gRPC)
[ ] GraphQL schema (`schema.graphql`)
[ ] None — reason: ___

---

## Versioning Strategy [REQUIRED]

[ ] URL path versioning (`/v1/`, `/v2/`)
[ ] Header versioning (`Accept: application/vnd.api+json;version=2`)
[ ] No versioning — reason: ___

**Breaking change policy:** How is a breaking change defined? What is the deprecation window?

**Backward compatibility requirement:** How many major versions supported simultaneously? ___

---

## Endpoint Inventory [REQUIRED]

Every endpoint must be named here before any Executor wave begins.

| Method | Path | Auth required | Idempotent | Description |
|---|---|---|---|---|
| GET | /health | No | Yes | Health check |
| GET | /ready | No | Yes | Readiness check |
| [METHOD] | [/path] | [Yes/No] | [Yes/No] | [description] |

**Total endpoints:** ___
**Mutating endpoints (POST/PUT/PATCH/DELETE):** ___

---

## Auth Scheme [REQUIRED]

[ ] Bearer token (JWT) — validation: [ ] local (verify signature) [ ] remote (introspection endpoint)
[ ] API key in header (`X-API-Key` or `Authorization: ApiKey`)
[ ] mTLS (service-to-service only)
[ ] OAuth 2.0 — flow: [ ] client credentials [ ] authorization code
[ ] No auth — reason: ___ (public read-only API? internal only?)
[ ] Multiple — declare per-endpoint in inventory above

**Token source:** Where do clients obtain credentials? ___

**Token lifetime:** ___ (short-lived? refresh token pattern?)

**Unauthenticated request behavior:** 401 with body: ___

---

## Rate Limiting [REQUIRED]

[ ] Per client (API key / IP)
[ ] Per endpoint
[ ] Global
[ ] None — reason: ___

If rate limiting implemented:
- Limit: ___ requests per ___
- Burst allowance: ___
- Response when exceeded: 429 with `Retry-After` header
- Headers returned on every response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Error Response Schema [REQUIRED]

Declare the error response format used across all endpoints. RFC 7807 (Problem Details) preferred.

```json
{
  "type": "https://example.com/errors/not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "User with id '123' does not exist",
  "instance": "/users/123"
}
```

[ ] RFC 7807 Problem Details
[ ] Custom format — document here: ___

**Consistency requirement:** All error responses use the same schema. No endpoint-specific error formats.

---

## Health and Readiness Endpoints [REQUIRED]

**Health endpoint** (`/health` or equivalent):
- Returns 200 when process is alive
- No dependency checks (liveness only)
- Response body: `{"status": "ok"}` (or equivalent)

**Readiness endpoint** (`/ready` or equivalent):
- Returns 200 only when all dependencies are reachable (database, cache, upstream services)
- Returns 503 when any dependency is unavailable
- Response body includes dependency status

**Kubernetes probe targets:** Health → liveness probe. Ready → readiness probe.

---

## Data Store [REQUIRED if applicable]

[ ] No persistent data store
[ ] Relational database (PostgreSQL / MySQL / SQLite)
[ ] Document database (MongoDB / DynamoDB)
[ ] Key-value / cache (Redis / Memcached)
[ ] Multiple — list: ___

**Migration strategy:** How are schema changes applied? (Flyway, Alembic, golang-migrate, manual)

**Connection pool size:** ___ min / ___ max

---

## Observability Strategy [REQUIRED]

**Structured logging:**
[ ] JSON logs (required for production)
[ ] Log level controlled by env var (`LOG_LEVEL=info`)

**Metrics:**
[ ] Prometheus endpoint (`/metrics`)
[ ] OpenTelemetry SDK — exporter: ___
[ ] None — reason: ___

**Distributed tracing:**
[ ] OpenTelemetry traces — propagation: W3C TraceContext
[ ] No tracing — reason: ___

**Required log fields (per request):** `timestamp`, `level`, `method`, `path`, `status_code`, `duration_ms`, `trace_id`

---

## Deployment Target [REQUIRED]

[ ] Containerized (Docker) — orchestrator: [ ] Kubernetes [ ] ECS [ ] Nomad [ ] Docker Compose
[ ] Serverless — platform: [ ] AWS Lambda [ ] GCP Cloud Functions [ ] Azure Functions
[ ] VM / bare metal
[ ] Multiple — declare primary: ___

**Config injection:** How does config reach the running process?
[ ] Environment variables (12-factor)
[ ] Mounted secrets (Kubernetes Secrets / Vault agent)
[ ] Config file at known path
[ ] SSM Parameter Store / Secrets Manager at startup

---

## GWT Acceptance Scenarios (API/Service-specific)

These are the platform-specific gate tests that Verifier runs. Generic templates do not include these.

```
Given: any request arrives at any endpoint
When: the request has no Authorization header (or invalid credentials)
Then: response is 401 with error body matching declared error schema
      AND no sensitive data is included in the error response
      AND no endpoint logic executes before auth is checked

Given: an authenticated request arrives at a resource owned by another user
When: the request is valid and the user is authenticated
Then: response is 403 (not 404 — no resource enumeration via 404)
      AND no data from the other user's resource is returned

Given: a mutating endpoint (POST/PUT/PATCH/DELETE) receives concurrent identical requests
When: idempotency is declared for that endpoint
Then: only one state change occurs regardless of how many duplicate requests arrive
      AND all duplicate responses return the same result

Given: request rate exceeds declared limit for a client
When: the client sends requests beyond the limit
Then: response is 429 with Retry-After header
      AND limit headers are present on the 429 response

Given: the /health endpoint is called
When: the process is running
Then: response is 200 within 50ms
      AND response does not perform any database or network operations

Given: the /ready endpoint is called
When: a downstream dependency (database, cache) is unreachable
Then: response is 503 within declared timeout
      AND response body names which dependency is unavailable

Given: a request causes an unhandled server error
When: any endpoint encounters an unexpected exception
Then: response is 500 with RFC 7807 error body
      AND stack trace does not appear in the response body
      AND the full error with stack trace is written to structured log
```

---

## Open Questions

List any unresolved design decisions here. Specify module will block receipt until all REQUIRED sections are complete and no blocking open questions remain.
