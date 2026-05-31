---
name: translate
description: i18n/l10n infrastructure, string extraction, locale management, and translation verification. BCP 47 locale tags, CLDR formatting conventions.
layer: L6
---

# Translate

You handle the full lifecycle of internationalization and localization. String extraction, locale file scaffolding, translation production, and verification. You ensure translated strings render correctly, fit their UI context, and follow platform-standard locale formats.

## What this skill does

Translate does not just translate words. It manages the i18n infrastructure: extracting translatable strings, producing locale manifests, scaffolding locale files for new languages, verifying that translated strings meet length and rendering constraints, and flagging strings that require locale-sensitive formatting.

## When to use

Translate activates when:
- A product needs to support one or more non-English locales
- UI strings need to be extracted from source files for translation
- A new locale needs to be scaffolded into an existing i18n setup
- Translated strings need to be verified against UI constraints
- Date, currency, or number formatting needs locale-sensitive handling

## Inputs

- **Mode** — `extract | scaffold | verify | format` (required)
- **Source path** — path to source file(s) for extraction (required for extract mode)
- **Target locale** — BCP 47 locale tag, e.g. `fr-FR`, `ja-JP`, `es-419` (required for scaffold and format modes)
- **Locale file path** — path to existing locale file to verify or extend (required for verify mode)
- **Platform** — `react-intl | i18next | flutter | ios | android | generic` (default: generic)
- **Base locale** — source locale of the strings (default: `en-US`)

## Reference Routing

| Situation | Reference |
|---|---|
| Translate receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` for the base, then `--extra-json` for the module-specific fields defined in `modules/l6/translate/schemas/translate-receipt.schema.json` |

## Output contract

**Receipt:** `.wabblespec/state/receipts/translate-{timestamp}.json`

```json
{
  "mode": "string",
  "base_locale": "string",
  "target_locale": "string or null",
  "strings_extracted": 0,
  "strings_verified": 0,
  "verification_failures": [
    {
      "key": "string",
      "issue": "string",
      "severity": "FAIL | WARN"
    }
  ],
  "locale_manifest_path": "string or null",
  "output_path": "string or null",
  "verdict": "PASS | FAIL | WARN",
  "processed_at": "ISO-8601"
}
```

`verdict: FAIL` when any verification failure is severity `FAIL`. WARN does not fail.

## Steps

### Mode: extract

**Step 1 — Scan source.** Walk declared source path(s). For each file, identify strings matching the `string-extraction.md` qualification criteria: user-visible, not code identifiers, not purely numeric.

**Step 2 — Generate keys.** Assign a dot-separated namespace key to each string: `component.context.variant`. Preserve any existing keys if a key map is provided.

**Step 3 — Write base locale file.** Output a locale file in the declared platform format (JSON for react-intl/i18next, .strings for iOS, .arb for Flutter, etc.) for `en-US` (or declared base locale).

**Step 4 — Write locale manifest.** Append to or create `locale-manifest.json` with all extracted keys and their source locations.

### Mode: scaffold

**Step 1 — Load base locale file.** Read the base locale file for the declared platform.

**Step 2 — Scaffold target locale file.** Create a copy of the base locale file with all values replaced by `[UNTRANSLATED: {original_value}]`. This is the translation work order.

**Step 3 — Apply locale-specific format rules.** For date, currency, and number keys (identified by key suffix or declared type): apply CLDR formatting conventions for the target locale. See `rules/locale-format.md`.

### Mode: verify

**Step 1 — Load both files.** Load base locale and target locale files.

**Step 2 — Verify completeness.** Every key present in the base must be present in the target. Missing keys are FAIL severity.

**Step 3 — Verify rendering constraints.** For strings with declared length constraints: verify the translated string does not exceed the constraint. Exceeding is WARN by default; FAIL if `--strict` is passed.

**Step 4 — Verify no base-locale bleed.** No string in the target locale file should still contain `[UNTRANSLATED:` markers. Any remaining are FAIL severity.

### Mode: format

Apply locale-sensitive formatting to a specific value: date, currency, number, plural. Output formatted string for declared locale using CLDR rules.

## Failure modes

**Translating code:** String extraction must not extract variable names, class names, enum values, or identifiers. These are not user-visible and must not appear in locale files.

**Ignoring plurality:** Languages have different plural forms. A string with a count variable must use the platform's plural syntax, not naive string interpolation. Flag these during extraction.

**Silent truncation:** A translated string that exceeds a UI constraint and is silently truncated is worse than an untranslated string. Always verify length constraints.
