# API/Service Systems Design Template (P2)

> **Platform:** API/Service
> **Template version:** 1.0
> **Populated by:** Specify module (P2 pass)
> **Prerequisite:** design-document.md complete (P1 receipt exists)

---

## Request Pipeline

Document the full lifecycle of a request through the service.

```
Incoming request
  └─ TLS termination (load balancer / ingress)
  └─ Rate limiting middleware
  └─ Auth middleware (validate token / API key)
  └─ Request validation (schema, required fields, types)
  └─ Route handler
        └─ Business logic
        └─ Data access layer (DB / cache / upstream)
        └─ Response serialization
  └─ Structured logging middleware (log after handler)
  └─ Response
```

**Middleware order matters.** Auth must run before any handler logic. Logging must capture status code and duration.

---

## Middleware Stack

List all middleware in execution order. Declare what each does and whether it can short-circuit the request.

| Order | Middleware | Short-circuits on | Notes |
|---|---|---|---|
| 1 | Rate limiter | Limit exceeded → 429 | |
| 2 | Auth | Invalid/missing token → 401 | Must run before any handler |
| 3 | Request ID injection | — | Adds trace ID to context |
| 4 | Request validation | Schema violation → 400 | |
| 5 | [Additional] | | |
| Last | Request logger | — | Logs after handler completes |

---

## Auth Implementation

**Token validation approach:**

[ ] Local JWT verification
```
1. Extract Bearer token from Authorization header
2. Verify signature against public key / shared secret
3. Check exp claim — reject if expired
4. Check required claims (iss, aud, scope)
5. Attach decoded claims to request context
```

[ ] Remote introspection
```
1. Extract token
2. POST /introspect to auth server with token
3. Check active=true in response
4. Cache introspection result for token TTL duration
5. Attach claims to request context
```

[ ] API key
```
1. Extract X-API-Key header (or Authorization: ApiKey <key>)
2. Hash key (constant-time comparison — no timing attacks)
3. Look up in key store
4. Check active status and rate limit tier
5. Attach client identity to request context
```

**Auth failure behavior:** Return 401 immediately. Do not log the submitted token value. Do log the client IP and endpoint.

---

## Authorization (RBAC / Scopes)

Is authorization enforced beyond authentication?
[ ] Yes — mechanism: [ ] Scopes in JWT [ ] Role in user record [ ] Policy engine (OPA, Casbin)
[ ] No — all authenticated users have equal access

**Authorization check location:** [ ] Middleware (coarse-grained) [ ] Handler (fine-grained) [ ] Both

**IDOR protection:** For any endpoint that returns a resource by ID, verify the authenticated user owns or has permission for that resource before fetching.

---

## Data Access Layer

**ORM / query builder:** ___

**Connection pool configuration:**
- Min connections: ___
- Max connections: ___
- Connection timeout: ___ms
- Idle timeout: ___

**Query patterns:**
- Raw SQL used? [ ] Yes [ ] No. If yes: parameterized queries only — no string interpolation.
- ORM used? [ ] Yes — which: ___. Verify ORM does not permit raw unparameterized queries.

**Transaction boundaries:** Which operations require a transaction? List here.

**N+1 prevention:** Batch loading strategy for related data: ___

---

## Caching Layer (if applicable)

[ ] No caching
[ ] In-memory (single instance only — no shared state between replicas)
[ ] Redis / Memcached

**Cache key scheme:** `<service>:<resource>:<id>:<version>`

**TTL strategy:**
| Cache key pattern | TTL | Invalidation trigger |
|---|---|---|
| [pattern] | [duration] | [event or explicit purge] |

**Cache stampede protection:** [ ] Locking (single-flight) [ ] Probabilistic early expiry [ ] Not applicable

---

## Idempotency

For each mutating endpoint declared as idempotent in design-document:

**Idempotency key mechanism:**
- Source: [ ] `Idempotency-Key` request header [ ] Request body field [ ] Derived from payload hash
- Storage: [ ] Redis [ ] Database `idempotency_keys` table
- TTL: ___ (how long is a duplicate request recognized?)
- Response: Return stored result for duplicate — do not re-execute

**Non-idempotent operations:** Declare explicitly. These must not be retried without user confirmation.

---

## Error Handling Model

**Unhandled exception behavior:**
```
Unhandled exception
  └─ Catch in global error handler
  └─ Log: full error + stack trace to structured log (with trace_id)
  └─ Return: 500 with RFC 7807 body (no stack trace, no internal details)
  └─ Increment error counter metric
```

**Error categorization:**

| HTTP status | Meaning | Log level |
|---|---|---|
| 400 | Client error (validation failure) | WARN or omit |
| 401 | Auth failure | WARN |
| 403 | Authorization failure | WARN |
| 404 | Not found | INFO |
| 409 | Conflict / duplicate | WARN |
| 429 | Rate limited | INFO |
| 500 | Server error | ERROR |
| 503 | Dependency unavailable | ERROR |

**Never expose in error response:** stack traces, database query text, internal hostnames, secret values, user data from other accounts.

---

## Structured Logging

**Log format:** JSON (required for production log aggregation).

**Required fields on every log entry:**

```json
{
  "timestamp": "2026-05-21T12:34:56.789Z",
  "level": "info",
  "service": "<service-name>",
  "version": "<build-version>",
  "trace_id": "<w3c-trace-id>",
  "span_id": "<span-id>",
  "method": "POST",
  "path": "/users",
  "status_code": 201,
  "duration_ms": 45,
  "client_id": "<api-key-id or user-id>"
}
```

**Fields never logged:**
- Raw auth tokens or API keys
- Request/response bodies containing PII (or: log with fields redacted)
- Database connection strings
- Full stack traces at WARN or below (ERROR level only, to log file / aggregator)

**Log level env var:** `LOG_LEVEL` — values: `debug`, `info`, `warn`, `error`

---

## Distributed Tracing

**Propagation standard:** W3C TraceContext (`traceparent` / `tracestate` headers)

**Trace injection:** On every incoming request, extract or generate trace context and attach to request context. Propagate to all downstream calls (DB, cache, upstream services).

**Span naming:** `<METHOD> <route-pattern>` (not path with IDs — e.g., `GET /users/:id` not `GET /users/123`)

---

## Graceful Shutdown

```
SIGTERM received
  └─ Stop accepting new connections
  └─ Complete in-flight requests (drain timeout: ___ seconds)
  └─ Close database connections
  └─ Flush log buffer
  └─ Exit 0
```

**Drain timeout:** Kubernetes default terminationGracePeriodSeconds = 30s. Set drain timeout to 25s to allow kubelet overhead.

---

## Config Loading

**12-factor pattern:** All config from environment variables. No config files bundled in container image.

**Required env vars (declare all):**

| Var | Type | Default | Description |
|---|---|---|---|
| `PORT` | int | 8080 | HTTP listen port |
| `LOG_LEVEL` | string | info | Log verbosity |
| `DATABASE_URL` | string | — | Connection string (injected via secret) |
| [Additional] | | | |

**Startup validation:** On boot, validate all required env vars are present before binding to port. If any required var is missing, log the var name and exit 1.

**Secrets:** Never log env var values for sensitive vars. Log only the var name and whether it was found.
