# WabbleSpec v6.1 — AI

**Gateway:** AI
**Layer:** L4 Capability
**Tier:** 1 — CRITICAL ROUTING
**Document scope:** AI gateway — LLM evaluation, prompt engineering, chain and agent design, safety and alignment

---

## Overview

The AI gateway applies to any project embedding AI features — not only the AI/Agent build target. Any target with an LLM SDK dependency activates the AI gateway. The AI/Agent build target routes all implementation content through this gateway. The gateway owns the standards that apply across all LLM-embedded work: prompt engineering, chain and agent design, evaluation policy, model governance, and safety requirements.

**In scope:**
- Prompt engineering standards (system prompts, few-shot examples, temperature, token budgets)
- Chain and agent design (step contracts, branching, error recovery, context passing)
- Agent architecture (tool declaration, loop bounds, human-in-the-loop gates)
- Evaluation policy (dimensions, dataset, regression, red-teaming)
- Safety requirements (output validation, PII handling, bias, refusal handling)
- Model governance (version pinning, fallback declaration, eval before version bump)

**Applies to:** AI/Agent build target (always), any other target with LLM SDK dependency detected by Explore.

---

## Gateway Structure

```
.wabblespec/gateways/ai/
  SKILL.md
  skill-rules.json
  references/
    prompt-engineering.md
    chain-design.md
    agent-architecture.md
    evaluation.md
    safety.md
  rules/
    model-pinning.md
    eval-policy.md
  evaluations/
  schemas/
    receipt.schema.json
```

---

## Activation

`skill-rules.json` triggers AI gateway on:
- AI/Agent build target (always active)
- Any target with LLM SDK dependency detected by Explore (auto-activate)
- P3 Technical Spec for AI features on any target
- Explicit `/ai` command

---

## Prompt Engineering

**Reference:** `references/prompt-engineering.md`

### System Prompt

- Declarative — describes behavior and constraints, does not narrate a persona
- Versioned — committed to source control alongside the code that uses it
- Tested — eval suite covers system prompt behavior, not just user inputs
- Not ad hoc — no system prompts written inline at runtime without a declared template

### Few-Shot Examples

- Curated: examples selected for representativeness, not convenience
- Updated: failure cases observed in production added to few-shot set on regular cadence
- Separate: few-shot examples stored separately from system prompt (not inline)
- Annotated: each example includes a rationale note for why it was included

### Temperature Declaration

| Task type | Temperature guidance |
|---|---|
| Deterministic (classification, structured extraction) | 0 or near-0 |
| Balanced (summarization, Q&A) | 0.3–0.5 |
| Creative (generation, ideation) | 0.7–1.0 |

Temperature is declared per task type in spec — not defaulted. Undeclared = 0 (deterministic) as the safe default.

### Token Budget

Declared in spec for each LLM call:

```markdown
## Token Budget — <call name>

**system_prompt:** N tokens (measured)
**few_shot_examples:** N tokens (measured)
**user_input_max:** N tokens
**output_max:** N tokens
**total_budget:** N tokens
**model_context_window:** N tokens
**headroom:** N tokens
```

Total budget must not exceed model context window minus declared headroom. No implicit assumptions about token counts.

---

## Chain Design

**Reference:** `references/chain-design.md`

### Step Contracts

Each step in a chain has declared:
- **Input schema:** what the step expects (JSON Schema or equivalent)
- **Output schema:** what the step produces
- **Validation:** output validated against schema before passed to next step

No implicit data passing between steps. No step assumes the previous step's output format without a declared contract.

### Branching

Conditional routing declared explicitly. No implicit branching based on model output parsing. Branch conditions declared as deterministic logic (regex, schema check, confidence threshold) — not "the model decides."

### Error Recovery

Fallback declared per step — not per chain. Chain-level error handling cannot mask step-level failures. Per-step fallback options:
- Retry with modified input
- Return structured error to caller
- Route to human review

### Context Passing

Explicit — no global state between chain steps. Each step receives only what it needs. Shared context is passed as a declared parameter, not through a shared mutable object.

---

## Agent Architecture

**Reference:** `references/agent-architecture.md`

### Tool Declaration

Every tool the agent can call has declared:

```markdown
## Tool — <tool-name>

**description:** <what this tool does — used by model for tool selection>
**input_schema:** <JSON Schema>
**output_schema:** <JSON Schema>
**side_effects:** true|false
**reversible:** true|false
**attestation_required:** true|false (for irreversible side effects)
```

Tools with `side_effects: true` and `reversible: false` require `attestation_required: true` — human confirmation before execution.

### Tool Selection

Model selects which tool to call. Tool execution is deterministic — the tool does what it declares, unconditionally. The model cannot influence tool behavior through its arguments beyond the declared input schema.

### Loop Bounds

Maximum iterations declared for all agent loops. No unbounded agent loops. Default maximum if not declared: 10 iterations. Reaching maximum iterations is a declared error state with a declared fallback (not silent termination).

### Observation Format

Tool output returned to model as structured observation — not raw text. Structured observations improve model reliability and make tool output auditable.

