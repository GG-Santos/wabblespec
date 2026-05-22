---
name: gateway-ai
description: AI capability gateway. Cross-cutting standards for any project embedding LLM features — prompt engineering, chain design, agent architecture, evaluation, safety, and model governance. Activates on AI/Agent build target always; activates on any other target when Explore detects an LLM SDK dependency.
---

# Gateway: AI

Cross-cutting AI standards layer. Activates on top of (not instead of) the active platform package. Platform modules handle platform-specific threats. This gateway handles concerns that apply to any LLM-embedded project regardless of platform: prompt engineering standards, chain contracts, agent loop bounds, evaluation policy, safety requirements, and model governance.

## What this gateway adds beyond platform modules

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

## When to activate

- AI/Agent build target: always active
- Any target where Explore detects LLM SDK dependency
- P3 Technical Spec for AI features on any target
- Explicit `/ai` command

## Activation sequence

```
1. Confirm platform package (L3) has activated and written its receipt
2. Load prompt-engineering.md
3. Load chain-design.md
4. Load agent-architecture.md
5. Load evaluation.md
6. Load safety.md
7. Load model-pinning.md
8. Load eval-policy.md
9. Register audit-gates.md with Verifier (supplements platform gates)
10. Write gateway activation receipt
```

## What this gateway produces

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
