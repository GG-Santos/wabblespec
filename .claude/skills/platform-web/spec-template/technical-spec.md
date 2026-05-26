# Web Technical Spec Template (P3)

> **Platform:** Web
> **Template version:** 1.0
> **Populated by:** Specify module (P3 pass) + Decompose
> **Prerequisite:** systems-design.md complete (P2 receipt exists)

---

## Implementation Constraints

Non-negotiable for all Web targets. Verifier checks each one.

| Constraint | Rule | Verification method |
|---|---|---|
| XSS prevention | No dangerouslySetInnerHTML / v-html without DOMPurify | Code review + static analysis |
| CSP | Content-Security-Policy header in production | Gate 1: response headers check |
| CSRF | CSRF token or SameSite=Strict on all state-mutating cookie requests | Gate 2: auth flow check |
| LCP | < 2.5s on simulated 4G | Gate 3: Lighthouse CI |
| CLS | < 0.1 | Gate 3: Lighthouse CI |
| INP | < 200ms | Gate 3: Lighthouse CI |
| Bundle budget | Initial JS < declared budget (default 200KB gzipped) | Gate 4: bundle analysis |
| Accessibility | axe-core zero critical violations | Gate 5: automated a11y scan |
| Browser matrix | Tested on all declared browsers | Gate 6: cross-browser smoke test |
| Auth tokens | No JWT/session tokens in localStorage | Code review |

---

## Wave Breakdown

Decompose populates this. Expected shape for Web tasks:

**Wave 0 — Foundation**
- Project scaffold (framework + toolchain)
- Routing setup (all declared routes registered, even if empty)
- Design system / CSS baseline installed
- Acceptance: all routes return 200, no console errors, Lighthouse run possible

**Wave 1 — Layout + Navigation**
- App shell, navigation, responsive breakpoints
- Error boundaries placed
- Loading state components built (skeleton / spinner)
- Acceptance: navigates between all routes; passes axe-core on shell; no CLS from layout

**Wave 2+ — Feature implementation**
- One wave per key journey (from design-document.md §Key Journeys)
- Each wave: implement → a11y check → CWV check → error state check

**Final wave — Production hardening**
- CSP headers configured
- Bundle analysis and optimization (if over budget)
- Lighthouse CI run (all three CWV gates must pass)
- Cross-browser smoke test

---

## Acceptance Criteria (GWT format)

All scenarios from design-document.md reproduced here, assigned to waves.

### XSS prevention

```
Given: a component renders user-supplied content
When: that content contains <script>alert(1)</script>
Then: the script tag is escaped or stripped — not executed
      AND the rendered output is visually correct (text, not blank)
      AND no console errors appear

Given: rich text content is rendered
When: dangerouslySetInnerHTML or v-html is used
Then: DOMPurify.sanitize() wraps every value before render
      AND the sanitization call is covered by a unit test
```

### Core Web Vitals

```
Given: a page has a Largest Contentful Paint element
When: Lighthouse runs on production URL with 4G simulation
Then: LCP < 2.5s
      AND the LCP element has fetchpriority="high" (or equivalent)
      AND no render-blocking resources precede it

Given: images or embeds load below the LCP element
When: the page loads
Then: no layout shift occurs as they load (CLS contribution < 0.01 per element)
      AND all images have explicit width and height attributes declared
```

### Accessibility

```
Given: any interactive element exists on the page
When: a keyboard-only user tabs through the page
Then: every interactive element receives visible focus
      AND tab order follows left-to-right, top-to-bottom reading order
      AND no keyboard trap exists (user can always tab out)

Given: axe-core runs against any page
When: the scan completes
Then: zero critical violations
      AND zero serious violations
      AND any moderate violations are documented with justification
```

### Auth security

```
Given: a form submits a state-mutating request with cookie auth
When: the request is examined
Then: CSRF token is present in request headers OR SameSite=Strict is set on session cookie
      AND the server rejects requests missing the CSRF token with 403

Given: auth token is issued on login
When: token storage is inspected
Then: token is in httpOnly cookie — not in localStorage, sessionStorage, or JS-accessible memory
```

### Environment variables

```
Given: the built client bundle is inspected
When: bundle contents are searched for secret patterns
Then: no API keys, database URLs, or private tokens appear in the bundle
      AND only NEXT_PUBLIC_ / VITE_ prefixed variables are present
```

---

## Not Tested (explicit)

- [ ] IE11 (explicitly unsupported — declare in browser matrix)
- [ ] Screen magnification > 400% (WCAG AAA — not required at AA)
- [ ] Non-declared browsers
- [ ] [Other explicit exclusions]

---

## Platform Verification Gates

See `verification/gates.md`. All gates blocking before Delivery.

1. CSP header present and non-report-only in production
2. CSRF protection confirmed on all state-mutating endpoints (if auth present)
3. Lighthouse CI: LCP < 2.5s, CLS < 0.1, INP < 200ms
4. Bundle budget: initial JS within declared limit
5. axe-core: zero critical violations
6. Cross-browser: smoke test on all declared browsers
7. No secrets in client bundle
8. No dangerouslySetInnerHTML without sanitization
