# AI/Agent Systems Design Template (P2)

> **Platform:** AI/Agent | **Prerequisite:** design-document.md complete.

---

## System Architecture

```
User input
  └── Input sanitization + safety check
        └── Prompt construction (template + context)
              └── Model API call (pinned model)
                    ├── Tool calls (if applicable)
                    │     └── Tool executor → result → back to model
                    └── Output
                          └── Output safety scan
                                └── Response to user
```

---

## Prompt Architecture

**System prompt:** Stored in `prompts/system.txt` (version-controlled). Never hardcoded inline.

**Prompt template:** Jinja2 / f-string template. Variables declared:

| Variable | Source | Validation |
|---|---|---|
| `{{user_input}}` | User | Sanitized, length-capped |
| `{{context}}` | Retrieved documents | Truncated to fit context window |
| `{{history}}` | Conversation store | Last N turns only |

**Prompt versioning:** Each prompt version tagged in git. Eval suite tied to prompt version. Rollback = revert prompt file.

**Context window budget:**
```
Total context window: ___ tokens
  ├── System prompt: ~___ tokens (fixed)
  ├── Conversation history: up to ___ tokens
  ├── Retrieved context: up to ___ tokens
  └── User input: up to ___ tokens (enforce hard limit)
```

---

## RAG Architecture (if applicable)

```
Query
  └── Embedding model → vector
        └── Vector search → top-K chunks
              └── Reranker (optional)
                    └── Context assembly → prompt
```

**Embedding model:** ___ (pinned version)
**Vector store:** ___ (Pinecone / Chroma / pgvector)
**Top-K:** ___ chunks
**Chunk size:** ___ tokens with ___ overlap
**Staleness:** Index refresh frequency: ___

---

## Memory Architecture (multi-turn)

| Memory type | Storage | TTL | What stored |
|---|---|---|---|
| Working memory | In-request context | Request lifetime | Current conversation |
| Short-term | Redis / DB | ___ hours | Recent sessions |
| Long-term | Vector store | Permanent | Summarized user context |

**Memory injection:** Injected into prompt within context budget. Oldest turns summarized and compressed when budget exceeded.

---

## Tool Execution

```
Model returns tool_call
  └── Validate tool name against allowlist
        └── Validate parameters against schema
              └── Execute tool with timeout
                    └── Return result to model
```

**Tool timeout:** ___ seconds. Exceeded → return error to model, model decides next step.
**Max tool calls per request:** ___ (prevents runaway loops)
**Irreversible tools:** Require confirmation before execution (separate from model output).

---

## Observability

| Signal | Storage | Retention |
|---|---|---|
| Request + response (sampled) | Structured log | ___ days |
| Token counts (all) | Metrics | ___ days |
| Latency (all) | Metrics | ___ days |
| Cost per request | Metrics | 90 days |
| Safety rejections | Audit log | 1 year |
| Eval scores | Eval store | Permanent |

**PII in logs:** Requests containing PII must be masked before logging. Never log raw user input without scrubbing.
