# Cold-Start Behavior — Organize

Defines what Organize does when its audit target or repair policy are absent.

## Absent: target scope for organization

Condition: Organize invoked without declaring what to organize.
Action: Surface: "Organize requires a scope. Specify: directory path, module set, or 'project' for full project scan."
Do NOT: Organize the entire project without explicit scope declaration.

## Absent: audit-dimensions.md

Condition: `rules/audit-dimensions.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md audit dimension defaults. Log: "audit-dimensions.md missing — using SKILL.md defaults."

## Absent: repair-policy.md

Condition: `rules/repair-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md repair policy defaults. Log: "repair-policy.md missing — using SKILL.md defaults."

## Absent: baseline state (first run)

Condition: No prior Organize receipt for this scope.
Detection: Receipt absent.
Action: Treat as first audit. No prior state to diff against. Produce full current-state report.

## Absent: permission to modify

Condition: Organize finds disorganization to repair but has not been explicitly authorized to make changes.
Detection: Invocation is read-only or no write confirmation given.
Action: Produce audit report only. Surface list of repair actions as proposals. Do NOT auto-repair without explicit user confirmation.
Do NOT: Make structural changes without confirmation, even when repair-policy.md permits them.

## Default state on cold start

| Field | Default |
|---|---|
| `scope` | Not declared — must be specified |
| `mode` | audit (read-only) until write confirmation given |
| `auto_repair` | false — requires explicit authorization per item |
| `diff_required` | true for all proposed repairs |
| `preserve_history` | true — no destructive operations without explicit flag |
