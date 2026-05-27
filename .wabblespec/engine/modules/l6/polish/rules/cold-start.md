# Cold-Start Behavior — Polish

Defines what Polish does when its target documents or rule files are absent.

## Absent: target scope

Condition: Polish invoked without a declared scope (specific files, directory, or project-wide).
Action: Surface: "Polish requires a scope. Specify: file path, directory, or 'project' for project-wide pass."
Do NOT: Polish the entire project without explicit scope declaration.

## Absent: rule files

Condition: `rules/pass-sequence.md`, `rules/excluded-types.md`, or `rules/diff-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md Polish rules. Log: "Polish rule file missing — using SKILL.md defaults."

## Absent: prior Polish receipt (for incremental runs)

Condition: Polish run but no prior polish receipt for this scope.
Detection: Receipt absent.
Action: Treat as full first pass — all 4 passes run on all in-scope files.

## Excluded types (enforced even without excluded-types.md)

These are excluded even if `rules/excluded-types.md` is absent:
- Code files (`.js`, `.ts`, `.py`, `.go`, `.rs`, `.java`, etc.)
- Schema files (`.json`, `.yaml` with schema content)
- Receipt files (`*-receipt.json`)
- Memory drawers (`memory/**`)
- Plan files (`.plan.md`, `*.plan`)

## Default state on cold start

| Field | Default |
|---|---|
| `passes` | All 4 (register enforcement, redundancy removal, structural consistency, spec compliance) |
| `pass_4_severity` | flag only — does not block Delivery |
| `diff_required` | true — no silent overwrites |
| `excluded_types` | Code, schemas, receipts, memory drawers, plans (enforced regardless) |
| `auto_trigger` | false — Polish is never auto-triggered; requires explicit invocation |
