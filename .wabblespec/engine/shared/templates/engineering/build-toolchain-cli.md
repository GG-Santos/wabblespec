# Build Toolchain — CLI

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Language and runtime

**Language:** [ ] Node.js/TypeScript  [ ] Python  [ ] Go  [ ] Rust  [ ] Other: ___
**Runtime version:** `___ UNDECLARED` _(pin major.minor; users run this on diverse machines)_

---

## Build

**Build tool:** [ ] esbuild (Node)  [ ] PyInstaller (Python)  [ ] go build  [ ] cargo build  [ ] Other: ___
**Distribution format:** [ ] npm package  [ ] PyPI package  [ ] standalone binary  [ ] Homebrew formula  [ ] Other: ___
**Single-binary:** [ ] yes (no runtime required for end users)  [ ] no (runtime required)

---

## Test runner

**Unit:** [ ] Jest/Vitest  [ ] pytest  [ ] go test  [ ] cargo test  [ ] Other: ___
**Integration (subprocess):** [ ] child_process exec  [ ] subprocess.run  [ ] os/exec  [ ] assert_cmd  [ ] Other: ___
**Coverage:** [ ] Istanbul  [ ] coverage.py  [ ] go cover  [ ] llvm-cov  [ ] Other: ___
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
- [ ] Integration tests (actual subprocess invocation)
- [ ] Cross-platform build matrix: [ ] Linux  [ ] macOS  [ ] Windows
- [ ] Binary size check (no regression above declared ceiling)
- [ ] Cold start timing (≤ 100ms gate from performance-budgets.md)
- [ ] Dependency audit

---

## Distribution / release

**Package registry:** [ ] npm  [ ] PyPI  [ ] pkg.go.dev  [ ] crates.io  [ ] GitHub Releases (binary)  [ ] Other: ___
**Release trigger:** [ ] tag push (`v*`)  [ ] manual  [ ] Other: ___
**Signing:** [ ] GPG-signed npm  [ ] PyPI trusted publisher  [ ] cosign (binary)  [ ] None
**Changelog:** [ ] conventional-commits auto-generate  [ ] manual  [ ] Other: ___

---

## Observability

CLI tools typically have no server-side observability. Declare if the tool phones home:

**Telemetry:** [ ] None  [ ] opt-in usage analytics  [ ] error reporting (declare consent mechanism)
**Crash reporting:** [ ] None  [ ] Sentry  [ ] Other: ___

_(If no telemetry: Monitor generates no server-side configs. Engineering gateway confirms this is intentional.)_

---

## Notes

_Supported shells, minimum OS versions, known platform quirks:_
