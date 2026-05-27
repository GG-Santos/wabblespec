# Audit Dimensions

Audit checks against four dimensions. Each produces a violation count. Total violations drive the compliance report.

## Dimension 1 — WCAG Accessibility (wcag-aa)

Check UI output artifacts (HTML, React components, templates, design specs) against WCAG 2.1 AA criteria.

Key criteria checked:
- 1.4.3 Contrast Ratio: minimum 4.5:1 for normal text, 3:1 for large text
- 1.1.1 Non-text content: all images have meaningful alt text
- 2.1.1 Keyboard: all interactive elements reachable via keyboard
- 2.4.6 Headings and labels: descriptive and hierarchically correct
- 3.3.1 Error identification: form errors identified in text, not color only
- 4.1.2 Name, Role, Value: ARIA roles correct on custom components

Level outcomes: `AA` (all criteria pass), `AAA` (AA + enhanced criteria), `PARTIAL` (some criteria fail), `FAIL` (multiple criteria fail), `not-applicable` (no UI artifacts in scope).

---

## Dimension 2 — GDPR / Privacy (gdpr)

Check data handling artifacts (schemas, API contracts, log schemas, database schemas) for GDPR compliance signals.

Checks:
- PII fields declared and labeled in data schemas
- Retention periods declared for PII stores
- Log schema excludes unmasked PII (per Monitor rule: no PII in logs)
- Data subject rights paths documented (access, deletion, portability)
- Third-party data processors identified in relevant contracts

Violations: count of undeclared PII fields, missing retention declarations, PII in log schema.

---

## Dimension 3 — License Compliance (license-compliance)

Cross-reference all dependency licenses (from Deps SBOM if available, or direct scan) against project license.

Violations: count of INCOMPATIBLE and REVIEW_REQUIRED licenses in direct dependencies.

If no SBOM is available: note `deps_sbom_missing: true` in compliance report and flag as incomplete audit.

---

## Dimension 4 — Guard Log Review (guard-log-review)

Read Guard operation logs for the current session. Identify:
- Operations blocked by Guard: list by operation type and invariant triggered
- Risk escalations: any CRITICAL tier trigger
- Repeat blocks: same operation blocked 3+ times (systemic issue, not one-off)

`guard_logs_consumed: true` when Guard logs were available and read. `guard_log_violations_found: N` = count of blocked operations classified as policy violations (not legitimate guards on dangerous operations).

`attestation_required: true` when any WCAG FAIL, any GDPR violation involving PII, or any CRITICAL Guard log finding exists.
