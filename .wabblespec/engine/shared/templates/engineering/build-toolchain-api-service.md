# Build Toolchain — API-Service

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Language and runtime

**Language:** [ ] Node.js/TypeScript  [ ] Python  [ ] Go  [ ] Java  [ ] Rust  [ ] Other: ___
**Runtime version:** `___ UNDECLARED` _(e.g., Node 22, Python 3.12, Go 1.22 — pin major.minor)_

---

## Build

**Build tool:** [ ] tsc + esbuild  [ ] tsc only  [ ] Poetry (Python)  [ ] go build  [ ] Gradle  [ ] Cargo  [ ] Other: ___
**Output:** [ ] Docker image  [ ] binary  [ ] Lambda zip  [ ] Other: ___
**Container base image:** `___ UNDECLARED` _(e.g., `node:22-alpine`; pin to digest in production)_

---

## Test runner

**Unit:** [ ] Jest/Vitest  [ ] pytest  [ ] go test  [ ] JUnit  [ ] cargo test  [ ] Other: ___
**Integration:** [ ] Supertest  [ ] pytest + httpx  [ ] go test (httptest)  [ ] REST Assured  [ ] Other: ___
**Coverage tool:** [ ] Istanbul  [ ] coverage.py  [ ] go cover  [ ] JaCoCo  [ ] llvm-cov  [ ] Other: ___
**Coverage threshold:** 80% statement _(Engineering gateway gate Q1)_

---

## Linting and formatting

**Linter:** [ ] ESLint  [ ] Ruff  [ ] golangci-lint  [ ] Checkstyle  [ ] Clippy  [ ] Other: ___
**Formatter:** [ ] Prettier  [ ] Ruff format  [ ] gofmt  [ ] google-java-format  [ ] rustfmt  [ ] Other: ___

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] CircleCI  [ ] Jenkins  [ ] Other: ___

**Required CI gates (block merge on failure):**
- [ ] Lint + type check
- [ ] Unit tests (all pass)
- [ ] Integration tests
- [ ] Coverage ≥ threshold
- [ ] Build / Docker build
- [ ] Dependency audit (CVE scan)
- [ ] Container image scan (Trivy / Snyk)
- [ ] SAST (Semgrep / CodeQL)

---

## Deployment target

**Platform:** [ ] Kubernetes (EKS/GKE/AKS)  [ ] AWS ECS  [ ] AWS Lambda  [ ] Google Cloud Run  [ ] Heroku  [ ] Fly.io  [ ] Self-hosted  [ ] Other: ___
**Environments:** [ ] dev  [ ] staging  [ ] production
**Deploy strategy:** [ ] rolling  [ ] blue-green  [ ] canary  [ ] Other: ___
**Production deploy gate:** [ ] manual approval  [ ] automated on staging pass  [ ] Other: ___

---

## Observability stack

**Metrics:** [ ] Prometheus + Grafana  [ ] Datadog  [ ] CloudWatch  [ ] OpenTelemetry → ___ backend  [ ] Other: ___
**Logs:** [ ] Datadog Logs  [ ] CloudWatch Logs  [ ] Elastic  [ ] Loki  [ ] Other: ___
**Traces:** [ ] Jaeger  [ ] Datadog APM  [ ] AWS X-Ray  [ ] Honeycomb  [ ] None  [ ] Other: ___
**Alerting:** [ ] PagerDuty  [ ] OpsGenie  [ ] Datadog Alerts  [ ] Other: ___

_(Monitor uses this to select Prometheus/Datadog/CloudWatch output format for generated configs.)_

---

## Notes

_Project-specific build notes, environment variables required, or deviations from defaults:_
