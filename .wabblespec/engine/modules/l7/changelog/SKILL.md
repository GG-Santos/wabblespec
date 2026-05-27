---
name: changelog
description: Converts git commit history into user-facing release notes. Conventional commit parsing, user-language translation, structured output.
layer: L7
---

# Changelog

You read git history and write release notes that users can understand. You do not summarize for developers — you write for the person who uses the product and wants to know what changed and why it matters to them.

## What this skill does

Changelog parses a git commit range, classifies commits by type using conventional commit conventions, filters to user-relevant changes, translates technical language into user-facing descriptions, and produces a structured release notes entry.

## When to use

Changelog activates:
- Before every release: given the commit range since last release, produce release notes
- In the Polish pipeline: `Review → Clean → [Proofread] → [Markdown] → Changelog → Commit`
- When Archive is triggered and the release notes file needs updating
- Explicitly by human when a changelog entry for a version is needed

## Inputs

- **From ref** — git ref (tag, SHA, branch) for the start of the range (required)
- **To ref** — git ref for the end of the range (default: `HEAD`)
- **Version** — release version to be labeled (required; e.g., `v1.2.0`)
- **Audience** — `user | developer | mixed` (default: user)
- **Output path** — file to append or write the changelog entry to (default: `CHANGELOG.md`)
- **Format** — `keepachangelog | github-releases | plain` (default: keepachangelog)

## Output contract

**Receipt:** `.wabblespec/state/receipts/changelog-{timestamp}.json`

```json
{
  "version": "string",
  "from_ref": "string",
  "to_ref": "string",
  "commits_parsed": 0,
  "commits_included": 0,
  "commits_excluded": 0,
  "sections": {
    "added": 0,
    "changed": 0,
    "deprecated": 0,
    "removed": 0,
    "fixed": 0,
    "security": 0
  },
  "output_path": "string",
  "format": "string",
  "verdict": "PASS | WARN",
  "generated_at": "ISO-8601"
}
```

`verdict: WARN` when the commit range contains commits that could not be parsed as conventional commits (poorly formed messages). These are listed in a `skipped_commits` field.

## Steps

**Step 1 — Parse commit range.**
Run `git log {from_ref}..{to_ref} --format="%H %s %b"`. For each commit, parse against the conventional commit pattern: `type(scope)!: subject`. See `rules/git-parsing.md` for parsing rules and edge cases.

**Step 2 — Filter.**
Exclude commits that are not user-relevant: `chore`, `ci`, `build`, `test`, `style` type commits are excluded by default unless `audience: developer` or `mixed` is declared. `docs` commits are included only if they affect user-facing documentation.

BREAKING CHANGE footer and `!` in the type are always promoted to the `Changed` section regardless of type.

**Step 3 — Translate to user language.**
For each included commit: rewrite the subject line from developer language to user language. See `rules/user-language.md`. The scope becomes a product area label where meaningful.

Example:
- Input: `feat(auth): add OAuth2 PKCE flow for mobile clients`
- Output: `Added secure sign-in support for mobile apps (no password required)`

**Step 4 — Organize into sections.**
Map translated entries to Keep a Changelog sections: Added, Changed, Deprecated, Removed, Fixed, Security. Security commits (type `security` or `sec`, or containing security-related keywords) are always in the Security section.

**Step 5 — Write output.**
Prepend the new entry to the declared output file (or create it if absent). Apply declared format. Use the template at `templates/changelog-entry.md` for section structure.

**Step 6 — Write receipt.**

## Failure modes

**Non-conventional commits:** Commits without conventional commit formatting cannot be parsed automatically. Flag them in `skipped_commits` and do not invent translations. Surface to human for manual entry.

**Technical jargon in user-facing sections:** The user-facing description must not contain: function names, class names, internal system names, database table names, or acronyms without expansion. These are caught in translation step — see `rules/user-language.md`.

**Missing BREAKING CHANGE promotion:** Any commit with `BREAKING CHANGE:` in the footer must appear in the Changed section with a "Breaking:" prefix regardless of type classification. Never omit breaking changes.
