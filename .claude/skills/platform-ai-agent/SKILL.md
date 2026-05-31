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

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/ai/core.md
    - .wabblespec/engine/shared/dev/frameworks/ai/safety.md
  conditional_load:
    - signal: "langchain in dependencies"
      load: .wabblespec/engine/shared/dev/frameworks/ai/langchain.md
    - signal: "openai in dependencies"
      load: .wabblespec/engine/shared/dev/frameworks/ai/openai-sdk.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-ai/references/             # always for AI/Agent
```

## MCP tool annotation standard

When the project builds or consumes MCP tools, every tool declaration must include these four annotations. Missing annotations are a spec incompleteness — add them before Executor writes code:

| Annotation | Set true when |
|---|---|
| `readOnlyHint: true` | Tool only reads, never modifies state (queries, lists, fetches) |
| `destructiveHint: true` | Tool deletes or irreversibly modifies (delete, drop, overwrite) |
| `idempotentHint: true` | Multiple identical calls produce the same result (safe to retry) |
| `openWorldHint: true` | Tool interacts with external state (filesystem, APIs, databases) |

Tool naming: use consistent action-prefixed names. Description must state: what it does, when to use it, what it accepts, what it returns.

## Sub-Agent Context Enrichment

When delegating a task to an external agent via any `~~agent-delegate` capability, enrich the task prompt with these 5 context fields before dispatching. Each field improves sub-agent output coherence without requiring it to re-derive project state.

| Field | What to inject |
|---|---|
| Active branch | Current git branch name |
| Recently modified files | Files changed in the last 3–5 commits (limit to 10) |
| Recent commits | Last 5 commit messages, one line each |
| Staged changes | Files currently staged but not committed |
| Active task context | Active task card goal and current wave objective (1–2 sentences) |

**AGENTS.md structure:** An `AGENTS.md` file in the project root gives an external agent persistent project context across sessions. Recommended sections:

```
## Project Overview
[one-paragraph description]

## Tech Stack
[language, framework, testing approach]

## Code Conventions
[linter, naming, file organization]

## Testing Requirements
[coverage target, test types required]

## Build and Deploy
[build command, test command]
```

This file replaces ad-hoc context injection for external agents that support it. Treat it as a machine-readable project brief that improves first-turn task quality.

## Reference Routing

| Situation | Reference |
|---|---|
| ai-agent receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type platform-activation` |

## Output contract

**Platform activation receipt** (`.wabblespec/state/receipts/platform-ai-agent-{timestamp}.json`)

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
