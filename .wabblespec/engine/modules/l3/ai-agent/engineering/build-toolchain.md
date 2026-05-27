# AI/Agent Engineering — Build Toolchain

## Python AI Stack

**Package management:** `uv` with pinned `requirements.txt`.

**Core dependencies (pin exact versions):**
```
anthropic==0.40.0
openai==1.54.0
# or litellm==1.51.0 for multi-provider
instructor==1.6.4       # structured outputs
pydantic==2.9.2         # input/output validation
```

**Eval tooling:**
```
inspect-ai==0.3.0       # Anthropic eval framework
braintrust==0.0.150     # eval tracking
# or: langsmith, phoenix, weights-and-biases
```

---

## Prompt Version Control

**Prompts are code.** Every prompt file in version control. Never inline prompts in application code.

```
prompts/
  system_v1.txt         # current production version
  system_v2.txt         # in development
  changelog.md          # what changed and why
```

**Prompt change process:**
1. Edit prompt file in new branch
2. Run eval suite: `python evals/run_evals.py --prompt prompts/system_v2.txt`
3. Compare pass rate to baseline (must not regress)
4. Merge only if eval passes
5. Tag commit with prompt version: `git tag prompt-v2`

---

## Eval CI Integration

```yaml
# .github/workflows/evals.yml
name: Eval Gate
on: [pull_request]
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python evals/run_evals.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      # Blocks PR if pass rate < threshold
```

**Eval cost:** Declare expected eval suite cost per CI run. Budget in project secrets store.

---

## Cost Monitoring

```python
# middleware/cost_tracking.py
import time
from dataclasses import dataclass

@dataclass
class UsageRecord:
    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    request_id: str
```

**Alert:** When daily cost exceeds 150% of budget, alert + optional circuit-break.

**Dashboard:** Cost per request × daily request volume = daily cost. Track weekly trend.

---

## Structured Output

**Use structured output / instructor for all non-freeform responses:**

```python
import instructor
from anthropic import Anthropic
from pydantic import BaseModel

client = instructor.from_anthropic(Anthropic())

class Analysis(BaseModel):
    summary: str
    confidence: float  # 0.0-1.0
    sources: list[str]

result = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    response_model=Analysis,
    messages=[{"role": "user", "content": prompt}]
)
# result is typed Analysis — no JSON parsing errors
```

---

## CI Gates

Before any deployment:
1. Type check: `mypy src/ --strict`
2. Unit tests (non-LLM logic): `pytest tests/unit/`
3. Eval suite: `python evals/run_evals.py` — pass rate ≥ threshold
4. Safety check: red-team prompt suite passes refusal test
5. Cost estimate: eval suite total cost within declared budget
6. Dependency audit: `pip-audit` — zero high/critical
