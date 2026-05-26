# Platform: API Service

REST or GraphQL API / backend service target. Activates when Recipe identifies a server-side API, microservice, or backend as the primary build target.

**Skill:** `modules/l3/api-service/SKILL.md`

## What makes API Service different

| Concern | API Service approach |
|---------|---------------------|
| Contract | OpenAPI or GraphQL schema — declared and versioned |
| Auth | AuthN strategy (JWT, OAuth, API key) declared up front |
| Authorization | RBAC or ABAC — declared per endpoint |
| Rate limiting | Strategy declared — per-user, per-IP, per-plan |
| Idempotency | All mutating operations declare idempotency strategy |
| Pagination | Cursor or offset — declared for all list endpoints |
| Versioning | URL versioning (`/v1/`) or header versioning — chosen up front |
| Error format | RFC 7807 (Problem Details) or equivalent — consistent across all endpoints |

## Platform-specific spec sections

- API contract: endpoint list with methods, path params, query params, request/response shapes
- Authentication flow: token acquisition, refresh, revocation
- Error catalog: all error codes with descriptions and recovery actions
- Rate limit policy: limits, window, response headers, retry guidance
- Backwards compatibility: change classification for every proposed change (ADDITIVE, BREAKING, DEPRECATION)

## Security controls loaded

- SQL injection: parameterized queries required; ORM raw query usage flagged
- Auth bypass: every endpoint declares its auth requirement — unauthenticated paths must be explicit
- Mass assignment: input shapes validated against allowlist — no pass-through of raw request body
- SSRF: outbound URL fetches validated against allowlist
- Secrets: no credentials in logs, no credentials in error responses

## Gateway interaction

API Service targets typically activate:
- `gateway-security` — always (auth, injection, SSRF surface)
- `gateway-engineering` — always at Medium/High complexity
- `gateway-ai` — if any endpoint integrates an LLM
