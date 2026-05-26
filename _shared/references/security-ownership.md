# Security Ownership

Module security responsibility map. Who owns what in the security posture. Consumers: gateway-security, audit, guard.

## Responsibility matrix

| Security concern | Primary owner | Supporting modules |
|---|---|---|
| Threat modeling | gateway-security | specify (threat surface in task card) |
| Vulnerability detection | gateway-security, deps | audit |
| Secure code patterns | apply | gateway-security (gate), gateway-engineering |
| Input validation | executor (implementation) | guard (enforcement), gateway-security (review) |
| Dependency CVEs | deps | gateway-security |
| License compliance | deps | audit |
| Accessibility (WCAG) | audit | gateway-experience |
| Privacy / GDPR | audit | specify (PII declarations in task card) |
| Secret management | apply | guard (blocks hardcoded secrets) |
| Authentication patterns | apply | gateway-security, secure-defaults.md |
| Log sanitization | executor | guard (PII check) |
| TLS configuration | apply, deploy | gateway-security |

## Guard's security scope

Guard is enforcement, not design. Guard:
- Blocks operations that match command-risk-policy.md CRITICAL tier
- Flags scope violations (module writing outside declared boundary)
- Detects prompt injection attempts in reviewed artifacts
- Does NOT design security — that is gateway-security's role

## Gateway-security scope

gateway-security is the security gate, not the security implementer. It:
- Reviews the task card for security surface (threat model)
- Evaluates wave plan for security risks before execution
- Emits PASS/FLAG/BLOCK verdict
- Does NOT write secure code — Apply implements; gateway-security reviews

## Deps scope

Deps is supply chain security only:
- CVE scanning of declared dependencies
- License compliance
- Maintainer activity / supply chain integrity
- Does NOT audit code written in this session — that is gateway-security's role

## Audit scope

Audit is compliance verification post-execution:
- WCAG accessibility
- GDPR / privacy
- License compliance (cross-reference with Deps SBOM)
- Guard log review (policy violations in this session)
- Does NOT run during execution — runs after, as a gate before delivery

## Security incident escalation path

```
Detected security issue
  → severity CRITICAL: BLOCK immediately → surface to human → halt execution
  → severity HIGH: FLAG in receipt → notify human → human decides to proceed or halt
  → severity MEDIUM: LOG in receipt → continue → address in next session
  → severity LOW: LOG only
```

Any module detecting a security issue routes through this escalation path. Modules do not silently absorb security findings.
