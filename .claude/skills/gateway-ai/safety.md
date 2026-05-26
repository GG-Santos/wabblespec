# Safety Requirements

## Output Validation

LLM output never directly executed or rendered without validation. Every LLM output that affects state (code execution, API call, database write) passes through a declared validator before execution.

No raw string interpolation of LLM output into SQL, shell commands, or HTML.

## PII Handling

No PII in prompts without:
- Explicit Data Processing Agreement (DPA) with the model provider
- Declared processing purpose (what the LLM is doing with the PII)
- Anonymization applied where technically feasible

PII in prompts requires GDPR compliance scope declaration (Security gateway).

## Bias

For public-facing applications, eval suite includes fairness dimensions:
- Demographic parity check (outputs consistent across declared demographic groups)
- Disparate impact analysis for decision-support applications

Fairness dimensions declared — not assumed covered by generic accuracy metrics.

## Refusal Handling

Declared: what happens when the model refuses a valid request?
- Retry with modified prompt
- Return structured error to user with explanation
- Route to human review queue

No silent failure on refusal. No infinite retry without declared termination condition.

## Audit Gates

- [ ] No LLM output directly executed or rendered without a declared validator
- [ ] No raw LLM output interpolated into SQL, shell commands, or HTML
- [ ] PII in prompts has DPA + declared purpose + anonymization (where feasible)
- [ ] PII in prompts has Security gateway GDPR scope declaration
- [ ] Refusal handling declared (not silent failure)
- [ ] Public-facing applications include fairness dimensions in eval
