# WabbleSpec v6.1 — Security

**Gateway:** Security
**Layer:** L4 Capability
**Tier:** 1 — CRITICAL ROUTING
**Document scope:** Security gateway — cross-cutting threat modeling, OWASP, continuous security, compliance

---

## Overview

The Security gateway is a cross-cutting capability that applies to every build target. It does not own target-specific security concerns — those live in their respective L3 platform packages. The Security gateway owns the principles, checklists, and policy that apply regardless of target: threat modeling, OWASP compliance, continuous security cycles, and compliance framework scoping.

**In scope (cross-cutting):**
- Threat modeling (STRIDE methodology, DFD, trust boundaries)
- OWASP checklists (Top 10, API Security Top 10, Mobile Top 10, ASVS)
- Continuous security (dependency scanning, SAST, secret scanning, pentest)
- Compliance frameworks (GDPR, SOC 2, HIPAA, PCI-DSS)
- Cross-cutting auth and secrets policy

**Explicitly not in scope (owned by L3 platform packages):**
- Firmware signing (IoT/Embedded platform)
- App permissions and entitlements (Mobile platform)
- Extension sandboxing (Extension/Plugin platform)
- Library supply chain security (Library/Package platform)

---

## Gateway Structure

```
.wabblespec/gateways/security/
  SKILL.md
  skill-rules.json
  references/
    threat-modeling.md
    owasp.md
    continuous-security.md
    compliance.md
  rules/
    auth-policy.md
    secrets-policy.md
  evaluations/
  schemas/
    receipt.schema.json
```

---

## Activation

`skill-rules.json` triggers Security gateway on:
- P3 or P4 spec stage — security review always runs before Technical Spec locks
- Explicit `/security` command
- Verifier Audit mode — Security consulted for Audit verification
- Platform security modules forwarding cross-cutting concerns upward from L3

---

## Threat Modeling

**Reference:** `references/threat-modeling.md`

**Methodology:** STRIDE

| Threat | Definition |
|---|---|
| Spoofing | Impersonating something or someone |
| Tampering | Modifying data or code without authorization |
| Repudiation | Performing actions that cannot be traced or denied |
| Information Disclosure | Exposing data to unauthorized parties |
| Denial of Service | Degrading service availability |
| Elevation of Privilege | Gaining capabilities beyond what is granted |

**Threat model artifact:** Required in P2 Systems Design for all targets. No P3 Technical Spec without a threat model present.

**DFD (Data Flow Diagram):**
- Level 0: required for all targets — system boundary and external actors
- Level 1: required for all targets — major components and data flows
- Level 2: required for complex targets (API/Service, Data/Pipeline, AI/Agent)

**Trust boundaries:** Every external input crosses a trust boundary. All trust boundaries must be declared in the threat model. No undeclared data entry points.

---

## OWASP Checklists

**Reference:** `references/owasp.md`

| Target | Applicable checklist |
|---|---|
| Web | OWASP Top 10 (Web) |
| API/Service | OWASP Top 10 (Web) + OWASP API Security Top 10 |
| Mobile | OWASP Mobile Top 10 (forwarded from Mobile platform package) |
| All targets | OWASP ASVS Level 1 baseline |
| High-assurance targets | OWASP ASVS Level 2 |

**OWASP ASVS Level 1** is the baseline for all targets regardless of complexity. High-assurance applications (healthcare, finance, government) require Level 2. Level 3 is not required by v6.1 — it must be explicitly declared in spec.

---

## Continuous Security

**Reference:** `references/continuous-security.md`

| Control | When | Gate behavior |
|---|---|---|
| Dependency scanning | Every build | Block on critical CVEs |
| SAST (static analysis) | CI — every push | Block on high/critical findings |
| Secret scanning | Pre-commit hook + CI | Block on any detected secret |
| Penetration testing | Scope declared in spec | When and by whom declared at P1 |

**Dependency scanning:** Automated. Uses declared tooling (Snyk, Dependabot, OSV-Scanner, or platform equivalent). Critical CVEs block build. High CVEs flag with required resolution window declared in spec.

