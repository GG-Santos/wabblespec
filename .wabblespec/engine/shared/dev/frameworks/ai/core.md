# AI/Agent Framework Core

Cross-framework knowledge for LLM-embedded systems, agents, and AI-powered workflows. Loaded by Apply for every AI/Agent platform task.

## AI-first spec requirements

Every AI/Agent spec must declare:
- **Model**: provider + model ID + version pinned (e.g., `claude-sonnet-4-6`, `gpt-4o-2024-08-06`)
- **Eval harness**: dataset of 20+ input/output examples; pass threshold declared (e.g., 85% on task accuracy)
- **Cost budget**: max tokens per call; max calls per user action; monthly cost ceiling
- **Latency budget**: p50 and p99 response time targets; streaming vs non-streaming
- **Failure modes**: what happens when model returns wrong answer, refuses, or times out

## Model pinning

Never use unpinned model aliases in production (`claude-sonnet`, `gpt-4`). Pin to a dated version:

```python
# WRONG: behavior changes when provider updates the alias
model = "claude-sonnet"

# RIGHT: pinned to specific version
model = "claude-sonnet-4-6"  # review and update deliberately
```

Model updates change behavior without code changes. Pin, test, then upgrade deliberately.

## Prompt versioning

Prompts are code. They must be:
- Version-controlled alongside code (not stored in a database without migration tracking)
- Tested before deployment (eval suite must pass)
- Changed via PR with eval results in the description

```
prompts/
  system-v1.txt      — tagged in git
  system-v2.txt      — tagged in git
  CHANGELOG.md       — documents behavior changes per version
```

## Eval harness requirements

```yaml
eval:
  task: "classify_sentiment"
  dataset: "evals/sentiment-200.jsonl"     # 200 labeled examples
  metrics:
    accuracy:
      threshold: 0.90                       # must pass 90%
    latency_p99:
      threshold_ms: 3000
  judge: "llm-as-judge"                    # or "exact-match", "human"
  judge_model: "claude-opus-4-7"           # separate from production model
```

Spec must include: dataset size, metric definitions, pass thresholds, and judge type. Evals run in CI on every prompt change.

## Context and token budget

```
Context window budget:
  System prompt:      ~10% of window
  Retrieved context:  ~40% of window
  Conversation:       ~30% of window
  Headroom:           ~20% (for model output)
```

Spec must declare: what fills each budget zone. Running out of context silently truncates input — this is a bug.

## Chain design

When multiple LLM calls are chained (agent loop, multi-step pipeline):
- Declare the graph: nodes (LLM calls), edges (data flow), termination conditions
- Declare max iterations for any loop — unbounded loops are cost explosions
- Declare what happens when a node fails: retry, fallback, abort

```
Input → [Extract] → [Validate] → [Generate] → [Review] → Output
          LLM          Rule        LLM           LLM
```

## Failure handling

| Failure type | Required handling |
|---|---|
| Model timeout | Retry with backoff (max 3 attempts); surface error to user |
| Model refusal | Detect via structured output check; return fallback response |
| Hallucination | Detect via grounding check or confidence score; do not silently pass |
| Cost overrun | Hard token budget per call; circuit breaker for loops |
| Context overflow | Truncation strategy declared; important content preserved |

## Output validation

LLM output is untrusted user input. Validate before using:

```python
response = model.invoke(prompt)

# Parse and validate structured output
try:
    result = MySchema.model_validate_json(response.content)
except ValidationError as e:
    # Handle invalid output — retry, fallback, or surface error
    raise OutputValidationError(f"Model returned invalid output: {e}")
```

If the model returns free text: parse with the minimum assumption; validate format; do not assume the model followed instructions.
