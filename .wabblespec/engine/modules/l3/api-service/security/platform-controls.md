# API/Service Security — Platform Controls

These controls apply to all API/Service targets. Enforced by Verifier via `verification/gates.md`.

---

## Control 1: Auth Middleware Before All Protected Handlers

**Rule:** Authentication middleware must be registered at the framework level and execute before any handler logic on protected routes. Per-handler auth checks are insufficient.

**Required pattern:**
```typescript
// Fastify — register globally, then exempt public routes
app.addHook('onRequest', authMiddleware)
app.get('/health', { onRequest: [] }, healthHandler)  // exempt

// Express — apply before routes
app.use('/api', authMiddleware)
app.use('/api', routes)
```

**Banned pattern:**
```typescript
// Per-handler auth check — easy to forget on new endpoints
app.get('/api/users', async (req, res) => {
  if (!req.headers.authorization) return res.status(401).send()  // missed on next endpoint
  // handler logic
})
```

**Exception process:** Public endpoints (health, ready, well-known) must be explicitly exempted by name in middleware registration — not by omitting the middleware.

---

## Control 2: Parameterized Queries Only

**Rule:** No user-supplied value may be concatenated into a database query string.

**Banned patterns:**
```python
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")  # SQL injection
cursor.execute("SELECT * FROM users WHERE name = " + user_input)    # SQL injection
```
```typescript
db.query(`SELECT * FROM users WHERE name = '${req.body.name}'`)     // SQL injection
```
```go
db.Query("SELECT * FROM users WHERE name = '" + name + "'")         // SQL injection
```

**Required patterns:**
```python
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```
```typescript
db.query('SELECT * FROM users WHERE name = $1', [req.body.name])
```
```go
db.Query("SELECT * FROM users WHERE name = $1", name)
```

---

## Control 3: Input Schema Validation at Boundary

**Rule:** Every endpoint that accepts a request body or query parameters must validate input against a declared schema before any processing.

**Implementation:**
- Request body: validate type, required fields, field constraints before handler runs
- Query parameters: validate type and format (e.g., UUID format for ID params)
- Schema validation runs in middleware or framework-level validation layer — not ad-hoc in handler
- Invalid input: 400 with error body naming the offending field(s)

**Tools:** Zod (TypeScript), Pydantic (Python), go-validator (Go), serde (Rust), JSON Schema.

---

## Control 4: Ownership Check Before Resource Access

**Rule:** Any endpoint that returns, modifies, or deletes a resource identified by an ID must verify the authenticated user has access to that specific resource.

**Implementation order:**
1. Authenticate (middleware)
2. Validate input (middleware or handler start)
3. Check resource ownership (before DB read — or check in DB query with `WHERE id = $1 AND user_id = $2`)
4. Return data

**Banned pattern:**
```python
user = db.get_user(user_id)           # fetches without ownership check
return user                            # IDOR: returns any user's data
```

**Required pattern:**
```python
user = db.get_user(user_id, owner_id=current_user.id)  # ownership in query
if not user:
    raise ForbiddenError()             # 403, not 404
return user
```

---

## Control 5: No Secrets in Logs

**Rule:** Auth tokens, API keys, passwords, and secret values must never appear in log output.

**Implementation:**
- Request logger: log Authorization header presence (`present` / `absent`), never its value
- Error handler: scrub known secret patterns before logging (regex on message and context fields)
- Application logs: never log request body fields marked as sensitive in schema

**Scrub pattern (TypeScript example):**
```typescript
function scrubHeaders(headers: Record<string, string>) {
  return {
    ...headers,
    authorization: headers.authorization ? '[REDACTED]' : undefined,
    'x-api-key': headers['x-api-key'] ? '[REDACTED]' : undefined,
  }
}
```

---

## Control 6: RFC 7807 Error Responses

**Rule:** All error responses (4xx and 5xx) must use the declared error schema. No raw exceptions, framework default error pages, or ad-hoc error formats.

**Implementation:**
- Register a global error handler that catches all unhandled exceptions
- Serialize errors to RFC 7807 (or declared schema) before sending
- HTTP status code must match the `status` field in the body
- Stack traces, database error messages, and internal paths must never appear in the response body

**Exception handling chain:**
```
Exception thrown in handler
  → Caught by global error handler
  → Classified (4xx vs 5xx, client vs server error)
  → Serialized to RFC 7807
  → Full error logged at ERROR level with trace_id
  → Sanitized response sent to client
```

---

## Control 7: SSRF Prevention for URL-Fetching Endpoints

**Rule:** If the service fetches a URL supplied by a client, it must validate the URL against an explicit allowlist before making the request.

**Applies only if:** The service makes outbound HTTP requests to client-supplied URLs.

**Validation steps (must all pass before fetch):**
1. Parse URL — reject if not valid HTTP/HTTPS
2. Resolve hostname to IP
3. Reject if IP is in private/reserved range
4. Reject if scheme is not http or https
5. Fetch using resolved IP (prevent DNS rebinding)

**Private ranges to block:** 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16, ::1

---

## Control 8: Security Headers on All Responses

**Rule:** The following headers must be present on all HTTP responses.

| Header | Required value |
|---|---|
| `Content-Type` | Must be set and accurate (never `text/html` for JSON responses) |
| `X-Content-Type-Options` | `nosniff` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (HTTPS only) |
| `X-Frame-Options` | `DENY` (APIs should not be embedded in frames) |

**For JSON APIs specifically:** `Content-Type: application/json` on all successful responses. `application/problem+json` on error responses (RFC 7807).

**Not required for APIs (differs from web):** `Content-Security-Policy` (no HTML), `Referrer-Policy` (no browser interaction).

---

## Control 9: Dependency Audit Gate

**Rule:** Zero critical or high dependency vulnerabilities before release.

**CI integration:**
```bash
npm audit --audit-level=high     # fail on high or critical
pip-audit --fail-on-known        # fail on any known CVE
cargo audit --deny warnings      # fail on advisory
```

**Container image:**
```bash
trivy image --exit-code 1 --severity HIGH,CRITICAL <image>:<tag>
```

**Waiver process:** Critical findings with no fix available documented in `SECURITY.md` with: CVE ID, affected version, impact assessment, mitigating controls, remediation timeline.
