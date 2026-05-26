# Performance Budgets — Web

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/web`.
> Reference: `_shared/references/performance-budgets.md`.

---

## Core Web Vitals

### LCP (Largest Contentful Paint)

**Target:** ≤ 2.5s at p75 measured from navigation start
**Rationale:** Google "Good" tier; correlates with user-perceived load completion
**Measurement:** field data via CrUX or RUM; lab via Lighthouse CI on critical pages
**PII impact:** none

### CLS (Cumulative Layout Shift)

**Target:** ≤ 0.1 at p75 measured over page lifetime
**Rationale:** Google "Good" tier; layout shift above 0.1 causes mis-taps and disorientation
**Measurement:** field data via CrUX; lab via Lighthouse CI
**PII impact:** none

### INP (Interaction to Next Paint)

**Target:** ≤ 200ms at p75 measured from user interaction to next paint
**Rationale:** Google "Good" tier; interactions above 200ms feel unresponsive
**Measurement:** field data via CrUX or RUM with event timing API
**PII impact:** none

---

## Network / Server

### Time to First Byte (TTFB)

**Target:** ≤ 800ms at p75 for HTML document
**Rationale:** LCP target requires TTFB headroom; high TTFB consumes the entire LCP budget
**Measurement:** Navigation Timing API; server-side request logging
**PII impact:** none

### API response latency (page-critical calls)

**Target:** ≤ 200ms p99 for synchronous calls blocking first render
**Rationale:** Delays above 200ms on critical-path calls violate INP and LCP budgets
**Measurement:** server-side request duration histogram
**PII impact:** ___ UNDECLARED — declare if user identity is in request path

---

## Bundle

### JavaScript bundle size (initial load)

**Target:** ≤ 200KB gzipped for first-load JS (excluding vendor split)
**Rationale:** Main thread parse time for 200KB gzipped JS is ≈ 1s on mid-range mobile
**Measurement:** build output; Lighthouse bundle analysis
**PII impact:** none

### CSS bundle size

**Target:** ≤ 50KB gzipped for critical CSS
**Rationale:** Render-blocking CSS above 50KB delays FCP
**Measurement:** build output
**PII impact:** none

---

## Error rate

### Client-side JS errors

**Target:** < 1% of page sessions with uncaught errors
**Rationale:** Above 1%, errors are likely hitting real user paths, not rare edge cases
**Measurement:** error monitoring (Sentry / equivalent); sessions with error events / total sessions
**PII impact:** ensure stack traces do not log user data

### HTTP 5xx error rate

**Target:** < 0.5% of requests over 5-minute window
**Rationale:** Tier 1 standard for user-facing web; above 0.5% indicates systematic failure
**Measurement:** server access logs; CDN error rate
**PII impact:** none

---

## Availability

**Target:** 99.9% uptime measured monthly (≤ 43.8 minutes downtime/month)
**Rationale:** Standard for user-facing web products; below 99.9% is noticeable to users
**Measurement:** synthetic monitoring (uptime checks every 60s from 3 regions)
**PII impact:** none

---

## PII fields (excluded from log schema)

<!-- Declare any PII-bearing fields that must not appear in logs or monitoring data -->
<!-- Example:
- user_email
- ip_address (if applicable under GDPR)
- session_token
-->
___ UNDECLARED — populate before running Monitor
