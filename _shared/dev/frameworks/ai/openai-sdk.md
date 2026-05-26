# OpenAI / Anthropic SDK

Loaded by Apply when openai or anthropic is detected in dependencies.

## Anthropic SDK (Python)

```python
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from env

# Basic message
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(message.content[0].text)

# With system prompt
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Streaming

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a long essay."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Tool use

```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    }
}]

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}]
)

# Check if model wants to call a tool
if message.stop_reason == "tool_use":
    tool_call = next(b for b in message.content if b.type == "tool_use")
    # Execute tool, then continue conversation
```

### Structured output

Use tool use to get structured JSON output:

```python
schema_tool = {
    "name": "output_result",
    "description": "Output the structured result",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            "confidence": {"type": "number"}
        },
        "required": ["sentiment", "confidence"]
    }
}

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    tools=[schema_tool],
    tool_choice={"type": "tool", "name": "output_result"},
    messages=[{"role": "user", "content": "Analyze: I love this!"}]
)
result = message.content[0].input  # {"sentiment": "positive", "confidence": 0.98}
```

## OpenAI SDK (Python)

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

# Chat completion
response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)

# Structured output (JSON schema enforcement)
response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[...],
    response_format=MyPydanticModel,
)
result: MyPydanticModel = response.choices[0].message.parsed
```

## Error handling and retry

```python
from anthropic import RateLimitError, APITimeoutError
import time

def call_with_retry(client, **kwargs, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # exponential backoff
        except APITimeoutError:
            if attempt == max_retries - 1:
                raise
            continue
```

Spec must declare: retry policy, backoff strategy, and timeout per call.

## Cost tracking

```python
# Anthropic SDK returns usage
message = client.messages.create(...)
input_tokens = message.usage.input_tokens
output_tokens = message.usage.output_tokens
cost = (input_tokens / 1_000_000 * INPUT_PRICE) + (output_tokens / 1_000_000 * OUTPUT_PRICE)
```

Log token counts for every production call. Set a circuit breaker at the declared cost budget.
