# Severity Matrix — Triage

## Severity levels

| Level | Criteria | Examples |
|---|---|---|
| Critical | Production broken, data loss risk, or security vulnerability | Auth bypass, data corruption, service down for all users |
| High | Core functionality broken, no workaround exists | Primary user flow fails, blocking error with no alternative path |
| Medium | Functionality degraded, workaround exists | Feature works with extra steps, degraded performance, non-blocking error |
| Low | Minor issue, cosmetic, or enhancement with no functional impact | UI misalignment, typo, minor UX friction |

## Classification rules

Assign the highest severity that any single criterion matches. Do not average across criteria.

**Critical overrides:** Any confirmed security vulnerability is Critical regardless of other factors. Any confirmed data loss risk is Critical regardless of scope.

**Workaround test:** If a workaround exists and a user can complete their goal using it, severity is Medium or lower. If no workaround exists, severity is High or Critical.

**Scope does not lower severity:** A bug that affects only 1% of users but causes data loss is still Critical. Impact breadth affects priority scheduling, not severity classification.

## Recurrence effect on severity

Recurrence escalation is applied after base severity is assigned:

| Occurrence | Effect |
|---|---|
| First | Base severity — no change |
| Second | Escalate one level (Low → Medium, Medium → High, High → Critical, Critical → Critical) |
| Third+ | Escalate to High minimum; trigger Synth proposal |

Critical cannot be escalated further — it is already maximum.
