# Web Systems Design Template (P2)

> **Platform:** Web
> **Template version:** 1.0
> **Populated by:** Specify module (P2 pass)
> **Prerequisite:** design-document.md complete (P1 receipt exists)

---

## Component Architecture

**Framework:** [from activation — React/Next/Vue/Svelte/Angular/Vanilla]

**Component model:**
```
Page/Route components          (data fetching, layout)
  └─ Feature components        (business logic, state)
       └─ UI components        (presentational, stateless where possible)
            └─ Primitive components (design system atoms)
```

**State management:**
[ ] Component-local state only (React useState / Vue ref)
[ ] Shared state: ___ (Zustand, Jotai, Pinia, NgRx, Svelte stores)
[ ] Server state: ___ (TanStack Query, SWR, Apollo)
[ ] Form state: ___ (React Hook Form, Formik, VeeValidate)

Declare which state solution handles which concern. No single global store for everything.

---

## Data Fetching Strategy

**SSR/SSG data loading** (if applicable):
- Data fetched at: [ ] Build time (SSG) [ ] Request time (SSR) [ ] Client side (CSR) [ ] Mixed
- Cache strategy: revalidation interval declared for each data source
- Error states: loading / error / empty declared for every async data path

**Client-side fetching:**
- HTTP client: [ ] fetch (native) [ ] axios [ ] ky [ ] other: ___
- Request deduplication: handled by? (TanStack Query / SWR / manual)
- Optimistic updates: declared per mutation that uses them

**API contract:**
- Type safety: [ ] Generated from OpenAPI schema [ ] Manual types [ ] tRPC [ ] GraphQL codegen
- Error shape: declare the error response format expected from the API

---

## Routing

**Router:** [Next.js App Router / Next.js Pages Router / React Router / Vue Router / SvelteKit / Angular Router]

**Route map:**

| Route | Auth required | Rendering | Notes |
|---|---|---|---|
| `/` | No | SSG/CSR | |
| `/[route]` | Yes | SSR/CSR | |

**Dynamic routes:** List all `[param]` routes. Declare 404 behavior for missing params.

**Loading states:** Declare loading UI for each route that fetches data (skeleton / spinner / layout shift strategy).

**Error boundaries:** Declare per-route or app-level error boundary behavior.

---

## Asset Pipeline

**Images:**
- Format: WebP with JPEG fallback (or next/image / equivalent)
- Lazy loading: all below-fold images
- LCP image: `loading="eager"` + `fetchpriority="high"` — no lazy loading on LCP element
- Responsive sizes: `srcset` or next/image sizes prop declared

**Fonts:**
- Web fonts: `font-display: swap` required to prevent FOIT
- Self-hosted: preferred over CDN for CLS stability
- Preload: `<link rel="preload">` for fonts on critical path

**CSS:**
- Critical CSS: inlined in `<head>` for above-fold styles (SSR/SSG)
- Non-critical CSS: deferred load or async
- CSS-in-JS (if used): declare SSR extraction strategy to prevent FOUC

---

## State Persistence

**Local storage:** What data is stored client-side?

| Key | Purpose | Sensitive? | Expiry |
|---|---|---|---|
| [key] | [purpose] | Yes/No | Session / [duration] |

**Cookies:**

| Name | Purpose | httpOnly | SameSite | Secure | Expiry |
|---|---|---|---|---|---|
| [name] | [purpose] | Yes/No | Strict/Lax/None | Yes | [duration] |

**Rule:** No auth tokens in localStorage. Session tokens in httpOnly cookies only.

---

## Error Handling Model

**User-facing errors:**
- Network error: toast / inline message / error page (declare per context)
- 4xx from API: user-readable message — never expose raw API error to user
- 5xx from API: generic error message + retry where appropriate
- Form validation: inline field errors, not modal

**Error boundary placement:**
```
App root boundary        (catch-all: full page error UI)
  Route-level boundary   (route fails: keep nav, show route error)
    Feature boundary     (widget fails: keep page, show feature error)
```

**Logging:** Client-side errors → ___  (Sentry / LogRocket / custom endpoint). PII must not appear in error payloads.

---

## Build Configuration

**Bundler:** [Vite / Next.js built-in / Webpack — from engineering/build-toolchain.md]

**Environment variables:**
- Build-time (public): `NEXT_PUBLIC_` / `VITE_` prefix — declare each
- Never in client bundle: API keys, secrets, private URLs

**Feature flags:** [ ] Used [ ] Not used. If used: declare provider and flag key naming convention.

**Source maps:** [ ] Generated [ ] Not generated. If generated: do not expose in production (upload to error tracker, do not serve publicly).
