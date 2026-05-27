# AI Gateway — Cost and Latency Reference

Token budget declaration, latency targets, and model abstraction requirements.

## Token budget declaration

Every AI/Agent spec must declare token budgets. Token costs are real money; unbounded agents can cost thousands per day.

### Budget structure

```yaml
token_budget:
  per_call:
    input_tokens_max: 8000          # hard limit; truncate if exceeded
    output_tokens_max: 1000         # max_tokens parameter to model
    
  per_user_action:
    calls_max: 5                    # max model calls triggered by one user action
    total_tokens_max: 20000         # sum of all calls for one action
    
  per_user_per_day:
    tokens_max: 100000              # daily per-user token limit
    cost_max_usd: 1.00              # cost circuit breaker
    
  per_month:
    cost_alert_usd: 1000            # alert when approaching
    cost_max_usd: 5000              # hard budget ceiling
```

### Context window management

When input exceeds the context window, content must be truncated. Truncation strategy must be declared:

| Strategy | When to use |
|---|---|
| Truncate oldest messages | Conversation history — recent context more relevant |
| Truncate retrieved context | RAG — prioritize highest-relevance chunks |
| Truncate middle content | Documents — beginning and end are typically most relevant |
| Reject and error | When truncation would produce incorrect output (structured tasks) |

Spec must declare: which strategy is used and how the system signals to the user when context was truncated.

### Token counting

Before sending to model, count tokens to enforce budget:

```python
from anthropic import Anthropic

client = Anthropic()

def count_tokens(messages: list, system: str = None) -> int:
    """Count tokens before sending to avoid over-budget calls."""
    response = client.messages.count_tokens(
        model="claude-sonnet-4-6",
        system=system,
        messages=messages,
    )
    return response.input_tokens
```

Count before calling; truncate if over budget. Do not rely on post-hoc accounting only.

## Latency targets

Spec must declare latency targets per interaction type:

| Interaction type | p50 target | p99 target | Strategy if exceeded |
|---|---|---|---|
| Real-time chat | < 1s to first token | < 3s to first token | Stream; abort after 10s |
| Document analysis | < 10s total | < 30s total | Background job with webhook |
| Batch processing | < 1 min per item | < 5 min per item | Async queue; status polling |
| Autocomplete suggestion | < 300ms | < 800ms | Cache; pre-generate; abort early |

### Streaming for perceived latency

Streaming reduces perceived latency for long responses — users see output start immediately.

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=messages,
    stream=True,
) as stream:
    for chunk in stream:
        yield chunk.text   # yield each chunk to the UI as it arrives
```

Declare in spec: which interactions use streaming and which wait for complete response.

### Caching

Cache model outputs when the same input is likely to repeat:

```python
import hashlib

def get_or_compute(prompt: str, ttl_seconds: int = 3600) -> str:
    cache_key = hashlib.sha256(prompt.encode()).hexdigest()
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    result = model.invoke(prompt)
    cache.set(cache_key, result, ttl=ttl_seconds)
    return result
```

Cache candidates: classification of fixed categories, extraction from static documents, code generation from stable specs.

Do not cache: personalized responses, responses depending on current time/state, responses with PII.

## Model selection and cost

Spec must declare model selection rationale. Different tasks have different cost/capability trade-offs:

| Task type | Recommended model tier | Rationale |
|---|---|---|
| Simple classification | Haiku / small model | Low complexity; high volume; cost-sensitive |
| Complex reasoning | Sonnet / medium model | Balance of capability and cost |
| Expert analysis, long documents | Opus / large model | High capability required |
| Guard / content classification | Small model | Must be fast and cheap; runs on every call |
| LLM-as-judge | Large model (stronger than evaluated model) | Judgment quality matters |

### Cost estimation

```python
# Anthropic pricing (verify current pricing at anthropic.com)
PRICING = {
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},      # per million tokens
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-opus-4-7": {"input": 15.00, "output": 75.00},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING[model]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000
```

Include cost estimate in spec based on expected daily call volume and token counts.

## Model abstraction requirement

Do not scatter provider client calls throughout the codebase. Centralize behind an abstraction:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ModelResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str

class ModelClient(ABC):
    @abstractmethod
    def complete(self, messages: list[dict], system: str = None, **kwargs) -> ModelResponse: ...
    
    @abstractmethod
    def stream(self, messages: list[dict], system: str = None, **kwargs): ...

class AnthropicClient(ModelClient):
    def complete(self, messages, system=None, **kwargs) -> ModelResponse:
        response = self._client.messages.create(
            model=self.model_id,
            system=system,
            messages=messages,
            **kwargs,
        )
        return ModelResponse(
            content=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=response.model,
        )
```

Benefits:
- Swap providers without touching business logic
- Inject mock clients in tests
- Add observability (logging, cost tracking) in one place
- Enforce token budgets consistently

Spec must declare the abstraction layer and which parts of the codebase use it.
