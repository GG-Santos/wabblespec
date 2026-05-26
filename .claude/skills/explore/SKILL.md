---
name: explore
description: Graph-first codebase discovery. Traverses from high-value nodes (entry points, config files, test files, dependency manifests) to produce project-map.md. Writes findings to Memory as FRESH drawers. Notifies EntityGraph for entity extraction. Per-target traversal order follows platform conventions from the active L3 package.
---

# Explore

You build a structured map of the codebase before spec work or execution that depends on codebase understanding. You start at high-value nodes and traverse outward — you do not scan the entire repo blindly.

## What this skill does

Graph-first codebase discovery. Traverses from high-value nodes (entry points, config files, test files, dependency manifests) to produce project-map.md. Writes findings to Memory as FRESH drawers. Notifies EntityGraph for entity extraction. Per-target traversal order follows platform conventions from the active L3 package.

## When to use

- Research phase at session start for any execution involving existing code
- After Scaffold generates initial project structure
- When Autopilot detects project-map.md is STALE or EXPIRED
- Explicit `/explore` command

Active during Research phase only; invoke before execution waves begin.

## Traversal order

Start from high-value nodes. Per-target traversal order from the active L3 platform package. Default order when no platform package is active:

1. Dependency manifests (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `pom.xml`, etc.)
2. Entry points (main files, index files, app entry, server root)
3. Configuration files (env templates, build config, CI config)
4. Test files (test directory root, first test file as pattern signal)
5. High-churn files (git log: most frequently modified in last 30 commits)
6. Files referenced in spec artifacts (if P1–P4 exist)

Stop when: project-map.md captures enough to answer the current research question, OR all high-value nodes exhausted, OR Memory drawer count limit reached (default: 50 new drawers per Explore session).

## Freshness policy

Every project-map.md carries a `freshness_state` and `valid_until`. Explore sets these at write time. Downstream modules (ReferenceLoad, Decompose, Guard) check `freshness_state` before consuming the map.

| State | Condition | Consumer action |
|---|---|---|
| `FRESH` | Within `valid_until` window (default 24h from `explored_at`) | Load and use |
| `AGING` | 24–72h past `explored_at`, no structural change detected | Load with staleness noted |
| `STALE` | 72h+ elapsed, OR new packages added, OR entry-points changed | Trigger Explore re-run before planning |
| `EXPIRED` | Entry-points or tech-stack changed in git since last map | Block consumption — Explore re-run required |

Set `valid_until` to `explored_at + 24h` for most targets. High-churn projects (>5 commits per day) may use 8h. Explore re-runs always write a new map and reset `freshness_state` to `FRESH`.

## Output contract

Write to `.wabblespec/plans/project-map.md`. Schema contract: `_shared/schemas/project-map.schema.json`.

```markdown
# Project Map

**Explored at:** ISO 8601
**Build target:** string (from Recipe)
**Freshness state:** FRESH|AGING|STALE|EXPIRED
**Valid until:** ISO 8601 (explored_at + 24h default)
**Entry points:** [list]

## Tech Stack

| Area | Technology | Version | Confidence |
|---|---|---|---|
| runtime | Node.js | 20.x | exact |

## Spec Artifacts Found

| File | Artifact Type | Status |
|---|---|---|

## Conventions Observed

- <naming convention>
- <project structure pattern>
- <notable architectural pattern>

## Risk Files

| Path | Risk Reason | Notes |
|---|---|---|
| <path> | high-churn | <N> changes in last 30 commits |
| <path> | edit-warning | <annotation note> |
| <path> | no-tests | no test file references this path |
| <path> | cross-cutting | imported by >5 modules |

## Impact Slices

Named slices of this map. ReferenceLoad consumes these instead of raw file trees.

### Slice: entry-points
**Primary paths:** <ranked list of entry-point files>
**Test paths:** <test files covering entry points>
**Reason:** main application entry — read first for any execution-path question

### Slice: api-surface
**Primary paths:** <ranked list of public API/interface files>
**Test paths:** <test files covering API surface>
**Reason:** external contract — read for any spec or migration question

### Slice: test-coverage
**Primary paths:** <test directory root, key test files>
**Reason:** test posture — read before declaring verification mode

### Slice: risk
**Primary paths:** <paths from Risk Files table>
**Reason:** files requiring extra care before editing — feed to Executor wave planning

### Slice: conventions
**Primary paths:** <config files, linting rules, directory structure files>
**Reason:** project conventions — read before Specify or Clean

## Git State

**Active branch:** string
**Recent changes:** <files modified in last N commits>
**Uncommitted changes:** <count>

## Gaps

- <unknown area 1 — what Explore could not determine>
- <at least one gap is required — do not claim full coverage>
```

## Memory writes

For each distinct finding, write one Memory drawer as FRESH:
- One drawer per tech stack component (not one drawer per file)
- One drawer per observed convention
- One drawer per architectural pattern
- One drawer per gap identified

Notify EntityGraph after all drawers written — pass list of entity candidates (file paths, module names, technology names) for extraction.

## What not to do

- Do not scan every file — traverse from high-value nodes only
- Do not write one drawer per file — write one drawer per distinct finding
- Do not run during active execution waves
- Do not block on incomplete traversal — write what is found, declare gaps
- Do not write project-map.md without `freshness_state` and `valid_until` — a map without these fields cannot be used as a reference slice
- Do not list individual files where a named impact slice suffices — slices are the consumption unit, not raw file lists
- Do not claim zero gaps — at least one gap entry is required to prevent false completeness
