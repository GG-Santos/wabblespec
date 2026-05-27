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

---

## Eval Tooling

No mandatory tool. Eval receipt must include: the command run, the dataset version, and the full dimension results. Tool-neutral criteria:

| Requirement | What to produce |
|---|---|
| Prompt sweep | Test each system prompt variant against the dataset; report per-variant results |
| Temperature sweep | For non-deterministic tasks, test ≥ 2 temperature settings; declare which was selected and why |
| Provider comparison | If comparing model versions or providers, run on same dataset version; report side-by-side |
| Output extraction | Define a transform or parser that extracts the specific field being evaluated — do not eval raw LLM output when structured output was requested |

**Promptfoo** is one suitable tool for prompt/temperature sweeps (`promptfooconfig.yaml` → prompts → providers → tests → output). Any other evaluation harness is acceptable provided it produces a receipt-compatible result artifact.

**Receipt fields for eval runs:**

```json
{
  "eval_tool": "promptfoo | pytest | custom | other",
  "dataset_version": "<git-sha or path>",
  "prompt_variants_tested": 1,
  "temperature_values_tested": [0.0],
  "dimensions": {
    "<dimension_name>": {
      "threshold": 0.90,
      "result": 0.93,
      "passed": true
    }
  },
  "eval_baseline_comparison": {
    "random": { "accuracy": 0.21, "macro_f1": 0.19 },
    "majority_class": { "accuracy": 0.35, "macro_f1": 0.09 },
    "proposed": { "accuracy": 0.91, "macro_f1": 0.89 }
  }
}
```

`eval_baseline_comparison` is required for all classification tasks. Omit for generation or latency-only evals.

---

## Safety Checklist for AI Feature Specs

Required when AI features are declared in P1. Complete before Delivery wave:

- [ ] Eval dimensions declared at P1 — specific to this feature, not generic
- [ ] Thresholds declared with "block on failure" flag per dimension
- [ ] Eval dataset committed to source control with version reference in receipt
- [ ] Baseline comparison run for classification tasks — proposed model beats all baselines
- [ ] LLM output validated before execution at every agent tool call site
- [ ] Model version pinned — no `latest` alias in any environment
- [ ] Fallback model declared or outage explicitly accepted
- [ ] Red-team coverage: prompt injection + edge cases + out-of-scope inputs
- [ ] Provider-specific claims qualified — performance claims apply to named model version only
- [ ] PII in prompts: DPA and declared purpose on file before production deploy
