# AI Gateway — Audit Gates

Verifier registers these gates when AI gateway activates. All HARD gates must PASS for gateway receipt to be PASS. SOFT gates flag only — do not block.

## Prompt Engineering Gates

| Gate | Severity | Check |
|---|---|---|
| PE-1 | HARD | System prompt committed to source control |
| PE-2 | HARD | Temperature declared per call type |
| PE-3 | HARD | Token budget declared and within context window minus headroom |
| PE-4 | SOFT | Few-shot examples stored separately from system prompt |
| PE-5 | SOFT | No inline ad hoc system prompts in runtime code |

## Chain Design Gates

| Gate | Severity | Check |
|---|---|---|
| CD-1 | HARD | Every chain step has declared input and output schema |
| CD-2 | HARD | Output validated before passing to next step |
| CD-3 | HARD | Branch conditions are deterministic (not model-resolved) |
| CD-4 | SOFT | Per-step fallback declared |

## Agent Architecture Gates

| Gate | Severity | Check |
|---|---|---|
| AG-1 | HARD | Every tool has complete declaration (all 6 fields) |
| AG-2 | HARD | All irreversible side-effect tools have attestation_required:true |
| AG-3 | HARD | Maximum iterations declared for every agent loop |
| AG-4 | HARD | Tool observations returned as structured JSON |

## Evaluation Gates

| Gate | Severity | Check |
|---|---|---|
| EV-1 | HARD | Eval dimensions declared at P1 |
| EV-2 | HARD | Eval suite ran before this model/prompt version |
| EV-3 | HARD | All blocking dimensions passed declared thresholds |
| EV-4 | SOFT | Red-team coverage completed |
| EV-5 | SOFT | Red-team findings written to Memory |

## Safety Gates

| Gate | Severity | Check |
|---|---|---|
| SA-1 | HARD | No LLM output directly executed without validator |
| SA-2 | HARD | No raw LLM output interpolated into SQL, shell, or HTML |
| SA-3 | HARD | PII in prompts has DPA + declared purpose |
| SA-4 | HARD | Refusal handling declared |
| SA-5 | SOFT | Fairness dimensions in eval (public-facing applications) |

## Model Governance Gates

| Gate | Severity | Check |
|---|---|---|
| MG-1 | HARD | Model version pinned in all environments |
| MG-2 | HARD | Fallback model declared or outage accepted explicitly |
| MG-3 | HARD | Version bump followed: eval → red-team → staging → production |
