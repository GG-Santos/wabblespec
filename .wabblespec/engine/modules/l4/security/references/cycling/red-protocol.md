# Red Protocol — Attack Phase

Activated by `/security-red` or as Phase B of a security cycle. Conducts adversarial attack simulation against the declared scope.

## Role

Red is the attacker. Red operates within the declared scope only. Red's job is to find exploitable vulnerabilities — not theoretical ones. A finding without a proof-of-concept is a suggestion, not a Red finding.

Every Red finding must produce a PoC-as-test-case: a reproducible demonstration that can be verified fixed.

## Pre-phase: InferenceGuard activation

Before Red phase begins, confirm InferenceGuard is active:

1. Check that `inference_guard: false` is NOT present in the task card
2. Verify a `gateway-security-spec-receipt-*.json` exists in the session
3. Confirm InferenceGuard tier: default is `standard` for Red protocol
4. Confirm technique: default is `leetspeak`

If InferenceGuard activation fails (module unavailable or suppressed), note in the Red cycle receipt and proceed. InferenceGuard is a support tool — Red does not block on it.

### ContextTuner profile for Red tasks

Red tasks use the `security-review` context type (temperature=0.50, top_p=0.90, top_k=50). This is model-router's default for any task shape classified as `review` with `gateway-security` active.

### Inference refusal tracking

If a PoC generation attempt is refused or truncated by the runtime:
- Set `inference_refusal: true` on the affected finding
- Document what was attempted and what was refused/truncated
- Continue with the next finding — do not halt Red phase on a single refusal

These flags accumulate into `inference_guard_summary` in the Red receipt.

## Scope enforcement

Before attacking, read the scope declaration from the security profile or task card:
- **In scope**: declared targets, environments, and attack surfaces
- **Out of scope**: explicitly excluded systems, third parties, and attack types
- **Prohibited**: DoS attacks that affect production availability; accessing data of real users

If a finding exists but requires violating scope to demonstrate it, document it as a theoretical finding with a note that verification requires explicit scope expansion.

## Attack categories (in priority order)

### Tier 1 — Authentication and Authorization
- JWT attacks: algorithm confusion (RS256 vs HS256), `alg=none`, weak signing key, missing expiry check
- BOLA/IDOR: access other users' resources by changing IDs in requests
- Privilege escalation: access higher-privilege endpoints with lower-privilege account
- Authentication bypass: skip auth entirely via parameter manipulation, direct object access

### Tier 2 — Injection
- SQL injection: union-based, blind boolean, time-based blind
- NoSQL injection: operator injection (`$gt`, `$where`)
- Command injection: via shell-executed user input
- Template injection: SSTI via template engines
- XXE: XML external entity via XML parsers

### Tier 3 — Session and State
- CSRF: state-changing requests via cross-site form or fetch
- Session fixation: attacker sets victim's session ID before login
- Session token entropy: brute-forceable session tokens
- Clickjacking: UI redress via iframe embedding

### Tier 4 — Configuration and Supply Chain
- Security headers: missing CSP, HSTS, X-Frame-Options
- CORS misconfiguration: wildcard origin with credentials
- Debug endpoints: exposed development/debugging endpoints
- Default credentials: default passwords on admin interfaces
- Outdated dependencies: known CVEs in dependencies

### Tier 5 — Business Logic
- Race conditions: TOCTOU in purchase/inventory flows
- Price manipulation: negative quantities, integer overflow in pricing
- Workflow bypass: skip required steps in multi-step processes
- Rate limit bypass: rotating IPs, header manipulation

## Finding format

Every Red finding must follow this format:

```markdown
## FINDING: {title}

**ID**: RED-{number}  
**Severity**: CRITICAL | HIGH | MEDIUM | LOW  
**Category**: {attack category from list above}  
**STRIDE**: S | T | R | I | D | E  

### Description
{One paragraph: what the vulnerability is, why it is exploitable}

### Steps to Reproduce
1. {Exact step}
2. {Exact step}
3. {Observe: expected vs actual behavior}

### Proof of Concept
```
{HTTP request, curl command, or code snippet that demonstrates the vulnerability}
```

### Impact
{What an attacker can achieve with this vulnerability}

### Affected Components
{List of affected endpoints, functions, or services}

### PoC as Test Case
```
{A test that verifies the vulnerability exists — Blue must make this test pass by fixing the vulnerability, not by patching the test}
```
```

## Severity classification

| Severity | Criteria |
|---|---|
| CRITICAL | Unauthenticated RCE, authentication bypass granting admin, mass PII exfiltration, direct payment fraud |
| HIGH | Authenticated RCE, IDOR accessing any user's data, privilege escalation to admin |
| MEDIUM | Limited IDOR (own data only), stored XSS, CSRF on sensitive actions |
| LOW | Reflected XSS, information disclosure (non-sensitive), missing security headers |

## Cycle adaptation rules

On subsequent Red cycles (Red 2, Red 3, etc.):
- Do not re-test findings that Blue has fixed and verified
- Focus on: new attack surfaces introduced since last cycle, variations of previously-found vulnerability classes, areas Blue's mitigations may not fully cover
- Escalate: if the same vulnerability class keeps appearing across cycles, flag it as a systemic issue (training gap or architecture problem)

## Output

Red produces:
1. Findings list (formatted per above)
2. PoC-as-test-case for each finding
3. Attack surface map (what was tested, what was not)
4. Cycle recommendation (continue cycling? terminate?)
5. `inference_guard_summary` in Red receipt:
   ```json
   {
     "inference_guard_active": true,
     "tier_applied": "standard",
     "activation_count": 4,
     "refusal_count": 0,
     "trigger_tier_breakdown": { "tier1": 3, "tier2": 7 }
   }
   ```
