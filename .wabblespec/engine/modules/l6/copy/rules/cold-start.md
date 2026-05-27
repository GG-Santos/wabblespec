# Cold-Start Behavior — Copy

Defines what Copy does when its input context or rule files are absent.

## Absent: target context (product, flow, or component)

Condition: Copy invoked without specifying what copy to write for.
Action: Surface: "Copy requires a target context: product name, user flow, UI component, or error condition."
Do NOT: Generate generic microcopy without a declared target.

## Absent: rule files

Condition: `rules/microcopy-principles.md` or `rules/security-warning-format.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md copy rules. Log: "Copy rule file missing — using SKILL.md defaults."

## Absent: tone/voice declaration in spec

Condition: Copy invoked but spec has no tone declaration.
Detection: Spec scan finds no voice or tone section.
Action: Default to: neutral, active voice, second-person ("you"), no jargon, no blame language. Surface in receipt: "No tone declaration found — using neutral defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `tone` | Neutral, active, second-person — until spec declares voice |
| `reading_level` | Grade 8 target (accessible to most users) |
| `security_warnings` | Use security-warning-format.md if present; else: specific + actionable + no blame |
| `character_limits` | Not declared — Copy will note when text exceeds common UI constraints |