**SAST:** Integrated into CI pipeline before deploy stage. High and critical findings block deployment. Medium findings escalate to Engineering gateway review.

**Secret scanning:** Pre-commit hook required. CI gate as second layer. Any detected secret blocks push. No exceptions — rotation required after any exposure event.

**Penetration testing:** Scope must be declared in spec at P1 (none / internal / third-party / continuous). Not required, but must be explicitly declared. Undeclared = internal review minimum.

---

## Compliance Frameworks

**Reference:** `references/compliance.md`

Compliance scope declared in P1 Design Document. Undeclared = no compliance framework applied beyond OWASP baseline.

| Framework | Trigger | Key requirements |
|---|---|---|
| GDPR | Personal data of EU residents processed | Data processing inventory, consent management, right to erasure |
| SOC 2 | SaaS products with enterprise customers | Controls mapping (declared type: Type I / Type II) |
| HIPAA | Health data in scope | Encryption at rest and in transit, audit logging, BAA required |
| PCI-DSS | Payment card data in scope | Scope reduction via tokenization preferred over full PCI-DSS |

**Scope reduction principle:** For PCI-DSS, the preferred approach is tokenization — reduce the scope of cardholder data to the minimum. Full PCI-DSS scope is avoided unless the business case requires it.

---

## Cross-Cutting Rules

### Auth Policy (`rules/auth-policy.md`)

- Every external endpoint has a declared auth requirement — unauthenticated access must be explicit, not default
- Session management: tokens expire (access tokens: short-lived, refresh tokens: longer with rotation)
- Refresh token rotation: every use generates a new refresh token; old token invalidated
- MFA: required for admin interfaces and high-value actions (payment, deletion, account changes)
- Auth mechanism declared in P2 Systems Design (OAuth 2.0, OIDC, API keys, mTLS, etc.)

### Secrets Policy (`rules/secrets-policy.md`)

- No secrets in: code, config files, committed environment files, logs, error messages, URLs
- Rotation policy: API keys rotated on any exposure event, no grace period
- Production secret management: vault or secret manager declared in spec (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, etc.)
- Development secrets: `.env` files only, `.env` in `.gitignore`, never `.env.example` with real values
- Signing credentials: env vars only — never from code or spec files (Package module enforces this)

---

## Integration Points

| Module | Relationship |
|---|---|
| Apply | Apply reads Security gateway SKILL.md for routing decisions during execution |
| Verifier | Verifier Audit mode consults Security gateway for checklist completion |
| Platform packages (L3) | Platform security modules forward cross-cutting concerns upward to Security gateway |
| Reviewer | Reviewer consults Security gateway during budget-gated review of security-relevant changes |
| Specify | Specify consults Security rules when classifying spec changes as BREAKING (auth changes = BREAKING) |
| Package (L7) | Package signing policy cross-checked against Security gateway credentials policy |
| Deploy (L7) | Deploy production hardening checklist sourced from Security gateway |
| Monitor (L7) | Security alerts and anomaly detection patterns from Security gateway |

---

## Verification Mode

**Audit** — security checklist completed per target, threat model present in P2 artifacts, no critical or high SAST findings, no secrets in repo, compliance scope declared.

---

## Receipt Extension Fields

```json
{
  "threat_model_present": true,
  "owasp_checklist": "OWASP Top 10 + API Security Top 10",
  "critical_findings": 0,
  "high_findings": 0,
  "compliance_scope": ["GDPR"],
  "pentest_required": false
}
```

---

## Cross-References

- L3 Platform packages (platform-specific security): `WabbleSpec v6.1 — Platform.md`
- L7 Package (artifact signing): `WabbleSpec v6.1 — Delivery.md` § Package
- L7 Deploy (production hardening): `WabbleSpec v6.1 — Delivery.md` § Deploy
- Engineering gateway (CI pipeline, SAST integration): `WabbleSpec v6.1 — Engineering.md`
- Verification modes: `WabbleSpec v6.1 — Core.md` § Verification Modes
