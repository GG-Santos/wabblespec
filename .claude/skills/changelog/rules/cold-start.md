# Cold-Start Behavior — Changelog

Defines what Changelog does when its git history or CHANGELOG.md file are absent.

## Absent: git repository

Condition: `git log` returns error — no git repo in current directory.
Detection: Git command fails.
Action: BLOCK Changelog. Surface: "Changelog requires a git repository. Initialize git first."

## Absent: git commits since last changelog entry

Condition: Git log between last changelog tag and HEAD returns empty.
Detection: `git log <last-tag>..HEAD` returns no commits.
Action: Surface: "No commits since last changelog entry. Nothing to add."
Do NOT: Generate fabricated changelog entries.

## Absent: CHANGELOG.md

Condition: CHANGELOG.md does not exist.
Detection: File read returns 404.
Action: Create CHANGELOG.md with header and initial entry format. Log: "CHANGELOG.md created."

## Absent: version tag in git

Condition: No version tags in git history.
Detection: `git tag` returns empty.
Action: Use full commit history since repo init. Note in entry: "Initial version — no prior tag found."

## Absent: rule files

Condition: `rules/git-parsing.md`, `rules/user-language.md`, or template missing.
Detection: File read returns 404.
Action: Apply SKILL.md changelog rules. Log: "Changelog rule file missing — using SKILL.md defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `format` | Keep a Changelog convention (## [version] — YYYY-MM-DD) |
| `commit_parse` | Conventional commits preferred; fallback to subject line grouping |
| `user_language` | User-facing language — no internal ticket IDs or jargon |
| `empty_commit_handling` | Skip merge commits and automated commits (bot, ci-skip) |
| `version_source` | Git tag preferred; VERSION file fallback |
