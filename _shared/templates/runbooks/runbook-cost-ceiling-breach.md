# Runbook: Cost Ceiling Breach

**Alert:** `CostCeilingBreach` (or `MonthlyCostCeilingBreach`)  
**Severity:** warning (approaching limit) | critical (at or exceeding limit)  
**SLO:** Cost ≤ $___ per operation / ≤ $___ per month — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** AI Agent platform  

---

## Symptoms

- Cost monitoring dashboard showing per-operation cost or monthly spend above declared ceiling
- LLM provider billing alert firing (OpenAI / Anthropic / Google / Azure budget alert)
- Token usage per request exceeding declared token budget
- Monthly projected spend trending above declared monthly ceiling
- Unexpected spike in request volume or token count per request

---

## Immediate triage

1. Distinguish: per-operation cost breach (individual call too expensive) vs. monthly volume breach (aggregate cost from high usage)?
2. **Per-operation:** Which operation type is over budget? Which model is being called?
3. **Monthly volume:** Is request volume higher than expected, or is per-request cost elevated?
4. Check if a new code path is calling a more expensive model than declared.
5. Check if prompt length has grown (system prompt bloat, large context windows being passed unnecessarily).
6. Is this correlated with a recent deploy?

---

## Diagnosis

**Per-operation cost query:** `___ UNDECLARED` (insert cost tracking query — LangSmith / Datadog / custom cost tracker)

**Token usage breakdown per operation type:**
```
___ UNDECLARED  # insert query for input_tokens + output_tokens by operation
```

**Model routing log:** `___ UNDECLARED` (confirm which model each operation is hitting)

**Common causes:**
- New code path calling primary model (e.g., GPT-4o, Claude Opus) for tasks that could use a smaller model
- System prompt grew significantly (added long examples, docs, or tool schemas without pruning)
- Context window being loaded unnecessarily (passing full conversation history when only last N turns needed)
- Streaming not properly truncated — agent loop iterating more times than declared ceiling
- Eval suite accidentally hitting production model instead of test model
- Model version unpinned — provider silently upgraded to more expensive model
- Retry storms multiplying costs (exponential backoff not capped)

---

## Remediation

### Per-operation cost too high
1. If wrong model: route operation to declared model in `___ UNDECLARED` (model-router config).
2. If prompt bloat: audit system prompt in `___ UNDECLARED`; remove examples that can be moved to few-shot at call time; prune tool schemas to only tools needed for this operation.
3. If context window overload: implement sliding window or summarization for long conversations in `___ UNDECLARED`.
4. If agent loop overrunning: enforce iteration ceiling declared in performance-budgets.md; see `___ UNDECLARED`.

### Monthly volume too high
1. Check for runaway agent or retry storm in logs: `___ UNDECLARED`.
2. Implement request rate limiting per user/session at `___ UNDECLARED` if not already present.
3. Review whether all operation types are still necessary — remove any redundant LLM calls.
4. Consider caching common responses for high-frequency low-variance queries via `___ UNDECLARED`.

### Emergency cost containment
1. Enable cost kill switch at `___ UNDECLARED` — routes all non-critical operations to smallest available model.
2. Disable non-essential agent operations until spend stabilizes.
3. Set hard spending limit at LLM provider dashboard: `___ UNDECLARED`.

---

## Escalation

- Monthly projected spend > ___ % above ceiling: page ___ UNDECLARED (engineering lead + finance/product owner)
- Cost spike caused by unbounded agent loop in production: treat as P1 incident; page ___ UNDECLARED
- LLM provider hard limit reached (service suspended): page ___ UNDECLARED immediately

---

## Post-incident

- [ ] Root cause documented (wrong model / prompt bloat / context overload / loop / volume)
- [ ] Cost tracking instrumentation verified complete for all operation types
- [ ] Model version pinned in `___ UNDECLARED` if not already (per build-toolchain requirement)
- [ ] Agent iteration ceiling enforced in code, not just policy
- [ ] Monthly budget alert thresholds reviewed and tightened
- [ ] Runbook updated with operation-specific cost breakdown

---

*Generated from `_shared/templates/runbooks/runbook-cost-ceiling-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
