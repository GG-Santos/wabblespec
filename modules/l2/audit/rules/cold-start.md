# Cold-Start Behavior — Audit

Defines what Audit does when its compliance targets or Guard logs are absent.

## Absent: audit target

Condition: Audit invoked without declaring what to audit.
Action: Surface: "Audit requires a declared target. Specify: UI components (WCAG), data flows (GDPR), dependencies (license), or Guard logs."
Do NOT: Audit the entire project without scope declaration.

## Absent: declared audit dimensions

Condition: Audit target declared but no dimensions specified.
Detection: No dimension list in invocation or task card.
Action: Run all default dimensions: WCAG (if UI involved), GDPR (if user data involved), license compliance (if new dependencies added), Guard log review (if guard logs exist).
Log: "No dimensions declared — running applicable defaults based on target type."

## Absent: Guard operation log

Condition: Guard log (`guard/operation-log.json`) requested but file absent.
Detection: File read returns 404.
Action: Log: "Guard operation log absent — Guard log dimension skipped." Proceed with other dimensions.
Do NOT: Block audit because Guard log is absent.

## Absent: WCAG reference (for accessibility dimension)

Condition: WCAG audit dimension active but `modules/l4/experience/references/wcag.md` absent.
Detection: File read returns 404.
Action: Apply WCAG 2.1 AA minimums from SKILL.md knowledge. Log: "wcag.md missing — using SKILL.md WCAG 2.1 AA defaults."

## Absent: compliance report output directory

Condition: `compliance/` or `.wabblespec/audit/` directory does not exist.
Action: Create directory before writing report. This is normal on first run.

## Absent: prior audit receipt

Condition: No prior `audit-receipt-<timestamp>.json` for this scope.
Action: Treat as first audit. No prior state to compare against.

## Default state on cold start

| Field | Default |
|---|---|
| `dimensions` | WCAG + GDPR + license + Guard log — all applicable by default |
| `wcag_target` | WCAG 2.1 AA (minimum) |
| `attestation_required` | true for findings requiring human sign-off |
| `fix_mode` | false — Audit surfaces and gates; does not fix |
| `report_path` | `.wabblespec/audit/audit-<timestamp>.md` |
