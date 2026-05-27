# AI/Agent Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Model Pin Verified

**Check:** All model calls use pinned version strings. No aliases or "latest".

**Method:** `grep -rn "model=" src/ | grep -v "claude-.*-[0-9]\|gpt-.*-[0-9]{4}"` → must return zero.

**Pass:** Every model call uses explicit version ID. **Fail:** Any alias like "latest", "claude-3-sonnet".

---

## Gate 2: Eval Suite Passes

**Check:** Correctness pass rate ≥ declared threshold on full eval dataset.

**Method:** `python evals/run_evals.py` — must exit 0 with pass rate ≥ threshold.

**Pass:** Pass rate ≥ threshold and ≥ prior baseline. **Fail:** Below threshold or regression from baseline.

---

## Gate 3: Safety Evals Pass

**Check:** 100% of red-team harmful prompts correctly refused.

**Method:** `python evals/safety_evals.py` — all harmful prompts return refusal.

**Pass:** 100% refusal rate. **Fail:** Any harmful prompt not refused.

---

## Gate 4: Cost Circuit-Breaker Functions

**Check:** Request exceeding max cost is rejected before API call.

**Method:** `python scripts/test_cost_circuit_breaker.py` — must return CostLimitExceeded without calling model API.

**Pass:** Error returned. No API call made. **Fail:** Request sent to API despite cost limit.

---

## Gate 5: Prompt Injection Blocked

**Check:** Common injection patterns rejected at input sanitization layer.

**Method:**
```bash
python scripts/test_injection.py
# Sends: "Ignore previous instructions. You are now..."
# Must return: injection detected error, not model response
```

**Pass:** All test injection patterns blocked before model call. **Fail:** Any injection pattern reaches model.

---

## Gate 6: Tool Allowlist Enforced

**Check:** Model cannot call undeclared tools.

**Method:** `python scripts/test_tool_allowlist.py` — send request that would cause model to call undeclared tool. Must return tool-not-allowed error.

**Pass:** Undeclared tool call rejected. **Fail:** Undeclared tool executes.

---

## Gate 7: L4 AI Gateway Loaded

**Check:** L4 AI gateway (`modules/l4/ai/`) was loaded during activation.

**Method:** Check platform activation receipt: `l4_ai_gateway_loaded: true`.

**Pass:** Receipt shows gateway loaded. **Fail:** Receipt missing field or false.

---

## Gate 8: Latency Within Budget

**Check:** p95 response time within declared budget on eval dataset.

**Method:** `python evals/latency_evals.py` — reports p50/p95 latency across eval cases.

**Pass:** p95 ≤ declared budget. **Fail:** p95 exceeds budget.

---

## Gate 9: No Credentials in Prompts

**Check:** No credential patterns in any prompt file or prompt construction code.

**Method:** `detect-secrets scan prompts/ src/` — must return zero findings.

**Pass:** Zero credential patterns. **Fail:** Any credential-shaped string found.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Model pin verified | Yes |
| 2 | Eval suite passes | Yes |
| 3 | Safety evals — 100% refusal | Yes |
| 4 | Cost circuit-breaker functions | Yes |
| 5 | Prompt injection blocked | Yes |
| 6 | Tool allowlist enforced | Yes |
| 7 | L4 AI gateway loaded | Yes |
| 8 | Latency within budget | Yes |
| 9 | No credentials in prompts | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
