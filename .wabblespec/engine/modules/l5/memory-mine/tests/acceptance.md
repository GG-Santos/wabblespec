# Acceptance Tests — MemoryMine (L5)

## AT-MINE-01: 50-drawer gate enforced

**Given** a MemoryMine invocation when fewer than 50 drawers exist
**When** the gate check runs
**Then** MemoryMine FAILS with a gate-not-met error and produces no analysis output

---

## AT-MINE-02: Offline-only enforcement

**Given** a MemoryMine invocation
**When** any LLM call would be attempted
**Then** MemoryMine FAILS — no LLM calls are permitted; all analysis is script-driven

---

## AT-MINE-03: PID lock prevents concurrent runs

**Given** a `.mine.pid` file exists from a prior MemoryMine run
**When** a new MemoryMine invocation starts
**Then** the new invocation FAILS with a lock-conflict error and does not proceed

---

## AT-MINE-04: Schema version mismatch triggers NEEDS_REBUILD

**Given** drawers with a schema version different from the current MemoryMine schema
**When** MemoryMine encounters those drawers
**Then** they are counted in `drawers_skipped_schema_mismatch` and the run emits `NEEDS_REBUILD` status for those drawers

---

## AT-MINE-05: Five analysis outputs are written

**Given** a successful MemoryMine run (50+ drawers, no lock conflict)
**When** execution completes
**Then** the following files are written:
- `gap-map.md`
- `mine-clusters.md`
- `pattern-summary.md`
- `staleness-map.md`
- `dedup-candidates.md`

---

## AT-MINE-06: Receipt contains all required counters

**Given** a completed MemoryMine run
**Then** the receipt contains:
- `drawers_analyzed`
- `drawers_skipped_schema_mismatch`
- `gaps_found`
- `clusters_found`
- `patterns_found`
- `dedup_candidates_found`
- `staleness_critical`
- `run_duration_ms`
