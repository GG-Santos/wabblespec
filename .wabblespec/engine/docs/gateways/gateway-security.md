# Gateway: Security

Cross-cutting security layer. Activates on any target with security-sensitive characteristics — auth, payments, PII, secrets, infra, or external APIs. Handles threats that L3 platform modules do not cover.

**Skill:** `modules/l4/security/SKILL.md`
**Rules files:** `modules/l4/security/audit-gates.md`, `controls.md`, `threat-model.md`, `vulnerability-patterns.md`

## What this gateway covers (that L3 does not)

| Threat | L3 platform | L4 security gateway |
|--------|-------------|---------------------|
| Shell injection | CLI platform | — |
| XSS / CSRF | Web platform | — |
| SQL injection | API/Service platform | — |
| Auth bypass | API/Service platform | — |
| Secrets in git history | No L3 covers this | Yes |
| Weak cryptographic algorithms | No L3 covers this | Yes |
| Insecure randomness in security context | No L3 covers this | Yes |
| SAST findings (Semgrep / Bandit / CodeQL) | No L3 covers this | Yes |
| Hardcoded secrets in source | No L3 covers this | Yes |
| Cross-service trust (blind data acceptance) | No L3 covers this | Yes |
| Encryption at rest | No L3 covers this | Yes |
| TLS configuration (cipher suites, cert management) | No L3 covers this | Yes |

## When this gateway activates

- Any target at Medium/High complexity
- Any target tagged: `security`, `authentication`, `payments`, `PII`, `secrets`, `infra`, `external-api`
- Explicit invocation: `/gateway-security`

## Sequencing

This gateway runs first in the gateway chain. A BLOCK from this gateway stops the entire chain — remaining gateways do not run on a security-blocked execution.

## Verdict rules

**BLOCK** on:
- Hardcoded credentials or secrets in any file reaching product space
- Use of known-broken algorithms (MD5/SHA1 for security, DES, RC4)
- Unauthenticated endpoints handling PII
- SAST findings at severity HIGH or CRITICAL

**FLAG** on:
- Secrets management not declared (no vault, no env-based secrets)
- Missing encryption at rest declaration for PII storage
- TLS configuration not explicitly specified
- Dependencies with unpatched CVEs at MEDIUM severity

**PASS** when all BLOCK conditions are absent and FLAG items are either absent or accepted.
