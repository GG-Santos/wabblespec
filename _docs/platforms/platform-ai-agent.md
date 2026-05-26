# Platform: AI Agent

AI/LLM-backed agent target. Activates when Recipe identifies an AI agent, LLM application, RAG system, or AI-powered feature as the primary build target.

**Skill:** `modules/l3/ai-agent/SKILL.md`

## What makes AI Agent different

| Concern | AI Agent approach |
|---------|-----------------|
| Prompt injection | User-controlled input paths to LLM identified and sanitized |
| Output validation | LLM output validated before use in downstream operations |
| Eval harness | Evaluation strategy declared — what metrics, what fixtures |
| Tool permissions | Tool-using agents declare minimal permission set per tool |
| Hallucination | Strategy declared for factual tasks — retrieval grounding, confidence scoring, or human review |
| Model abstraction | Implementation uses capability descriptors via model-router — no hard-coded model names |
| Cost control | Token budget declared per operation — unbounded inference calls flagged |

## Platform-specific spec sections

- Agent architecture: prompt chain, tool list, memory strategy, output routing
- Eval spec: held-out fixtures, metrics, acceptance thresholds — required before deployment
- Prompt design: system prompt, few-shot examples, output format instructions — all versioned
- Tool manifest: each tool with name, description, parameter schema, permission level
- Safety boundaries: what the agent may and may not do autonomously
- Fallback strategy: what happens when LLM fails, times out, or returns invalid output

## Security controls loaded

- Prompt injection: all user inputs validated and sanitized before LLM context assembly
- Tool boundary enforcement: agent cannot invoke tools outside declared manifest
- Output sandboxing: LLM output used in code execution, shell commands, or file writes requires explicit validation step
- Data leakage: PII must not appear in prompts sent to external LLM APIs without declared consent handling

## Mandatory gateway

`gateway-ai` activates for all AI Agent targets — it is not optional. The gateway-ai checks listed in `_docs/gateways/gateway-ai.md` apply in full.

## Gateway interaction

AI Agent targets activate:
- `gateway-security` — always (prompt injection, tool permissions)
- `gateway-engineering` — Medium/High complexity
- `gateway-ai` — always and mandatory
