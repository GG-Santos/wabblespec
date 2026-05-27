# Runbook Structure Reference

**Consumed by:** l7/monitor (Step 3 alert generation), l7/scaffold (project setup)  
**Purpose:** Defines the required structure and fields for runbook stub files. Monitor alerts must reference a runbook at `docs/runbooks/{alert-slug}.md`. Stub files are acceptable at generation time — they must be filled before going to production.

---

## Required runbook fields

Every runbook must contain the following sections. Missing sections = INCOMPLETE stub, not a complete runbook.

### 1. Header block

```markdown
# Runbook: {Alert Name}

**Alert:** `{AlertName}` (matches alert name in alerts.yml exactly)  
**Severity:** warning | critical  
**SLO:** {dimension} {threshold} — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
```

### 2. Symptoms

What the on-call engineer sees when this alert fires. Be specific: which dashboard panel, which log pattern, which metric.

```markdown
## Symptoms

- Dashboard panel "___ panel name" shows value exceeding ___ threshold
- Log pattern: `___ UNDECLARED`
- Downstream impact: ___ UNDECLARED
```

### 3. Immediate triage

Steps to determine whether the alert is a true positive or artifact. Ordered list. First step should always be: check if alert is sustained (not a spike).

```markdown
## Immediate triage

1. Confirm alert is sustained (≥ 2 min) — not a transient spike.
2. Check deployment log — was a deploy in the last 30 min?
3. Check dependency health — are upstream/downstream services healthy?
4. ___ UNDECLARED — project-specific triage step
```

### 4. Diagnosis steps

How to root-cause the issue. Reference specific tools, dashboards, log queries.

```markdown
## Diagnosis

- Query: `___ UNDECLARED` (insert PromQL / log query / APM trace search)
- Dashboard: `___ UNDECLARED` — link to relevant dashboard
- Common causes:
  - ___ UNDECLARED
```

### 5. Remediation steps

Ordered actions to resolve. Include rollback as an explicit option when appropriate.

```markdown
## Remediation

1. ___ UNDECLARED — first action
2. ___ UNDECLARED — second action
3. If cause is a bad deploy: initiate rollback via `___ UNDECLARED`
```

### 6. Escalation

Who to page if the runbook steps do not resolve within the declared time window.

```markdown
## Escalation

- Unresolved after ___ UNDECLARED min: page ___ UNDECLARED
- Severity critical + customer impact: page ___ UNDECLARED immediately
- External dependency failure: contact ___ UNDECLARED
```

### 7. Post-incident

Required for every resolved incident — not required in the stub, but must be filled on first use.

```markdown
## Post-incident

- [ ] Incident report filed
- [ ] Root cause documented
- [ ] Runbook updated with new learnings
- [ ] Follow-up tickets created
```

---

## How Monitor references runbooks

Monitor Step 3 (alert generation) writes the runbook path into each alert annotation:

```yaml
annotations:
  runbook: "docs/runbooks/{alert-slug}.md"
```

The alert slug must match the runbook filename exactly. Scaffold generates stub runbook files from `.wabblespec/engine/shared/templates/runbooks/` at project creation time.

**Slug convention:** lowercase, hyphen-separated, describes the failure condition.  
Examples: `latency-breach`, `error-rate-breach`, `slo-miss`, `crash-rate-breach`, `memory-breach`, `throughput-drop`, `budget-exceeded`.

---

## Stub vs. complete runbook

| State | Description | Production-safe |
|---|---|---|
| STUB | Required sections present; `___ UNDECLARED` placeholders unfilled | No |
| PARTIAL | Some `___ UNDECLARED` placeholders filled; others remain | No |
| COMPLETE | All `___ UNDECLARED` placeholders replaced with project-specific values | Yes |

Monitor marks alerts that reference STUB or PARTIAL runbooks with `runbook_status: incomplete` in the monitor receipt. A production deploy with incomplete runbooks is a policy violation under l7/deploy (Attestation check).

---

## Cross-references

- `.wabblespec/engine/shared/templates/runbooks/` — stub templates for common alert types
- `.wabblespec/engine/shared/references/performance-budgets.md` — SLO tier definitions Monitor reads
- `modules/l7/monitor/SKILL.md` — alert generation step (Step 3)
- `modules/l7/deploy/SKILL.md` — Attestation check (incomplete runbooks block prod)
- `modules/l7/scaffold/SKILL.md` — copies runbook stubs at project generation time
