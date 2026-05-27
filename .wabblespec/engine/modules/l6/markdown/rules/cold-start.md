# Cold-Start Behavior — Markdown

Defines what Markdown does when its format rules or input documents are absent.

## Absent: target document

Condition: Markdown invoked with no document specified.
Action: Surface: "Markdown requires a target document. Specify the file to format."

## Absent: format rule files

Condition: `rules/agentskills-format.md` or `rules/obsidian-format.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md format rules for the missing file. Log: "Format rule file missing — using SKILL.md defaults."

## Absent: target format declaration

Condition: No format specified (agentskills / obsidian / generic).
Detection: Invocation has no `--format` flag or explicit format in request.
Action: Surface: "Specify target format: agentskills, obsidian, or generic markdown."
Do NOT: Guess the format from document content.

## Default state on cold start

| Field | Default |
|---|---|
| `format` | Not declared — must be specified |
| `diff_required` | true — no silent overwrites |
| `template_applied` | false — templates are optional; default to format rules only |
| `frontmatter` | Preserved if present; not added unless format requires it |
