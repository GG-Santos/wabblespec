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

**Dataset structure for classification tasks:**
- Minimum 50 labeled examples per class; 150+ total preferred
- Difficulty tiers declared: easy / medium / hard per example
- Class balance documented — if classes are imbalanced, macro F1 is the primary metric (not accuracy)
- Ground-truth labels are human-verified, not model-generated

**Eval output requirements:**
- Per-class precision, recall, and F1 reported for all multi-class tasks
- Macro F1 is the headline metric for multi-class tasks where all classes matter equally
- Accuracy alone is insufficient when classes are imbalanced

---

## Baseline Comparison

**Rule:** Model eval results must beat naive baselines. Passing a threshold in isolation is insufficient — a random classifier may nearly match a weak model on a balanced dataset.

Required baselines for classification tasks:

| Baseline | Description | When required |
|---|---|---|
| Random | Uniform random class assignment | Always |
| Majority class | Always predict the most common class | Always |
| Simple heuristic | Length or keyword rule with no model | When applicable |

**Pass condition:** Proposed model's macro F1 must exceed all applicable baselines. If it does not, the eval FAILS even if it passes the declared threshold — the threshold must be recalibrated.

**Why this matters:** A model reaching 90% accuracy while random gets 85% on the same balanced 5-class task only outperforms chance by ~12.5% relative. Baseline comparison surfaces this before production.

**Receipt field:** `eval_baseline_comparison` — object with keys for each baseline and values for their accuracy and macro F1. Populated for all classification evals.

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
