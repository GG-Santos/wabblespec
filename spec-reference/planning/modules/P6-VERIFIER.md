# Module Plan — Verifier (L2)

**Tier:** 1 — CRITICAL
**Layer:** L2 Orchestration
**v5.3 origin:** Verification gates embedded across pipeline — formalized as standalone module in v6.1

---

## Purpose

Run verification gates at every checkpoint. Selects verification mode from the target module's `skill-rules.json`. Manages REVISE loop (max 3 cycles). Routes to Reviewer when adversarial review is needed. Issues PASS / FAIL / BLOCKED verdicts. Every non-trivial output passes through Verifier before the next phase begins (I4).

---

## Activation

`skill-rules.json` triggers:
- Executor triggers after each wave completes
- Spec stage locks (P1, P2, P3, P4) trigger Verifier before next stage opens
- Delivery gate triggers Verifier before Archive
- Explicit `/verify` command with target artifact

---

## Verification Modes

Verifier selects mode from target module's `skill-rules.json`. Does not override declared mode.

| Mode | Verifier behavior |
|---|---|
| Test | Runs test suite or assertion script against output. Pass = all assertions green. |
| Review | Routes to Reviewer for structured critique. Pass = ACCEPT verdict from Grader. |
| Audit | Checks output against spec artifact and declared standards. Pass = no violations. |
| Measurement | Reads quantitative metric (performance, coverage, score). Pass = above threshold. |
| Observation | Checks file existence, state, and declared conditions. Pass = all conditions met. |
| Attestation | Requires explicit human confirmation before issuing PASS. No automated path to PASS. |
| Demonstration | Checks working proof runs against real conditions. Pass = behavior confirmed. |

---

## REVISE Loop

```
Verifier issues verdict
  -> PASS: write verification receipt, signal Executor to advance
  -> FAIL:
       Cycle 1:
         -> Generate fix recommendation (what specifically failed + how to fix)
         -> Originating module applies fix
         -> Verifier re-runs gate
       Cycle 2: same
       Cycle 3: same
       Cycle 4+: BLOCKED
         -> Write verification receipt with BLOCKED status
         -> Require Attestation (human sign-off)
         -> Execution pauses until Attestation received
  -> BLOCKED (immediate): issued when failure is categorically unresolvable by automation
       -> Require Attestation
```

Cycle count is per-gate per-wave. Resets at next wave. A wave that blocked in cycle 3 does not carry that count to the next wave.

---

## Spec Compliance Check (all modes)

Regardless of declared mode, Verifier always checks output against the locked spec artifact:

1. Output artifacts declared in wave plan exist
2. No artifacts produced outside declared scope (scope.md)
3. No BREAKING changes without delta proposal receipt
4. EARS requirements in spec are traceable to output

Spec compliance failure is always FAIL regardless of mode-specific checks.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Verification receipt | `.wabblespec/receipts/verification-<wave>-<timestamp>.md` | I10 compliance |
| REVISE guidance | Returned to originating module (in-context) | Fix instructions |
| BLOCKED notification | Written to receipt + surfaced to Executor | Human escalation trigger |

### Verification receipt structure

```markdown
# Verification Receipt

**wave:** integer
**stage:** P1|P2|P3|P4|Execution
**module_verified:** string
**verification_mode:** mode
**verdict:** PASS|FAIL|BLOCKED
**revise_cycles_used:** 0-3
**spec_compliance:** PASS|FAIL
**mode_result:** <mode-specific result>
**failure_reason:** <if FAIL or BLOCKED>
**fix_applied:** <if REVISE cycle — what was fixed>
**timestamp:** datetime
```

---

## Workflow

```
1. Receive: output artifact + spec artifact + wave plan entry

2. Read verification_mode from target module skill-rules.json

3. Run spec compliance check (always):
   -> Artifacts exist
   -> No out-of-scope output
   -> No undeclared BREAKING changes
   -> EARS requirements traceable

4. Run mode-specific check:
   -> Test: execute test script/suite
   -> Review: invoke Reviewer
   -> Audit: compare against spec + standards
   -> Measurement: read metric, compare to threshold
   -> Observation: check file/state conditions
   -> Attestation: pause, await human confirmation
   -> Demonstration: run working proof

5. Issue verdict:
   -> Spec compliance PASS + mode check PASS = PASS
   -> Either FAIL = FAIL -> REVISE loop
   -> Cycle 4+ or categorical failure = BLOCKED

6. On REVISE:
   -> Generate specific fix recommendation
   -> Return to originating module
   -> Increment cycle count
   -> Re-run from step 3

7. Write verification receipt

8. Signal Executor: PASS (advance) | FAIL (retry) | BLOCKED (pause, escalate)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over verification receipts |
| `rules/mode-selection.md` | Rules | How to interpret declared mode; fallback if mode unclear |
| `rules/revise-bounds.md` | Rules | Max 3 cycles hard limit, cycle reset rules |
| `rules/spec-compliance.md` | Rules | Spec compliance check criteria |
| `rules/blocked-conditions.md` | Rules | What constitutes categorical (immediate BLOCKED) failure |
| `schemas/verification-receipt.schema.json` | Schema | Receipt validation |
| `schemas/receipt.schema.json` | Schema | Module receipt extension |
| `evaluations/mode-cases.md` | Evaluations | Known PASS/FAIL/BLOCKED cases per mode for calibration |

---

## Integration Points

| Module | Relationship |
|---|---|
| Executor | Executor invokes Verifier after each wave. Verifier signals PASS/FAIL/BLOCKED back. |
| Reviewer | Verifier invokes Reviewer for Review mode and when REVISE loop produces ambiguous fix |
| Apply | Verifier sends fix recommendations to Apply (via Executor) on REVISE |
| Specify | Spec compliance check reads Specify artifacts as ground truth |
| Archive | Verifier receipt is read by Archive during delivery |
| Grader | For Review mode, Grader provides score that feeds PASS/FAIL verdict |

---

## Verification Mode

Verifier is itself the verification infrastructure — it does not verify itself. Verifier receipts are audited by Archive during delivery.

---

## Receipt Extension Fields

```json
{
  "verification_mode": "string",
  "verdict": "PASS|FAIL|BLOCKED",
  "spec_compliance": "PASS|FAIL",
  "revise_cycles_used": "integer",
  "immediate_blocked": "boolean",
  "attestation_required": "boolean",
  "attestation_received": "boolean",
  "fix_recommendations_issued": "integer"
}
```

---

## v5.3 Mapping

| v5.3 verification | v6.1 Verifier |
|---|---|
| Verification gates embedded in each module | Standalone Verifier invoked by Executor |
| 3 REVISE cycles max (v5.3) | Same — hard limit |
| Deploy gate re-validation after fix (v5.2+) | Same — Verifier re-runs all checks after fix |
| No unified verification mode declaration | Mode declared in skill-rules.json per module |
| No verification receipt | Verification receipt per wave per gate |
| 7 verification modes (v6.1 expansion) | Test, Review, Audit, Measurement, Observation, Attestation, Demonstration |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Cycle count scope | Per-gate-per-wave reset (current) vs. cumulative per stage | Per-module planning |
| Attestation timeout | Wait indefinitely vs. timeout after N minutes with auto-BLOCKED | Per-module planning |
| Test mode runner | Executor runs test script vs. Verifier invokes dedicated Test module | Resolve during Test carry-forward planning |
| Measurement thresholds | Declared in skill-rules.json (current) vs. in spec artifact | Per-module planning |
