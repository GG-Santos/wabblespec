# Cold-Start Behavior — Writer

Defines what Writer does when its input context or structural templates are absent.

## Absent: content type declaration

Condition: Writer invoked without specifying what type of content to produce.
Action: Surface: "Writer requires a content type. Specify: blog post, technical article, user guide, release note, or other."
Do NOT: Default to a content type without confirmation.

## Absent: rule files

Condition: `rules/content-types.md` or `rules/structure-templates.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md structure rules. Log: "Writer rule file missing — using SKILL.md defaults."

## Absent: audience declaration

Condition: Content type declared but no target audience specified.
Detection: Invocation has no audience context.
Action: Surface: "Who is the target audience? (e.g., developers, end users, decision makers, technical buyers)"
Do NOT: Write content without audience context.

## Absent: topic brief

Condition: Writer invoked with only a content type and audience, no topic or outline.
Action: Request a brief: "Provide a topic, key points to cover, and any constraints (length, tone, forbidden topics)."

## Default state on cold start

| Field | Default |
|---|---|
| `format` | Markdown |
| `length` | Not declared — Writer will surface a length recommendation based on content type |
| `tone` | Not declared — must be specified or defaulted from spec |
| `citations` | Verified facts only — no invented references |
| `review_required` | true — Writer output is a draft; human review before publication |
