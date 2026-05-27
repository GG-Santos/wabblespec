# Adversary Budget Thresholds

Adversary is invoked when any one of the following conditions is true. A caller that meets no threshold must not invoke Adversary — log "Adversary not triggered — budget gate not met" and return without invoking.

## Trigger conditions

| Condition | Threshold | Invokes Adversary? |
|---|---|---|
| Output confidence | < 0.7 | Yes |
| Decision impact: spec stage lock | any | Yes |
| Decision impact: BREAKING change | any | Yes |
| Decision impact: irreversible action | any | Yes |
| Decision impact: security or infrastructure scope | any | Yes |
| Plan complexity High + touches security/infra/irreversible scope | both true | Yes |
| Explicit adversarial review requested by caller | any | Yes |
| Decision impact: routine LOW implementation | — | No |
| All impact conditions LOW | — | No |
| Identical output challenged this session, no new information | — | No |

## Who applies the budget gate

The caller applies the gate before invoking Adversary. Adversary does not gate itself — it executes when invoked.

**Exception:** Reviewer always invokes Adversary after its own budget gate passes. Reviewer owns the gate for the Reviewer → Adversary → Grader cycle. Any direct caller (Plan, Specify) applies the gate independently.
