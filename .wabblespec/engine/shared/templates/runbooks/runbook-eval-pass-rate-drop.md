# Runbook: Eval Pass Rate Drop

**Alert:** `EvalPassRateDrop`  
**Severity:** warning (pass rate declining) | critical (below declared floor — blocks version bump)  
**SLO:** Eval suite pass rate ≥ ___ % — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** AI Agent platform  

---

## Symptoms

- CI eval gate failing — eval pass rate below declared floor, blocking version bump
- Eval pass rate trending downward across recent model versions or prompt changes
- Specific eval categories failing while others pass (regression is localized)
- Model version drift: provider updated underlying model, breaking previously passing evals
- New fixtures added that the current prompt/model cannot handle

---

## Immediate triage

1. Is this a CI gate failure (blocking a deploy) or a live production degradation signal?
2. **CI gate failure:** Which eval fixtures are newly failing? Compare against the last passing run.
3. **Production degradation:** Is the drop correlated with a model version change, prompt change, or traffic pattern change?
4. How many fixtures are failing, and are they clustered in one capability category?
5. Was the eval suite recently extended with harder fixtures? (Legitimate difficulty increase vs. regression)

---

## Diagnosis

**Eval run output:** `___ UNDECLARED` (insert eval harness invocation and output path — e.g., `pytest evals/`, `promptfoo run`, `langsmith run evals`)

**Failing fixture list:** `___ UNDECLARED` (insert command to list failed eval cases with expected vs. actual output)

**Model version in use:** `___ UNDECLARED` (confirm pinned model version matches what is declared in build-toolchain.md)

**Eval category breakdown:**
```
___ UNDECLARED  # insert eval result grouped by category/tag
```

**Common causes:**
- Model version drift: provider silently upgraded underlying model, changing behavior on edge cases
- Prompt regression: a change to system prompt or tool schema altered model behavior on previously passing fixtures
- New fixtures were added that test capabilities the current model/prompt cannot reliably handle
- Context window change: prompt is now longer, pushing relevant content outside the effective context
- Tool schema change: renamed or restructured tool parameters that model was relying on by name
- Evaluation logic change: scorer/judge model changed behavior (for LLM-as-judge evals)

---

## Remediation

### CI gate failure — prompt/system regression
1. Run eval diff: `___ UNDECLARED` (compare eval results of current vs. previous prompt version).
2. Identify the prompt change that caused the regression via git blame on `___ UNDECLARED`.
3. Revert the offending change or add few-shot examples targeting the failing fixture category.
4. Do not bump the pass-rate floor to paper over the regression — fix the root cause.

### CI gate failure — model version drift
1. Confirm model version in `___ UNDECLARED` matches what the eval was last run against.
2. If provider updated the model without notice: pin to the previous version explicitly in `___ UNDECLARED`.
3. If pinning is not possible: adapt prompt/fixtures to the new model behavior; re-establish baseline.
4. Add model version drift check to CI (see `engineering/build-toolchain.md` AI Agent template).

### CI gate failure — new fixtures too hard
1. Review whether the new fixtures represent a legitimate capability requirement.
2. If yes: improve the agent before deploying; do not ship below the declared floor.
3. If the fixture is aspirational (future capability): mark it as `xfail` with a dated comment and track separately.

### Production degradation
1. Identify the traffic pattern or input type causing degraded outputs.
2. Add a fixture representing the failing real-world case to the eval suite.
3. Treat as a CI regression and follow the remediation above.

---

## Escalation

- Eval pass rate below floor blocking a time-critical deploy: page ___ UNDECLARED (engineering lead) for exception review — exception must be documented with a resolution timeline
- Pass rate drop > ___ % in production on a safety-critical operation (irreversible actions): page ___ UNDECLARED immediately; consider disabling the operation until resolved
- Prompt injection detected in failing evals: treat as security incident; see `___ UNDECLARED` security runbook

---

## Post-incident

- [ ] Failing fixtures documented with root cause (model drift / prompt regression / new fixtures)
- [ ] Eval suite updated with fixtures covering the regression scenario
- [ ] Model version pinned explicitly (not `latest`) in build-toolchain.md
- [ ] Model version drift check added to CI if not already present
- [ ] Eval pass rate floor reviewed — confirm it is set at the minimum acceptable quality, not aspirationally
- [ ] Runbook updated with eval harness specifics

---

*Generated from `.wabblespec/engine/shared/templates/runbooks/runbook-eval-pass-rate-drop.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
