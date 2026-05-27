# Web Verification Gates

All gates blocking before Delivery wave.

## Standards Basis

| Gate | Standard | Source |
|---|---|---|
| 1 | Content-Security-Policy, HSTS, X-Frame-Options, X-Content-Type-Options | OWASP Secure Headers Project; MDN Security Headers |
| 2 | CSRF via SameSite or token | OWASP CSRF Prevention Cheat Sheet |
| 3 | LCP ≤ 2500ms, CLS ≤ 0.1, INP ≤ 200ms | Google Core Web Vitals (web.dev/vitals); W3C Web Performance WG |
| 4 | Initial JS bundle ≤ 200KB gzipped | Google Lighthouse performance budget; HTTP Archive median baseline |
| 5 | WCAG 2.1 AA — zero critical/serious violations | W3C WCAG 2.1 §1-4; axe-core ruleset |
| 6 | Declared browser matrix passes smoke test | Project support matrix declaration in design-document.md |
| 7 | No secrets in client bundle | OWASP Sensitive Data Exposure (A02:2021) |
| 8 | No unsanitized innerHTML equivalent | OWASP XSS Prevention Cheat Sheet |
| 9 | Page renders non-blank at all declared viewports | Browser capture baseline — superpowers-chrome CDP pattern |
| 10 | No horizontal overflow at mobile breakpoint | CSS box model; mobile-first design contract |
| 11 | `prefers-reduced-motion` honored | WCAG 2.1 §2.3.3 (AAA); W3C CSS Media Queries Level 5 |

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

---

## Gate 9: Browser Capture Smoke Test

**Check:** Page renders non-blank at each declared viewport. No unhandled JS errors during load.

**Method (Playwright):**
```bash
npx playwright test --project=chromium tests/browser-smoke.spec.ts
```

**Minimum spec for `tests/browser-smoke.spec.ts`:**
```typescript
import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'mobile',  width: 375,  height: 812 },
  { name: 'tablet',  width: 768,  height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const vp of viewports) {
  test(`renders non-blank at ${vp.name}`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', e => errors.push(e.message));

    await page.setViewportSize(vp);
    await page.goto('<base-url>');
    await page.waitForLoadState('networkidle');

    // Non-blank: at least one element with visible text
    const text = await page.innerText('body');
    expect(text.trim().length).toBeGreaterThan(0);

    // Screenshot for manual audit
    await page.screenshot({ path: `screenshots/${vp.name}.png`, fullPage: false });

    // No unhandled JS errors
    expect(errors).toHaveLength(0);
  });
}
```

**Pass:** All viewports render visible text. Zero unhandled JS errors. Screenshots written to `screenshots/`.
**Fail:** Any viewport produces blank body, or any unhandled JS error during load.

**Note:** Screenshots are evidence artifacts — attach paths to platform activation receipt in `captures[]`.

---

## Gate 10: Mobile Viewport Overflow

**Check:** No horizontal scrollbar or overflow at 375px width (minimum declared mobile breakpoint).

**Method (Playwright):**
```typescript
test('no horizontal overflow at mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('<base-url>');
  await page.waitForLoadState('networkidle');

  const overflowing = await page.evaluate(() => {
    return document.body.scrollWidth > document.body.clientWidth;
  });
  expect(overflowing).toBe(false);
});
```

**Alternative (manual):**
```bash
# DevTools device emulation: set width to 375px
# Check: Elements > Computed > scrollWidth vs clientWidth on body
```

**Pass:** `scrollWidth <= clientWidth` at 375px. No horizontal scroll.
**Fail:** Horizontal overflow detected. Identify element with `overflow: auto` or fixed-width > 375px.

---

## Gate 11: Reduced Motion Compliance

**Check:** Animations and transitions respect `prefers-reduced-motion: reduce`. No motion when user has opted out.

**Method (Playwright):**
```typescript
test('respects prefers-reduced-motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('<base-url>');
  await page.waitForLoadState('networkidle');

  // Check no animation-duration or transition-duration > 0 on key elements
  const hasMotion = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    for (const el of elements) {
      const style = getComputedStyle(el);
      const animDuration = parseFloat(style.animationDuration);
      const transDuration = parseFloat(style.transitionDuration);
      if (animDuration > 0 || transDuration > 0.05) return true;
    }
    return false;
  });
  expect(hasMotion).toBe(false);
});
```

**Static audit (if no Playwright):**
```bash
# Find animation/transition definitions not guarded by reduced-motion query:
grep -rE "animation:|transition:" src/ --include="*.css" --include="*.scss" \
  | grep -v "prefers-reduced-motion"
```

**Pass:** Zero computed animation/transition durations above threshold when `reducedMotion: reduce`. Zero unguarded CSS animation/transition rules.
**Fail:** Any animation or transition runs under reduced-motion preference. Any CSS file missing `@media (prefers-reduced-motion: reduce)` guard on its animations.

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
| 9 | Browser capture smoke test — non-blank at all viewports | Yes |
| 10 | No horizontal overflow at mobile breakpoint | Yes |
| 11 | Reduced motion compliance | Yes |
