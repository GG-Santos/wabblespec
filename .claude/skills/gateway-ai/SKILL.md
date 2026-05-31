---
name: gateway-ai
description: AI capability gateway. Cross-cutting standards for any project embedding LLM features — prompt engineering, chain design, agent architecture, evaluation, safety, and model governance. Activates on AI/Agent build target always; activates on any other target when Explore detects an LLM SDK dependency.
---

# Gateway: AI

Cross-cutting AI standards layer. Activates on top of (not instead of) the active platform package. Platform modules handle platform-specific threats. This gateway handles concerns that apply to any LLM-embedded project regardless of platform: prompt engineering standards, chain contracts, agent loop bounds, evaluation policy, safety requirements, and model governance.

## What this skill does

| Concern | Covered by L3 platform | Covered by L4 AI gateway |
|---|---|---|
| Platform-specific injection (shell, SQL, XSS) | Yes (L3) | — |
| System prompt versioning and testing | No L3 module | Yes |
| Token budget declaration per call | No L3 module | Yes |
| Step contracts in chains | No L3 module | Yes |
| Agent loop bounds | No L3 module | Yes |
| Attestation gate for irreversible tool calls | No L3 module | Yes |
| Eval suite before model/prompt version bump | No L3 module | Yes |
| Red-team adversarial coverage | No L3 module | Yes |
| PII in prompts (DPA required) | Partial (Security gateway) | Yes — prompt-level |
| Model version pinning (no `latest` in prod) | No L3 module | Yes |
| Fallback model declaration | No L3 module | Yes |
| LLM output validation before execution | No L3 module | Yes |

## When to use

- AI/Agent build target: always active
- Any target where Explore detects LLM SDK dependency
- P3 Technical Spec for AI features on any target
- Explicit `/ai` command

## Activation sequence

### Phase A (Specify time — knowledge injection)

```
1. Confirm platform package (L3) has activated and written its receipt
2. Load references/ directory into Specify context:
   - references/safety.md (prompt injection, output validation, hallucination handling)
   - references/evals.md (eval harness design, fixtures, metrics)
   - references/cost.md (token budget, latency targets, model abstraction)
3. Write gateway-spec-receipt (Phase A)
```

### Phase B (pre-Executor — verdict)

```
1. Load prompt-engineering.md
2. Load chain-design.md
3. Load agent-architecture.md
4. Load evaluation.md
5. Load safety.md
6. Load model-pinning.md
7. Load eval-policy.md
8. Register audit-gates.md with Verifier (supplements platform gates)
9. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Reference Routing

| Situation | Reference |
|---|---|
| ai receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type gateway-spec` / `gateway-verdict` (two-phase)` |

## Output contract

- Prompt engineering compliance check
- Chain step contract audit
- Agent tool declaration completeness check
- Eval suite pass/fail against declared thresholds
- Safety dimension audit
- Model governance check (pinning, fallback, regression)
- Gateway activation receipt with all gate results

## Agent design decision tree

Before committing to an agent tier, verify all four criteria:

- **Complexity** — Is the task multi-step and hard to fully specify in advance?
- **Value** — Does the outcome justify higher cost and latency?
- **Viability** — Is the agent capability-adequate for the task type?
- **Cost of error** — Can errors be caught and recovered from? (tests, review, rollback)

If any criterion is "no": stay at a simpler tier (single call or workflow). Agents add latency, cost, and non-determinism — only use them when the task genuinely requires open-ended model-driven exploration.

## Compaction and prompt caching standards

**Compaction contract:** For long-running conversations using server-side compaction, always append `response.content` (not just the text string) back to messages on every turn. Compaction blocks in the response must be preserved — the API uses them to replace compacted history on the next request. Appending only text silently loses compaction state.

**Prompt caching anti-patterns to gate in spec:**
- Stable content must go before volatile content in the rendering order (tools → system → messages)
- Timestamps, per-request IDs, or varying user inputs must go after the last cache breakpoint — never before
- Cache breakpoints have a minimum token threshold (~1024 tokens) — shorter prefixes silently do not cache
- Verify caching is working via `cache_read_input_tokens` field — if zero across repeated requests, a silent invalidator is active

## MCP tool design standards

When the project builds MCP tools, apply these annotations to every tool declaration:

| Annotation | Meaning | When to set true |
|---|---|---|
| `readOnlyHint` | Tool reads state, never modifies | Query/read/list tools |
| `destructiveHint` | Tool deletes or irreversibly modifies | Delete, drop, overwrite tools |
| `idempotentHint` | Multiple calls with same input = same result | Safe to retry without side effects |
| `openWorldHint` | Tool interacts with external state | Any tool touching external APIs or filesystems |

Tool names must use consistent prefixes — action-oriented and discoverable. Descriptions must answer: what does it do, when to use it, what it accepts, what it returns.

## Files loaded by this module

```
modules/l4/ai/
  prompt-engineering.md
  chain-design.md
  agent-architecture.md
  evaluation.md
  safety.md
  model-pinning.md
  eval-policy.md
  audit-gates.md
```
