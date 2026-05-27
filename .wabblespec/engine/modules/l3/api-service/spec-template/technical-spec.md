# API/Service Technical Spec Template (P3)

> **Platform:** API/Service
> **Template version:** 1.0
> **Populated by:** Specify module (P3 pass) + Decompose
> **Prerequisite:** systems-design.md complete (P2 receipt exists)

---

## Implementation Constraints

Non-negotiable for all API/Service targets. Verifier checks each one.

| Constraint | Rule | Verification method |
|---|---|---|
| Auth before logic | No handler executes before auth middleware validates | Integration test: unauthenticated request → 401, no side effects |
| Parameterized queries | No raw SQL string interpolation | Code review: grep for string concat in query context |
| No secrets in logs | Auth tokens, keys, passwords never logged | Log output review: send known token, grep logs for it |
| No secrets in responses | Stack traces, internal paths, DB details absent from error bodies | Test: trigger 500, inspect response body |
| Health endpoint | /health returns 200 without DB access | Test: kill DB, /health must still return 200 |
| Ready endpoint | /ready returns 503 when DB is unreachable | Test: kill DB, /ready must return 503 |
| Structured logs | JSON log output with required fields on every request | Log capture test: parse log output as JSON |
| Rate limiting | 429 returned when limit exceeded, Retry-After present | Load test or unit test at limit boundary |
| Error schema | All error responses match declared schema | Test every error path, validate response body |

---

## Wave Breakdown

Decompose populates this section. Shown here as the expected shape for API/Service tasks.

**Wave 0 — Scaffold**
- HTTP server bound to PORT
- /health and /ready endpoints (no dependencies yet)
- Request logger middleware wired
- Graceful shutdown handler (SIGTERM)
- Acceptance: `curl localhost:$PORT/health` returns 200; SIGTERM drains and exits 0

**Wave 1 — Auth middleware**
- Token validation or API key lookup
- Auth middleware registered before all routes
- 401 response with correct error schema on missing/invalid credentials
- Acceptance: unauthenticated request → 401; authenticated request → passes to next handler

**Wave 2 — Data layer**
- Database connection pool initialized
- Connection validated at startup (fail fast if unreachable)
- /ready reflects actual DB state
- Migrations applied (or migration runner invoked)
- Acceptance: /ready returns 200 with DB up; 503 with DB down

**Wave 3+ — Endpoint implementations**
- One wave per logical endpoint group or resource
- Each wave: implement handler → parameterized queries only → test auth enforcement → test error paths → test response schema

**Final wave — Observability + hardening**
- Structured log fields complete on all requests
- Metrics endpoint (if declared)
- Rate limiting enforced
- Integration tests covering all GWT scenarios

---

## Acceptance Criteria (GWT format)

All scenarios from design-document.md reproduced here and assigned to waves.

### Auth enforcement

```
Given: any protected endpoint
When: request has no Authorization header
Then: response is 401 with RFC 7807 error body
      AND no handler logic executes (no DB queries, no side effects)
      AND no token value appears in response or logs

Given: request has Authorization header with expired token
When: token exp claim is in the past
Then: response is 401 with error body citing token expiry
      AND Retry hint names where to get a new token (if applicable)
```

### Authorization (IDOR prevention)

```
Given: endpoint returns a resource identified by ID
When: authenticated user requests a resource they do not own
Then: response is 403 (not 404)
      AND no data from the other user's resource is returned
```

### Input validation

```
Given: endpoint with declared required fields
When: request body omits a required field
Then: response is 400 with error body naming the missing field
      AND no partial writes occur
      AND no stack trace appears in the response

Given: endpoint with type constraints on fields
When: request body contains a field of wrong type
Then: response is 400 with error body naming field and expected type
```

### Error safety

```
Given: any endpoint encounters an unhandled exception
When: the exception propagates to the global error handler
Then: response is 500 with RFC 7807 error body
      AND response body contains no stack trace, no file path, no internal hostname
      AND structured log contains full error with stack trace and trace_id
```

### Health and readiness

```
Given: /health endpoint
When: called regardless of dependency state
Then: response is 200 within 50ms
      AND no database query is made during the health check

Given: /ready endpoint
When: database is unreachable
Then: response is 503 within declared timeout
      AND response body names which dependency is unavailable
```

### Rate limiting

```
Given: rate limiting is declared for an endpoint
When: client exceeds the declared request limit within the window
Then: response is 429
      AND Retry-After header is present with seconds until reset
      AND X-RateLimit-Limit and X-RateLimit-Remaining headers are present
```

### Observability

```
Given: any request completes (success or error)
When: the request logger middleware runs
Then: a JSON log line is emitted with: timestamp, level, method, path, status_code, duration_ms, trace_id
      AND the log line is valid JSON
      AND no auth token or secret value appears in the log line
```

---

## Not Tested (explicit)

List what is out of scope. Verifier requires this field.

- [ ] Load testing beyond functional rate limit verification (requires separate load test environment)
- [ ] mTLS certificate rotation (ops concern — declare if in scope)
- [ ] Multi-region failover behavior (infra concern)
- [ ] [Other explicit exclusions]

---

## Platform Verification Gates

See `verification/gates.md`. These gates are registered with Verifier and must pass before Delivery wave.

1. Auth enforcement: unauthenticated request → 401 on every protected endpoint
2. Health endpoint: 200 without DB access
3. Ready endpoint: 503 when dependency is down
4. No secrets in logs: token sent, grep logs, zero matches
5. No secrets in response: 500 triggered, response body parsed, no internals exposed
6. Structured log format: every request log line is valid JSON with required fields
7. SQL injection: parameterized queries verified by code review or dynamic test
8. Rate limit: 429 returned at declared limit with Retry-After header
9. Container health: image builds, starts, passes /health check, shuts down cleanly on SIGTERM
