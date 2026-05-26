# Security Report Template

Final output produced at cycle termination. Consolidates all cycles into a single deliverable.

## Template

```markdown
# Security Assessment Report: {System Name}

**Date**: {YYYY-MM-DD}  
**Engagement duration**: {start date} → {end date}  
**Cycles completed**: {N}  
**Final posture score**: {X.X / 10}  
**Posture status**: EXCELLENT | GOOD | FAIR | POOR | CRITICAL  

---

## Executive Summary

{2-3 paragraphs for non-technical stakeholders:
- What was assessed and why
- Overall security posture finding
- Most significant risks found and how they were addressed
- Recommendation: ready to ship / conditional / do not ship}

**Recommendation**: {SHIP | CONDITIONAL SHIP | DO NOT SHIP}  
**Conditions (if conditional)**: {what must be done before shipping}

---

## Scope

### In scope
{List of systems, URLs, environments}

### Out of scope
{List of explicitly excluded items}

### Test accounts
{Types of test accounts used; confirm no production user data accessed}

---

## Findings Summary

| ID | Title | Severity | Status | Cycle found | Cycle fixed |
|---|---|---|---|---|---|
| RED-001 | {title} | CRITICAL | Fixed | 1 | 1 |
| RED-002 | {title} | HIGH | Fixed | 1 | 2 |
| RED-003 | {title} | MEDIUM | Deferred | 2 | — |

### By severity

| Severity | Found | Fixed | Deferred | Risk accepted by |
|---|---|---|---|---|
| CRITICAL | 0 | 0 | 0 | — |
| HIGH | 2 | 2 | 0 | — |
| MEDIUM | 5 | 4 | 1 | {Name}, {Date} |
| LOW | 3 | 3 | 0 | — |

---

## Cycle Results

### Cycle 1

**Red findings**: {N} total ({C} critical, {H} high, {M} medium, {L} low)  
**Blue response**: {N} fixed, {N} deferred  
**Posture score**: {X.X}  
**Decision**: CONTINUE — {reason}

### Cycle 2

...

### Final Cycle

**Red findings**: {N} — {diminishing returns / all critical+high closed / posture target met}  
**Blue response**: {N} fixed, {N} deferred  
**Posture score**: {X.X}  
**Decision**: TERMINATE — {reason}

---

## Detailed Findings

{For each finding, include the full finding format from red-protocol.md}

---

## Defenses Applied

{For each Blue response, include the defense summary from blue-protocol.md}

---

## Class-Level Hardening Summary

Changes made beyond individual finding fixes:
- {Hardening item}: {what changed and why}

---

## Deferred Items

{For each deferred item:}
### {Finding ID}: {title}

**Risk**: {description of risk if not fixed}  
**Compensating control**: {what reduces the risk in the interim}  
**Fix timeline**: {YYYY-MM-DD}  
**Risk accepted by**: {Name, Title, Date}  
**Re-test required**: Yes — schedule for {YYYY-MM-DD}

---

## Posture Score Breakdown (Final Cycle)

| Component | Weight | Score | Weighted |
|---|---|---|---|
| Coverage | 15% | {X} | {X×0.15} |
| Severity distribution | 20% | {X} | {X×0.20} |
| Fix quality | 15% | {X} | {X×0.15} |
| Fix completeness | 15% | {X} | {X×0.15} |
| Defense depth | 10% | {X} | {X×0.10} |
| Regression coverage | 10% | {X} | {X×0.10} |
| Cycle efficiency | 5% | {X} | {X×0.05} |
| Response time | 10% | {X} | {X×0.10} |
| **Total** | 100% | | **{X.X}** |

---

## Recommendations

### Immediate (before next deployment)
{Items that must be addressed before shipping}

### Short-term (within 30 days)
{Items to address soon}

### Long-term (architecture / process improvements)
{Structural recommendations}

---

## Attestation

This report represents the security assessment conducted under the declared scope. Findings are based on testing performed during the engagement dates. New features or infrastructure changes since the assessment date are not covered.

**Assessed by**: {WabbleSpec security-gateway — cycle-based adversarial review}  
**Date**: {YYYY-MM-DD}  
**Next scheduled assessment**: {date or trigger condition}
```
