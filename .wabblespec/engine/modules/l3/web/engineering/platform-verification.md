# Web Engineering — Platform Verification

How to run and interpret web verification gates.

## Running All Gates

```bash
# Build first
npm run build

# Gates 1, 7, 8: static checks
curl -sI <url> | grep -i content-security-policy
grep -rE "(sk-|secret|api_key)" dist/ --include="*.js"
grep -r "dangerouslySetInnerHTML" src/ | grep -v DOMPurify

# Gate 3: Lighthouse CI
npx lhci autorun --collect.url=<url>

# Gate 4: bundle size
npx vite-bundle-analyzer dist/  # or @next/bundle-analyzer

# Gate 5: accessibility
npx axe <url> --exit

# Gate 6: manual cross-browser (or Playwright matrix)
```

## Interpreting Failures

**LCP over budget:**
- Check LCP element with Chrome DevTools Performance tab
- Most common cause: LCP image not preloaded, render-blocking scripts, large server response time
- Fix priority: 1) Add preload link, 2) Add fetchpriority="high", 3) Defer non-critical scripts

**CLS over budget:**
- Open Chrome DevTools → Performance → record page load → look for layout shift events
- Most common cause: images without width/height, fonts causing reflow, late-injected content above fold
- Fix: explicit dimensions on all images, font-display: swap, reserve space for dynamic content

**Bundle over budget:**
- Use bundle analyzer to find largest chunks
- Check for: full lodash import (use lodash-es per-function), moment.js (use date-fns), large icon sets (import individual icons)
- Add route-based code splitting if not already present

**axe-core violations:**
- `color-contrast`: check foreground/background pairs against 4.5:1 ratio
- `image-alt`: add descriptive alt text to all `<img>` elements
- `label`: every form input needs associated `<label>` or `aria-label`
- `button-name`: every `<button>` needs visible text or `aria-label`

## Regression Prevention

After all gates pass:
1. Record gate results in platform activation receipt
2. Add Lighthouse CI, axe-core, and bundle budget checks to CI pipeline
3. Security headers: verify at every deploy (CDN config can reset headers)
4. Re-run full gate suite before any major dependency upgrade