```json
{
  "tool_name": "string",
  "call_id": "string",
  "status": "success|error",
  "result": {},
  "error": null
}
```

### Human-in-the-Loop

Irreversible tool calls (file deletion, payment, API calls with side effects) require Attestation gate — human confirms before execution. This mirrors the core Attestation pattern (I8) applied to agent tool use.

---

## Evaluation Policy

**Reference:** `references/evaluation.md` and `rules/eval-policy.md`

### Eval Dimensions

Declared per use case at P1. No universal eval dimension set — dimensions depend on what the LLM is being asked to do.

Common dimensions:

| Dimension | Measurement approach |
|---|---|
| Accuracy | Ground truth comparison on labeled dataset |
| Helpfulness | Human rating or LLM-as-judge on curated set |
| Safety | Red-team adversarial input pass rate |
| Latency | p50 / p99 measured against declared budget |
| Cost | Token cost per call measured against budget |
| Refusal rate | Valid requests refused (false positive refusal) |

### Eval Dataset

- Curated: selected for representativeness, not convenience
- Versioned: committed to source control alongside prompt versions
- Separate: development data never used in eval without explicit separation
- No production data: production data not in eval suite without anonymization

### Regression

Eval suite runs on every model or prompt change. Not optional. Regression before any prompt or model version bump ships to production. Eval-policy.md: eval suite must pass declared thresholds before change proceeds.

### Red-Teaming

Adversarial inputs tested. Failure modes documented. Red-team coverage:
- Prompt injection attempts
- Jailbreak attempts (for safety-critical applications)
- Edge case inputs (empty, malformed, very long, unicode edge cases)
- Out-of-scope requests

Red-team findings written to Memory as FRESH drawers for Instinct pattern tracking.

---

## Safety Requirements

**Reference:** `references/safety.md`

### Output Validation

LLM output never directly executed or rendered without validation. Every LLM output that affects state (code execution, API call, database write) passes through a declared validator before execution.

No raw string interpolation of LLM output into SQL, shell commands, or HTML.

### PII Handling

No PII in prompts without:
- Explicit Data Processing Agreement (DPA) with the model provider
- Declared processing purpose (what the LLM is doing with the PII)
- Anonymization applied where technically feasible

PII in prompts requires GDPR compliance scope declaration (Security gateway).

### Bias

For public-facing applications, eval suite includes fairness dimensions:
- Demographic parity check (outputs consistent across declared demographic groups)
- Disparate impact analysis for decision-support applications

Fairness dimensions declared — not assumed covered by generic accuracy metrics.

### Refusal Handling

Declared: what happens when the model refuses a valid request?
- Retry with modified prompt
- Return structured error to user with explanation
- Route to human review queue

No silent failure on refusal. No infinite retry without declared termination condition.

---

## Model Governance

**Reference:** `rules/model-pinning.md`

### Version Pinning

Model version pinned in all environments — no `latest` alias in production. Pinned version format: provider-specific model ID (e.g., `claude-sonnet-4-6`, `gpt-4o-2024-08-06`).

### Version Bump Process

Before promoting to a new model version:
1. Eval suite runs against new model version
2. All declared dimensions must pass thresholds
3. Red-team pass on known failure cases
4. Staged rollout: staging first, production after validation
5. Rollback plan declared before promotion begins

### Fallback Model

Declared for each model use: what model is used if primary model is unavailable? Fallback model must pass eval suite at baseline threshold. No fallback = model unavailability is a declared outage (acceptable if explicitly stated).

---

## Integration Points

| Module | Relationship |
|---|---|
| Apply | Apply reads AI gateway SKILL.md for routing during AI feature execution |
| Verifier | Verifier Measurement mode reads AI gateway eval dimensions for quantitative verification |
| Explore | Explore detects LLM SDK dependencies and notifies AI gateway to activate |
| Security gateway | PII in prompts crosses into Security/GDPR compliance scope |
| Platform packages (L3) | AI/Agent platform package routes all implementation content through AI gateway |
| Memory | Red-team findings and eval results written to Memory for Instinct pattern tracking |
| ModelRouter (L4) | ModelRouter implements AI gateway model selection and routing decisions |

---

## Verification Mode

**Measurement** — eval suite passes declared thresholds, model version pinned, token budget declared and within spec, safety dimensions evaluated, tool declarations complete.

---

## Receipt Extension Fields

```json
{
  "model_pinned": true,
  "eval_dimensions": ["accuracy", "safety", "latency"],
  "eval_pass": true,
  "token_budget_declared": true,
  "tools_declared": 0,
  "attestation_gates": 0
}
```

---

## Cross-References

- L3 AI/Agent platform package: `WabbleSpec v6.1 — Platform.md` § AI/Agent
- L4 ModelRouter: `WabbleSpec v6.1 — Core.md` § L4 Capability
- Security gateway (PII, GDPR): `WabbleSpec v6.1 — Security.md`
- Verification modes (Measurement): `WabbleSpec v6.1 — Core.md` § Verification Modes
- Invariants (I8 — human gates for irreversible tool calls): `WabbleSpec v6.1 — Core.md` § Invariants
