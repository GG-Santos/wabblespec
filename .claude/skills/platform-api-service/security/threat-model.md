# API/Service Security — Threat Model

## Threat Surface

An API or service accepts requests from untrusted callers over a network. Primary attack vectors:

1. **Broken authentication** — missing, bypassable, or incorrectly implemented auth
2. **Injection** — SQL, NoSQL, command, LDAP injection via unsanitized input
3. **IDOR (Insecure Direct Object Reference)** — accessing another user's resources by guessing IDs
4. **SSRF (Server-Side Request Forgery)** — service making requests to internal infrastructure via attacker-supplied URLs
5. **Mass assignment** — accepting and persisting fields the client should not control
6. **Sensitive data exposure** — leaking secrets, PII, or internal details in responses or logs
7. **Rate limit abuse** — credential stuffing, enumeration, denial-of-service via API
8. **Supply chain** — malicious code in dependencies

---

## Threat 1: Broken Authentication

**Description:** Endpoints that require authentication are reachable without valid credentials, or auth can be bypassed by crafting specific inputs.

**Attack scenarios:**
```http
GET /api/users/123
# No Authorization header → should be 401, but handler runs anyway

GET /api/admin/users
Authorization: Bearer eyJ...  (valid user token, not admin scope)
# Should be 403, but returns data
```

**Mitigations:**
- Auth middleware runs before every protected handler — no exceptions
- Auth is applied at framework level (middleware registration), not per-handler (easy to forget)
- Token validation is complete: signature, expiry, issuer, audience, required scopes
- Admin/privileged scopes checked separately from basic auth
- JWT `none` algorithm rejected — validate algorithm is in explicit allowlist

**Verification gate:** Unauthenticated request to every protected endpoint returns 401. No handler logic or DB query executes.

---

## Threat 2: Injection

**Description:** Attacker sends crafted input that changes the meaning of a database query, shell command, or template.

**Attack scenarios:**
```
# SQL injection via filter parameter
GET /api/users?name=' OR '1'='1

# NoSQL injection via JSON body
POST /api/login
{"username": {"$gt": ""}, "password": {"$gt": ""}}

# Command injection if service shells out
POST /api/convert
{"filename": "file.pdf; rm -rf /data"}
```

**Mitigations:**
- SQL: parameterized queries exclusively. No string concatenation in query construction.
- NoSQL: schema validation on input before passing to DB driver. Type-check all operator fields.
- Shell: never shell out with user-supplied input. If unavoidable, use exec-array form (never shell=True / exec with string).
- Template injection: user-supplied values are data, not template fragments.

**Verification gate:** Code review for string interpolation in query context. Dynamic test: `' OR '1'='1` as filter parameter → 400, no data returned.

---

## Threat 3: IDOR (Insecure Direct Object Reference)

**Description:** Service returns or modifies resources identified by predictable IDs without verifying the authenticated user has access to that specific resource.

**Attack scenario:**
```http
GET /api/invoices/1001
Authorization: Bearer <user-A's-token>
# Returns user B's invoice if ownership is not checked
```

**Mitigations:**
- For every endpoint that returns a resource by ID: verify resource ownership before fetching, or use authorization policy that includes ownership check
- Use opaque IDs (UUIDs) rather than sequential integers — does not eliminate the bug but raises the bar
- 403 (not 404) when user lacks access — 404 leaks resource existence
- Add ownership check to integration test suite for every resource endpoint

**Verification gate:** Integration test: user A requests user B's resource with valid auth → 403. No data from user B returned.

---

## Threat 4: SSRF (Server-Side Request Forgery)

**Description:** Service accepts a URL from a client and fetches it server-side. Attacker supplies an internal URL to probe or attack internal infrastructure.

**Attack scenarios:**
```json
POST /api/webhooks
{"callback_url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}

POST /api/fetch
{"url": "http://internal-db-host:5432"}
```

**Mitigations:**
- If user-supplied URLs are fetched: validate against an explicit allowlist of permitted domains/schemes
- Block private IP ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.1, 169.254.0.0/16
- Block non-HTTP schemes: file://, gopher://, ftp://
- DNS rebinding protection: resolve hostname once, validate IP, use resolved IP for connection
- If no URL fetching needed: do not implement it

**Verification gate:** If URL-fetching exists: test with `http://169.254.169.254/` → request rejected before network call made.

---

## Threat 5: Mass Assignment

**Description:** API accepts object fields the client should not control (e.g., `is_admin`, `role`, `user_id`) because it blindly maps request body to data model.

**Attack scenario:**
```json
POST /api/users/profile
{
  "name": "Alice",
  "is_admin": true,
  "account_balance": 99999
}
```

**Mitigations:**
- Declare explicit allowed fields for each endpoint — never pass raw request body to ORM/DB
- Use a dedicated input schema (DTO/Pydantic model/Zod schema) per endpoint that excludes privileged fields
- Fields like `id`, `created_at`, `is_admin`, `role`, `user_id` are server-controlled — strip from input before persistence

**Verification gate:** POST /api/users/profile with `is_admin: true` in body → field is ignored, user remains non-admin. Confirm via GET of the user record.

---

## Threat 6: Sensitive Data Exposure

**Description:** Secrets, PII, internal paths, stack traces, or other sensitive data leaks in API responses or logs.

**Attack scenarios:**
```
# Stack trace in 500 response reveals framework, file paths, internal logic
# Error message reveals "User with email X not found" — confirms email exists (enumeration)
# Log line contains Bearer token value — logged by default request logger
```

**Mitigations:**
- Global error handler serializes all errors to RFC 7807 format — no raw exceptions
- Auth tokens and secrets scrubbed from log lines (replace header value with `[REDACTED]`)
- Enumeration prevention: "user not found" and "wrong password" return identical 401 response
- Source maps not served publicly
- Response bodies for 4xx/5xx never include database query text, internal hostnames, or file paths

**Verification gate:** Trigger 500 — response body contains no stack trace. Send known token — grep logs, zero matches.

---

## Threat 7: Rate Limit Abuse

**Description:** Attacker sends high-volume requests to enumerate resources, brute-force credentials, or degrade service for other users.

**Attack scenarios:**
```
# Credential stuffing: POST /api/login with list of common passwords
# Resource enumeration: GET /api/users/1, /users/2, /users/3...
# Denial of service: flood expensive endpoint
```

**Mitigations:**
- Rate limiting on all public endpoints: per-IP for unauthenticated, per-client-identity for authenticated
- Auth endpoints (login, token refresh): tighter limit than read endpoints
- 429 response with Retry-After header — do not silently drop, communicate the limit
- Account lockout for repeated auth failures (with reset mechanism)
- Exponential backoff signaling via Retry-After

**Verification gate:** Send requests at limit+1 rate → 429 returned at declared threshold with Retry-After.

---

## Threat 8: Supply Chain

**Description:** Malicious code injected via compromised npm/PyPI/crates.io package.

**Mitigations:**
- Lock file committed (package-lock.json / requirements.txt pinned / Cargo.lock / go.sum)
- Dependency audit in CI: `npm audit` / `pip-audit` / `cargo audit` — block on critical/high
- Container image scanning: Trivy or equivalent — block on critical CVEs
- Minimize dependencies — each package is an attack surface
- Private packages: verify registry source. Use registry allowlist in npm config if applicable.

**Verification gate:** `npm audit` / `pip-audit` zero critical/high findings. Trivy image scan zero critical CVEs (or waived with documented justification).
