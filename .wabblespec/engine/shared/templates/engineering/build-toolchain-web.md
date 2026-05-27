# Build Toolchain — Web

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Package manager

**Tool:** [ ] npm  [ ] pnpm  [ ] yarn
**Lock file:** _(package-lock.json / pnpm-lock.yaml / yarn.lock — commit to repo)_

---

## Build

**Bundler:** [ ] Vite  [ ] Next.js (built-in)  [ ] webpack  [ ] esbuild  [ ] Parcel  [ ] Other: ___
**Target environments:** `___ UNDECLARED` (e.g., `es2022, chrome>=100, firefox>=100`)
**Output directory:** `dist/` _(or declare)_
**Source maps:** [ ] production  [ ] staging only  [ ] never

---

## Test runner

**Unit/component:** [ ] Vitest  [ ] Jest  [ ] Playwright Component  [ ] Other: ___
**E2E:** [ ] Playwright  [ ] Cypress  [ ] None
**Coverage tool:** [ ] v8 (Vitest)  [ ] Istanbul (Jest)  [ ] Other: ___
**Coverage threshold:** 80% statement _(Engineering gateway gate Q1; adjust if higher)_

---

## Linting and formatting

**Linter:** [ ] ESLint  [ ] Biome  [ ] Other: ___
**Formatter:** [ ] Prettier  [ ] Biome  [ ] Other: ___
**TypeScript:** [ ] strict mode  [ ] standard  [ ] None

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] CircleCI  [ ] Bitbucket  [ ] Other: ___

**Required CI gates (block merge on failure):**
- [ ] Lint + type check
- [ ] Unit tests (all pass)
- [ ] Coverage ≥ declared threshold
- [ ] Build (no build errors)
- [ ] E2E tests (smoke suite)
- [ ] Bundle size check (no regression above declared ceiling)
- [ ] Dependency audit (`npm audit --audit-level=high`)

---

## Deployment target

**Hosting:** [ ] Vercel  [ ] Netlify  [ ] AWS S3+CloudFront  [ ] GCP Cloud Storage+CDN  [ ] Self-hosted  [ ] Other: ___
**Environments:** [ ] dev  [ ] staging  [ ] production
**Deploy trigger:** [ ] merge to main  [ ] manual approval for production  [ ] Other: ___
**CDN invalidation:** [ ] automatic on deploy  [ ] manual  [ ] N/A

---

## Observability stack

**Error monitoring:** [ ] Sentry  [ ] Datadog RUM  [ ] None  [ ] Other: ___
**Analytics / RUM:** [ ] Datadog RUM  [ ] Google Analytics  [ ] PostHog  [ ] None  [ ] Other: ___
**Log aggregation:** [ ] Datadog Logs  [ ] Logtail  [ ] CloudWatch  [ ] None  [ ] Other: ___

_(Monitor uses this to select output format for alert rules and dashboard templates.)_

---

## Notes

_Project-specific build notes, quirks, or deviations from defaults:_
