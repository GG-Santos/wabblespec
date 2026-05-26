# Performance Budgets — AI Agent

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l4/ai`, `l3/ai-agent`.
> Reference: `_shared/references/performance-budgets.md`.
> Note: AI agent budgets combine cost, latency, quality, and safety targets.

---

## Latency

### End-to-end agent response latency

**Target:** ≤ ___ s for single-turn completion (p95); ≤ ___ s for multi-step agent loop completion (p95)
**Rationale:** Declare realistic targets based on model and chain complexity; unreachable targets cause alert fatigue
**Measurement:** trace from user request received to final response delivered; include all LLM calls, tool calls, and memory reads in span
**PII impact:** traces must not capture prompt or response content without explicit consent

### LLM call latency (per call)

**Target:** ≤ ___ ms to first token (TTFT) at p95; ≤ ___ ms to completion at p95
**Rationale:** TTFT determines perceived responsiveness in streaming interfaces; completion latency determines throughput ceiling
**Measurement:** OpenTelemetry span around each model call; TTFT = time to first streaming chunk
**PII impact:** none — log latency only, not content

---

## Cost

### Token budget per operation

**Target:** ≤ ___ input tokens + ≤ ___ output tokens per declared operation type
**Rationale:** Token budgets prevent runaway cost from adversarial inputs or recursive loops; required by `l4/ai` prompt-safety-policy P5
**Measurement:** token count logged per call; alert on p99 exceeding declared budget by > 2×
**PII impact:** token count logs must not include prompt content

### Cost per operation ceiling

**Target:** ≤ $___ per operation (declare based on business model; alert at 80% of ceiling)
**Rationale:** Cost ceiling prevents prompt injection attacks that drain API budget through forced large outputs
**Measurement:** cost tracking via provider billing API; per-operation cost calculation
**PII impact:** none

### Monthly cost ceiling

**Target:** ≤ $___ / month (declare and set hard cutoff, not just an alert)
**Rationale:** Unbounded LLM cost is an operational risk; hard cutoffs with graceful degradation are required for production AI agents
**Measurement:** billing API polling; circuit breaker pattern that pauses non-critical operations at 90% of ceiling
**PII impact:** none

---

## Quality

### Eval suite pass rate

**Target:** ≥ ___ % on declared eval suite before each model or prompt version bump
**Rationale:** Required by `l4/ai` model-governance-policy M2; no version bump without passing eval
**Measurement:** eval harness run in CI against held-out fixture set; block deploy on failure
**PII impact:** eval fixtures must not contain real user data

### Hallucination rate (if applicable)

**Target:** ≤ ___ % factually incorrect claims in structured-output tasks (declare based on use case risk)
**Rationale:** Hallucination rate is use-case dependent; high-risk domains (medical, legal, financial) require near-zero
**Measurement:** automated fact-checking eval against ground truth; human spot-check sample
**PII impact:** eval data must be anonymized

---

## Safety

### Agent loop iteration ceiling

**Target:** ≤ ___ iterations per agent invocation (required — no unbounded loops)
**Rationale:** Required by `l4/ai` model-governance-policy M3; unbounded loops are both a cost and a safety risk
**Measurement:** iteration counter enforced in agent loop code; assert in integration tests
**PII impact:** none

### Irreversible tool call rate requiring Attestation

**Target:** 100% of irreversible tool calls (file delete, external POST, email send, database write) require explicit Attestation before execution
**Rationale:** Required by `l4/ai` agent-architecture; tool calls without Attestation gates are a safety failure
**Measurement:** code audit; integration test that verifies Attestation prompt fires before each irreversible operation
**PII impact:** Attestation logs must record who approved and when

### Prompt injection detection rate

**Target:** ≥ ___ % of injected prompt attacks caught by input validation layer (red-team benchmark)
**Rationale:** Required by `l4/ai` safety.md; user text must be delimited and validated before insertion into system context
**Measurement:** red-team benchmark with injection fixture set; gate must catch known injection patterns
**PII impact:** none

---

## Availability

### Agent service availability

**Target:** 99.5% uptime (lower than standard web SLA because LLM provider outages are outside control)
**Rationale:** Declare realistic availability; dependency on third-party LLM providers introduces unavoidable variance
**Measurement:** synthetic probe hitting the agent endpoint every 60s; measure separately from provider availability
**PII impact:** probe requests must not contain real user data

### Fallback model availability

**Target:** Fallback model declared and reachable; failover to fallback if primary model p99 latency > 2× SLA for 2 consecutive minutes
**Rationale:** Required by `l4/ai` model-governance-policy; single-model dependency is a reliability failure
**Measurement:** health check for both primary and fallback models; failover test in staging
**PII impact:** none

---

## PII fields (excluded from log schema)

<!-- AI agents process high-risk PII: prompts contain user intent, responses may contain generated PII -->
<!-- Example:
- prompt_content (may contain user-supplied PII)
- response_content (may contain generated personal data)
- user_id (if tied to prompt history)
- conversation_id (if linkable to individual)
-->
___ UNDECLARED — REQUIRED before production deployment; AI systems often have heightened DPA obligations
