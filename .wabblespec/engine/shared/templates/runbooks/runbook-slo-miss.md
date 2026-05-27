# Runbook: SLO Miss

**Alert:** `SLOMiss` (or per-SLO alert, e.g., `AvailabilitySLOMiss`)  
**Severity:** warning (budget burn rate high) | critical (budget exhausted)  
**SLO:** Availability ___ % — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  

---

## Symptoms

- Error budget burn rate alert — consuming more budget than the sustained rate allows
- Monthly or rolling-window availability dropping below declared SLO (e.g., 99.9%)
- Repeated latency or error-rate alerts that each individually resolved but collectively burned budget
- SLO dashboard showing budget remaining < ___ % (fast-burn threshold)

---

## Immediate triage

This alert typically fires as a compound signal — it does not indicate a single point failure but a pattern. Triage starts with understanding how fast budget is being consumed.

1. Check error budget burn rate: is it fast-burn (hours remaining) or slow-burn (days remaining)?
2. Review the last 24h for which alerts fired and how long they lasted.
3. Identify the dominant failure mode: latency, errors, or availability.
4. Fast-burn rate (> ___ x normal): treat as incident — page immediately.
5. Slow-burn rate: schedule within-SLO remediation for next sprint.

---

## Diagnosis

**PromQL — error budget burn rate (adapt window to your SLO):**
```
1 - (
  sum_over_time(up[1h]) / count_over_time(up[1h])
) / (1 - ___ )   # insert SLO target as decimal, e.g. 0.999
```

**Dashboard:** `___ UNDECLARED` — SLO burn rate panel

**Error budget consumed this period:** `___ UNDECLARED` (insert calculation or dashboard link)

**Common causes (slow burn):**
- Recurring latency spikes during peak hours not yet addressed
- Background job failures accumulating over time
- Flaky dependency causing occasional errors
- Insufficient retry/fallback logic

**Common causes (fast burn):**
- Partial outage sustained for > 30 min
- Database degradation reducing availability for a subset of traffic
- Bad deploy not fully rolled back

---

## Remediation

### Fast-burn (immediate)
1. Identify the active alert(s) contributing to burn — treat each as a separate incident.
2. Follow the runbook for the active failure: `runbook-latency-breach.md`, `runbook-error-rate-breach.md`, or `runbook-crash-rate-breach.md`.
3. If burn rate is caused by infrastructure instability: freeze deploys until stabilized.

### Slow-burn (within-SLO)
1. Review the recurring alert history for the past 7 days.
2. Identify the highest-contribution failure mode.
3. Create remediation tickets tagged `slo-remediation`.
4. Adjust error budget policy if SLO target is unachievable given current architecture: update `engineering/performance-budgets.md` with revised target + rationale.

---

## Escalation

- Fast-burn: error budget < ___ % remaining → page ___ UNDECLARED immediately
- Slow-burn unaddressed after ___ UNDECLARED sprint: escalate to ___ UNDECLARED (engineering lead / product owner)

---

## Post-incident

- [ ] Error budget consumption for the period documented
- [ ] Dominant failure mode identified and ticket created
- [ ] SLO target reviewed (realistic vs. aspirational)
- [ ] Reliability roadmap item added if structural fix needed
- [ ] Runbook updated

---

*Generated from `.wabblespec/engine/shared/templates/runbooks/runbook-slo-miss.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
