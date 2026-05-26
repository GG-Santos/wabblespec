# Acceptance Tests — Dream (L5)

## AT-DREAM-01: Dream runs dream.py — zero LLM

**Given** a Dream invocation
**When** execution occurs
**Then** no LLM call is made; all processing is performed by `dream.py` script

---

## AT-DREAM-02: EMA confidence decay formula

**Given** a drawer with `old_confidence` value C and current `base_freshness` F
**When** Dream processes the drawer
**Then** `new_confidence = C * 0.9 + F * 0.1` is applied exactly

---

## AT-DREAM-03: base_freshness values by staleness state

**Given** drawers with staleness states FRESH, AGING, STALE, EXPIRED
**When** Dream computes base_freshness
**Then**:
- FRESH -> 1.0
- AGING -> 0.7
- STALE -> 0.3
- EXPIRED -> 0.0

---

## AT-DREAM-04: PID lock prevents concurrent runs

**Given** a `.dream.pid` file exists
**When** a new Dream invocation starts
**Then** the new invocation FAILS with a lock-conflict error

---

## AT-DREAM-05: State transitions are NOT performed by Dream

**Given** a drawer whose staleness state should change (e.g., from AGING to STALE)
**When** Dream runs
**Then** Dream does not perform the transition — staleness-checker.py is responsible for all state transitions, not Dream

---

## AT-DREAM-06: Three output files written each run

**Given** a successful Dream run
**When** execution completes
**Then** the following files are updated:
- `gap-map.md`
- `staleness-map.md`
- `dream-log.json`

---

## AT-DREAM-07: Validation gate requires 10 runs

**Given** fewer than 10 entries in `dream-log.json`
**When** the Dream validation gate is checked
**Then** the gate is NOT MET and the status reflects this deficit

---

## AT-DREAM-08: Stop hook and PreCompact hook are registered

**Given** Dream is active in a session
**When** session ends or context compaction triggers
**Then** the registered Stop hook and PreCompact hook fire — Dream does not depend on manual invocation for these events
