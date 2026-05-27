# Flag Lifecycle

Feature flags move through four states. Transitions must be deliberate — no flag skips a state.

## States

### DRAFT
Flag is defined but not active. Code exists behind the flag but the flag evaluates to `false` for all users. Safe to deploy. Not visible to users.

**Entry:** Flag is created via `mode: create`.
**Exit:** Flag moves to ACTIVE via `mode: rollout` after rollout gate passes.

---

### ACTIVE
Flag is live. Evaluates to `true` for all users (or a defined cohort). Feature is exposed.

**Entry:** Rollout gate passed. Full or cohort rollout confirmed.
**Exit:** Flag moves to ROLLING (if partial rollout in progress) or RETIRED (if feature is permanent or abandoned).

---

### ROLLING
Flag is in a partial rollout. Some users see `true`, others see `false`. Rollout percentage or cohort is being expanded.

**Entry:** Rollout gate passed at partial percentage.
**Exit:** ACTIVE when rollout reaches 100%. RETIRED if rollout is aborted.

**Rules during ROLLING:** No new behavior may be added behind this flag while rolling. Lock the implementation. Changes require reverting to DRAFT.

---

### RETIRED
Flag is removed from evaluation logic. Code behind the flag is either shipped as permanent or removed entirely.

**Entry:** `mode: retire` after feature confirmed stable OR after feature abandoned.
**Exit:** No exit — RETIRED is terminal.

**Retirement rule:** A flag must not remain in ROLLING or ACTIVE indefinitely. If a flag is ACTIVE for more than 30 sessions without retiring, Flag audit mode flags it as stale.

## State machine

```
DRAFT → ACTIVE (rollout gate pass, 100% cohort)
DRAFT → ROLLING (rollout gate pass, partial cohort)
ROLLING → ACTIVE (100% reached)
ROLLING → RETIRED (rollout aborted)
ACTIVE → RETIRED (feature permanent or removed)
```

No other transitions are valid. Attempting an invalid transition produces a FAIL receipt.
