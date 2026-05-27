# Locale Format

BCP 47 locale tags and CLDR formatting conventions.

## BCP 47 locale tag format

Format: `{language}-{region}` where language is ISO 639-1 (2-letter) and region is ISO 3166-1 alpha-2 (2-letter).

Examples: `en-US`, `fr-FR`, `fr-CA`, `es-ES`, `es-419` (Latin America), `zh-CN`, `zh-TW`, `pt-BR`, `pt-PT`

Use region code when:
- The same language has different conventions between regions (date format, currency, vocabulary)
- The product is available in multiple variants of the same language

Use `es-419` (not individual countries) for generic Latin American Spanish unless a specific country is targeted.

## Date formatting by locale

| Locale | Format | Example |
|---|---|---|
| `en-US` | M/D/YYYY | 5/23/2026 |
| `en-GB` | D/M/YYYY | 23/5/2026 |
| `de-DE` | DD.MM.YYYY | 23.05.2026 |
| `fr-FR` | DD/MM/YYYY | 23/05/2026 |
| `ja-JP` | YYYY年M月D日 | 2026年5月23日 |
| `zh-CN` | YYYY-MM-DD | 2026-05-23 |
| `ko-KR` | YYYY.M.D | 2026.5.23 |

For ISO 8601 (API/technical contexts): always `YYYY-MM-DD`. This is locale-independent.

## Number formatting by locale

| Locale | Decimal | Thousands | Example |
|---|---|---|---|
| `en-US`, `en-GB` | `.` | `,` | 1,234.56 |
| `de-DE`, `fr-FR`, `es-ES` | `,` | `.` or space | 1.234,56 |
| `ja-JP`, `zh-CN` | `.` | `,` | 1,234.56 |

## Currency formatting

- Symbol placement varies: `$1,234.56` (US) vs `€1.234,56` (DE) vs `£1,234.56` (GB)
- Always use the locale's currency symbol for the declared locale's home currency
- For international prices: use the ISO 4217 code (`USD`, `EUR`) for unambiguous reference

## Plural forms

Languages vary in plural forms. CLDR plural categories: `zero`, `one`, `two`, `few`, `many`, `other`.

Key examples:
- English: `one` (1 item) / `other` (0, 2, 3... items)
- Russian: `one` (1, 21, 31...) / `few` (2-4, 22-24...) / `many` (5-20, 25-30...)
- Arabic: 6 plural forms
- Japanese, Chinese, Korean: no plural distinction

Always use the platform's plural syntax (ICU MessageFormat, Flutter plural, etc.) when a string contains a count variable.
