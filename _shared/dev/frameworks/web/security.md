# Web Security Framework

Security patterns and requirements for browser-targeted frontends. Loaded by Apply alongside web/core.md.

## Authentication patterns

### Session-based (stateful)
```
Cookie: session_id=<opaque-token>
Set-Cookie: session_id=...; HttpOnly; Secure; SameSite=Strict; Path=/
```
- Session token is opaque — no data embedded
- HttpOnly: JS cannot read it (XSS protection)
- Secure: HTTPS only
- SameSite=Strict: CSRF protection

### Token-based (stateless SPA)
```
Authorization: Bearer <JWT>
```
- Store JWT in memory (JS variable) — NOT localStorage (XSS steals it)
- Refresh token in HttpOnly cookie
- Access token: short-lived (15 min)
- Refresh token: rotates on use

### OAuth / OIDC (federated)
- Authorization Code + PKCE — required for SPAs (no implicit flow)
- State parameter: CSRF protection for OAuth flow
- Nonce: replay protection for ID token

## XSS prevention

Do not construct HTML from user input. If unavoidable:
1. Sanitize with DOMPurify before inserting
2. Declare the use in spec: which component, which input, which sanitizer
3. Review output: confirm tags and attributes are allowlisted, not blocked

Framework-specific risks:
- React: `dangerouslySetInnerHTML` — must declare and sanitize
- Vue: `v-html` — must declare and sanitize
- Angular: `bypassSecurityTrustHtml` — must declare and sanitize
- Vanilla: `innerHTML`, `outerHTML`, `document.write` — must sanitize

## Content Security Policy

Declare full CSP header in spec. Example strict policy:
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  font-src 'self';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self'
```

Deviations require justification in spec:
- `unsafe-inline` for scripts: blocks most XSS — avoid; use nonces if legacy code requires it
- Wildcard origins (`*`): do not use
- `unsafe-eval`: blocks eval() and Function() — never allow

## CORS

CORS is a browser protection. Spec must declare:
- Allowed origins (explicit list; no wildcard for credentialed requests)
- Allowed methods
- Allowed headers
- Whether credentials are allowed (`credentials: 'include'`)

Anti-pattern: `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` — this is impossible and means your config is wrong.

## Dependency security

- Lock file committed (package-lock.json or yarn.lock or pnpm-lock.yaml)
- `npm audit` / `pnpm audit` run in CI — failures block build
- No direct `http://` CDN imports (use npm + bundler)
- Subresource integrity (SRI) for any CDN script that remains after migration

## Sensitive data

Never in:
- URL parameters (logged in proxies, browser history)
- localStorage (XSS readable)
- `console.log` calls in production

Acceptable: HttpOnly cookies (session tokens), in-memory variables (access tokens), sessionStorage (tab-scoped, still XSS-readable — use only for non-sensitive state)
