---
name: reference-load-l0
description: Loads external references with declared source trust levels (HIGH/MEDIUM/LOW). Staleness recheck policy enforced: STALE sources recheck before loading, EXPIRED sources require explicit override. Every reference load writes to Memory as FRESH drawers with Provenance records and triggers a ResearchLog entry. No silent external calls.
---

# ReferenceLoad

You load external references before spec work or execution that depends on external knowledge. You make loaded knowledge persistent, trustworthy, and staleness-tracked. You never load silently — every load is declared and logged.

## What this skill does

Loads external references with declared source trust levels (HIGH/MEDIUM/LOW). Staleness recheck policy enforced: STALE sources recheck before loading, EXPIRED sources require explicit override. Every reference load writes to Memory as FRESH drawers with Provenance records and triggers a ResearchLog entry. No silent external calls.

## When to use

- Research phase before spec work that depends on external references
- Recipe identifies build target requiring platform-specific reference knowledge
- Explicit `/reference-load` command with source declared

## Trust levels

Every loaded reference receives a trust level at load time:

| Trust level | Criteria |
|---|---|
| HIGH | Official documentation, published specs, test outputs from the project itself |
| MEDIUM | Code inspection of active codebase, project configuration files, verified secondary sources |
| LOW | Inference, assumption, second-hand reports, community discussions, unchecked external sources |
| UNVERIFIED | Loaded but not cross-checked — requires explicit flag in drawer |

Trust level is declared at load time and recorded in the Provenance record. Trust level cannot be upgraded without re-verification.

## Staleness recheck policy

Before loading from a source with existing Memory drawers:

| Existing staleness | Action before loading |
|---|---|
| FRESH | Load without recheck |
| AGING | Load with staleness noted in receipt |
| STALE | Recheck source before loading — if unchanged, reload as FRESH; if changed, load new version |
| EXPIRED | Require explicit override from human before loading — document override reason in receipt |
| NEEDS_REVERIFICATION | Treat as STALE — recheck required |
| SUPERSEDED | Do not load superseded drawer — load the superseding drawer instead |

No silent loading of EXPIRED sources.

## Load process

### Step 0 — Project-map slice check

Before declaring any external sources, check `.wabblespec/plans/project-map.md` for a named impact slice covering the reference area.

| Map state | Action |
|---|---|
| Map absent | Proceed to Step 1 — no map to check |
| `freshness_state: FRESH` or `AGING`, relevant slice exists | Load from that slice; do not load raw file trees for the same area |
| `freshness_state: STALE` | Note staleness in receipt; proceed with caution; flag for Explore re-run |
| `freshness_state: EXPIRED` | Block — trigger Explore re-run before loading; do not proceed until map is refreshed |

Relevant slice: a named slice in `## Impact Slices` whose `Reason` covers the question being answered. If no slice covers the area, proceed to Step 1 and load from raw sources as normal.

When a slice is used: record which slice was consumed (`slice_name`, `slice_freshness_state`, `explored_at`) in the receipt.

### Step 1 — Declare sources

List every reference to be loaded with:
- Source identifier (URL, file path, document name)
- Declared trust level with rationale
- Purpose (what question this reference answers)

### Step 2 — Staleness check

For each source: check Memory index for existing drawers from this source. Apply staleness recheck policy.

### Step 3 — Load content

Load each source. Do not load sources not declared in Step 1 during this session.

### Step 4 — Write to Memory

For each loaded reference, write one Memory drawer per distinct finding (not one drawer per source):

```markdown
---
drawer_id: <generated>
topic: <what this finding is about>
staleness: FRESH
confidence: <0.0-1.0 based on trust level — HIGH=0.9, MEDIUM=0.7, LOW=0.4, UNVERIFIED=0.2>
source_module: reference-load
written_at: <ISO 8601>
last_verified_at: <ISO 8601>
---

<finding content — specific, citable, not a summary>
```

### Step 5 — Write Provenance records

For each drawer written: write Provenance record with source, trust level, load date, and any contradictions with existing drawers.

### Step 6 — Trigger ResearchLog

Notify ResearchLog with: sources loaded, drawer IDs written, findings count, any EXPIRED override decisions.

## Outputs

Receipt declaring: sources loaded, trust levels, drawer IDs written, staleness actions taken, any EXPIRED overrides with reasons.

## What not to do

- Do not load sources not declared before loading begins
- Do not merge multiple findings into one drawer — one distinct finding per drawer
- Do not silently load EXPIRED sources
- Do not assign HIGH trust to unverified sources
- Do not load without writing Provenance records
- Do not load raw file trees for an area when a FRESH or AGING project-map slice covers it — consume the slice instead
- Do not proceed when project-map `freshness_state` is `EXPIRED` — trigger Explore re-run first
