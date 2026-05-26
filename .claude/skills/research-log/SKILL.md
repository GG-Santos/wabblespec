---
name: research-log
description: Logs research findings as memory drawers with provenance. Use when an Executor wave produces factual evidence worth preserving — API behavior, library constraints, external system behavior, design decisions with evidence. Delegates storage to Memory module.
---

# Research Log

You log research findings. You do not store them yourself — Memory does. You are the interface that formats findings into drawer-ready entries and hands them to Memory.

## What this skill does

Logs research findings as memory drawers with provenance. Use when an Executor wave produces factual evidence worth preserving — API behavior, library constraints, external system behavior, design decisions with evidence. Delegates storage to Memory module.

## When to use

- During or after a wave where external research was conducted (API docs read, library tested, system behavior observed)
- When a finding will inform future waves or future sessions
- When the same question would otherwise need to be re-researched

**Do not activate for:**
- Internal reasoning or design decisions without external evidence (use Memory directly)
- Findings that are already in an existing FRESH drawer (check MemorySearch first)
- Per-wave implementation notes (those belong in receipts)

## Output contract

One or more drawer entries, each containing:

| Field | Content |
|---|---|
| `topic` | The specific question the finding answers |
| `body` | The finding — concrete, evidence-backed |
| `evidence` | Source: URL, file path, test output, doc version |
| `confidence` | 0.0–1.0 based on evidence quality |
| `staleness_state` | FRESH on creation |
| `expires_at` | Declared when finding has known expiry (e.g., API version) |
| `spec_binding` | Object — binds finding to a named spec requirement (see below) |

### spec_binding field

Links the research finding to the specific spec artifact and requirement it was gathered for. Required when research was conducted in support of a spec-writing wave.

```json
{
  "spec_artifact_path": ".wabblespec/plans/task-card.md",
  "requirement_name": "<requirement name or section heading in that artifact>",
  "wave_id": "<wave-id from decompose plan — e.g. wave-2>",
  "binding_type": "supports | contradicts | qualifies"
}
```

**`binding_type`:**
- `supports` — finding provides positive evidence for this requirement
- `contradicts` — finding reveals the requirement as stated is incorrect or infeasible
- `qualifies` — finding adds a condition or constraint the requirement does not yet capture

**When `spec_binding` is absent:** finding is session-scoped only. Valid for exploratory research with no current spec target. Specify cannot cite it as requirement evidence without a `spec_binding`.

**OpenSpec alignment:** each spec is per-capability (`specs/<capability>/spec.md`). `spec_binding.requirement_name` maps to the `### Requirement: <name>` heading in that spec file.

## Freshness rules

- If finding depends on a specific library version: set `expires_at` to next major version release estimate
- If finding is from official docs with a version stamp: cite version in evidence
- If finding is from observed behavior with no version anchor: confidence ≤ 0.7, set staleness_state AGING

## Memory citation step

After Memory confirms the drawer write, Research Log notifies Provenance with a citation-record:

```json
{
  "drawer_id": "<drawer_id just written>",
  "spec_artifact_path": "<spec_binding.spec_artifact_path>"
}
```

This populates `cited_by` in the drawer's provenance record. When the spec artifact later changes with `change_class: BREAKING`, Provenance cascade marks this drawer NEEDS_REVERIFICATION automatically.

**If `spec_binding` is absent:** skip citation notification. Provenance only tracks citations for spec-bound research.

## Relationship to Memory module

Research Log is a caller of Memory. It formats entries; Memory writes them. If Memory is not active in this session, Research Log writes the entry directly using Memory's drawer schema.

## Feature-scoped research artifact

When `spec_binding` is present, Research Log writes a second output in addition to the session receipt:

**Path:** `research/{feature-slug}/research.md`

**Feature-slug derivation:** extract the final path segment (without extension) from `spec_binding.spec_artifact_path`.
- Example: `spec_binding.spec_artifact_path: ".wabblespec/plans/task-card.md"` → slug = `task-card`
- Example: `spec_binding.spec_artifact_path: "specs/auth-flow/spec.md"` → slug = `auth-flow`

**File content:** Markdown summary of all findings bound to this spec artifact. Sections per `requirement_name`. Each finding includes body, evidence, confidence, and binding_type.

**Lifecycle:** This file follows the spec into Specify → Propose → Executor (feature-scoped lifecycle). Specify may cite it as requirement evidence. It is updated (not replaced) each time new findings arrive for the same feature-slug.

**When `spec_binding` is absent:** skip this step. Session receipt only.

## Receipt

Research Log writes a receipt to `.wabblespec/receipts/research-log-{timestamp}.json` confirming:
- Number of drawers written
- Topics covered
- Confidence range across entries
- `feature_scoped_path`: path to `research/{slug}/research.md` if written, else null
