# Cold-Start Behavior — Legal

Defines what Legal does when its templates, jurisdiction data, or spec context are absent.

## Absent: target legal document type

Condition: Legal invoked without specifying which document to produce.
Action: Surface: "Legal requires a document type: privacy policy, terms of service, data processing agreement, disclaimer, or other."

## Absent: jurisdiction declaration

Condition: Document type specified but no jurisdiction declared.
Detection: Spec scan or invocation has no jurisdiction.
Action: Surface: "Which jurisdiction(s) govern this product? (e.g., EU/GDPR, US/CCPA, UK, global)" Do NOT default to a jurisdiction.
Do NOT: Apply GDPR clauses to a US-only product, or vice versa, without explicit declaration.

## Absent: template files

Condition: `rules/required-clauses.md`, `rules/jurisdiction-defaults.md`, or a template file missing.
Detection: File read returns 404.
Action: Apply SKILL.md legal rules. Log: "Legal rule file missing — using SKILL.md defaults."

## Absent: product data model (for privacy policy)

Condition: Privacy policy requested but no data model declared in spec.
Detection: No `data_collected` section in spec.
Action: Surface: "Privacy policy requires a declared data model. List the personal data your product collects, stores, and processes."
Do NOT: Generate a privacy policy without knowing what data is collected.

## Default state on cold start

| Field | Default |
|---|---|
| `jurisdiction` | Not declared — must be specified |
| `governing_law` | Not declared — must match jurisdiction |
| `review_required` | true — Legal output must be reviewed by qualified counsel before publication |
| `template_version` | Current (from templates/ directory if present) |
| `disclaimer` | Appended to all outputs: "This is not legal advice. Review with qualified counsel." |
