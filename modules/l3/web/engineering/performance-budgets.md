# Web Engineering — Performance Budgets

## Core Web Vitals (Production)

Measured via Lighthouse CI on production URL or representative staging environment.

| Metric | Good | Needs Improvement | Poor (gate fails) |
|---|---|---|---|
| LCP | < 2.5s | 2.5–4.0s | > 4.0s |
| CLS | < 0.1 | 0.1–0.25 | > 0.25 |
| INP | < 200ms | 200–500ms | > 500ms |

**Gate:** Lighthouse CI must score all three in "Good" range before Delivery wave. Not "Needs Improvement" — Good.

**Measurement command:**
```bash
npx lhci autorun --collect.url=<url> --assert.preset=lighthouse:recommended
```

---

## Bundle Size

**Initial JS load (gzipped):**
- Default budget: 200KB
- Override: declare in design-document.md §Performance Budget with justification
- Measurement: `vite-bundle-analyzer` / `@next/bundle-analyzer` output

**Initial CSS load (gzipped):**
- Default budget: 50KB
- Tailwind purge must be verified: no unused classes in production bundle

**Largest image (LCP path):**
- Default budget: 150KB for LCP image
- WebP format required, JPEG fallback

**Per-route JS (lazy-loaded chunks):**
- No single route chunk > 100KB gzipped (excluding vendor code)
- Code-split at route boundaries (minimum)

---

## Time to Interactive

**Target:** TTI < 3.5s on simulated 4G (Lighthouse Moto G4 simulation)

**Blocking resources:**
- No render-blocking scripts in `<head>` without `defer` or `async`
- No render-blocking CSS beyond critical inline styles
- Third-party scripts deferred until after interactive

---

## Runtime Performance

**Main thread budget:** No long tasks > 50ms on initial load (blocks INP)

**React/Vue/Svelte specific:**
- No unnecessary re-renders in hot paths (profile with React DevTools / Vue DevTools)
- List virtualization required for lists > 100 items (TanStack Virtual or equivalent)
- Memo/useMemo only where profiler shows it helps — not by default

**Animation:**
- CSS transforms and opacity only (compositor-thread, no layout/paint)
- No JavaScript animation of `width`, `height`, `top`, `left` properties (causes layout thrash)
- `will-change: transform` only on elements that animate — not globally

---

## Image Performance

**LCP element specific:**
- `fetchpriority="high"` attribute
- `loading="eager"` (no lazy)
- Preload link in `<head>`
- Explicit `width` and `height` to prevent CLS

**All other images:**
- `loading="lazy"` for below-fold
- Explicit `width` and `height` on all `<img>` elements
- `srcset` with at least 2 sizes (mobile + desktop)

**Format waterfall:** WebP → JPEG (use `<picture>` element with `<source type="image/webp">`)

---

## Web Font Performance

**Font display:** `font-display: swap` — text visible during font load

**FOUT (Flash of Unstyled Text):** Acceptable. Better than invisible text (FOIT).

**Font subsetting:** Subset fonts to used characters if bundle size is constrained.

**Preload:** Only preload fonts used above the fold. Over-preloading competes with LCP image.

---

## Monitoring

**CrUX (Chrome User Experience Report):** Real user data for production sites. Check monthly.

**Lighthouse CI:** Synthetic, run on every deployment. Catches regressions before users see them.

**Budget enforcement:** CI fails build when bundle exceeds declared budget. Not a warning — a failure.
