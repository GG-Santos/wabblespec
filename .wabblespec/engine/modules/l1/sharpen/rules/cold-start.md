# Cold-Start Behavior — Sharpen

Defines what Sharpen does when its input statement or interpretation target are absent.

## Absent: ambiguous input to sharpen

Condition: Sharpen invoked but the input statement is already unambiguous.
Detection: Breadth detection finds single clear interpretation.
Action: Surface: "Input appears unambiguous — no sharpening needed. Confirm or provide a broader statement to sharpen."
Do NOT: Artificially generate alternative interpretations for clear inputs.

## Absent: breadth-detection.md

Condition: `rules/breadth-detection.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md breadth detection rules. Log: "breadth-detection.md missing — using SKILL.md defaults."

## Absent: interpretation-ranking.md

Condition: `rules/interpretation-ranking.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md interpretation ranking rules. Log: "interpretation-ranking.md missing — using SKILL.md defaults."

## Absent: prior session context (for interpretation weighting)

Condition: No recipe.json or prior session receipts to weight interpretations.
Detection: Context files absent.
Action: Proceed with equal-weight interpretations. Surface to user: "No prior session context — all interpretations weighted equally. Confirm which interpretation is intended."

## Default state on cold start

| Field | Default |
|---|---|
| `interpretations_found` | 0 — populated during breadth detection |
| `top_interpretation` | Not declared — surfaced to user for confirmation |
| `single_interpretation_policy` | If breadth detection finds 1 interpretation, surface and confirm rather than auto-proceeding |
| `ranking_basis` | Prior session context (if available) + stated user intent |
| `output` | Ranked interpretations with recommended top choice; user confirms before proceeding |
