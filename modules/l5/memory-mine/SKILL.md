---
name: memory-mine
description: Deep pattern mining across the full memory store. Detects gaps, clusters related drawers, extracts patterns, maps staleness. Runs offline only — never during active execution. PID-locked to prevent concurrent runs. Schema-version-aware — triggers rebuild on mismatch.
---

# MemoryMine

You run between sessions, never during them. You read the full memory store and produce a structural analysis: what is missing, what clusters together, what patterns repeat, and what is going stale. You do not write drawers — you produce analysis files. Dream and MemorySearch consume your output.

## When to use / when not to use

**Use when:**
- Explicitly invoked between sessions (never mid-execution)
- Drawer count ≥ 50 (declared gate in Phase 3 deferral)
- Dream reports recurring uncertainty on a topic cluster
- MemorySearch reports frequent misses in a domain

**Do not use when:**
- Any execution wave is in progress
- Drawer count < 50 (insufficient signal for cluster detection)
- Called from within an Executor wave (hard block — defer and log)
- PID lock file exists and process is alive (another mine is running)

## Concurrency guard (adapted from mempalace miner PID reservation)

MemoryMine writes a PID lock file before starting any analysis:

```
.wabblespec/memory/.mine.pid   — lock file: contains PID + start timestamp
```

On startup, the script checks:
1. If `.mine.pid` exists and process is alive → exit immediately, log "Mine already running"
2. If `.mine.pid` exists but process is dead (crashed) → remove stale lock, proceed
3. If no lock → write lock, proceed

Lock is removed via `atexit` on clean exit or crash. Stale locks older than `WABBLESPEC_MINE_TIMEOUT_HOURS` (default 24h) are reclaimed automatically.

## Schema-version tracking (adapted from mempalace normalize_version pattern)

Each drawer contains a `schema_version` field. The current declared version lives in `modules/l5/memory/rules/schema-version.md`.

On each mine run, MemoryMine checks every drawer's `schema_version` against the current version:
- **Match**: drawer included in analysis as-is
- **Mismatch**: drawer flagged in staleness-map as `NEEDS_REBUILD`, excluded from cluster and pattern analysis (stale schema = unreliable structure)

When schema version bumps (e.g. v1 → v2), all v1 drawers appear as `NEEDS_REBUILD` in the next mine output. Dream's gap-map will surface them for re-verification. Drawers are never purged automatically — rebuild is a human-triggered re-write via the Memory module.

## What this skill does

Reads `.wabblespec/memory/index.json` and all drawer files. Runs four analyses:

### 1. Gap detection → gap-map.md

Identifies topics that are referenced by multiple drawers but have no drawer of their own. Also flags: drawers with `confidence < 0.5` on high-citation topics, and topics mentioned in receipts but absent from memory entirely.

```
Gap types:
  REFERENCED_BUT_ABSENT  — topic cited by 3+ drawers, no authoritative drawer
  LOW_CONFIDENCE_ANCHOR  — topic has drawer but confidence < 0.5, high citation count
  RECEIPT_ONLY           — appears in receipts, never written to memory
  NEEDS_REBUILD          — schema_version mismatch, excluded from analysis
```

### 2. Cluster detection → mine-clusters.md

Groups drawers by semantic proximity using topic taxonomy and explicit links. A cluster is 3+ drawers sharing a wing + overlapping topic keywords. Names the cluster. Identifies the anchor drawer (highest confidence + freshest).

Cluster output per cluster:
```
Cluster: <name>
Anchor drawer: <drawer-id>
Members: <drawer-ids>
Coherence: HIGH / MEDIUM / LOW (based on topic overlap)
Recommendation: CONSOLIDATE / KEEP / EXPAND
```

### 3. Pattern extraction → pattern-summary.md

Finds recurring structural patterns in drawer content:
- Repeated decision rationale across drawers → candidate for a policy drawer
- Repeated external constraints → candidate for a constraints index
- Repeated failure modes → candidate for a failure-mode library

Each pattern entry:
```
Pattern: <short name>
Evidence: <drawer-ids that exhibit it>
Recurrence: <count>
Recommendation: <action>
```

### 4. Staleness map → staleness-map.md

Summarizes staleness distribution across the store:
- Count per staleness state (FRESH / AGING / STALE / NEEDS_REVERIFICATION / EXPIRED / NEEDS_REBUILD)
- Drawers approaching staleness threshold within 7 days
- Wings with highest STALE concentration (candidate for targeted re-verification)
- Schema-version breakdown: how many drawers at each version

## Backend

Reads drawers via `mempalace.Palace.filter_drawers()` (ChromaDB). Does NOT scan flat JSON files.

```python
from mempalace.palace import Palace
from mempalace.miner import Miner
import os

palace = Palace(os.environ["MEMPALACE_PALACE_PATH"])

# Fetch all drawers for analysis
all_drawers = palace.filter_drawers(limit=10000)

# Check schema version per drawer
for drawer in all_drawers:
    schema_ver = drawer["metadata"].get("wabblespec_schema_version", 0)
    if schema_ver < CURRENT_SCHEMA_VERSION:
        flag_needs_rebuild(drawer)

# Miner for ingesting new content into palace (used when MemoryMine
# also writes new drawers from discovered patterns)
miner = Miner(palace_path=os.environ["MEMPALACE_PALACE_PATH"])
```

`MEMPALACE_PALACE_PATH` must be set (see `modules/l5/memory/rules/mempalace-config.md`).

## Inputs

- mempalace palace at `MEMPALACE_PALACE_PATH` — all drawer content via `Palace.filter_drawers()`
- `modules/l5/memory/rules/staleness-thresholds.md` — threshold definitions
- `modules/l5/memory/rules/schema-version.md` — current schema version

## Outputs

All four files written to `.wabblespec/memory/mine/`:

```
.wabblespec/memory/mine/
  gap-map.md
  mine-clusters.md
  pattern-summary.md
  staleness-map.md
  mine-receipt-{timestamp}.json
```

Files are overwritten on each run — always reflects current store state.

## Output contract

**mine-receipt** (`.wabblespec/receipts/mine-receipt-{timestamp}.json`):
```json
{
  "drawers_analyzed": "integer",
  "drawers_skipped_schema_mismatch": "integer",
  "schema_version_current": "integer",
  "gaps_found": "integer",
  "clusters_found": "integer",
  "patterns_found": "integer",
  "staleness_critical": "integer",
  "run_duration_ms": "integer"
}
```

## Common failure modes

1. **Running during active execution.** MemoryMine reads and analyzes — it does not block execution. But its output files may be stale if written mid-session. Hard rule: invoke only between sessions.

2. **Treating gap-map.md as a task list.** Gaps are signals, not mandates. Dream decides which gaps to pursue. MemoryMine surfaces; it does not decide.

3. **Running with < 50 drawers.** Cluster detection on sparse data produces noise. 50+ drawers is the minimum for meaningful signal — below that, patterns are artifacts of small sample size.

4. **Ignoring NEEDS_REBUILD drawers.** Schema-version mismatches accumulate silently if gap-map is not read. After a schema version bump, run MemoryMine and address all NEEDS_REBUILD entries before relying on analysis output.

## Reference

Pattern source: `mempalace-develop/mempalace/miner.py` (per-file PID locking, schema bump purge+rebuild trigger), `mempalace-develop/mempalace/hooks_cli.py` (PID slot reservation, stale lock reclaim via timeout), `mempalace-develop/mempalace/convo_miner.py` (normalize_version check, locked purge + batched rebuild).
