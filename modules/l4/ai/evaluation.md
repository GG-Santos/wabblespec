# Evaluation Policy

## Eval Dimensions

Declared per use case at P1. No universal dimension set — dimensions depend on what the LLM is being asked to do.

Common dimensions:

| Dimension | Measurement approach |
|---|---|
| Accuracy | Ground truth comparison on labeled dataset |
| Helpfulness | Human rating or LLM-as-judge on curated set |
| Safety | Red-team adversarial input pass rate |
| Latency | p50 / p99 measured against declared budget |
| Cost | Token cost per call measured against declared budget |
| Refusal rate | Valid requests refused (false positive refusal rate) |

## Eval Dataset

- Curated: selected for representativeness, not convenience
- Versioned: committed to source control alongside prompt versions
- Separate: development data never used in eval without explicit separation
- No production data: production data not in eval suite without anonymization

## Regression

Eval suite runs on every model or prompt change. Not optional. All declared dimensions must pass thresholds before change proceeds.

## Red-Teaming

Adversarial inputs tested. Failure modes documented. Red-team coverage:

- Prompt injection attempts
- Jailbreak attempts (safety-critical applications)
- Edge case inputs (empty, malformed, very long, unicode edge cases)
- Out-of-scope requests

Red-team findings written to Memory as FRESH drawers for Instinct pattern tracking.

## Audit Gates

- [ ] Eval dimensions declared at P1 (not generic — specific to use case)
- [ ] Eval dataset committed to source control
- [ ] Eval suite runs before any model or prompt version bump
- [ ] Red-team coverage includes prompt injection and edge case inputs
- [ ] Red-team findings written to Memory
