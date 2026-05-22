# Module Plan — Memory (L5)

**Tier:** 1 — CRITICAL
**Layer:** L5 Memory
**v5.3 origin:** Memory module — expanded with staleness states and I9

---

## Purpose

Primary evidence store. All sourced facts are written here with staleness metadata. Nothing is trusted without a Memory entry and a Provenance record. Local-first, plain files. Zero external dependencies.

---

## Activation

`skill-rules.json` triggers:
- Any evidence write request from any module
- Any drawer read request
- Staleness state transition request
- Dream consolidation trigger (background, zero active-session cost)

---

## Storage Structure

```
.wabblespec/memory/
  drawers/                   <- active evidence, organized by topic
    <drawer-id>.md           <- one file per drawer
  closets/                   <- archived/expired evidence
    <drawer-id>-<timestamp>.md
  index.md                   <- drawer registry with staleness states
  tracker.json               <- Instinct pattern tracker (Evolution reads this)
```

### Drawer File Format

```markdown
# Drawer: <topic>

**id:** <drawer-id>
**staleness:** FRESH|AGING|STALE|EXPIRED|NEEDS_REVERIFICATION|SUPERSEDED
**last_verified:** <timestamp>
**source_module:** <module that wrote this>
**confidence:** 0.0-1.0

## Evidence

<evidence content>

## Provenance

- Source: <source path or URL>
- Written: <timestamp>
- Written by: <module>
- Contradiction: none|<contradicting drawer id>
```

### index.md Format

```markdown
# Memory Index

| drawer-id | topic | staleness | last_verified | confidence |
|---|---|---|---|---|
| <id> | <topic> | FRESH | <timestamp> | 0.9 |
```

---

## Staleness State Machine

```
FRESH
  -> AGING    (time threshold or project activity threshold crossed)
  -> STALE    (verification threshold crossed, no re-verification)
  -> EXPIRED  (max staleness, quarantine on access)
  -> NEEDS_REVERIFICATION  (upstream source changed — BREAKING spec change)
  -> SUPERSEDED  (newer evidence for same topic exists)

AGING
  -> STALE
  -> NEEDS_REVERIFICATION

STALE
  -> EXPIRED
  -> FRESH  (re-verified)
  -> NEEDS_REVERIFICATION

EXPIRED
  -> closets/ (archived by Forget or Dream)
  -> FRESH  (re-verified from source — only valid path back)

NEEDS_REVERIFICATION
  -> FRESH  (re-verified)
  -> EXPIRED  (not re-verified within grace period)

SUPERSEDED
  -> closets/ (archived)
```

Staleness is NOT calendar-time-based. Driven by:
- Project activity (file changes since last verification)
- Spec change events (BREAKING classification triggers NEEDS_REVERIFICATION)
- Explicit invalidation by Provenance or Dream

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Drawer files | `.wabblespec/memory/drawers/` | Evidence storage |
| index.md | `.wabblespec/memory/index.md` | Drawer registry |
| Memory write receipt | `.wabblespec/receipts/memory-write-<timestamp>.md` | I10 compliance |
| Staleness transition log | Appended to drawer file | Audit trail |

---

## Workflow

### Write Path

```
1. Receive evidence item (content, source, confidence, topic)
2. Check index.md for existing drawer on this topic
   -> IF exists: check staleness state
      -> IF SUPERSEDED or EXPIRED: write new drawer, archive old
      -> IF FRESH/AGING/STALE: update existing drawer, bump confidence
   -> IF not exists: create new drawer
3. Assign staleness state = FRESH
4. Notify Provenance (writes lineage record)
5. Update index.md
6. Write receipt
```

### Read Path (MemorySearch handles query — Memory handles retrieval)

```
1. Receive drawer-id or topic from MemorySearch
2. Read drawer file
3. Check staleness state
   -> FRESH/AGING: return content + state
   -> STALE: return content + state + STALE flag (caller must acknowledge)
   -> EXPIRED: return STALENESS_VIOLATION error, do not return content
   -> NEEDS_REVERIFICATION: return content + NEEDS_REVERIFICATION flag
   -> SUPERSEDED: redirect to superseding drawer
4. Log access to drawer file
```

### Staleness Transition Path

```
1. Receive transition event (source: spec change, Dream, Provenance, explicit)
2. Find affected drawers (by source reference or topic)
3. Apply transition rule from state machine
4. Update drawer file + index.md
5. If NEEDS_REVERIFICATION: notify all specs citing this drawer (cascade via Provenance)
6. Write transition log entry
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration: write, read, transition workflows |
| `skill-rules.json` | Required | Activation patterns, authority over drawers/ and index.md |
| `schemas/drawer.schema.json` | Schema | Drawer file structure validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |
| `scripts/staleness-checker.py` | Script | Deterministic staleness threshold evaluation |
| `rules/staleness-thresholds.md` | Rules | What triggers AGING, STALE, EXPIRED transitions |
| `rules/drawer-naming.md` | Rules | Drawer ID generation convention |

---

## Integration Points

| Module | Relationship |
|---|---|
| MemorySearch | Queries Memory for evidence. Memory retrieves, MemorySearch filters/ranks. |
| Provenance | Memory notifies Provenance on every write. Provenance owns lineage records. |
| Dream | Reads all drawers, updates staleness, clusters patterns, archives EXPIRED. |
| Forget | Moves drawers to closets/ with deletion provenance. |
| EntityGraph | Reads drawers for entity and relationship extraction. |
| MemoryMine | Reads execution receipts and writes implicit knowledge to drawers. |
| ReferenceLoad | Writes fetched external evidence as drawers. |
| Instinct | Reads tracker.json (co-located in memory/) for pattern tracking. |
| Archive | Reads memory_updates field from receipts for delivery documentation. |

---

## Verification Mode

**Observation** — drawer exists, staleness state is set, index.md is updated, Provenance notified. Verifier observes file state.

---

## Receipt Extension Fields

```json
{
  "drawer_id": "string",
  "operation": "write|read|transition|archive",
  "topic": "string",
  "staleness_before": "string",
  "staleness_after": "string",
  "provenance_notified": "boolean",
  "cascade_count": "integer — number of downstream specs flagged NEEDS_REVERIFICATION"
}
```

---

## v5.3 Mapping

| v5.3 Memory | v6.1 Memory |
|---|---|
| Evidence store, local files | Same |
| No formal staleness states | 6 staleness states with state machine |
| No staleness propagation | Cascade on BREAKING spec changes |
| No STALENESS_VIOLATION error type | STALENESS_VIOLATION added to error taxonomy |
| Drawers and closets concept | Same — closets for archived evidence |
| Nexus integration | EntityGraph replaces Nexus for relationship indexing |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Staleness thresholds | Activity-based (N file changes) vs. time-based fallback | Per-module planning |
| Max drawer size | Unlimited vs. soft limit triggering split | Per-module planning |
| Auto-archive trigger | Dream-only vs. Memory auto-archives on EXPIRED access | Per-module planning |
| tracker.json ownership | Memory owns file, Instinct reads/writes | Confirm during Instinct planning |
