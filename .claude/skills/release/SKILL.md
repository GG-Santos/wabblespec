---
name: release
description: Creates an annotated git tag with Attestation, extracts release notes from Archive changelog, and publishes to GitHub Releases. Requires production Deploy receipt. Tag is signed and pushed. Release notes are derived from CHANGELOG.md — not written from scratch.
---

# Release

You make a release official and visible. You tag the commit, sign the tag, extract release notes from the changelog, and publish to GitHub Releases. You do not write release notes from scratch — Archive wrote them. You do not release without a production deploy receipt.

## What this skill does

Creates an annotated git tag with Attestation, extracts release notes from Archive changelog, and publishes to GitHub Releases. Requires production Deploy receipt. Tag is signed and pushed. Release notes are derived from CHANGELOG.md — not written from scratch.

## When to use

Invoked per activators declared in `skill-rules.json`.

## Inputs

- `deploy-receipt-production-*.json` — confirms production deploy succeeded
- `.wabblespec/CHANGELOG.md` — source of release notes for this version
- `.wabblespec/VERSION` — current version string
- Signing key reference (for tag signature)
- GitHub token (from CI secrets)

## How to do it

### Step 1 — Verify production deploy receipt

Load most recent `deploy-receipt-production-*.json`. Confirm `status: DEPLOYED` (not ROLLED_BACK or FAILED). If absent or not DEPLOYED: FAIL with `PRODUCTION_NOT_DEPLOYED`.

### Step 2 — Determine tag name

Tag format: `v{VERSION}` where VERSION is the string from `.wabblespec/VERSION`.

Check tag does not already exist:
```bash
git tag --list "v${VERSION}"
# Must return empty — do not re-tag an existing version
```

If tag exists: FAIL with `TAG_ALREADY_EXISTS`. Do not force-push tags.

### Step 3 — Extract release notes from CHANGELOG.md

Read `.wabblespec/CHANGELOG.md`. Find the section for the current version:
```markdown
## [1.2.3] — 2026-05-22T10:00:00Z
...content...
## [1.2.2] — ...   <- stop here
```

Extract the content between current version header and the next version header. This is the release notes body. Do not edit or summarize — use verbatim.

### Step 4 — Create and push annotated tag

```bash
git tag -a "v${VERSION}" \
  -m "Release v${VERSION}

${RELEASE_NOTES_FIRST_PARAGRAPH}

Signed-off-by: ${ACTOR}
Attestation: ${ATTESTATION_REF}"

# Sign tag (requires GPG or SSH signing configured)
git tag -s "v${VERSION}" -m "..."   # GPG signed
# or: git -c gpg.format=ssh tag -s "v${VERSION}"

# Push tag
git push origin "v${VERSION}"
```

**Do not use `git push --tags` (pushes all local tags).** Push only this specific tag.

### Step 5 — Publish GitHub Release

```bash
gh release create "v${VERSION}" \
  --title "v${VERSION}" \
  --notes-file release-notes-extracted.md \
  --verify-tag \
  dist/firmware.bin \
  dist/firmware.bin.sha256 \
  dist/firmware.bin.sig
```

Attach: all artifacts from the package manifest + their SHA-256 files + signature files.

### Step 6 — Write release receipt

## Output contract

**release-receipt** (`.wabblespec/receipts/release-receipt-{timestamp}.json`):
```json
{
  "version": "string",
  "tag": "string",
  "tag_signed": "boolean",
  "tag_pushed": "boolean",
  "github_release_url": "string",
  "artifacts_attached": "integer",
  "release_notes_source": "CHANGELOG.md"
}
```

## Non-negotiable rules

1. Production deploy receipt required — no release without confirmed production deploy.
2. Tag must be annotated and signed — lightweight tags are not releases.
3. Never force-push a release tag. If wrong: create a patch version.
4. Release notes sourced from CHANGELOG.md verbatim — Archive wrote them, Release publishes them.
5. All Package artifacts (+ signatures + SHA-256 files) attached to GitHub Release.

## Common failure modes

1. **Creating a release before production deploy.** Release is the public record. Publishing before production confirms means the release may describe code that isn't running.

2. **Force-pushing a tag.** Once pushed, a release tag should be immutable. Users and package managers pin to tags — mutating a tag breaks their pins silently.

3. **Writing release notes from scratch.** Archive generated changelog entries from wave receipts. Release notes derived from there have an audit trail. Hand-written notes do not.
