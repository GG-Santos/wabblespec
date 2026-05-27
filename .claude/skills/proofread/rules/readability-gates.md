# Readability Gates

Flesch-Kincaid reading ease targets by content type. Reading ease ranges from 0 (very hard) to 100 (very easy).

## Targets by content type

| Content type | Reading ease target | Grade level equivalent | Rationale |
|---|---|---|---|
| `ui-copy` | ≥ 70 | Grade 7 | Users scan, not read |
| `marketing-copy` | ≥ 60 | Grade 8–9 | Persuasion requires clarity |
| `blog-post` | ≥ 60 | Grade 8–9 | General audience |
| `release-notes` | ≥ 55 | Grade 10 | Mixed developer/user audience |
| `technical-doc` | ≥ 40 | Grade 12 | Developer audience with domain knowledge |
| `legal-doc` | ≥ 30 | College | Precision required; complexity acceptable |

## Measurement method

Flesch-Kincaid reading ease formula:
`206.835 − (1.015 × ASL) − (84.6 × ASW)`

Where:
- ASL = average sentence length (words per sentence)
- ASW = average number of syllables per word

Estimate syllable count by counting vowel groups per word (consecutive vowels = 1 syllable).

## Failure conditions

- Reading ease below target → FAIL finding
- Any single sentence exceeding 35 words → WARN finding (always, regardless of content type)
- Passive voice density > 20% → WARN for `ui-copy` and `marketing-copy`; INFO for all others

## Exemptions

Code blocks, URLs, proper nouns, technical identifiers, and table cell content are excluded from reading ease calculation.
