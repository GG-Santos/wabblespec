# Secure Defaults

Secure-by-default coding patterns. Consumers: apply, gateway-security, deps.

## Principle

Security is opt-out, not opt-in. The default code path is the secure path. Insecure behavior requires explicit declaration.

## Authentication defaults

- New API endpoints: require authentication by default. Unauthenticated access requires explicit `@public` annotation or equivalent.
- Session tokens: use httpOnly + Secure + SameSite=Strict cookies. Never localStorage for auth tokens.
- Password hashing: bcrypt (cost ≥ 12) or Argon2id. Never MD5, SHA1, or unsalted SHA-256.
- Token expiry: access tokens expire in ≤ 1 hour. Refresh tokens expire in ≤ 30 days with rotation.

## Input validation defaults

- Validate at every system boundary: HTTP handlers, CLI argument parsing, file reads, queue consumers.
- Reject, then accept: default to rejecting all input and explicitly whitelist valid patterns.
- Max length enforcement on all string inputs before processing.
- Parameterized queries always. No string concatenation in SQL. No exception for "simple" queries.

## Output encoding defaults

- HTML context: always HTML-escape user-controlled strings. Never `innerHTML` with user data.
- URL context: percent-encode user data in URL components.
- JSON APIs: set `Content-Type: application/json`. Never `text/html` for JSON responses.
- Log output: sanitize user-controlled strings before logging. Never log raw request bodies containing PII.

## Cryptography defaults

- Random: use cryptographically secure RNG (`crypto.randomBytes`, `secrets.token_urlsafe`, `rand::thread_rng`). Never `Math.random()` or `random.random()` for security-sensitive values.
- Encryption: AES-256-GCM. Never ECB mode. Generate fresh IV per encryption operation.
- TLS: minimum TLS 1.2. Default TLS 1.3. Never allow SSL 3.0, TLS 1.0, TLS 1.1.

## Error handling defaults

- Public error messages: generic. Never expose stack traces, file paths, or internal state to external callers.
- Internal error messages: detailed. Log the full error for debugging.
- Auth failures: return 401 or 403. Never return 200 with an error body (confuses automated tooling).

## Dependency defaults

- Lock dependency versions in manifests (lock files committed to repo).
- Do not pin to `*` or `latest`. Specify exact or minimum version with patch ceiling.
- Review transitive dependencies for known CVEs before adding a new direct dependency.

## Common anti-patterns

| Anti-pattern | Risk | Fix |
|---|---|---|
| Storing API keys in source code | Credential exposure | Environment variables or secrets manager |
| `eval()` with user input | Remote code execution | Reject or parse with safe parser |
| Trusting user-supplied Content-Type | MIME confusion attacks | Re-detect MIME from content, not header |
| Logging full request body | PII exposure | Redact or exclude sensitive fields before logging |
| Disabled TLS cert verification | MITM | Never `verify=False` outside local dev |
