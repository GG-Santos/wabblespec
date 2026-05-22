# Web Verification Gates

All gates blocking before Delivery wave.

---

## Gate 1: Security Headers

```bash
curl -sI <production-url> | grep -iE "content-security-policy|x-frame-options|x-content-type-options|strict-transport-security"
```

**Pass:** All 4 headers present. CSP is enforcing (not report-only).
**Fail:** Any header missing, or CSP is report-only only.

---

## Gate 2: CSRF Protection

For every cookie-authenticated state-mutating endpoint:
- Verify `SameSite=Strict` on session cookie, OR
- Verify CSRF token present and validated server-side

**Method:** Submit state-mutating request without CSRF token / cross-origin. Must return 403.

**Pass:** Cross-origin state-mutating request rejected.
**Fail:** Request accepted without CSRF protection.

---

## Gate 3: Core Web Vitals (Lighthouse CI)

```bash
npx lhci autorun \
  --collect.url=<url> \
  --collect.settings.throttling.rttMs=40 \
  --collect.settings.throttling.throughputKbps=10240 \
  --assert.assertions.largest-contentful-paint=["error",{"maxNumericValue":2500}] \
  --assert.assertions.cumulative-layout-shift=["error",{"maxNumericValue":0.1}] \
  --assert.assertions.interaction-to-next-paint=["error",{"maxNumericValue":200}]
```

**Pass:** All three CWV in "Good" range.
**Fail:** Any CWV in "Needs Improvement" or "Poor".

---

## Gate 4: Bundle Budget

```bash
# After build:
ls -la dist/assets/*.js | awk '{sum += $5} END {print sum/1024 " KB total JS"}'
# Or use bundler's built-in size report
```

**Pass:** Initial JS ≤ declared budget (default 200KB gzipped).
**Fail:** Over budget. Requires code-splitting or dependency audit before Delivery.

---

## Gate 5: Accessibility (axe-core)

```bash
npx axe <url> --exit
# Or via Playwright:
# await checkA11y(page, null, { runOnly: ['wcag2a', 'wcag2aa'] })
```

**Pass:** Zero critical violations. Zero serious violations.
**Fail:** Any critical or serious violation.

---

## Gate 6: Cross-Browser Smoke Test

For each browser in declared support matrix:
- Load home page: no console errors
- Complete primary key journey: no visual breakage
- Forms submit correctly
- Auth flow works (if applicable)

**Pass:** All declared browsers pass smoke test.
**Fail:** Any declared browser shows broken layout or JS errors.

---

## Gate 7: No Secrets in Bundle

```bash
# Scan built output
grep -rE "(sk-|api_key|apikey|secret|password|Bearer |postgres://|mongodb://)" dist/ \
  --include="*.js" --include="*.mjs"
```

**Pass:** Zero matches.
**Fail:** Any match. Stop — investigate before deploy.

---

## Gate 8: XSS Prevention Audit

```bash
# Static: find unsanitized dangerouslySetInnerHTML
grep -r "dangerouslySetInnerHTML" src/ --include="*.tsx" --include="*.jsx" \
  | grep -v "DOMPurify"

# Static: find v-html without sanitization
grep -r "v-html" src/ --include="*.vue" | grep -v "DOMPurify"
```

**Pass:** Zero results (all uses wrap DOMPurify, filtered out by second grep).
**Fail:** Any unsanitized usage found.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Security headers (CSP, X-Frame-Options, etc.) | Yes |
| 2 | CSRF protection on state-mutating endpoints | Yes (if auth present) |
| 3 | Core Web Vitals: LCP/CLS/INP | Yes |
| 4 | Bundle size within declared budget | Yes |
| 5 | axe-core zero critical/serious a11y violations | Yes |
| 6 | Cross-browser smoke test | Yes |
| 7 | No secrets in client bundle | Yes |
| 8 | No unsanitized dangerouslySetInnerHTML/v-html | Yes |
