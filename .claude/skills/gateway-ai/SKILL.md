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

## Output contract

- Prompt engineering compliance check
- Chain step contract audit
- Agent tool declaration completeness check
- Eval suite pass/fail against declared thresholds
- Safety dimension audit
- Model governance check (pinning, fallback, regression)
- Gateway activation receipt with all gate results

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
