# Acceptance Tests — Release (L7)

## AT-REL-01: Production deploy receipt required with DEPLOYED status

**Given** a Release invocation
**When** Release checks preconditions
**Then** it loads the most recent `deploy-receipt-production-*.json` and verifies `status: DEPLOYED`; absent receipt or `status: ROLLED_BACK` or `status: FAILED` causes FAIL with `PRODUCTION_NOT_DEPLOYED`

---

## AT-REL-02: Tag must be annotated and signed

**Given** a Release creating a git tag
**When** the tag is created
**Then** it is created as an annotated tag with `-a` flag and signed (`-s`); lightweight tags are not acceptable as release markers

---

## AT-REL-03: No force-push of release tags

**Given** a release tag that already exists
**When** Release detects the tag
**Then** Release FAILs with `TAG_ALREADY_EXISTS` and does not force-push; a patch version must be created instead

---

## AT-REL-04: Release notes sourced verbatim from CHANGELOG.md

**Given** a Release run
**When** release notes are produced
**Then** the content is extracted verbatim from the current version section in `CHANGELOG.md`; Release does not write new release notes or summarize

---

## AT-REL-05: All Package artifacts attached to GitHub Release

**Given** a Release creating a GitHub Release
**When** artifacts are attached
**Then** all artifacts from the package manifest plus their SHA-256 files and signature files are attached

---

## AT-REL-06: Only this specific tag is pushed

**Given** a Release pushing a tag
**When** the git push command runs
**Then** only the specific release tag is pushed (`git push origin "v${VERSION}"`); `git push --tags` is never used

---

## AT-REL-07: Release receipt contains required fields

**Given** a completed Release run
**Then** the receipt at `.wabblespec/receipts/release-receipt-{timestamp}.json` contains:
- `version`
- `tag`
- `tag_signed`
- `tag_pushed`
- `github_release_url`
- `artifacts_attached`
- `release_notes_source` (always "CHANGELOG.md")
