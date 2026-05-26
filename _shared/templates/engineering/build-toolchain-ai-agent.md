# Build Toolchain — AI Agent

> Template. Copy to `engineering/build-toolchain.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering` Phase A, `l4/ai` Phase A.
> Companion: `engineering/performance-budgets.md`.

---

## Language and runtime

**Language:** [ ] Python  [ ] Node.js/TypeScript  [ ] Other: ___
**Runtime version:** `___ UNDECLARED` _(pin; LLM SDKs ship breaking changes frequently)_

---

## AI framework

**Framework:** [ ] LangChain  [ ] LlamaIndex  [ ] OpenAI Agents SDK  [ ] Anthropic SDK (direct)  [ ] Custom  [ ] Other: ___
**Model provider(s):** `___ UNDECLARED` _(e.g., Anthropic, OpenAI, Google — list all used in prod)_
**Primary model:** `___ UNDECLARED` _(pinned model ID — no `latest`; required by l4/ai M1)_
**Fallback model:** `___ UNDECLARED` _(required by l4/ai model-governance; must be declared)_

---

## Build / packaging

**Build tool:** [ ] Poetry  [ ] pip + requirements.txt  [ ] npm  [ ] Docker image  [ ] Other: ___
**Dependency lock:** [ ] poetry.lock  [ ] package-lock.json  [ ] requirements.txt pinned  [ ] Other: ___

---

## Test runner

**Unit:** [ ] pytest  [ ] Jest/Vitest  [ ] Other: ___
**Eval harness:** `___ UNDECLARED` _(required by l4/ai M2 — declare eval framework and fixture location)_
**Eval fixture location:** `___ UNDECLARED` _(e.g., `tests/fixtures/evals/`)_
**Coverage threshold:** 80% statement (non-LLM code); eval suite pass rate declared in performance-budgets.md

---

## CI system

**Platform:** [ ] GitHub Actions  [ ] GitLab CI  [ ] Other: ___

**Required CI gates:**
- [ ] Lint + type check
- [ ] Unit tests (mocked LLM calls)
- [ ] Eval suite (held-out fixture set, not mocked)
- [ ] Eval pass rate ≥ declared threshold
- [ ] Prompt injection test suite
- [ ] Agent loop bound verification (no unbounded loops)
- [ ] Model version drift check (pinned IDs match expected)
- [ ] Dependency audit
- [ ] Secret scan (no API keys in source)

---

## Deployment target

**Platform:** [ ] AWS Lambda  [ ] Google Cloud Run  [ ] Kubernetes  [ ] Modal  [ ] Replicate  [ ] Self-hosted  [ ] Other: ___
**Environments:** [ ] dev  [ ] staging  [ ] production
**Production deploy gate:** [ ] manual approval + eval pass  [ ] automated on staging pass

---

## Observability

**Metrics:** [ ] Prometheus  [ ] Datadog  [ ] CloudWatch  [ ] LangSmith  [ ] Langfuse  [ ] Other: ___
**LLM tracing:** [ ] LangSmith  [ ] Langfuse  [ ] OpenTelemetry GenAI semconv  [ ] None  [ ] Other: ___
**Cost monitoring:** [ ] provider billing API  [ ] LangSmith cost tracking  [ ] Custom  [ ] None
**Alerting on:** [ ] cost ceiling breach  [ ] eval regression  [ ] latency p99 breach  [ ] error rate  [ ] Other: ___

_(Monitor generates token-budget, cost-ceiling, latency, and eval-regression alerts — not standard server configs.)_

---

## Notes

_API key rotation schedule, eval update cadence, red-team testing schedule:_
