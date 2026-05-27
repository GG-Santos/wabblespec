# Rollout Gate

Before a flag transitions from DRAFT to ROLLING or ACTIVE, it must pass the rollout gate.

## Gate conditions (all must pass)

### G1 — Implementation complete
Code behind the flag is complete and all tests pass. Not partial. The flag-off path (existing behavior) must also be tested.

### G2 — Flag-off path verified
Running with the flag disabled produces the same behavior as before the flag was added. Regression test required. `rollout_gate_passed: false` if flag-off path is untested.

### G3 — Rollback plan documented
A documented rollback procedure exists: what happens if the rollout is aborted at any point. Minimum: "retire the flag, the flag-off path is verified and clean."

### G4 — Monitoring declared
At least one metric or alert is declared that will detect if the flagged feature is degrading. This is the same as Monitor's output — reference the relevant alert rule from Monitor if it exists.

### G5 — Sunset date declared
Flags without a retirement plan accumulate. A sunset date (or sunset condition: "when feature is stable for N sessions") must be declared before rollout.

## Gate failure behavior

If any condition is not met: `rollout_gate_passed: false`. The flag remains in DRAFT. List which conditions failed in the flag receipt.

Do not proceed to rollout with a failed gate. A ROLLING flag with an untested flag-off path is a production incident waiting.

## Partial rollout

When gate passes, rollout may begin at a partial cohort (e.g., 10% of sessions, or a named beta cohort). Document the cohort definition in `flag-manifest.json`. Expand only after observing the monitoring declared in G4 for at least N sessions (minimum 3).

## Gate re-evaluation

If implementation changes after gate evaluation, re-run the gate. A gate pass is valid only for the implementation it evaluated.
