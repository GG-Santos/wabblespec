# Cold-Start Behavior — Scaffold

Defines what Scaffold does when its template or target directory are absent.

## Absent: target directory

Condition: Scaffold invoked without declaring where to write.
Action: Surface: "Scaffold requires a target directory path."
Do NOT: Default to the current directory without explicit declaration.

## Absent: platform declaration

Condition: Scaffold invoked without a declared platform target.
Action: Surface: "Scaffold requires a platform: web, cli, api-service, mobile, desktop, game, ai-agent, data-pipeline, library, extension, or iot."
Do NOT: Infer platform from current directory contents.

## Absent: idempotency guard

Condition: `rules/idempotency-guard.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md idempotency rules. Log: "idempotency-guard.md missing — using SKILL.md defaults."

## Non-empty target directory (idempotency)

Condition: Target directory already has content.
Detection: Directory read returns existing files.
Action: Run idempotency check: compare what Scaffold would write against what exists. Only write files that are absent or explicitly declared as regeneratable.
Do NOT: Overwrite existing files without explicit `--overwrite` flag.

## Absent: framework selection

Condition: Platform declared but no framework specified (e.g., web with no framework choice).
Action: Scaffold generates framework-agnostic skeleton. Log: "No framework declared — generating agnostic scaffold. Re-run with --framework [name] for framework-specific files."

## Default state on cold start

| Field | Default |
|---|---|
| `platform` | Not declared — must be specified |
| `framework` | Not declared — agnostic scaffold |
| `overwrite` | false — existing files preserved |
| `idempotent` | true — same scaffold on same empty directory = same output |
| `dry_run` | Available via --dry-run flag — lists files that would be created |
