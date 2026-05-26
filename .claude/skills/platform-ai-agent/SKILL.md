---
name: platform-ai-agent
description: AI/Agent platform. Activates when Recipe detects a project that embeds LLMs, builds autonomous agents, or implements AI-powered workflows. Routes entirely through L4 AI gateway. Loads agent-specific spec templates focused on model pinning, eval harness, prompt versioning, cost budgets, failure modes, and safety boundaries. Produces a materially different spec from Web or API targets — AI failure modes (hallucination, prompt injection, cost explosion) are absent from generic templates.
---

# Platform: AI/Agent

You are the AI/Agent platform layer. You activate when Recipe identifies an LLM-embedded system, autonomous agent, or AI-powered workflow.

## What this skill does

Loads AI/Agent-specific spec templates, engineering standards, security controls, and verification gates. Routes all LLM-specific concerns to L4 AI gateway. Writes a platform activation receipt.

## When to use

Recipe must have already run and identified AI/Agent as the primary target. Activation signals in `skill-rules.json`.

## What makes AI/Agent different from other targets

| Concern | AI/Agent | Web | API/Service |
|---|---|---|---|
| Failure mode | Hallucination, wrong answer, prompt injection, refusal | 5xx, timeout | 5xx, timeout |
| Determinism | Non-deterministic — same input ≠ same output | Deterministic | Deterministic |
| Success signal | Eval suite pass rate, human eval score | HTTP 200 | HTTP 2xx |
| Cost | Per-token cost — runaway loops can cost thousands | Server cost | Server cost |
| Model pinning | Required — model updates change behavior without code change | N/A | N/A |
| Versioning | Prompt changes are code changes — require version control | API versioning | API versioning |
| Safety | Harmful output, jailbreak resistance, PII leakage | XSS, injection | Injection, auth |
| Testing | Eval dataset + LLM-as-judge + human review | Unit + integration | Unit + integration |

A spec written without this platform context will miss: model pinning (behavior changes silently on model update), eval harness (no way to know if a prompt change regressed), cost safeguards (agent loops can exceed budget in minutes), prompt injection vectors, and safety boundaries.

## Mandatory L4 AI Gateway

AI/Agent platform ALWAYS loads the L4 AI gateway (`modules/l4/ai/`). This is not optional. The AI gateway contains: model pinning policy, eval requirements, chain design rules, safety controls, and audit gates.

## Activation sequence

```
1. Recipe identifies AI/Agent target and signals platform-ai-agent activation
2. Load L4 AI gateway (mandatory)
3. Load spec-template variant
4. Load engineering/build-toolchain.md and engineering/performance-budgets.md
5. Load security/threat-model.md and security/platform-controls.md
6. Register verification/gates.md with Verifier
7. Write platform activation receipt
```

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `_shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - _shared/dev/frameworks/ai/core.md
    - _shared/dev/frameworks/ai/safety.md
  conditional_load:
    - signal: "langchain in dependencies"
      load: _shared/dev/frameworks/ai/langchain.md
    - signal: "openai in dependencies"
      load: _shared/dev/frameworks/ai/openai-sdk.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-ai/references/             # always for AI/Agent
```

## Output contract

**Platform activation receipt** (`.wabblespec/receipts/platform-ai-agent-{timestamp}.json`)

## Files loaded by this module

```
modules/l4/ai/                          ← ALWAYS loaded
modules/l3/ai-agent/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
