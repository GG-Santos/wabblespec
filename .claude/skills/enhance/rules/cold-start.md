# Cold-Start Behavior — Enhance

Defines what Enhance does when its target spec or intent dimensions are absent.

## Absent: target spec or artifact to enhance

Condition: Enhance invoked without a declared target (no spec, document, or artifact path).
Action: Surface: "Enhance requires a target artifact. Specify the spec, document, or output to enhance."
Do NOT: Enhance an implied artifact without confirmation.

## Absent: intent-dimensions.md

Condition: `rules/intent-dimensions.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md intent dimension defaults. Log: "intent-dimensions.md missing — using SKILL.md defaults."

## Absent: critical-dimensions.md

Condition: `rules/critical-dimensions.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md critical dimension defaults. Log: "critical-dimensions.md missing — using SKILL.md defaults."

## Absent: question-budget.md

Condition: `rules/question-budget.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md question budget rules. Log: "question-budget.md missing — using SKILL.md defaults."

## Absent: original author intent

Condition: Target spec exists but no declared author intent or context is available.
Detection: No author notes, no recipe.json, no prior session context.
Action: Treat the spec text as the declared intent. Surface: "No author context found — enhancing based on spec text alone. Signal if intent differs from what is written."

## Default state on cold start

| Field | Default |
|---|---|
| `question_budget` | 3 clarifying questions maximum before proceeding |
| `enhancement_scope` | Declared in target — do not expand scope during enhancement |
| `intent_preservation` | true — enhancements must not alter declared intent |
| `diff_required` | true — show before/after for any content changes |
| `no_new_requirements` | true — Enhance refines; does not add new requirements |
