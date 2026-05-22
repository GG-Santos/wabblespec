# Module Plan — Archive (L7)

**Tier:** 1 — CRITICAL
**Layer:** L7 Delivery
**v5.3 origin:** Archive module — enriched with --sweep, --entomb modes, Nexus refresh hook

---

## Purpose

Close and finalize a change. Reads all receipts from execution, composes a delivery receipt, bumps version, writes changelog entry, and preserves full provenance trail. Receipts are never deleted — only superseded and archived. Archive is the permanent record of what happened.

---

## Activation

`skill-rules.json` triggers:
- Executor signals full execution complete (all waves passed Verifier)
- Explicit `/archive` command with target execution
- `--sweep` flag: batch entomb stale artifacts
- `--entomb` flag: archive specific artifact set

---

## Receipt Aggregation

Archive reads all receipts produced during execution and composes one delivery receipt:

| Receipt type | Source |
|---|---|
| Research receipts | `.wabblespec/receipts/referenceload-receipt.md`, `memorysearch-receipt.md`, `explore-receipt.md` |
| Plan receipts | `interview-receipt.md`, `scopeframe-receipt.md`, `specify-receipt.md`, `propose-receipt.md`, `decompose-receipt.md` |
| Runtime receipts | `runtime-<timestamp>.md` (one per wave) |
| Wave receipts | `wave-<N>-receipt.md` (one per wave) |
| Verification receipts | `verification-<wave>-<timestamp>.md` |
| Reviewer receipts | `reviewer-receipt-<timestamp>.md` |
| Execution receipt | `execution-receipt.md` |

---

## Not-Tested Compilation

Archive aggregates all `not_tested` fields from every receipt. Delivery receipt includes a consolidated not-tested list. No gaps are hidden. Implied completion is prohibited (I10).

```markdown
## Not Tested

- <item from wave 1 receipt>
- <item from verification receipt>
- <item from apply receipt>
```

Delivery is not blocked by not-tested items — they are recorded, not resolved. Resolution is a future task.

---

## Version Management

Archive bumps version following semantic versioning:
- BREAKING changes in any receipt → major bump
- ADDITIVE changes only → minor bump
- COSMETIC only → patch bump

Version written to `.wabblespec/VERSION`. Changelog entry appended to `CHANGELOG.md`.

### Changelog entry format

```markdown
## [version] — timestamp

### Changed
- <BREAKING or ADDITIVE items from receipts>

### Fixed
- <COSMETIC or correction items>

### Not Tested
- <aggregated not-tested list>

### Receipts
- execution-receipt: <path>
- verification summary: <N waves, N passed, N failed>
```

---

## Modes

### Default mode
Aggregate receipts, compose delivery receipt, bump version, write changelog.

### --sweep mode
Batch entomb stale artifacts. Reads `.wabblespec/memory/index.md` for EXPIRED drawers. Archives them to `.wabblespec/memory/closets/`. Writes sweep receipt listing what was archived.

### --entomb mode
Archive specific artifact set. Caller declares which artifacts. Archive moves to `.wabblespec/archive/<timestamp>/`, writes entomb receipt with provenance note.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Delivery receipt | `.wabblespec/receipts/delivery-receipt-<timestamp>.md` | Master I10 record |
| VERSION | `.wabblespec/VERSION` | Current framework/project version |
| CHANGELOG.md | `.wabblespec/CHANGELOG.md` | Human-readable change history |
| Sweep receipt | `.wabblespec/receipts/sweep-<timestamp>.md` | --sweep audit trail |
| Entomb receipt | `.wabblespec/archive/<timestamp>/entomb-receipt.md` | --entomb audit trail |

All prior receipts remain in `.wabblespec/receipts/`. Archive never deletes — only aggregates and records.

---

## Delivery Receipt Structure

```markdown
# Delivery Receipt

**version:** semver
**timestamp:** datetime
**target:** build target
**stages_completed:** [P1, P2, P3, P4, Execution]
**waves_completed:** integer
**confidence:** aggregate from wave receipts

## Receipts Aggregated

| Receipt | Path | Result |
|---|---|---|
| Research | ... | PASS |
| Plan | ... | PASS |
| Execution | ... | PASS |

## Not Tested

- <consolidated list>

## Change Classification

- BREAKING: integer count
- ADDITIVE: integer count
- COSMETIC: integer count

## Version Bump

- Previous: semver
- New: semver
- Reason: BREAKING|ADDITIVE|COSMETIC
```

---

## Workflow

```
1. Receive: execution complete signal from Executor (or explicit command)

2. Read all receipts from .wabblespec/receipts/ for this execution session

3. Aggregate not_tested lists from all receipts

4. Determine version bump from change classifications across receipts

5. Write changelog entry

6. Bump VERSION file

7. Compose delivery receipt

8. Notify Instinct (Evolution): execution complete, receipts available for pattern tracking

9. If --sweep: read memory index, archive EXPIRED drawers, write sweep receipt

10. If --entomb: move declared artifacts to archive/, write entomb receipt

11. Write delivery receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over CHANGELOG.md, VERSION, delivery receipts |
| `rules/version-bump.md` | Rules | BREAKING/ADDITIVE/COSMETIC to major/minor/patch mapping |
| `rules/not-tested-policy.md` | Rules | What qualifies as not-tested; aggregation rules |
| `rules/sweep-policy.md` | Rules | --sweep scope, what qualifies for entombment |
| `schemas/delivery-receipt.schema.json` | Schema | Delivery receipt validation |
| `schemas/receipt.schema.json` | Schema | Module receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Executor | Archive receives execution complete signal from Executor |
| Verifier | Archive reads all verification receipts for delivery record |
| Instinct | Archive notifies Instinct on completion — Instinct reads receipts for pattern tracking |
| Memory | Archive --sweep reads Memory index for EXPIRED drawers |
| Provenance | Archive --entomb records provenance note for archived artifacts |
| Deploy | Deploy reads delivery receipt as prerequisite gate |

---

## Verification Mode

**Audit** — all required receipts present, not-tested list complete, VERSION bumped, CHANGELOG updated, delivery receipt written with no missing fields.

---

## Receipt Extension Fields

```json
{
  "receipts_aggregated": "integer",
  "not_tested_items": "integer",
  "version_previous": "string",
  "version_new": "string",
  "version_bump_reason": "BREAKING|ADDITIVE|COSMETIC",
  "breaking_count": "integer",
  "additive_count": "integer",
  "sweep_mode": "boolean",
  "artifacts_swept": "integer",
  "entomb_mode": "boolean",
  "artifacts_entombed": "integer"
}
```

---

## v5.3 Mapping

| v5.3 Archive | v6.1 Archive |
|---|---|
| Close and finalize change | Same |
| Version bump + changelog | Same |
| `--entomb` mode | Same |
| `--sweep` mode (new v5.3) | Same |
| Nexus refresh hook (new v5.3) | Replaced by Instinct notification (Evolution pattern tracking) |
| Delta merge | Included in delivery receipt change classification |
| No consolidated not-tested | not_tested aggregated from all receipts into delivery receipt |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Receipt retention policy | Keep all indefinitely (current) vs. configurable retention window | Per-module planning |
| CHANGELOG format | Current markdown format vs. conventional commits format | Per-module planning |
| Sweep trigger | Manual --sweep only vs. auto-sweep on EXPIRED threshold | Per-module planning |
| Confidence aggregation | Min of all wave confidences vs. weighted average | Per-module planning |
