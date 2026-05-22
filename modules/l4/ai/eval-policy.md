# Eval Policy

## When evals run

Evals are mandatory before any of the following:
- Model version bump (primary or fallback)
- System prompt change
- Few-shot example set change
- Temperature or token budget change that affects declared task type
- Production deployment of any AI feature

Evals are not optional. "Ship and observe" is not a substitute for pre-ship eval.

## Threshold declaration

Thresholds declared per dimension at P1. No implicit passing threshold. Example format:

```markdown
## Eval Thresholds — <feature name>

| Dimension | Threshold | Block on failure |
|---|---|---|
| Accuracy | >= 0.90 | Yes |
| Safety | >= 0.99 | Yes |
| Latency p99 | <= 2000ms | Yes |
| Refusal rate | <= 0.05 | Yes |
| Cost per call | <= $0.02 | No (flag only) |
```

"Block on failure" = Yes means eval failure blocks the change from proceeding. Flag-only dimensions are recorded in the receipt but do not block.

## Regression policy

If any blocking dimension regresses below threshold on a change that did not intentionally modify that dimension, the change is BLOCKED until regression is investigated and resolved. "I only changed X, not Y" is not a bypass.

## Dataset versioning

Eval dataset version committed alongside the change that triggered the eval run. Eval run recorded in receipt: dataset version, dimensions evaluated, threshold results, pass/fail per dimension.

## LLM-as-judge

Permitted for helpfulness and qualitative dimensions only. Not permitted for safety, accuracy, or latency dimensions. LLM-as-judge model version must be pinned separately from the production model.
