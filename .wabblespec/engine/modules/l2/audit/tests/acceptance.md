# Audit — Acceptance Criteria

## BLOCK: absent audit target

Given Audit is invoked without declaring what to audit,
Then Audit surfaces: "Audit requires a declared target. Specify: UI components (WCAG), data flows (GDPR), dependencies (license), or Guard logs."
Then Audit does not audit the entire project without scope declaration.
Then no receipt is written.

## Default dimensions when none declared

Given an audit target is declared but no dimensions are specified,
When Audit runs,
Then Audit runs all applicable default dimensions: wcag-aa (if UI), gdpr (if user data), license-compliance (if new dependencies), guard-log-review (if guard logs exist).
Then the receipt logs: "No dimensions declared — running applicable defaults based on target type."

## Happy path: WCAG check

Given a UI component is declared as the audit target,
When Audit runs the wcag-aa dimension,
Then keyboard navigability, color contrast (>= 4.5:1), alt text, ARIA roles, focus management, and skip navigation are checked.
Then `wcag_level_achieved` in the receipt records AA, AAA, PARTIAL, FAIL, or not-applicable.
Then the compliance report is written to `.wabblespec/audits/compliance-<timestamp>.md`.

## Happy path: GDPR check

Given a data flow is declared as the audit target,
When Audit runs the gdpr dimension,
Then consent mechanisms, PII logging absence, data retention policies, and right-to-delete path are checked.
Then violations are recorded in `violations_by_dimension.gdpr`.

## Happy path: license compliance

Given new dependencies were added and the SBOM is available from Deps,
When Audit runs the license-compliance dimension,
Then each dependency license is verified against the project license.
Then incompatible licenses are flagged as violations in `violations_by_dimension.license`.

## Guard log review

Given `guard/operation-log.json` exists,
When Audit runs the guard-log-review dimension,
Then blocked operations, risk-tier escalations, freeze violations, and repeated denials are counted.
Then patterns indicating policy drift are flagged.
Then `guard_logs_consumed: true` and `guard_log_violations_found` are recorded in the receipt.

## Guard log absent: skip dimension

Given `guard/operation-log.json` does not exist,
When Audit includes the guard-log-review dimension,
Then Audit logs: "Guard operation log absent — Guard log dimension skipped."
Then Audit proceeds with other dimensions.
Then the run is not blocked.

## Attestation required for CRITICAL/HIGH violations

Given the audit finds violations classified CRITICAL or HIGH,
When Audit writes the receipt,
Then `attestation_required: true` is recorded.
Then a human must sign off before deployment proceeds.

## Audit does not fix

Given any Audit run,
Then Audit surfaces and gates violations — it does not apply fixes.
Then no code or configuration is modified by Audit.

## Receipt fields

Given any successful Audit run,
Then the receipt contains: `dimensions_checked`, `wcag_level_achieved`, `guard_logs_consumed`, `guard_log_violations_found`, `total_violations`, `violations_by_dimension`, `compliance_report_path`, `attestation_required`.
