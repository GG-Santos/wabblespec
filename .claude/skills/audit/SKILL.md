---
name: audit
description: Compliance and accessibility verification. WCAG, GDPR, license compliance, Guard log review. L2 — co-equal to Guard. Triggered on-demand or post-deployment.
---

# Audit

Compliance is not optional. You check the output against WCAG, GDPR requirements, license obligations, and Guard operation logs. You issue attestations. You do not fix — you surface and gate.

## What this skill does

Checks compliance across configured dimensions. Reads Guard logs for policy violations. Reports findings by dimension. Writes compliance report. Flags items requiring human attestation. Delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| Audit receipt write (Step 7) | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type audit` |

## When to use / when not to use

**Use when:** Any task touching accessibility, user data, privacy, licensing, or when Guard logs have accumulated since last audit.

**Do not use when:** Task is purely internal (no user-facing output, no data processing, no new dependencies).

## Inputs

- Artifacts to audit (UI components, data flows, dependency licenses)
- Guard operation logs (`.wabblespec/guard/operation-log.json`)
- Declared audit dimensions (from task card or explicit command)

## How to do it

### Step 1 — Determine audit dimensions

Default dimensions (run all unless task scoping excludes them):
- `wcag-aa` — WCAG 2.1 AA accessibility
- `gdpr` — data processing, consent, PII handling
- `license-compliance` — dependency licenses vs project license
- `guard-log-review` — Guard log policy violations

### Step 2 — WCAG check

Target: WCAG 2.1 AA minimum. AAA where feasible.

Check: keyboard navigability, color contrast ≥ 4.5:1, alt text on images, ARIA roles on interactive elements, focus management, skip navigation. Record `wcag_level_achieved`.

### Step 3 — GDPR check

Check: consent mechanisms exist before data collection, PII not logged (confirm with Monitor log schema), data retention policies declared, right-to-delete path exists if user data is stored.

### Step 4 — License compliance

Read SBOM if available (from Deps). Verify each dependency license is compatible with project license. Flag incompatible licenses as violations.

### Step 5 — Guard log review

Read Guard operation log. Count: blocked operations, risk-tier escalations, freeze violations, repeated denials. Flag patterns indicating policy drift.

Record: `guard_logs_consumed`, `guard_log_violations_found`.

### Step 6 — Attestation requirement

If any violations exist in CRITICAL or HIGH categories: `attestation_required: true`. A human must sign off before deployment proceeds.

### Step 7 — Write report and receipt

Write to `.wabblespec/audits/compliance-<timestamp>.md`. Then write receipt:

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type audit \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS|FAIL \
  --out .wabblespec/state/receipts/audit-receipt-<timestamp>.json
```

## Output contract

**audit-receipt.json** (`.wabblespec/state/receipts/audit-receipt-<timestamp>.json`):

```json
{
  "dimensions_checked": ["array"],
  "wcag_level_achieved": "AA | AAA | PARTIAL | FAIL | not-applicable",
  "guard_logs_consumed": "boolean",
  "guard_log_violations_found": "integer",
  "total_violations": "integer",
  "violations_by_dimension": { "wcag": 0, "gdpr": 0, "license": 0, "guard-log": 0 },
  "compliance_report_path": ".wabblespec/audits/compliance-<timestamp>.md",
  "attestation_required": "boolean"
}
```
