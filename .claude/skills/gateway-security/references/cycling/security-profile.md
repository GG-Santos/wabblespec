# Security Profile Template

Intel phase output. Produced by `/security-intel` before the first Red/Blue cycle. Describes the target from the attacker's perspective.

## Purpose

The security profile is the attacker's reconnaissance output. It captures what an attacker would learn about the system before attacking. This is the input to Red phase — Red uses it to prioritize attack paths.

## Template

```markdown
# Security Profile: {System Name}

**Date**: {YYYY-MM-DD}
**Version**: {application version or commit SHA}
**Engagement type**: {internal review | external pentest | pre-launch | annual}
**Posture target**: {target score from 0-10; default 7.5}
**Max cycles**: {default 5}
**InferenceGuard tier**: {light | standard | heavy — default: standard}
**InferenceGuard technique**: {leetspeak | unicode | mixedcase | random — default: leetspeak}

---

## 1. Asset Inventory

| Asset | Type | Criticality | Notes |
|---|---|---|---|
| {name} | {web app / API / service / database / file store} | {CRITICAL / HIGH / MEDIUM} | {notes} |

**Crown jewels** (highest-value assets that attackers target first):
- {asset}: {why it is high-value}

---

## 2. Technology Fingerprint

| Component | Technology | Version | Known CVEs |
|---|---|---|---|
| Frontend | {React 18 / Vue 3 / ...} | {version} | {none / CVE-XXX} |
| API | {Express / FastAPI / ...} | {version} | {none / CVE-XXX} |
| Auth | {JWT / sessions / OAuth} | {library + version} | {none / CVE-XXX} |
| Database | {PostgreSQL 15 / MongoDB 7} | {version} | {none / CVE-XXX} |
| Cache | {Redis 7 / Memcached} | {version} | {none / CVE-XXX} |
| Dependencies | {npm 847 packages, 3 high-severity CVEs pending} | | |

---

## 3. Attack Surface Map

### Entry points

| Entry point | Auth required | Rate limited | Notes |
|---|---|---|---|
| {POST /api/auth/login} | No | Yes (5/min) | Public auth endpoint |
| {GET /api/users/:id} | Yes | No | Potential IDOR |
| {POST /api/payments} | Yes | Yes | High-value target |
| {WebSocket /ws} | Yes | No | Real-time channel |
| {Admin panel /admin} | Yes (admin only) | No | Separate auth context |

### Interesting parameters

Parameters that accept user-controlled data affecting server behavior:
- `{id}` parameters: potential IDOR
- `redirect_url` parameter on login: potential open redirect
- File upload endpoints: type validation, path traversal
- Search fields: injection potential

---

## 4. Trust Boundaries

| Boundary | From | To | Authentication mechanism |
|---|---|---|---|
| Internet → API | Public internet | API gateway | Bearer JWT |
| API → Database | Application | PostgreSQL | Connection string (env var) |
| API → External | Application | Stripe, SendGrid | API keys (env var) |
| Admin → API | Admin users | Admin endpoints | JWT + admin role |

---

## 5. Data Flows — PII and Sensitive Data

| Data | Collected at | Stored in | Transmitted to | Protected by |
|---|---|---|---|---|
| Email | Registration | users table | SendGrid | TLS, AES-256 at rest |
| Password | Registration | users table (bcrypt hash) | Never transmitted | bcrypt hash |
| Payment info | Checkout | Stripe only (tokenized) | Stripe API | TLS, not stored locally |
| Session token | Login | Redis + HttpOnly cookie | All API requests | HttpOnly, Secure, SameSite |

---

## 6. Dependency Risk

Dependencies with known vulnerabilities at time of scan:
- {package@version}: {CVE-XXXX}: {severity}: {patch available: yes/no}

Dependencies of note:
- {package@version}: {why it is noteworthy — deprecated, no longer maintained, wide attack surface}

---

## 7. Configuration Baseline

| Setting | Current state | Expected state | Gap |
|---|---|---|---|
| HTTPS enforced | Yes | Yes | None |
| HSTS enabled | No | Yes | Missing |
| CSP header | Partial (unsafe-inline) | Strict | Reduce unsafe-inline |
| Rate limiting on auth | Yes | Yes | None |
| Debug mode in prod | Unknown | Off | Verify |
| Secrets in env vars | Yes | Yes | None |

---

## 8. Previous Findings (if re-engagement)

| Finding ID | Severity | Status | Notes |
|---|---|---|---|
| RED-001 | HIGH | Fixed (cycle 1) | IDOR on /users/:id — patched |
| RED-002 | MEDIUM | Deferred | CSRF on preference update — compensating control in place |

---

## Red Phase Input

Priority attack paths for Red (based on above analysis):
1. {Highest-priority attack path and why}
2. {Second priority}
3. {Third priority}

Areas to avoid (out of scope or already verified):
- {Area}: {reason}
```
