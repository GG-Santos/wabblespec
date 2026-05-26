# Threat Modeling Reference

Used by gateway-security Phase A to structure threat analysis output as spec inputs.

## STRIDE methodology

Apply STRIDE to each trust boundary and data flow in the system:

| Threat | Violated property | Examples |
|---|---|---|
| **S**poofing | Authentication | Impersonate user, forge tokens, ARP spoofing |
| **T**ampering | Integrity | Modify data in transit, corrupt stored records |
| **R**epudiation | Non-repudiation | Deny performing an action, forge audit logs |
| **I**nformation disclosure | Confidentiality | Read others' data, expose secrets in errors |
| **D**enial of service | Availability | Exhaust resources, crash service, rate flood |
| **E**levation of privilege | Authorization | Gain access beyond role, bypass permission check |

## Data flow diagram levels

### Level 0 — context diagram

Actors, system boundary, external systems:
```
[User] → [Our System] → [Payment Provider]
                      → [Email Service]
                      → [Database]
```

### Level 1 — system diagram

Decompose system into major components with trust boundaries:
```
[User] → |trust boundary| → [API Gateway] → [Auth Service]
                                           → [Business Service] → [Database]
                                           → [Payment Service] → [Stripe]
```

### Level 2 — component diagram

Decompose each component's internal data flows. Required for high-risk components (auth, payments, PII handling).

## Trust boundary taxonomy

Declare all trust boundaries in spec. Each boundary requires STRIDE analysis:

| Boundary type | Examples |
|---|---|
| Internet boundary | Any entry point from public internet |
| Authentication boundary | Before auth vs after auth |
| Authorization boundary | User data vs admin data |
| Service boundary | Microservice to microservice |
| Database boundary | Application to database |
| Third-party boundary | Calls to external APIs |
| Physical boundary | Client device to server |

## Threat prioritization — DREAD scoring

Score each identified threat:
- **Damage potential** (1-10): how bad is the impact?
- **Reproducibility** (1-10): how easy to reproduce?
- **Exploitability** (1-10): how much skill required?
- **Affected users** (1-10): how many users impacted?
- **Discoverability** (1-10): how easy to discover?

DREAD score = average of 5 dimensions.

Priority:
- 8-10: CRITICAL — must fix before launch
- 6-7: HIGH — fix in current sprint
- 4-5: MEDIUM — fix within 30 days
- 1-3: LOW — fix when convenient

## Threat model output format

gateway-security Phase A produces a threat model receipt with:

```json
{
  "phase": "A",
  "type": "gateway-security-phase-a",
  "assets": ["description of assets being protected"],
  "trust_boundaries": ["list of declared boundaries"],
  "threats": [
    {
      "id": "T-001",
      "stride_category": "S",
      "description": "Attacker spoofs JWT by using none algorithm",
      "affected_components": ["auth-service"],
      "dread_score": 8.5,
      "priority": "CRITICAL",
      "mitigation_required": "Verify signature algorithm in token validation; reject 'none'",
      "acceptance_criterion": "Token validation must reject any token with alg=none"
    }
  ],
  "security_requirements": [
    "Every token validation endpoint must verify the signature algorithm"
  ]
}
```

Security requirements from Phase A become acceptance criteria in the Specify output. They are not optional.

## Common threat patterns by domain

### Web applications
- XSS via user-controlled content rendered as HTML
- CSRF via state-changing GET requests or missing CSRF token
- Clickjacking via missing frame-ancestors CSP
- Open redirect via unvalidated redirect URLs

### APIs
- BOLA/IDOR via missing ownership checks on resource IDs
- Mass assignment via accepting unexpected fields
- SSRF via URL parameters used in server-side requests
- Broken authentication via JWT algorithm confusion

### Data pipelines
- SQL injection via unsanitized query construction
- PII exfiltration via misconfigured output destinations
- Data poisoning via unvalidated inputs

### IoT/Embedded
- Firmware tampering via unsigned OTA
- Credential theft via JTAG/UART access
- Network interception via missing TLS
