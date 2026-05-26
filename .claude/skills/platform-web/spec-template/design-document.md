# Web Design Document Template (P1)

> **Platform:** Web
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-web activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this web application does, who uses it in a browser, and the primary workflow it enables.

---

## Target Users [REQUIRED]

Who uses this in a browser? Describe the primary user type, their technical level, device usage patterns, and accessibility needs.

| User type | Device primary | Accessibility needs | Auth required |
|---|---|---|---|
| [User type 1] | Desktop / Mobile / Both | [Specific needs or "none declared"] | Yes / No |

---

## Key Journeys [REQUIRED]

List the 3–5 most important user journeys. These become the acceptance scenario subjects.

1. **[Journey name]** — [One sentence: user starts at X, does Y, ends at Z]
2. **[Journey name]** — ...

For each journey, declare:
- Entry point (URL or trigger)
- Authentication state (public / authenticated / specific role)
- Critical path (list of steps)
- Success state (what the user sees/has when done)

---

## Visual Direction

Design system in use:
[ ] Existing design system: ___ (name + version)
[ ] Tailwind CSS utility-first
[ ] CSS Modules with custom design tokens
[ ] No design system — declare typography + color baseline

**Responsive breakpoints:**
- Mobile: < ___px
- Tablet: ___–___px
- Desktop: > ___px

**Theme:** [ ] Light only [ ] Dark only [ ] System-follows (prefers-color-scheme)

---

## Accessibility Requirements [REQUIRED]

**Target standard:** WCAG 2.1 Level AA (minimum — non-negotiable for all Web targets)

**Specific requirements for this application:**
- Keyboard navigation: [ ] Full keyboard operability required [ ] Partial (declare scope)
- Screen reader: [ ] VoiceOver + NVDA tested [ ] VoiceOver only [ ] Declared out of scope (requires justification)
- Color contrast: 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- Focus indicators: visible on all interactive elements
- ARIA: semantic HTML first, ARIA only where semantics are insufficient

**Accessibility testing gate:** axe-core automated scan, zero critical violations, before Delivery.

---

## Browser Support Matrix [REQUIRED]

[REQUIRED] Declare supported browsers before Specify receipt is written.

| Browser | Minimum version | Notes |
|---|---|---|
| Chrome | ___ | |
| Firefox | ___ | |
| Safari | ___ | (iOS Safari is separate — declare if mobile required) |
| Edge | ___ | |
| iOS Safari | ___ or "not supported" | |
| Android Chrome | ___ or "not supported" | |

**Unsupported browsers:** Declare graceful degradation behavior (error page? no-JS fallback? redirect?).

---

## Performance Budget [REQUIRED]

**Core Web Vitals targets** (production — measured via Lighthouse CI or CrUX):

| Metric | Target | Threshold (fail gate) |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | > 4.0s |
| CLS (Cumulative Layout Shift) | < 0.1 | > 0.25 |
| INP (Interaction to Next Paint) | < 200ms | > 500ms |

**Bundle size budget:**
- Initial JS (gzipped): < ___KB (default: 200KB — override with justification)
- Initial CSS (gzipped): < ___KB (default: 50KB)
- Largest image on LCP path: < ___KB

Declare here. Enforced in CI via bundle analysis gate.

---

## Rendering Strategy [REQUIRED]

[ ] CSR (Client-Side Rendering) — SPA, all rendering in browser
[ ] SSR (Server-Side Rendering) — HTML rendered per request
[ ] SSG (Static Site Generation) — HTML pre-built at deploy time
[ ] ISR (Incremental Static Regeneration) — SSG with revalidation (Next.js)
[ ] Islands architecture — static shell with interactive islands (Astro)
[ ] Hybrid — declare which routes use which strategy

**Hydration concerns** (SSR/SSG only):
- Hydration mismatch prevention: declare strategy
- Loading states during hydration: skeleton / spinner / nothing (declare per component type)

---

## Auth Model

[ ] No authentication (public)
[ ] Session-based (server-side session + cookie)
[ ] JWT — storage: [ ] httpOnly cookie (recommended) [ ] localStorage (XSS risk — declare mitigation)
[ ] OAuth / OIDC — provider: ___
[ ] Auth service: ___

**Protected routes:** List routes that require authentication. Declare redirect behavior when unauthenticated.

**CSRF protection:** Required for all state-mutating requests when using cookie-based auth. Strategy: ___

---

## GWT Acceptance Scenarios (Web-specific)

Platform-specific gate tests that Verifier runs. Generic templates do not include these.

```
Given: a page contains user-controlled content rendered as HTML
When: Specify runs
Then: rendering path must not use dangerouslySetInnerHTML (React) or v-html (Vue)
      without explicit sanitization library (DOMPurify or equivalent)
      AND the sanitization call must be in the acceptance criteria

Given: the application makes authenticated requests
When: cookie-based auth is used
Then: CSRF token or SameSite=Strict cookie attribute must be declared in auth model
      AND every state-mutating endpoint must require the token

Given: a component renders external images or scripts
When: those resources are on external domains
Then: Subresource Integrity (SRI) hashes must be declared for scripts
      AND Content-Security-Policy img-src must list allowed domains explicitly

Given: a form accepts user input
When: that input is later displayed
Then: input must be sanitized before storage OR output-escaped at render time
      AND the sanitization point must be named in the acceptance criteria

Given: the application targets mobile users
When: the LCP element loads
Then: LCP time must be < 2.5s on a simulated 4G connection
      AND the LCP element must not have layout shift (CLS contribution 0)

Given: a user navigates using keyboard only
When: any interactive element is reached
Then: focus indicator must be visible with minimum 3:1 contrast ratio against adjacent colors
      AND tab order must follow visual reading order
```

---

## Open Questions

Unresolved design decisions. Specify blocks receipt until all REQUIRED sections complete and no blocking open questions remain.
