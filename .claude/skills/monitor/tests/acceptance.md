# Acceptance Tests — Monitor (L7)

## AT-MON-01: Monitor derives SLOs — never invents them

**Given** an engineering spec with no SLO declared for a specific dimension
**When** Monitor processes that dimension
**Then** it marks the dimension `UNDECLARED` and does not generate an alert with an invented threshold

---

## AT-MON-02: Five config artifacts generated

**Given** a successful Monitor run
**When** execution completes
**Then** the following files are written to `.wabblespec/observability/`:
- `metric-definitions.yml`
- `alert-rules.yml`
- `log-schema.json`
- `healthcheck.yml`
- `dashboard-template.json`

---

## AT-MON-03: Every alert has a runbook reference

**Given** Monitor generating alert rules
**When** an alert is produced
**Then** every alert includes a `runbook:` reference path; alerts without runbook references are not produced

---

## AT-MON-04: Alert thresholds match declared SLO targets exactly

**Given** a performance budget declaring P95 < 200ms
**When** Monitor generates the alert rule
**Then** the alert threshold is `> 0.200` — Monitor does not tighten or loosen thresholds without a spec change

---

## AT-MON-05: PII fields excluded from log schema

**Given** an engineering spec declaring PII fields (e.g., user email, IP address)
**When** Monitor generates the log schema
**Then** those fields are explicitly excluded from `log-schema.json`

---

## AT-MON-06: Guard log monitoring is additive

**Given** a Monitor run
**When** Guard operation logs are analyzed
**Then** Guard log monitoring runs regardless of SLO declarations; SLO monitoring runs regardless of Guard log findings; neither blocks the other

---

## AT-MON-07: Guard log patterns trigger Triage error events

**Given** Guard operation logs showing repeated blocks (>=3 same operation type in one session), CRITICAL tier triggers, or freeze violations
**When** Monitor evaluates the logs
**Then** a DEPENDENCY error event is auto-emitted to Triage with `source: guard-log-monitor`

---

## AT-MON-08: Receipt contains SLO counts and stack

**Given** a completed Monitor run
**Then** the receipt at `.wabblespec/state/receipts/monitor-receipt-{timestamp}.json` contains:
- `slos_codified`
- `slos_undeclared`
- `alerts_generated`
- `observability_stack`
- `pii_fields_excluded`
