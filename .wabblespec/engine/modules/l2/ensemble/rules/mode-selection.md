# Ensemble Mode Selection

Ensemble is triggered by ModelRouter only. Once triggered, mode selection follows this policy.

---

## Trigger Conditions (from ModelRouter)

ModelRouter activates Ensemble when any of these conditions are true:

| Condition | Trigger |
|---|---|
| Task spans multiple build targets simultaneously | e.g., "update both CLI and Web platform specs" |
| No single capability covers all required capabilities | ModelRouter capability gap detected |
| Verification mode is Attestation or Audit | Cross-check mandatory |
| Confidence below 0.7 after single-lane attempt | Lane returned low-confidence result |

If none of these conditions are met, ModelRouter does NOT activate Ensemble — single-lane execution proceeds.

---

## Mode Selection Rules

### Sequential

**Use when:** Lane B requires Lane A's output before it can start.

**Detection signal:** Task decomposition shows explicit data dependency between lanes (output of step N is input to step N+1 across lanes).

**Examples:**
- Lane A generates schema → Lane B generates migration for that schema
- Lane A produces API contract → Lane B generates client from contract

**Execution:** Run Lane A to completion and PASS before starting Lane B. If Lane A FAIL, Ensemble FAIL — do not start Lane B.

---

### Independent

**Use when:** Lanes produce separate artifacts with no shared dependencies.

**Detection signal:** Wave plan shows parallelizable output artifacts with no cross-lane reads.

**Examples:**
- Lane A writes CLI module, Lane B writes Web module for the same feature
- Lane A generates backend code, Lane B generates frontend code independently

**Execution:** Lanes run in parallel (or sequential if runtime does not support true parallelism). Combined receipt written when both complete. If one lane FAIL, report failure — the other lane's output is still valid.

---

### Cross-check

**Use when:**
- Verification mode is Attestation OR Audit (mandatory — no exception)
- Confidence gap between lanes is detected (one lane scored below 0.7, another above 0.8 on same task)

**Detection signal:** Verification mode declared in wave plan is Attestation or Audit; OR ModelRouter trigger was confidence < 0.7.

**Execution:** Both lanes run the same task independently. Grader (Reviewer module) compares outputs.

**Grader result:**
- Agree (`cross_check_agreement: true`): use higher-confidence lane's output. Write combined receipt.
- Disagree (`cross_check_agreement: false`): route to Reviewer for REVISE. Do NOT auto-pick one output.

**Lane disagreement definition:** Outputs contradict on at least one declared acceptance criterion from the task card.

---

## Mode Priority

When multiple modes could apply, use this priority:

1. **Cross-check** — Attestation/Audit verification mode always wins
2. **Sequential** — if data dependency exists between lanes
3. **Independent** — default for parallelizable tasks

---

## Receipt Format

One combined receipt per Ensemble run. Never separate receipts per lane.

```json
{
  "module": "ensemble",
  "mode": "Sequential | Independent | Cross-check",
  "trigger_condition": "string — which ModelRouter condition fired",
  "lanes": [
    {
      "capability": "string",
      "outcome": "PASS | FAIL",
      "artifacts": ["list of paths"],
      "confidence": 0.9
    }
  ],
  "combined_outcome": "PASS | FAIL",
  "cross_check_agreement": true
}
```

`combined_outcome: FAIL` when:
- Sequential: Lane A FAIL
- Independent: any lane FAIL where artifact is required by downstream wave
- Cross-check: Grader returns REVISE after exhausting REVISE cycles
