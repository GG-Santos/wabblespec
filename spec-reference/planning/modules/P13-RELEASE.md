# Module Plan — Release (L7)

**Tier:** 3 — SUPPORTING
**Layer:** L7 Delivery
**v5.3 origin:** Release module — release coordination, git tag, release notes, stakeholder communication

---

## Purpose

Coordinate release: git tag, release notes, stakeholder communication, and release artifact publishing. Release runs after Deploy succeeds. Marks the version as shipped in Archive. Writes the release to the project's release channel (GitHub Releases, changelog, internal tracking). Release is the final step in the Delivery pipeline before Evolution begins observing.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/release <version>` command
- Deploy receipt confirms successful deployment to production
- Cannot activate without:
  - Deploy receipt (production deployment confirmed)
  - Archive receipt (version bump and changelog entry present)
  - Package receipt (signed artifact exists)

---

## Release Artifacts

| Artifact | Source | Destination |
|---|---|---|
| Git tag | Archive version | `git tag v<semver>` + push |
| Release notes | Archive changelog entry + Memory research log | GitHub Releases body / release doc |
| Signed artifact attachment | Package artifact manifest | GitHub Releases assets (if applicable) |
| Internal announcement | Release notes (condensed) | Declared communication channel |

---

## Release Notes Structure

Release notes derived from Archive changelog entry — not invented:

```markdown
# Release v<semver> — <YYYY-MM-DD>

## What changed

<from Archive changelog: BREAKING / ADDITIVE / COSMETIC entries>

## Migration notes (if BREAKING)

<from Specify BREAKING delta records>

## Known issues

<from Verifier not-tested list + open decisions flagged as unresolved>

## Artifacts

| Platform | Download | SHA-256 |
|---|---|---|
| <platform> | <link> | <hash from Package manifest> |
```

---

## Workflow

```
1. Validate prerequisites:
   -> Deploy receipt present (production deploy confirmed)
   -> Archive receipt present (version + changelog)
   -> Package receipt present (signed artifact)
   -> Attestation received (release is irreversible — git tag cannot be un-pushed cleanly)

2. Compose release notes from Archive changelog

3. Append known issues from:
   -> Verifier not-tested compilation
   -> Open decisions flagged as unresolved at ship

4. Create and push git tag:
   -> Tag: v<semver>
   -> Annotated tag with release notes summary
   -> Push to origin (requires explicit Attestation)

5. Publish to release channel:
   -> GitHub Releases (if project uses GitHub)
   -> Or declared equivalent (GitLab, internal tracker)

6. Send internal announcement (if declared in spec)

7. Notify Archive: release complete (Archive marks version as RELEASED)

8. Notify Instinct: release event (release cycle signal for pattern tracking)

9. Write Release receipt
```

---

## Irreversibility Handling

Git tag push is irreversible in practice (force-delete is destructive and affects downstream consumers). Release activates Attestation gate before tag push — human explicitly confirms:

- Version string correct
- Deploy receipt confirmed
- Known issues documented
- Attestation: human signs off before push proceeds

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — post-Deploy, requires Attestation |
| `templates/release-notes.md` | Template | Release notes structure |
| `rules/attestation-required.md` | Rules | Git tag push requires Attestation (irreversible) |
| `rules/source-only.md` | Rules | Release notes sourced from Archive only — no invention |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Deploy | Release activates only after Deploy receipt confirms production success |
| Archive | Release reads Archive changelog for release notes; notifies Archive on release complete |
| Package | Release attaches Package artifact manifest (hash, links) to release notes |
| Verifier | Release reads Verifier not-tested compilation for known issues section |
| Instinct | Release notifies Instinct: release cycle complete (pattern signal) |
| Autopilot | Autopilot marks lifecycle complete after Release receipt written |

---

## Verification Mode

**Attestation** — human sign-off before git tag push, release notes sourced from Archive, Deploy receipt confirmed, release receipt written.

---

## Receipt Extension Fields

```json
{
  "version": "string",
  "git_tag": "string",
  "tag_pushed": "boolean",
  "release_channel": "string",
  "release_url": "string",
  "attestation_received": "boolean",
  "known_issues_count": "integer",
  "announcement_sent": "boolean"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Release channel | GitHub Releases (default) vs. declared per-project | Per-project at P1 |
| Internal announcement format | Slack/email/doc — declared in spec vs. always optional | Per-project |
| Pre-release support | RC/beta tags (v1.0.0-rc.1) vs. only stable releases | Per-project at P1 |
| Rollback after release | Release receipt triggers Rollback module vs. manual only | P15 Rollback planning |
