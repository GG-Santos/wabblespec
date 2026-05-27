# Verification Gates

Gates applied during Translate verify mode. Determines PASS/FAIL/WARN verdicts.

## Gate 1 — Completeness (FAIL)

Every key in the base locale file must have a corresponding key in the target locale file.

Missing keys are FAIL severity. The translator's work order scaffold (`[UNTRANSLATED: ...]` markers) remaining in the target file is equivalent to a missing key for verification purposes.

## Gate 2 — No base-locale bleed (FAIL)

The target locale file must contain no values that are identical to the base locale for user-visible strings.

Exception: proper nouns (brand names, product names, legal entity names) may legitimately be the same across locales. These are flagged as INFO, not FAIL, when the key suffix suggests a proper noun context (`_brand`, `_product_name`, `_company_name`).

Exception: numeric strings and codes that are locale-invariant (e.g., HTTP error codes, country codes).

## Gate 3 — Length constraints (WARN or FAIL)

When a locale file entry includes a `maxLength` annotation or when the key is known to map to a UI element with declared length constraints:

- Translated string length > maxLength → WARN by default; FAIL with `--strict` flag
- Translated string length > 2× base locale length → WARN (potential rendering issue even without explicit constraint)

## Gate 4 — Placeholder consistency (FAIL)

Translatable strings with variables (ICU placeholders: `{name}`, `{count}`, `{date}`) must preserve all variables in the translation.

- Missing placeholder in translation: FAIL
- Extra placeholder not in base: FAIL
- Placeholder renamed (different variable name): FAIL

## Gate 5 — Plural form coverage (FAIL for affected locales)

For strings with plural variants: the target locale file must include all plural categories required by that locale per CLDR.

English requires 2 forms (`one`, `other`). Russian requires 3. Arabic requires 6. A Russian locale file with only `one` and `other` is a FAIL.

## Gate 6 — RTL structural check (WARN)

For right-to-left locales (`ar-*`, `he-*`, `fa-*`, `ur-*`): flag strings containing embedded directional punctuation that may not render correctly in RTL context. These are WARN — they require visual verification that automated checking cannot fully cover.
