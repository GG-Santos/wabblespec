# Build Toolchain — Library

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Language and ecosystem

**Language:** [ ] TypeScript  [ ] Python  [ ] Go  [ ] Rust  [ ] Java  [ ] Other: ___
**Package registry:** [ ] npm  [ ] PyPI  [ ] pkg.go.dev  [ ] crates.io  [ ] Maven Central  [ ] Other: ___

---

## Build

**Build tool:** [ ] tsup  [ ] Rollup  [ ] esbuild  [ ] tsc only  [ ] Poetry  [ ] go build  [ ] cargo  [ ] Other: ___
**Output formats:** [ ] ESM  [ ] CJS  [ ] UMD  [ ] .whl  [ ] .so / .a  [ ] Other: ___
**TypeScript declarations:** [ ] included  [ ] N/A

---

## Test runner

**Unit:** [ ] Vitest  [ ] Jest  [ ] pytest  [ ] go test  [ ] cargo test  [ ] Other: ___
**Type tests:** [ ] tsd  [ ] expect-type  [ ] N/A
**Coverage threshold:** 80% statement

---

## Linting and formatting

**Linter:** [ ] ESLint  [ ] Ruff  [ ] golangci-lint  [ ] Clippy  [ ] Other: ___
**Formatter:** [ ] Prettier  [ ] Ruff format  [ ] gofmt  [ ] rustfmt  [ ] Other: ___

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] Other: ___

**Required CI gates:**
- [ ] Lint + type check
- [ ] Unit tests
- [ ] Type tests (public API correctness)
- [ ] Coverage ≥ threshold
- [ ] Bundle size check (no regression above declared ceiling from performance-budgets.md)
- [ ] Tree-shaking verification (no unintended side effects)
- [ ] Breaking change detection (API Extractor / publint)
- [ ] Dependency audit
- [ ] Semver compliance check (conventional commits → version bump)

---

## Release

**Versioning:** [ ] conventional-commits auto-bump  [ ] manual  [ ] Other: ___
**Release trigger:** [ ] tag push (`v*`)  [ ] manual workflow dispatch  [ ] Other: ___
**Changelog:** [ ] auto-generated from conventional commits  [ ] manual  [ ] Other: ___
**Publish:** [ ] automated on tag  [ ] manual `npm publish`  [ ] trusted publisher (PyPI)  [ ] Other: ___
**Access:** [ ] public  [ ] restricted (org-scoped)

---

## Observability

Libraries have no runtime server. Observability applies only if the library ships instrumentation:

**Instrumentation provided:** [ ] None  [ ] OpenTelemetry spans  [ ] Metrics hooks  [ ] Other: ___
**Download metrics:** [ ] npm/PyPI/crates download count (external; no action needed)

_(If no instrumentation: Monitor generates no runtime configs. Engineering gateway confirms intentional.)_

---

## Notes

_Supported peer dependency versions, known bundler compatibility issues, deprecation timeline:_
