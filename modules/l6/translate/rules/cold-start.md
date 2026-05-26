# Cold-Start Behavior — Translate

Defines what Translate does when its locale data or string inputs are absent.

## Absent: target locale declaration

Condition: Translate invoked without specifying target language/locale.
Action: Surface: "Translate requires a target locale (e.g., fr-FR, es-ES, de-DE, ja-JP)."
Do NOT: Default to any locale.

## Absent: source strings

Condition: No source strings or source file specified.
Action: Surface: "Translate requires source strings. Provide a string file, key-value pairs, or a document to translate."

## Absent: rule files

Condition: `rules/locale-format.md`, `rules/string-extraction.md`, or `rules/verification-gates.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md translation rules. Log: "Translate rule file missing — using SKILL.md defaults."

## Absent: existing translations to update

Condition: Target locale file exists — translate is an update operation, not first translation.
Detection: `locales/[locale]/strings.json` exists.
Action: Translate only new/changed strings. Log count: "Existing translations: [n]. New strings to translate: [m]."
Do NOT: Re-translate existing strings unless explicitly requested.

## Absent: term glossary

Condition: Product-specific terminology has no declared glossary.
Detection: No `locales/glossary.md` or `locales/glossary.json`.
Action: Proceed without glossary. Log: "No term glossary found — technical terms will be translated per locale norms."

## Default state on cold start

| Field | Default |
|---|---|
| `source_locale` | en-US (assumed) |
| `target_locale` | Not declared — must be specified |
| `string_format` | key=value (detected from source file format) |
| `placeholder_preservation` | Required — {name}, %s, {{variable}} patterns must be preserved verbatim |
| `review_required` | true for first translation of a locale; false for incremental updates to reviewed translations |
