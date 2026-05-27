# AI Gateway — Eval Harness Reference

Eval harness design, fixture selection, and metric declaration requirements.

## Eval harness requirements

An eval harness is the test suite for AI/LLM behavior. It is required before any prompt change is deployed to production.

### Minimum dataset size

| Task complexity | Minimum examples |
|---|---|
| Simple classification (2-3 classes) | 50 |
| Complex classification (4+ classes) | 100 |
| Generation with factual requirements | 100 |
| Multi-step reasoning | 50 |
| Extraction from documents | 75 |

### Dataset requirements

- **Representative**: covers the actual distribution of inputs, not just easy cases
- **Balanced**: if classification, roughly balanced across classes (or explicitly weighted)
- **Challenging**: include edge cases, ambiguous inputs, adversarial examples
- **Stable**: once created, the dataset should not change between eval runs (changes invalidate comparisons)
- **Labeled**: ground truth labels must be accurate; human-labeled for subjective tasks

### Dataset format

```jsonl
{"id": "001", "input": {"text": "This product is amazing!"}, "expected": {"label": "positive", "confidence_min": 0.8}}
{"id": "002", "input": {"text": "Hmm, it's okay I guess."}, "expected": {"label": "neutral", "confidence_min": 0.5}}
{"id": "003", "input": {"text": "Absolute garbage. Do not buy."}, "expected": {"label": "negative", "confidence_min": 0.9}}
```

One JSON object per line. `input` maps to model input; `expected` maps to validation criteria.

## Metric declaration

### Exact match metrics

For structured outputs with deterministic correct answers:

```python
def accuracy(predictions: list, labels: list) -> float:
    return sum(p == l for p, l in zip(predictions, labels)) / len(labels)

def precision_recall_f1(predictions, labels, label_of_interest):
    tp = sum(p == l == label_of_interest for p, l in zip(predictions, labels))
    fp = sum(p == label_of_interest and l != label_of_interest for p, l in zip(predictions, labels))
    fn = sum(p != label_of_interest and l == label_of_interest for p, l in zip(predictions, labels))
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1
```

### LLM-as-judge metrics

For subjective or open-ended outputs:

```python
JUDGE_PROMPT = """
You are evaluating AI responses. Score the following response on {criterion}.

Criterion: {criterion_description}
Scale: 1 (worst) to 5 (best)

User request: {user_input}
AI response: {ai_response}
Reference (if available): {reference}

Output a JSON object: {{"score": <1-5>, "reasoning": "<one sentence>"}}
"""

def judge_evaluate(examples, criterion, judge_model):
    scores = []
    for ex in examples:
        result = judge_model.invoke(JUDGE_PROMPT.format(
            criterion=criterion,
            criterion_description=criterion_descriptions[criterion],
            user_input=ex["input"],
            ai_response=ex["output"],
            reference=ex.get("reference", "N/A"),
        ))
        scores.append(json.loads(result)["score"])
    return sum(scores) / len(scores)
```

Use a stronger model as judge than the model being evaluated when possible.

### Common judge criteria

| Criterion | Description |
|---|---|
| accuracy | Is the information correct and factually grounded? |
| completeness | Does the response address all parts of the request? |
| relevance | Is the response on-topic and relevant to the request? |
| safety | Does the response avoid harmful content? |
| conciseness | Is the response appropriately concise without losing important information? |
| format | Does the response follow the declared output format? |

## Eval thresholds

Spec must declare thresholds for every metric. Evals fail CI when any threshold is not met.

```yaml
eval_thresholds:
  - metric: accuracy
    threshold: 0.90      # 90% of outputs must be correct
  - metric: judge_accuracy
    threshold: 4.0       # average judge score ≥ 4/5
  - metric: latency_p99
    threshold_ms: 3000   # p99 must be under 3 seconds
  - metric: cost_per_call
    threshold_usd: 0.05  # average cost ≤ $0.05 per call
```

## Running evals in CI

```yaml
# GitHub Actions
- name: Run eval suite
  run: |
    python evals/run.py \
      --dataset evals/fixtures/sentiment-200.jsonl \
      --model claude-sonnet-4-6 \
      --thresholds evals/thresholds.yaml \
      --output evals/results/latest.json
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

- name: Check eval results
  run: python evals/check_thresholds.py evals/results/latest.json evals/thresholds.yaml
```

Evals must run on every prompt change. Prompt changes without eval results are not permitted.

## Regression tracking

Track eval results over time:
```
evals/results/
  2026-05-20.json
  2026-05-21.json
  2026-05-22.json    ← this is when accuracy dropped 3%
```

Alert on: any metric dropping more than 5% from the previous 7-day average.

## Eval isolation

Evals must not use production data. Use:
- Synthetic data generated from real distribution characteristics
- Anonymized/pseudonymized production samples with PII removed
- Human-authored examples based on domain knowledge
