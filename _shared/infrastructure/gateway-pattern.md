# Gateway Pattern

Gateway architecture specification and routing protocol. Modules at L4 are gateways — they do not execute tasks, they determine whether execution is safe, complete, and appropriate for the target domain.

## Gateway role

A gateway module answers one question: "Is this execution ready to proceed in this domain?"

Gateways do not:
- Write code or spec artifacts
- Call Executor
- Modify receipts from other modules

Gateways do:
- Read the task card, platform declaration, and wave plan
- Apply domain-specific checks (security, engineering standards, design, experience, AI safety)
- Emit a PASS/BLOCK/FLAG verdict with reasoning
- Write their own gateway receipt

## Gateway layers (L4)

| Gateway | Domain | When it runs |
|---|---|---|
| gateway-security | Security threat model, vulnerability surface | Before any wave touching auth, data, infra, or external APIs |
| gateway-engineering | Build quality, standards compliance, architectural soundness | Before any wave in an engineering execution |
| gateway-ai | LLM safety, prompt injection, bias, evaluation | Before any wave producing AI/LLM output |
| gateway-aesthetic | Visual brand, style consistency | Before UI/design deliverables |
| gateway-design | UX, interaction design, user flow | Before UX/interaction deliverables |
| gateway-experience | Accessibility, performance, delight | Before user-facing experience work |

## Two-phase gateway activation

Gateways operate in two phases. Both are required.

### Phase A — Inform (Specify time)

Phase A runs during Specify, before any execution. Purpose: inject domain knowledge and requirements into the spec as acceptance criteria.

Phase A receipt type: `gateway-spec-receipt`

```json
{
  "type": "gateway-spec-receipt",
  "gateway": "string — which gateway",
  "phase": "A",
  "status": "INFORM",
  "knowledge_loaded": ["list of reference files loaded into Specify context"],
  "requirements_added": ["list of requirements injected as acceptance criteria"],
  "notes": "string — any domain-specific observations"
}
```

Phase A for gateway-security specifically:
- Runs STRIDE analysis on the task
- Produces security requirements as acceptance criteria in the spec
- Security requirements from Phase A are mandatory — they are not advisory

### Phase B — Verdict (pre-Executor)

Phase B runs after Specify and before Executor for each wave. Purpose: safety and quality verdict.

Phase B receipt type: `gateway-verdict-receipt` (also called "gateway receipt")

```json
{
  "type": "gateway-verdict-receipt",
  "gateway": "string",
  "phase": "B",
  "verdict": "PASS | FLAG | BLOCK",
  "domain": "string",
  "checks_run": ["array of check names"],
  "flags": ["array of FLAG items — empty if PASS"],
  "block_reason": "string | null",
  "override_required": "boolean"
}
```

### Routing protocol

Standard path with two-phase gateways:
```
Decompose (wave plan)
  → Phase A: [Gateway knowledge injection] → Specify (enriched with requirements)
  → Phase B: [Gateway verdict] → Executor → Verifier
```

A gateway runs once per execution (Phase A at Specify, Phase B before each wave), unless the platform declaration changes mid-execution.

### Gateway BLOCK
If a gateway emits BLOCK: Executor does not run. The BLOCK reason is surfaced to human. Execution is paused until the block condition is resolved (scope narrowed, spec updated, or human override granted).

### Gateway FLAG
FLAG is a non-blocking warning. Execution proceeds, but the FLAG is recorded in the gateway receipt and surfaces in the Archive delivery receipt. FLAGs are audit signals, not execution halts.

### Gateway PASS
PASS: Executor runs normally. Gateway receipt recorded.

## Gateway verdict schema

Each gateway receipt must include:
```json
{
  "verdict": "PASS | FLAG | BLOCK",
  "domain": "string — which gateway domain",
  "checks_run": ["array of check names"],
  "flags": ["array of FLAG items with description — empty if PASS"],
  "block_reason": "string — required if verdict = BLOCK; null otherwise",
  "override_required": "boolean — true if BLOCK requires explicit human override"
}
```

## Cross-gateway sequencing

When multiple gateways apply, run in this order:
1. gateway-security (highest risk — block here first)
2. gateway-engineering
3. gateway-ai (if AI/LLM output involved)
4. gateway-aesthetic / gateway-design / gateway-experience (parallel — domain-independent)

A BLOCK from gateway-security stops the chain — do not run remaining gateways on a security-blocked execution.
