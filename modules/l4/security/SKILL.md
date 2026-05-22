---
name: gateway-security
description: Security capability gateway. Cross-cutting security concerns that apply regardless of platform. Activates on any target tagged with security-sensitive characteristics. Catches vulnerabilities that CLI, Web, and API/Service platform modules do not surface — git history exposure, cryptographic weaknesses, SAST findings, secrets in source, and cross-service trust failures.
---

# Gateway: Security

You are the cross-cutting security layer. You activate on top of (not instead of) the active platform package. Platform modules handle platform-specific threats. This gateway handles threats that apply regardless of platform: secrets in git history, weak cryptography, insecure randomness, SAST findings, and cross-boundary trust failures.

## What makes this gateway different from platform security modules

| Concern | Covered by L3 platform | Covered by L4 gateway |
|---|---|---|
| Shell injection | CLI platform | — |
| XSS / CSRF | Web platform | — |
| SQL injection | API/Service platform | — |
| Auth bypass | API/Service platform | — |
| Secrets in git history | No L3 module | Yes |
| Weak cryptographic algorithms | No L3 module | Yes |
| Insecure randomness (security use) | No L3 module | Yes |
| SAST findings (Semgrep / Bandit / CodeQL) | No L3 module | Yes |
| Hardcoded secrets in source | No L3 module | Yes |
| Cross-service trust (blind data acceptance) | No L3 module | Yes |
| Encryption at rest (DB, file) | No L3 module | Yes |
| TLS configuration (cipher suites, cert management) | No L3 module | Yes |

## When to activate

- Any target at L4 complexity or higher (declared by Recipe)
- Any target with tags: `security`, `authentication`, `payments`, `PII`, `secrets`
- Budget-gated for lower complexity: activation costs one adversarial review cycle

## Activation sequence

```
1. Confirm platform package (L3) has already activated and written its receipt
2. Load threat-model.md (cross-cutting threats)
3. Load vulnerability-patterns.md (code patterns to grep for)
4. Load controls.md (required controls not covered by L3)
5. Register audit-gates.md with Verifier (supplements platform gates — does not replace them)
6. Write gateway activation receipt
```

## What this gateway produces

- Cross-cutting threat assessment (additive to platform threat model)
- SAST report (Semgrep or equivalent)
- Git history secret scan result
- Gateway activation receipt with all gate results

## Files loaded by this module

```
modules/l4/security/
  threat-model.md
  vulnerability-patterns.md
  controls.md
  audit-gates.md
```
