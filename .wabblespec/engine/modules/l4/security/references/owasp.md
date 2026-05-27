# OWASP Reference

Checklists and requirements derived from OWASP Top 10, API Top 10, and ASVS. Used by gateway-security during reviews.

## OWASP Top 10 Web Application (2021)

### A01 — Broken Access Control

Controls:
- Deny access by default; require explicit permission grants
- Log access control failures; alert on repeated failures
- Rate limit API calls to minimize automated attack impact
- IDOR: verify ownership on every resource access
- CORS: declare explicit allowed origins; do not use wildcard with credentials

Spec check: does every protected endpoint declare its authorization requirement?

### A02 — Cryptographic Failures

Controls:
- TLS 1.2 minimum (1.3 preferred) for all data in transit
- No sensitive data in URLs (logged by proxies, cached by browsers)
- Passwords: Argon2id (preferred), bcrypt, or scrypt — not MD5, SHA1, or unsalted hash
- Encryption at rest for PII, payment data, health data
- No hardcoded secrets in code; rotate exposed secrets immediately

Spec check: is all PII encrypted at rest and in transit?

### A03 — Injection

Controls:
- SQL: parameterized queries or ORM — never string interpolation
- NoSQL: type-validate all query parameters
- OS command: argument arrays, not shell strings
- LDAP: sanitize before query construction
- Template injection: do not render user input as templates

Spec check: are there any places user input reaches a query or command interpreter?

### A04 — Insecure Design

Controls:
- Threat model required for all new features with security impact
- Security requirements are acceptance criteria, not afterthoughts
- Limit resource consumption per user (rate limits, quotas)
- Fail securely — failure should default to denial, not access

### A05 — Security Misconfiguration

Controls:
- Remove default credentials and accounts
- Disable debug features and stack traces in production
- Security headers: HSTS, CSP, X-Content-Type-Options, X-Frame-Options
- List of used third-party components and versions — patch regularly
- Error messages: generic to user; detailed only in server logs

### A06 — Vulnerable and Outdated Components

Controls:
- Lock file committed; dependency versions pinned
- `npm audit` / `pip-audit` / `cargo audit` in CI — fail on critical
- No unmaintained dependencies in production
- Vulnerability database subscriptions for critical dependencies (GitHub dependabot or similar)

### A07 — Identification and Authentication Failures

Controls:
- Multi-factor authentication for admin and sensitive operations
- No default passwords; credential stuffing protection (rate limit + lockout)
- Session IDs: cryptographically random, 128+ bits; regenerate after login
- Session expiry: declare timeout; automatic logout on inactivity

### A08 — Software and Data Integrity Failures

Controls:
- Verify cryptographic signatures on software updates
- CI/CD pipeline secured: code changes require review before deployment
- Serialization: do not deserialize untrusted data without type validation
- Dependencies from trusted registries only; SRI for CDN content

### A09 — Security Logging and Monitoring Failures

Controls:
- Log all authentication events (success and failure)
- Log all access control failures
- Log format: structured JSON; timestamp, user_id, action, resource, result
- Alert on: repeated auth failures, admin actions, data export operations
- Logs must be immutable (write-once storage or SIEM)

### A10 — Server-Side Request Forgery (SSRF)

Controls:
- Validate and allowlist all URLs used in server-side requests
- Do not allow user-supplied URLs to reach internal network
- Use DNS resolution validation (TOCTOU: resolve once, check, use same resolution)
- Disable HTTP redirects on server-side requests, or validate each redirect target

## OWASP API Top 10 (2023)

| ID | Name | Key control |
|---|---|---|
| API1 | Broken Object Level Authorization | Check ownership on every object access |
| API2 | Broken Authentication | Verify token on every request; check exp, aud, iss |
| API3 | Broken Object Property Level Authorization | Filter response fields by permission; no mass assignment |
| API4 | Unrestricted Resource Consumption | Rate limits, payload size limits, query complexity limits |
| API5 | Broken Function Level Authorization | Admin functions require admin role; do not rely on obscurity |
| API6 | Unrestricted Access to Sensitive Business Flows | Bot detection; business logic rate limits |
| API7 | Server Side Request Forgery | Allowlist outbound request targets |
| API8 | Security Misconfiguration | Remove debug endpoints; secure headers; disable unused methods |
| API9 | Improper Inventory Management | Document all APIs; retire old versions; test shadow APIs |
| API10 | Unsafe Consumption of APIs | Validate third-party API responses; do not trust without verification |

## ASVS Level 1 baseline (minimum for all production systems)

ASVS Level 1 = testable via black-box testing:

- Authentication: use established authentication libraries; no custom crypto
- Session management: tokens cryptographically random; minimum 128 bits entropy
- Access control: deny by default
- Cryptography: no deprecated algorithms (MD5, SHA1, DES, RC4)
- Input handling: validate all inputs; reject rather than sanitize where possible
- Output encoding: encode output for context (HTML, SQL, shell)
- Error handling: no stack traces to users; log errors server-side

ASVS Level 2 (for applications handling sensitive data):

All Level 1 requirements + verified by code review and security testing:
- Authentication: brute force protection; MFA available
- Session: secure and HttpOnly cookies; CSRF protection
- Cryptography: approved algorithms; key management declared
- Logging: comprehensive audit log; tamper-resistant
