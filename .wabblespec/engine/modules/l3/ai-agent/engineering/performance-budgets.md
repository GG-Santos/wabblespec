# AI/Agent Engineering — Performance Budgets

## Latency Budgets

| Metric | Budget | Notes |
|---|---|---|
| Time to first token | < 1s | Streaming — show progress immediately |
| Total response time (short) | < 5s | Simple queries |
| Total response time (complex) | < 30s | Multi-step agent; show progress |
| Tool call round trip | < 3s | Tool execution + model processing |
| Max agent turns per request | ___ turns | Hard limit to prevent runaway loops |

**Streaming:** Always stream responses when latency budget exceeds 3s. Never make user wait for full response before showing anything.

---

## Token Budgets

| Component | Token limit | Enforcement |
|---|---|---|
| User input | ___ tokens | Hard cap before API call |
| System prompt | ___ tokens | Fixed — monitored for growth |
| Retrieved context (RAG) | ___ tokens | Truncate at retrieval |
| Conversation history | ___ tokens | Summarize oldest turns |
| Output | ___ tokens | `max_tokens` in API call |
| Total context | ≤ model context window | Always verified before call |

---

## Cost Budgets

| Metric | Budget |
|---|---|
| Cost per request (average) | < $___ |
| Cost per request (max, circuit-break) | < $___ |
| Daily cost | < $___ |
| Monthly cost | < $___ |
| Eval suite cost per CI run | < $___ |

**Cost by operation type:**

| Operation | Expected cost | Notes |
|---|---|---|
| Simple query | $0.00X | Short context, short output |
| Complex analysis | $0.0X | Long context, long output |
| Agent with tool calls | $0.0X | Multiple model calls |

---

## Throughput

| Metric | Target |
|---|---|
| Requests per minute (sustained) | ___ |
| Burst capacity | ___ (declare rate limit strategy) |
| Concurrent requests | ___ |

**Rate limiting:** Declare client-facing rate limits. These are lower than provider limits — protect cost budget.

---

## Eval Performance

| Metric | Target |
|---|---|
| Eval suite size | ___ examples minimum |
| Correctness pass rate | ≥ ___% |
| Safety refusal rate (harmful prompts) | 100% |
| Hallucination rate | ≤ ___% |
| Eval CI run duration | < ___ minutes |
