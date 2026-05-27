# AI/Agent Security — Platform Controls

---

## Control 1: Model Safety Features Enabled

**Rule:** Never disable provider safety features. Anthropic: no `disable_safety`. OpenAI: no `moderation: none`.

**Enforcement:** Code review. Grep for safety-disabling flags in all API calls.

---

## Control 2: Input Sanitization

**Rule:** User input sanitized before prompt insertion. Injection patterns removed or escaped.

```python
INJECTION_PATTERNS = [
    r"ignore (previous|above|all) instructions",
    r"you are now",
    r"new instructions:",
    r"system prompt:",
]

def sanitize_input(text: str) -> str:
    import re
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Potential prompt injection detected")
    return text[:MAX_INPUT_LENGTH]
```

---

## Control 3: Output PII Scan

**Rule:** All model outputs scanned for PII before returning to user.

**Implementation:** Regex patterns for email, phone, SSN, credit card, IP address applied to output. Match → mask or reject.

---

## Control 4: Tool Parameter Validation

**Rule:** All tool call parameters validated against declared schema before execution. Model's parameter values are untrusted.

```python
def execute_tool(name: str, params: dict) -> str:
    if name not in ALLOWED_TOOLS:
        raise ValueError(f"Tool not in allowlist: {name}")
    schema = TOOL_SCHEMAS[name]
    validated = schema.model_validate(params)  # Pydantic validation
    return TOOL_IMPLEMENTATIONS[name](validated)
```

---

## Control 5: Cost Circuit-Breaker

**Rule:** Requests estimated to exceed max cost are rejected before reaching the model API.

**Enforcement:** `estimate_cost(input_tokens, max_output_tokens) > MAX_REQUEST_COST → reject`.

---

## Control 6: Conversation Isolation

**Rule:** No user's conversation context is visible to or included in another user's prompt.

**Enforcement:** Session IDs enforced at storage layer. No global conversation state. Code review confirms user_id scoping on all history queries.

---

## Control 7: Credential-Free Prompts

**Rule:** No API keys, passwords, or secrets in any prompt — system or user.

**Enforcement:** Pre-send scan of all prompt content for credential patterns. CI: `detect-secrets scan prompts/`.

---

## Control 8: Audit Log for Safety Events

**Rule:** All safety rejections (input blocked, output blocked, cost limit, tool blocked) logged with: timestamp, event type, first 100 chars of trigger (not full content), user session ID.

**Retention:** 1 year. Used for: pattern analysis, red-team improvement, compliance.
