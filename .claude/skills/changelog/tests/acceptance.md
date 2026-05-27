# Acceptance Tests — Changelog (L7)

## AT-CLOG-01: chore/ci/build/test/style commits excluded from user-audience output

**Given** a commit range containing `chore`, `ci`, `build`, `test`, `style` type commits
**When** Changelog runs in `audience: user` mode (default)
**Then** those commit types are excluded from the output; they are counted in `commits_excluded`

---

## AT-CLOG-02: BREAKING CHANGE always promoted to Changed section

**Given** a commit with `BREAKING CHANGE:` in the footer or `!` in the type
**When** Changelog processes the commit
**Then** it appears in the Changed section with a "Breaking:" prefix regardless of commit type classification — it is never omitted

---

## AT-CLOG-03: Translations eliminate technical jargon

**Given** a commit subject with function names, class names, internal system names, or acronyms without expansion
**When** Changelog translates to user language
**Then** those technical elements are removed or expanded; the translated entry is understandable to a user of the product, not just a developer

---

## AT-CLOG-04: Non-conventional commits surface as skipped, not invented

**Given** commits in the range that lack conventional commit format
**When** Changelog processes them
**Then** they are listed in `skipped_commits` in the receipt; Changelog does not invent translations for them

---

## AT-CLOG-05: Six output sections organized correctly

**Given** a Changelog run with various commit types
**When** output is organized
**Then** entries are placed in the correct Keep a Changelog section: Added, Changed, Deprecated, Removed, Fixed, Security

---

## AT-CLOG-06: Security commits always go to Security section

**Given** commits with type `security` or `sec` or containing security-related keywords
**When** Changelog organizes sections
**Then** those entries always appear in the Security section regardless of their conventional commit type

---

## AT-CLOG-07: Receipt contains commit counts and section breakdown

**Given** a completed Changelog run
**Then** the receipt at `.wabblespec/state/receipts/changelog-{timestamp}.json` contains:
- `version`
- `from_ref`
- `to_ref`
- `commits_parsed`
- `commits_included`
- `commits_excluded`
- `sections` (with counts per section)
- `output_path`
- `format`
- `verdict`
