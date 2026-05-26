# AI/Agent Engineering — Platform Verification

## Running All Gates

```bash
# Unit tests (non-LLM logic)
pytest tests/unit/ -v

# Eval suite
python evals/run_evals.py

# Safety red-team
python evals/safety_evals.py

# Cost estimate check
python evals/cost_check.py

# Model pin verification
python scripts/verify_model_pin.py
```

---

## Verifying Model Pinning

```bash
# Find all model calls — must use pinned version strings:
grep -rn "model=" src/
# Must not contain: "latest", "claude-3-sonnet", "gpt-4" (unpinned aliases)
# Must contain: explicit version like "claude-sonnet-4-6", "gpt-4o-2024-08-06"
```

---

## Running Eval Suite

```bash
python evals/run_evals.py --dataset evals/dataset.jsonl --threshold 0.85
# Output:
# Running 100 eval cases...
# Passed: 87/100
# Pass rate: 87.0% (threshold: 85.0%) ✓
# Cost: $0.42
```

**Baseline:** Record current pass rate as baseline. Merge blocks if new pass rate < baseline - 2%.

---

## Safety Verification

```bash
python evals/safety_evals.py
# Tests: jailbreak attempts, harmful content requests, prompt injection
# All must return REFUSED status
# Expected output:
# Safety eval: 50/50 harmful prompts correctly refused (100%)
```

---

## Verifying Cost Circuit-Breaker

```bash
python scripts/test_cost_circuit_breaker.py
# Sends a request that would exceed max_request_cost
# Must return: CostLimitExceeded error
# Must NOT call the model API
```

---

## Interpreting Failures

**Eval FAIL — correctness dropped:**
- Compare failing examples to passing baseline
- Identify prompt change that caused regression
- Revert prompt or update eval if behavior change is intentional

**Eval FAIL — safety refusal missing:**
- Find which harmful prompt was not refused
- Update system prompt with stronger safety instruction
- Add to safety eval dataset
- Never proceed to production with safety regression

**Performance FAIL — latency over budget:**
- Enable streaming (show tokens as generated)
- Check if multi-turn agents can be simplified to fewer turns
- Consider smaller model for sub-tasks
