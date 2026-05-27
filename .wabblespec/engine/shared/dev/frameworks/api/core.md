# API/Service Framework Core

Cross-framework knowledge for HTTP APIs, gRPC services, and long-running backends. Loaded by Apply for every API/Service platform task.

## API contract requirements

Every API spec must declare:
- **Versioning strategy**: URL path (`/v1/`), header (`API-Version`), or content negotiation
- **Auth scheme**: Bearer token, API key, mTLS, or public (justify public)
- **Rate limiting**: per-user, per-IP, per-key — limits and response format
- **Pagination**: cursor-based (preferred) or offset; `limit` and `next_cursor` / `next` link
- **Error format**: RFC 7807 Problem Details or custom schema — declare and use consistently
- **Health endpoints**: `/health` (liveness) and `/ready` (readiness) — required

## REST conventions

```
GET    /resources           — list; paginated
POST   /resources           — create; returns 201 + Location header
GET    /resources/{id}      — get one; 404 if not found
PUT    /resources/{id}      — full replace; 200 or 204
PATCH  /resources/{id}      — partial update; 200 or 204
DELETE /resources/{id}      — delete; 204

POST   /resources/{id}/actions — non-CRUD action (avoid if possible)
```

### Response status codes

| Situation | Code |
|---|---|
| Created | 201 + Location |
| No content | 204 (DELETE, successful PATCH with no body) |
| Bad request / validation error | 400 + error body |
| Unauthorized (no credentials) | 401 |
| Forbidden (has credentials, no permission) | 403 |
| Not found | 404 |
| Conflict (duplicate, version mismatch) | 409 |
| Unprocessable (validation error) | 422 |
| Rate limited | 429 + Retry-After header |
| Server error | 500 |

## Error response — RFC 7807

```json
{
  "type": "https://example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 400,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/api/v1/users/create",
  "errors": [
    { "field": "email", "message": "Invalid format" }
  ]
}
```

## Observability requirements

Every API spec must declare:

- **Structured logging**: JSON format; every request logged with `request_id`, `method`, `path`, `status`, `duration_ms`, `user_id` (if authed)
- **Distributed tracing**: `X-Request-ID` or W3C `traceparent` header propagated through all service calls
- **Health check**: `GET /health` returns `200 OK` with `{"status": "ok"}` when service can receive traffic
- **Readiness check**: `GET /ready` returns `200` when dependencies (DB, cache) are connected; `503` otherwise
- **Metrics**: request count, p99 latency, error rate — declare Prometheus labels or APM service

## Idempotency

Mutating endpoints (POST creating resources) should support idempotency keys:
```
Idempotency-Key: <client-generated-uuid>
```
Server stores result for key; second request with same key returns cached result (not re-executed).

Required for: payment processing, order creation, any non-retryable operation.

## Database access patterns

- Connection pooling: declare pool size in spec (`min`, `max`, `idle_timeout`)
- Transactions: declare which operations require transactions and isolation level
- Migrations: forward-only; never destructive in the same migration as data-dependent logic
- Query timeouts: declare per-operation timeout; no unbounded queries

## Performance budget

Spec must declare:
- p99 latency target per endpoint class (read: < 100ms; write: < 200ms; batch: < 2s)
- Throughput target (RPS) at p99 target
- Database query count per request (N+1 detection required in review)
