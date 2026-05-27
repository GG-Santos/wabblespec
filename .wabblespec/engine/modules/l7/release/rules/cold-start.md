# Cold-Start Behavior — Release

Defines what Release does when its upstream artifacts or version data are absent.

## Absent: Package artifact

Condition: Release invoked but no Package receipt or signed artifact exists.
Detection: No `package-receipt.json` in `.wabblespec/state/receipts/`.
Action: BLOCK Release. Surface: "Release requires a Package receipt. Complete Package step first."
Do NOT: Release without a confirmed package artifact.

## Absent: CHANGELOG entry for this version

Condition: Release version has no corresponding CHANGELOG.md entry.
Detection: CHANGELOG.md does not contain the release version.
Action: FLAG: "No CHANGELOG entry found for version [v]. Add a CHANGELOG entry before releasing."
Do NOT: Block release entirely — flag and allow user to confirm proceed.

## Absent: git tag for this version

Condition: Release invoked but the version is not tagged in git.
Detection: `git tag -l [version]` returns empty.
Action: Offer to create the tag: "Git tag [version] not found. Create it before releasing?"
Do NOT: Create the tag without user confirmation.

## Absent: release notes template

Condition: Release notes needed but no template available.
Detection: No release notes template in changelog/templates/ or release/.
Action: Use CHANGELOG entry as release notes. Log: "No release notes template — using CHANGELOG entry."

## Absent: publish target declaration

Condition: Release invoked without specifying where to publish (npm, PyPI, GitHub Releases, etc.).
Action: Surface: "Release requires a declared publish target."

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | Package receipt required |
| `git_tag` | Required before publish |
| `changelog_required` | Required — flag if absent |
| `publish_confirmation` | Manual — user must confirm before publish |
| `rollback_window` | Declare unpublish/yank procedure for 24h post-release |
