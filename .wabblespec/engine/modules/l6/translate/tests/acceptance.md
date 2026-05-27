# Acceptance Tests — Translate (L6)

## AT-TRANS-01: Four modes supported

**Given** a Translate invocation
**When** mode is declared
**Then** the following are supported: `extract`, `scaffold`, `verify`, `format`

---

## AT-TRANS-02: Extract does not capture code identifiers

**Given** a Translate `extract` run on source files
**When** string extraction runs
**Then** variable names, class names, enum values, and code identifiers are not extracted — only user-visible strings are included in the locale file

---

## AT-TRANS-03: Scaffold produces [UNTRANSLATED:] markers

**Given** a Translate `scaffold` run for a target locale
**When** the scaffolded locale file is produced
**Then** all values are `[UNTRANSLATED: {original_value}]` — no value is left blank or pre-translated

---

## AT-TRANS-04: FAIL on untranslated markers remaining in verify mode

**Given** a Translate `verify` run on a locale file that still contains `[UNTRANSLATED:` markers
**When** verification runs
**Then** verdict is `FAIL` — any remaining untranslated markers are FAIL severity

---

## AT-TRANS-05: FAIL on missing keys in verify mode

**Given** a target locale file missing keys that are present in the base locale
**When** verify mode runs
**Then** missing keys produce FAIL-severity findings and verdict is `FAIL`

---

## AT-TRANS-06: Plural forms flagged during extraction

**Given** a string with a count variable during extraction
**When** Research Log processes it
**Then** the string is flagged for plural form handling — naive string interpolation is not acceptable; the platform's plural syntax must be used

---

## AT-TRANS-07: Length constraint exceedance is WARN by default, FAIL with --strict

**Given** a translated string that exceeds its UI length constraint
**When** verify mode runs without `--strict`
**Then** the finding is WARN severity

**Given** `--strict` is passed
**When** verify mode runs and a length constraint is exceeded
**Then** the finding is FAIL severity

---

## AT-TRANS-08: Receipt contains verification results

**Given** a completed Translate run
**Then** the receipt at `.wabblespec/state/receipts/translate-{timestamp}.json` contains:
- `mode`
- `base_locale`
- `target_locale`
- `strings_extracted`
- `strings_verified`
- `verification_failures`
- `locale_manifest_path`
- `output_path`
- `verdict`
