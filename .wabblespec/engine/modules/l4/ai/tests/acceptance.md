# Acceptance Tests — Gateway: AI (L4)

## AT-AI-GW-01: Always activates on AI/Agent build target

**Given** a build target of type AI/Agent
**When** Recipe declares the target
**Then** the AI gateway activates unconditionally — no explicit `/ai` command required

---

## AT-AI-GW-02: Activates on any target with detected LLM SDK dependency

**Given** a Web or API-Service build target where Explore detects an LLM SDK (e.g., openai, anthropic, langchain)
**When** Recipe processes the target
**Then** the AI gateway activates even though the target is not AI/Agent type

---

## AT-AI-GW-03: L3 platform receipt required before activation

**Given** an AI gateway invocation
**When** no L3 platform receipt exists
**Then** the gateway FAILs Phase A — it runs on top of, not instead of, the platform package

---

## AT-AI-GW-04: `latest` model identifier is a BLOCK condition

**Given** AI gateway Phase B evaluating model configuration
**When** any model identifier uses `latest` or equivalent non-pinned reference in production context (rule M1 from model-governance-policy.md)
**Then** verdict is BLOCK — unpinned model identifiers are a hard gate

---

## AT-AI-GW-05: Agent loop bounds must be declared

**Given** AI gateway Phase B evaluating an agent loop
**When** no maximum iteration bound is declared (rule M3)
**Then** verdict is BLOCK — unbounded agent loops are not permitted

---

## AT-AI-GW-06: User text must be delimited from system prompt

**Given** AI gateway Phase B evaluating prompt construction
**When** user-supplied text is not clearly delimited from the system prompt (rule P2 from prompt-safety-policy.md)
**Then** verdict is BLOCK — prompt injection defense is a hard requirement

---

## AT-AI-GW-07: Eval suite required before model/prompt version bump

**Given** AI gateway Phase B evaluating a version bump to a model or system prompt
**When** no eval suite has been run against the new version (rule M2)
**Then** verdict is BLOCK — regression detection gate is mandatory

---

## AT-AI-GW-08: Phase B loads eight files

**Given** AI gateway Phase B
**When** the knowledge load sequence runs
**Then** all eight files are loaded before the verdict is written: prompt-engineering.md, chain-design.md, agent-architecture.md, evaluation.md, safety.md, model-pinning.md, eval-policy.md, audit-gates.md

---

## AT-AI-GW-09: Gateway receipt contains all gate results

**Given** a completed AI gateway Phase B
**Then** the `gateway-verdict-receipt` contains:
- `gateway`
- `phase`
- `verdict` (PASS | FLAG | BLOCK)
- `prompt_engineering_pass`
- `chain_contracts_pass`
- `agent_bounds_declared`
- `eval_suite_run`
- `model_pinned`
- `platform_receipt_verified`
