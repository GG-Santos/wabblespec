# Build Toolchain — Browser Extension

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Manifest version

**Manifest version:** [ ] MV3 (required for new submissions)  [ ] MV2 (legacy; declare migration plan)
**Target browsers:** [ ] Chrome/Chromium  [ ] Firefox  [ ] Safari (via Web Extensions)  [ ] Edge  [ ] All

---

## Build

**Build tool:** [ ] Vite + CRXJS  [ ] webpack + CopyWebpackPlugin  [ ] Parcel  [ ] Plasmo  [ ] Other: ___
**Package manager:** [ ] npm  [ ] pnpm  [ ] yarn

---

## Test runner

**Unit:** [ ] Vitest  [ ] Jest  [ ] Other: ___
**E2E / browser automation:** [ ] Playwright  [ ] Puppeteer  [ ] WebdriverIO  [ ] Other: ___
**Coverage threshold:** 80% statement

---

## Linting and formatting

**Linter:** [ ] ESLint (with `plugin:@typescript-eslint/recommended`)  [ ] Biome  [ ] Other: ___
**Formatter:** [ ] Prettier  [ ] Biome  [ ] Other: ___
**Extension-specific lint:** [ ] `web-ext lint`  [ ] `webext-check`  [ ] Other: ___

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] Other: ___

**Required CI gates:**
- [ ] Lint + type check
- [ ] `web-ext lint` (manifest validation)
- [ ] Unit tests
- [ ] E2E tests (headless browser)
- [ ] CSP validation (no unsafe-inline / unsafe-eval)
- [ ] Permission audit (no unused permissions)
- [ ] Bundle size check (≤ 10MB unpacked)
- [ ] MV3 service worker stateless check
- [ ] Dependency audit

---

## Store submission

**Chrome Web Store:** [ ] manual upload  [ ] automated via Chrome Web Store API  [ ] N/A
**Firefox Add-ons (AMO):** [ ] manual  [ ] automated via `web-ext sign`  [ ] N/A
**Safari (App Store):** [ ] Xcode + App Store Connect  [ ] N/A
**Review notes:** _Project-specific store listing reviewer guidance_

---

## Observability

**Error monitoring:** [ ] Sentry  [ ] Bugsnag  [ ] None  [ ] Other: ___
**Usage analytics:** [ ] None (preferred — avoid `history`/`tabs` permission for analytics)  [ ] opt-in only  [ ] Other: ___
**Store dashboard:** Chrome Developer Dashboard / AMO Developer Hub (external; no action needed)

_(Monitor generates crash-rate alerts if crash reporting is declared; otherwise no runtime configs needed.)_

---

## Notes

_Browser compatibility matrix, known extension API differences between Chrome/Firefox/Safari:_
