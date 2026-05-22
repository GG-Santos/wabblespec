# Module Plan — Reviewer (L2)

**Tier:** 2 — CORE
**Layer:** L2 Orchestration
**v5.3 origin:** Adversary module + Grader module — merged into Reviewer in v6.1

---

## Purpose

Adversarial review of decisions. Budget-gated — activates only when trigger conditions are met. Contains two subagents: Adversary (counter-analysis) and Grader (evaluation). Issues ACCEPT / REVISE / ESCALATE verdicts. Bounded to max 3 REVISE cycles before human escalation. Writes gate receipts recording trigger condition, cycles used, and outcome.

---

## Activation

Budget gate — does not activate on every output. Triggers when:

1. Ambiguity above threshold in decision input
2. Confidence below threshold in decision output
3. Impact classified as HIGH (spec changes, architecture decisions, breaking changes)
4. Verification mode is Attestation (human sign-off path)
5. Any module explicitly requests adversarial review

Budget gate prevents Reviewer from running on every minor output. It is a quality investment, not a rubber stamp.

---

## Subagent Roles

### Adversary

Role: generate counter-analysis against the primary decision or output.

Adversary does not try to destroy — it tries to find the strongest case against the current approach. Output is a structured counter-argument listing: weaknesses, missed alternatives, unstated assumptions, and failure scenarios.

Adversary is given only the primary output, not the reasoning that produced it. This prevents anchoring.

### Grader

Role: evaluate both the primary output and the Adversary counter-analysis. Issue a verdict.

Grader receives: original output + Adversary counter-analysis + spec artifact (ground truth). Grader evaluates against the spec, not against its own preferences.

Grader output:
- Verdict: ACCEPT | REVISE | ESCALATE
- Score: 0.0-1.0 (quality assessment of primary output)
- Revision guidance: what specifically must change if REVISE
- Escalation reason: why human is needed if ESCALATE

---

## REVISE Loop

```
Reviewer triggers
  -> Adversary: counter-analysis
  -> Grader: verdict

  IF ACCEPT: write gate receipt, return output
  IF REVISE:
    -> Cycle 1: send revision guidance to originating module -> re-output -> Adversary -> Grader
    -> Cycle 2: same
    -> Cycle 3: same
    -> Cycle 4+: ESCALATE (human required regardless of Grader verdict)
  IF ESCALATE: human sign-off required (Attestation), write gate receipt with escalation reason
```

Max 3 REVISE cycles is a hard limit. Not configurable. A decision that cannot be resolved in 3 cycles requires human judgment.

---

## Trigger Thresholds (defaults — configurable in `rules/budget-gate.md`)

| Condition | Default threshold |
|---|---|
| Ambiguity threshold | > 0.4 on any ambiguity dimension |
| Confidence threshold | < 0.7 on primary output |
| Impact classification | HIGH = always triggers |
| Attestation mode | Always triggers |

Impact classification:
- HIGH: spec stage locks, architecture decisions, BREAKING changes, irreversible actions
- MEDIUM: significant design decisions (may trigger depending on confidence)
- LOW: routine implementation decisions (does not trigger)

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Gate receipt | `.wabblespec/receipts/reviewer-receipt-<timestamp>.md` | I10 compliance |
| Verdict | Returned to originating module | Decision outcome |
| Revision guidance | Returned to originating module (if REVISE) | What to fix |

### Gate receipt structure

```markdown
# Reviewer Gate Receipt

**timestamp:** <time>
**originating_module:** <module>
**trigger_condition:** ambiguity|confidence|impact|attestation|explicit
**trigger_value:** <measured value that triggered>
**adversary_summary:** <key points from counter-analysis>
**grader_score:** 0.0-1.0
**verdict:** ACCEPT|REVISE|ESCALATE
**revise_cycles_used:** 0-3
**escalation_reason:** <if ESCALATE>
**final_output_path:** <path to accepted artifact, if ACCEPT>
```

---

## Workflow

```
1. Receive: primary output + trigger condition + spec artifact

2. Budget gate check:
   -> Measure trigger conditions
   -> IF none met: pass through without review (log "not triggered")
   -> IF any met: proceed

3. Adversary subagent:
   -> Receives: primary output only (no reasoning)
   -> Produces: counter-analysis (weaknesses, alternatives, assumptions, failure scenarios)

4. Grader subagent:
   -> Receives: primary output + counter-analysis + spec artifact
   -> Evaluates against spec
   -> Produces: verdict + score + revision guidance (if REVISE)

5. On REVISE:
   -> Send revision guidance to originating module
   -> Originating module re-outputs
   -> Cycle count incremented
   -> Repeat from step 3
   -> After cycle 3: force ESCALATE regardless of Grader verdict

6. On ACCEPT: write gate receipt, return output to originating module

7. On ESCALATE: write gate receipt with escalation reason, require Attestation
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — budget-gated, not always-on |
| `agents/adversary.md` | Agent | Adversary subagent role definition |
| `agents/grader.md` | Agent | Grader subagent role definition |
| `rules/budget-gate.md` | Rules | Trigger thresholds, impact classification |
| `rules/revise-bounds.md` | Rules | Max 3 cycles hard limit rationale and enforcement |
| `schemas/gate-receipt.schema.json` | Schema | Gate receipt validation |
| `schemas/receipt.schema.json` | Schema | Module receipt extension |
| `evaluations/verdict-cases.md` | Evaluations | Known ACCEPT/REVISE/ESCALATE cases for calibration |

---

## Integration Points

| Module | Relationship |
|---|---|
| Specify | Reviewer reviews spec drafts at each stage lock |
| Decompose | Reviewer reviews wave plans before Executor runs |
| Verifier | Reviewer is invoked when Verifier FAIL triggers REVISE loop |
| Apply | Apply can request Reviewer on mid-execution scope decisions |
| All L1 modules | Any L1 module can trigger Reviewer when confidence is low |

---

## Verification Mode

Reviewer is itself a verification mechanism. Its internal process uses Review mode. Escalation path requires Attestation.

---

## Receipt Extension Fields

```json
{
  "triggered": "boolean",
  "trigger_condition": "string",
  "revise_cycles": "integer",
  "verdict": "ACCEPT|REVISE|ESCALATE",
  "grader_score": "number",
  "escalated": "boolean",
  "escalation_reason": "string"
}
```

---

## v5.3 Mapping

| v5.3 Adversary + Grader | v6.1 Reviewer |
|---|---|
| Adversary: standalone module | Adversary: subagent inside Reviewer |
| Grader: standalone module | Grader: subagent inside Reviewer |
| Budget-gated (v5.3 invariant) | Same — budget gate in rules/budget-gate.md |
| Max 3 REVISE cycles (v5.3) | Same — hard limit |
| No unified gate receipt | Gate receipt produced per review |
| REVISE loop: module calls Adversary, then Grader separately | REVISE loop: Reviewer manages entire cycle internally |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Adversary anchoring prevention | No reasoning provided (current) vs. provide reasoning with flag | Per-module planning |
| Grader scoring calibration | 0.0-1.0 scale (current) vs. rubric-based scoring | Per-module planning |
| Budget gate configurability | Per-project configurable (current) vs. fixed framework defaults | Per-module planning |
| ESCALATE path | Attestation always vs. Attestation only for HIGH impact | Per-module planning |
