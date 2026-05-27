# AI/Agent Design Document Template (P1)

> **Platform:** AI/Agent
> **Template version:** 1.0
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**
> **L4 AI gateway must be loaded before this template is used.**

---

## Overview

[REQUIRED] What AI capability this system provides, who uses it, what decisions or outputs it produces, and what happens when it fails or produces wrong output.

---

## Model Selection [REQUIRED]

| Property | Value |
|---|---|
| Model ID (pinned) | e.g. `claude-sonnet-4-6`, `gpt-4o-2024-08-06` |
| Capability required | code-generation / analysis / synthesis / long-context / vision |
| Fallback model | (if primary unavailable) |
| Why this model | [reasoning — not model name, but capability match] |

**Model pinning is mandatory.** Unpinned models change behavior on provider updates without any code change.

---

## Agent Architecture [REQUIRED]

[ ] Single-turn — one prompt, one response, done
[ ] Multi-turn — conversation with memory
[ ] Tool-calling — model calls declared tools, result fed back
[ ] Multi-agent — multiple specialized agents coordinated
[ ] RAG — retrieval + generation

**Agent roles** (for multi-agent):

| Agent | Responsibility | Can call | Cannot call |
|---|---|---|---|
| Orchestrator | Route tasks | Specialist agents | External APIs directly |
| Specialist | Execute task | Declared tools | Other specialists |

---

## Tool Declarations [REQUIRED] (if tool-calling)

Every tool the agent can call must be declared here. Undeclared tools are not built.

| Tool name | Description | Input | Output | Side effects |
|---|---|---|---|---|
| `search_web` | Search the web | `query: string` | `results: string[]` | Network call |
| `write_file` | Write to filesystem | `path, content` | `success: bool` | File I/O |

**No tools with irreversible side effects without a confirmation step.** (delete, send email, make payment)

---

## Eval Suite [REQUIRED]

Without an eval suite, there is no way to know if a prompt change or model update regressed behavior.

**Dataset:** ___ examples minimum. Stored at: `evals/dataset.jsonl`

**Pass threshold:** ___ % (e.g., 85% of eval cases must pass)

**Eval dimensions:**

| Dimension | Measurement | Threshold |
|---|---|---|
| Correctness | LLM-as-judge or exact match | ≥ ___% |
| Refusal rate (harmful) | Does model refuse harmful prompts? | 100% |
| Hallucination rate | Factual claims verifiable | ≤ ___% |
| Latency p95 | Time to first token + completion | < ___ seconds |

---

## Cost Budget [REQUIRED]

| Metric | Budget |
|---|---|
| Cost per request (average) | < $___  |
| Cost per request (max) | < $___ (circuit-break above this) |
| Monthly total | < $___ |
| Max tokens per request (input) | ___ |
| Max tokens per request (output) | ___ |

**Cost circuit-breaker:** Request exceeding max cost threshold is rejected before sending to model.

---

## Safety Boundaries [REQUIRED]

| Boundary | Input check | Output check |
|---|---|---|
| No harmful content generation | Input classifier or prompt instruction | Output scanner |
| No PII leakage | PII detection on input | PII scan on output before returning |
| No prompt injection | Sanitize user input before insertion | N/A |
| No jailbreak execution | System prompt hardening | Refusal detection |

**Escalation path:** When safety boundary is triggered: [ ] Return error to user [ ] Log + return safe fallback [ ] Alert + halt

---

## GWT Acceptance Scenarios (AI/Agent-specific)

```
Given: a prompt known to produce correct output in eval dataset
When: the agent is called with that prompt
Then: output matches expected within declared correctness threshold
      AND response time is within latency budget
      AND token count is within declared max

Given: a prompt injection attempt in user input
When: the agent processes the input
Then: the injected instruction is not executed
      AND the agent responds to the original intent
      AND the injection attempt is logged

Given: the declared model is unavailable
When: the agent attempts to call the model
Then: fallback model is used (if declared)
      AND response clearly indicates degraded mode
      AND cost metrics reflect fallback model pricing

Given: a harmful content request is submitted
When: the safety boundary classifier evaluates the input
Then: the request is rejected before reaching the model
      AND the user receives a safe refusal message
      AND the attempt is logged for audit
```

---

## Open Questions

Specify blocks receipt until REQUIRED sections complete and eval dataset exists with minimum example count.
