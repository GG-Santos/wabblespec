# API Security Framework

Security requirements for HTTP APIs and services. Loaded alongside api/core.md.

## Authentication

### Bearer token (JWT)

```
Authorization: Bearer <token>
```

- Verify signature on every request — do not trust unverified claims
- Check `exp` claim — reject expired tokens
- Check `aud` claim — token must be issued for this service
- Check `iss` claim — token must come from trusted issuer
- Use asymmetric keys (RS256/ES256) for token verification — no shared secrets across services

### API keys

- Keys must be hashed (SHA-256) before storage — never store raw
- Keys are not JWTs — use opaque random strings (32+ bytes, URL-safe base64)
- Associate key with: owner identity, created date, last used date, rate limit tier
- Key rotation: support multiple valid keys per owner; provide rotation workflow

### mTLS

- Required for: service-to-service internal calls in zero-trust environments
- Client certificate validated against CA; service identity extracted from certificate Subject
- Spec must declare: CA, certificate rotation policy

## Authorization

```
Authentication: Who are you? (identity)
Authorization: What are you allowed to do? (permission)
```

- RBAC (Role-Based): user has role; role has permissions — declare role matrix in spec
- ABAC (Attribute-Based): permission depends on resource attributes — declare policy rules
- Every endpoint must declare: authentication required? authorization check? which permission?

Anti-pattern: checking authorization in the business layer instead of at the handler/middleware level. Authorization belongs at the request boundary.

## Injection prevention

- SQL injection: parameterized queries only; never string-interpolate user input into SQL
- NoSQL injection: validate types; do not pass user objects directly as filter documents
- Command injection: never pass user input to shell commands; if subprocess is needed, use argument arrays
- SSRF (Server-Side Request Forgery): validate and allowlist URLs before making outbound requests on behalf of user input

## Input validation

- Validate at the boundary (request handler) before any business logic
- Type coercion is not validation — check constraints too (length, range, format)
- Reject unknown fields in strict mode (do not silently ignore extra fields — they may be injection vectors)
- File uploads: validate MIME type server-side (not from Content-Type header); check file size; scan if untrusted content

## Sensitive data in transit and storage

- TLS 1.2 minimum; TLS 1.3 preferred — declare in spec
- No sensitive data in URL params (logged in proxy, browser history): auth tokens, session IDs, PII
- Response bodies: mask PII in logs; declare which fields are masked
- Encryption at rest: declare for PII and secret fields

## IDOR (Insecure Direct Object Reference)

Every endpoint that takes a resource ID must:
1. Check that the authenticated user has permission to access that specific resource
2. Use opaque IDs (UUIDs) rather than sequential integers where possible
3. Declare the ownership check in spec (e.g., "user_id on resource must match authenticated user_id")

## Headers

Required response headers for all APIs:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Omit `Server` header or set to non-identifying value.
