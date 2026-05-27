# Cold-Start Behavior — Triage

Defines what Triage does when its expected upstream artifacts are absent.

## Absent: incoming issue or defect report

Condition: No issue, bug report, or defect description provided when Triage runs.
Detection: No input artifact with a reported symptom or failure.
Action: Ask the user for the issue description. Do not run Triage speculatively.
Do NOT: Invent defect scenarios to triage.

## Absent: prior receipts

Condition: No receipts from upstream modules when Triage is called.
Detection: `.wabblespec/state/receipts/` empty.
Action: Triage can run at the start of a session (before Recipe) when an urgent defect requires immediate classification. Surface a SOFT warning that Recipe should follow. Do not block Triage — it is designed for reactive use.

## Absent: defect-patterns reference

Condition: `.wabblespec/engine/shared/references/defect-patterns.md` absent.
Detection: File read returns 404.
Action: Proceed with built-in pattern recognition only. Log SOFT warning to receipt: `defect_patterns_reference: absent`.
Do NOT: Block triage because the reference file is missing — it is a reference aid, not a hard dependency.

## Default state on cold start

| Field | Default |
|---|---|
| `severity` | null — must be declared, never defaulted |
| `defect_pattern` | null — must be matched against defect-patterns.md or declared unknown |
| `routing` | null — determined after severity and pattern are known |
| `blocking` | false (default; change to true only for P0/P1 defects) |
