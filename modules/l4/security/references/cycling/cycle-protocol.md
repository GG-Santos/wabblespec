# Cycle Protocol — Red/Blue/Purple Orchestration

Controls the sequencing, termination conditions, and scoring for adversarial security cycling.

## Cycle structure

A security cycle consists of:
```
Phase A: Intel (Recon + Surface + Context)
  → produces: security profile, attack surface map

Phase B: Red (attack)
  → produces: findings with PoC-as-test-case

Phase C: Blue (defend)
  → produces: mitigations + regression tests + verification

Phase D: Purple (score + decision)
  → produces: posture score + cycle decision (continue / terminate)

[repeat B→C→D until termination condition met]
```

Phase A runs once per engagement. Phases B, C, D repeat until termination.

## Termination conditions

Evaluate after every Purple phase. Terminate when ANY of the following is met:

### 1. Posture target reached
Declared posture target score (from security profile) is achieved and maintained for one full cycle.

### 2. Diminishing returns
Three consecutive cycles where:
- No new CRITICAL or HIGH findings from Red
- No new MEDIUM findings affecting previously unexamined attack surfaces

### 3. Maximum cycles
Declared `max_cycles` reached (default 5 if not declared in scope).

### 4. All CRITICAL and HIGH findings closed
All CRITICAL and HIGH findings from all Red cycles are:
- Fixed (verified by Blue)
- OR explicitly deferred with documented risk acceptance

**CRITICAL escalation rule**: do not auto-terminate if any unmitigated CRITICAL finding exists, regardless of other termination conditions. Escalate to human for override decision.

## Turn sequencing

Within a cycle, Red and Blue operate sequentially:
1. Red produces all findings for this cycle
2. Blue reads all findings and produces all defenses
3. Blue runs regression tests; confirms passing
4. Purple scores the cycle
5. Decision: continue or terminate

Red and Blue do not interleave within a cycle — Red does not start a new attack while Blue is still defending from the same cycle.

## Scoring model — 9 components (Purple)

Score each component 0-10. Posture score = weighted average.

| Component | Weight | Scoring criteria |
|---|---|---|
| **Coverage** | 14.5% | What percentage of the attack surface was tested by Red? |
| **Severity distribution** | 19.5% | CRITICAL/HIGH findings found vs not found (fewer = better) |
| **Fix quality** | 14.5% | Root cause fixed vs symptom patched; class-level vs instance-level |
| **Fix completeness** | 14.5% | All findings addressed (fixed or explicitly deferred) |
| **Defense depth** | 9.5% | Two or more defense layers per finding |
| **Regression coverage** | 9.5% | Test coverage for findings and class-level hardening |
| **Cycle efficiency** | 5.0% | Did Blue fix issues found in previous cycles? (same finding re-appearing = 0) |
| **Response time** | 8.5% | Time from Red finding to Blue verification (faster = better) |
| **Inference quality** | 5.0% | Red PoC completeness — measured by `inference_refusal` flags in Red findings |

### Inference quality scoring (9th component)

```
Score 10: Zero inference_refusal flags across all Red findings in this cycle
Score 5–9: 1–3 inference_refusal flags; findings are mostly complete
Score 0–4: 4+ inference_refusal flags; Red findings likely incomplete — escalate
```

Source: InferenceGuard `inference_guard_summary.refusal_count` from Red receipt. If InferenceGuard was suppressed or unavailable: score 5 (neutral — no data, no penalty).

Weight rationale: original 8 components had weights totaling 100%. The new 9th component takes 5%; each original component weight reduced by ~0.5% proportionally to preserve total = 100%.

### Score interpretation

| Score | Posture | Meaning |
|---|---|---|
| 9-10 | Excellent | Cycle terminates; posture target met |
| 7-8 | Good | Continue if max cycles not reached; terminate if diminishing returns |
| 5-6 | Fair | Continue; Red should expand scope |
| 3-4 | Poor | Continue; Blue needs architecture review |
| 0-2 | Critical | Escalate; do not launch/deploy until CRITICAL findings closed |

## CRITICAL posture escalation

If posture score is below 4 (any cycle):
- Do not auto-terminate cycle
- Surface to human: "Security posture is below acceptable threshold. Do not proceed with deployment until CRITICAL and HIGH findings are resolved."
- Human must explicitly override to continue deployment
- Document override decision in security receipt

## Purple scoring output format

```json
{
  "cycle_number": 2,
  "red_findings": {
    "critical": 0,
    "high": 1,
    "medium": 3,
    "low": 2
  },
  "blue_responses": {
    "fixed": 5,
    "deferred": 1,
    "deferred_critical": 0
  },
  "scores": {
    "coverage": 8.5,
    "severity_distribution": 7.0,
    "fix_quality": 9.0,
    "fix_completeness": 8.0,
    "defense_depth": 9.0,
    "regression_coverage": 8.0,
    "cycle_efficiency": 10.0,
    "response_time": 8.0,
    "inference_quality": 10.0
  },
  "posture_score": 8.4,
  "termination_check": {
    "posture_target_met": false,
    "diminishing_returns": false,
    "max_cycles_reached": false,
    "all_critical_high_closed": true
  },
  "decision": "CONTINUE",
  "decision_reason": "Posture target not yet reached; MEDIUM findings remain open"
}
```

## Named activators

| Command | Action |
|---|---|
| `/security-red` | Run Red phase only (no Blue, no Purple) |
| `/security-blue` | Run Blue phase only (requires Red findings in context) |
| `/security-score` | Run Purple scoring only (requires Red + Blue in context) |
| `/security-cycle` | Run a full A→B→C→D cycle with decision |
| `/security-intel` | Run Intel phase only (Recon + Surface + Context) |
