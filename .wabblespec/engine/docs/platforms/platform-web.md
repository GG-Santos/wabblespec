# Platform: Web

Web application target. Activates when Recipe identifies a web app, SPA, SSR app, or static site as the primary build target.

**Skill:** `modules/l3/web/SKILL.md`

## What makes Web different

| Concern | Web approach |
|---------|-------------|
| Security surface | XSS, CSRF, CSP, clickjacking, open redirects |
| State management | Browser state, URL state, server state — all declared |
| Performance | Core Web Vitals (LCP, FID/INP, CLS) — thresholds declared |
| Accessibility | WCAG 2.1 AA minimum — keyboard nav, screen reader, contrast |
| SEO | Semantic HTML, meta tags, structured data — if public-facing |
| Compatibility | Declared browser targets — IE exclusion must be explicit |
| Hydration | SSR/SSG/CSR strategy declared up front |

## Platform-specific spec sections

- Browser support matrix: declared target browsers and versions
- Rendering strategy: CSR, SSR, SSG, or ISR — with justification
- State architecture: local, URL, server, cache — which lives where
- Bundle strategy: code splitting points, lazy load boundaries
- Meta and SEO: title, description, OG tags — required for public pages

## Security controls loaded

- XSS: all user content sanitized before DOM insertion; CSP declared
- CSRF: token strategy declared for all state-mutating requests
- Clickjacking: `X-Frame-Options` or `frame-ancestors` CSP directive declared
- Open redirect: all redirects to user-supplied URLs validated against allowlist
- Dependency audit: `npm audit` or equivalent required in CI

## Gateway interaction

Web targets typically activate:
- `gateway-security` — always
- `gateway-engineering` — Medium/High complexity
- `gateway-aesthetic` — any UI work
- `gateway-design` — any UX/flow work
- `gateway-experience` — any user-facing feature (requires design PASS)
