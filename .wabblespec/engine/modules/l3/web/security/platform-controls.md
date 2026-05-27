# Web Security — Platform Controls

Enforced by Verifier via `verification/gates.md`. All controls apply to all Web targets.

---

## Control 1: Content Security Policy

**Rule:** CSP header required in production. `report-only` does not satisfy this gate.

**Minimum viable CSP:**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' <declared-api-origins>;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self'
```

**`unsafe-inline` for scripts:** Not permitted. If inline scripts required, use nonces or hashes.
**`unsafe-eval`:** Not permitted. React/Vue/Svelte do not require eval in production.

**Process:** Start with `report-only`, monitor violations, tighten to enforcing. Gate requires enforcing mode.

---

## Control 2: Security Headers Baseline

Required headers on all HTML responses:

| Header | Required value |
|---|---|
| `Content-Security-Policy` | Enforcing (not report-only) |
| `X-Frame-Options` | `DENY` (or CSP frame-ancestors) |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Declare — restrict unused browser features |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (HTTPS only) |

**Verification:** `curl -I <url>` output checked. Missing headers = gate failure.

---

## Control 3: No dangerouslySetInnerHTML Without Sanitization

**Rule:** Every use of `dangerouslySetInnerHTML` (React), `v-html` (Vue), or `innerHTML` assignment with variable content must wrap the value in `DOMPurify.sanitize()`.

**Required pattern:**
```typescript
import DOMPurify from 'dompurify'

// Only acceptable form:
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
```

**Banned patterns:**
```typescript
<div dangerouslySetInnerHTML={{ __html: userContent }} />     // no sanitization
element.innerHTML = userInput                                  // DOM manipulation
document.write(userInput)                                     // always banned
```

**Enforcement:** ESLint rule `react/no-danger` configured to warn, code review escalates to block on any unreviewed usage.

---

## Control 4: Auth Token Storage

**Rule:** Session tokens and JWTs that grant API access must be stored in `httpOnly` cookies.

**Forbidden storage locations:**
- `localStorage` — XSS accessible
- `sessionStorage` — XSS accessible
- Non-httpOnly cookies — XSS accessible

**Required cookie attributes:**
```
Set-Cookie: session=<token>; HttpOnly; Secure; SameSite=Strict; Path=/
```

**Exception:** Short-lived, non-privileged tokens for non-sensitive read operations may use memory storage (not localStorage). Must be declared in auth model with justification.

---

## Control 5: No Secrets in Client Bundle

**Rule:** Environment variables that are not `NEXT_PUBLIC_` / `VITE_` prefixed must never appear in client-side code.

**Pre-deploy check (CI):**
```bash
# Scan built bundle for common secret patterns
grep -r "sk-" dist/
grep -r "Bearer " dist/
grep -r "postgres://" dist/
grep -rE "[A-Za-z0-9]{32,}" dist/ | grep -v "node_modules"
```

**Framework enforcement:**
- Next.js: server-only imports via `import 'server-only'` in data fetching modules
- Vite: `import.meta.env.VITE_*` only in client code

---

## Control 6: CORS Configuration

**Rule:** `Access-Control-Allow-Origin: *` forbidden in production for authenticated endpoints.

**Required:** Explicit origin allowlist. Wildcard permitted only for fully public, unauthenticated static assets.

**Declare in systems-design.md:** Which origins are permitted for which endpoint groups.

---

## Control 7: Subresource Integrity

**Rule:** Any `<script>` or `<link>` tag referencing an external domain must include `integrity` and `crossorigin` attributes.

```html
<!-- Required form for external scripts -->
<script
  src="https://cdn.example.com/lib.min.js"
  integrity="sha384-<hash>"
  crossorigin="anonymous"
></script>
```

**Process:** Generate hash with `openssl dgst -sha384 -binary lib.min.js | openssl base64 -A`.

**Verification gate:** Any external script without SRI in production HTML = gate failure.

---

## Control 8: Dependency Audit

**Rule:** `npm audit --audit-level=high` zero findings before release.

**Waiver:** Critical findings with no available fix must be documented in `SECURITY.md` with CVE ID, impact assessment, and remediation timeline.

**CI integration:** `npm audit` as required CI step. Block deploy on any critical/high finding without documented waiver.
