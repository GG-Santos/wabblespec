---
name: memory-mine
description: Deep pattern mining across the full memory store. Detects gaps, clusters related drawers, extracts patterns, maps staleness, finds near-duplicates. Runs offline only — never during active execution. PID-locked to prevent concurrent runs. Schema-version-aware — triggers rebuild on mismatch.
---

# MemoryMine

You run between sessions, never during them. You read the full memory store and produce a structural analysis: what is missing, what clusters together, what patterns repeat, what is going stale, and what drawers are near-duplicates. You do not write drawers — you produce analysis files. Dream and MemorySearch consume your output.

## When to use / when not to use

**Use when:**
- Explicitly invoked between sessions (never mid-execution)
- Drawer count >= 50 (declared gate in Phase 3 deferral)
- Dream reports recurring uncertainty on a topic cluster
- MemorySearch reports frequent misses in a domain

**Do not use when:**
- Any execution wave is in progress
- Drawer count < 50 (insufficient signal for cluster detection)
- Called from within an Executor wave (hard block — defer and log)
- PID lock file exists and process is alive (another mine is running)

## Concurrency guard

MemoryMine writes a PID lock file before starting any analysis:

```
.wabblespec/state/memory/.mine.pid   — lock file: contains PID + start timestamp
```

On startup, the script checks:
1. If `.mine.pid` exists and process is alive → exit immediately, log "Mine already running"
2. If `.mine.pid` exists but process is dead (crashed) → remove stale lock, proceed
3. If no lock → write lock, proceed

Lock is removed via `atexit` on clean exit or crash. Stale locks older than `WABBLESPEC_MINE_TIMEOUT_HOURS` (default 24h) are reclaimed automatically.

## Schema-version tracking

Each drawer contains a `wabblespec_schema_version` field. The current declared version lives in `modules/l5/memory/rules/schema-version.md`.

On each mine run, MemoryMine checks every drawer's `wabblespec_schema_version` against the current version:
- **Match**: drawer included in analysis as-is
- **Mismatch**: drawer flagged in staleness-map as `NEEDS_REBUILD`, excluded from cluster and pattern analysis (stale schema = unreliable structure)

When schema version bumps (e.g. v1 to v2), all v1 drawers appear as `NEEDS_REBUILD` in the next mine output. Dream's gap-map will surface them for re-verification. Drawers are never purged automatically — rebuild is a human-triggered re-write via the Memory module.

Note: ConvoMiner drawers (`wing_sessions`) are written without `wabblespec_schema_version` and will appear as `NEEDS_REBUILD`. This is expected — wing_sessions drawers are secondary evidence and are not subject to the curated schema.

## What this skill does

Reads the full ChromaDB memory store. Runs five analyses:

### 1. Gap detection -> gap-map.md

Identifies topics that are referenced by multiple drawers but have no drawer of their own. Also flags: drawers with `confidence < 0.5` on high-citation topics, and topics mentioned in receipts but absent from memory entirely.

```
Gap types:
  REFERENCED_BUT_ABSENT  — topic cited by 3+ drawers, no authoritative drawer
  LOW_CONFIDENCE_ANCHOR  — topic has drawer but confidence < 0.5, high citation count
  RECEIPT_ONLY           — appears in receipts, never written to memory
  NEEDS_REBUILD          — schema_version mismatch, excluded from analysis
```

### 2. Cluster detection -> mine-clusters.md

Groups drawers by semantic proximity using topic taxonomy and explicit links. A cluster is 3+ drawers sharing a wing + overlapping topic keywords. Names the cluster. Identifies the anchor drawer (highest confidence + freshest).

### 3. Pattern extraction -> pattern-summary.md

Finds recurring structural patterns in drawer content:
- Repeated decision rationale across drawers → candidate for a policy drawer
- Repeated external constraints → candidate for a constraints index
- Repeated failure modes → candidate for a failure-mode library

### 4. Staleness map -> staleness-map.md

Summarizes staleness distribution across the store: count per state, drawers approaching staleness threshold within 7 days, wings with highest STALE concentration, schema-version breakdown.

### 5. Dedup candidates -> dedup-candidates.md

For each curated drawer, queries ChromaDB for near-duplicates (similarity >= 0.95). Only checks curated drawers (`wing_sessions` excluded). Flags pairs for manual review.

## Backend

Reads all drawers via `get_collection().get()` from ChromaDB in batches of 2000. Does not scan flat JSON files.

```python
from _shared.memory_backend import get_collection
import os

col = get_collection()
total = col.count()

# Fetch in batches
offset = 0
while offset < total:
    r = col.get(limit=2000, offset=offset)
    ids = r.ids if hasattr(r, "ids") else r.get("ids", [])
    metas = r.metadatas if hasattr(r, "metadatas") else r.get("metadatas", [])
    docs = r.documents if hasattr(r, "documents") else r.get("documents", [])
    offset += len(ids)
    if len(ids) < 2000:
        break

# Dedup semantic query
qr = col.query(query_texts=[content[:200]], n_results=4)
# qr.ids[0], qr.distances[0] — similarity = 1.0 - distance
```

`WABBLESPEC_MEMORY_PATH` must be set (see `modules/l5/memory/rules/memory-backend-config.md`).

## Inputs

- Memory store at `WABBLESPEC_MEMORY_PATH` — all drawer content via `get_collection().get()`
- `modules/l5/memory/rules/staleness-thresholds.md` — threshold definitions
- `modules/l5/memory/rules/schema-version.md` — current schema version

## Outputs

All five files written to `.wabblespec/state/memory/mine/`:

```
.wabblespec/state/memory/mine/
  gap-map.md
  mine-clusters.md
  pattern-summary.md
  staleness-map.md
  dedup-candidates.md
```

Plus a mine receipt written to `.wabblespec/state/receipts/mine-receipt-{timestamp}.json`.

Files are overwritten on each run — always reflects current store state.

## Output contract

**mine-receipt** (`.wabblespec/state/receipts/mine-receipt-{timestamp}.json`):
```json
{
  "drawers_analyzed": "integer",
  "drawers_skipped_schema_mismatch": "integer",
  "schema_version_current": "integer",
  "gaps_found": "integer",
  "clusters_found": "integer",
  "patterns_found": "integer",
  "dedup_candidates_found": "integer",
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

`modules/l5/memory-mine/scripts/memory-mine.py` (implementation), `modules/l5/memory/rules/memory-backend-config.md` (env var setup).
