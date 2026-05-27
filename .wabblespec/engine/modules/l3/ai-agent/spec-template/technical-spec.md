# AI/Agent Technical Spec Template (P3)

> **Platform:** AI/Agent | **Prerequisite:** systems-design.md complete.

---

## Model API Integration

```python
import anthropic

client = anthropic.Anthropic()

def call_model(
    system: str,
    messages: list[dict],
    max_tokens: int = 1024,
) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",          # pinned — never use "latest"
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text
```

**No model aliases.** Always use explicit version string. Add comment: `# pinned YYYY-MM-DD — update requires eval re-run`.

---

## Prompt Construction

```python
from pathlib import Path
import jinja2

SYSTEM_PROMPT = Path("prompts/system.txt").read_text()  # version-controlled file

def build_prompt(user_input: str, context: str) -> list[dict]:
    # Validate and cap input length
    if len(user_input) > MAX_INPUT_CHARS:
        raise ValueError(f"Input exceeds {MAX_INPUT_CHARS} character limit")

    # Sanitize: remove injection patterns
    sanitized = sanitize_input(user_input)

    return [{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {sanitized}"}]
```

---

## Eval Implementation

```python
# evals/run_evals.py
import json
from pathlib import Path

def run_evals(model_fn, dataset_path="evals/dataset.jsonl", threshold=0.85):
    dataset = [json.loads(l) for l in Path(dataset_path).read_text().splitlines()]
    passed = 0
    for example in dataset:
        output = model_fn(example["input"])
        if judge(output, example["expected"]):
            passed += 1
    pass_rate = passed / len(dataset)
    assert pass_rate >= threshold, f"Eval failed: {pass_rate:.1%} < {threshold:.1%}"
    return pass_rate
```

**Eval CI gate:** Evals run on every prompt change. PR blocked if pass rate drops below threshold.

---

## Cost Safeguards

```python
def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    # prices per million tokens — update when model pricing changes
    INPUT_PRICE_PER_M = 3.00   # $ per million input tokens
    OUTPUT_PRICE_PER_M = 15.00  # $ per million output tokens
    return (input_tokens * INPUT_PRICE_PER_M + output_tokens * OUTPUT_PRICE_PER_M) / 1_000_000

MAX_REQUEST_COST = 0.10  # $0.10 per request hard limit

def guarded_call(input_text: str) -> str:
    estimated_input_tokens = len(input_text) // 4  # rough estimate
    if estimate_cost(estimated_input_tokens, MAX_OUTPUT_TOKENS) > MAX_REQUEST_COST:
        raise ValueError("Request exceeds cost budget")
    return call_model(...)
```

---

## Safety Implementation

```python
HARMFUL_PATTERNS = [...]  # maintained list of injection / harmful patterns

def safety_check_input(text: str) -> bool:
    """Returns True if input is safe."""
    for pattern in HARMFUL_PATTERNS:
        if pattern.search(text):
            log_safety_event("input_blocked", text[:100])  # log first 100 chars only
            return False
    return True

def safety_check_output(text: str) -> bool:
    """Returns True if output is safe to return."""
    # Check for PII patterns, harmful content patterns
    return True  # implement per declared safety boundaries
```

---

## Failure Mode Handling

| Failure | Response | Logged |
|---|---|---|
| Model API timeout | Return error, do not retry automatically | Yes |
| Model API rate limit | Exponential backoff, max 3 retries | Yes |
| Safety check fail (input) | Return safe refusal message | Yes (audit) |
| Safety check fail (output) | Return safe fallback, re-query with stricter prompt | Yes (audit) |
| Cost limit exceeded | Return error before API call | Yes |
| Eval regression detected in CI | Block merge | Yes |
| Tool execution timeout | Return timeout error to model, model decides | Yes |
