# Module Plan — Dream (L5)

**Tier:** 3 — SUPPORTING
**Layer:** L5 Memory
**v5.3 origin:** Dream consolidation phase concept from v5.3 memory architecture

---

## Purpose

Background Memory consolidation. Runs at zero active-session cost — never during active execution. Clusters related evidence, decays stale patterns in tracker.json, updates EntityGraph, flags contradictions for Provenance. Keeps Memory healthy without user intervention.

---

## Activation

`skill-rules.json` triggers:
- Session end (always runs cleanup pass)
- Explicit `/dream` command
- Threshold-based: N new drawers written since last Dream run (N configurable, default 20)
- Scheduled by Autopilot after major execution waves

Dream never activates during active execution. It waits.

---

## Consolidation Tasks

### 1. Staleness Decay

Read all drawers in Memory index. Apply staleness transitions based on thresholds from `rules/staleness-thresholds.md`:

```
FRESH -> AGING     (threshold: project activity since last verification)
AGING -> STALE     (threshold: further activity or time fallback)
STALE -> EXPIRED   (threshold: max staleness limit reached)
```

Write transitions to Memory. Notify Provenance of each transition.

### 2. Pattern Decay in tracker.json

Read Instinct tracker.json. For patterns with no new observations since last Dream:
- Apply decay: `confidence_new = 0.9 * confidence_old + 0.1 * 0` (zero outcome signal)
- Patterns below confidence 0.2 AND count below 2: remove from tracker.json
- Log pruned patterns to Dream receipt

### 3. Evidence Clustering

Identify drawers on related topics (by entity overlap from EntityGraph, by keyword similarity). Flag clusters for potential consolidation — do not auto-merge. Write cluster suggestions to `.wabblespec/memory/dream-clusters.md` for human or MemoryMine review.

### 4. EntityGraph Update

After staleness transitions: remove EntityGraph nodes whose only drawer_refs are now EXPIRED. Recalculate confidence scores for remaining nodes. Remove orphaned edges.

### 5. Contradiction Resolution

Read Provenance contradictions.md. For each flagged contradiction:
- Check if one drawer is now EXPIRED or SUPERSEDED: auto-resolve (remove contradiction flag)
- If both still FRESH: leave flagged, increment age counter
- If age counter > threshold: escalate to human (write to `.wabblespec/memory/unresolved-contradictions.md`)

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Updated Memory drawers | `.wabblespec/memory/drawers/` | Staleness transitions applied |
| Updated tracker.json | `.wabblespec/memory/tracker.json` | Decayed patterns, pruned entries |
| Dream clusters | `.wabblespec/memory/dream-clusters.md` | Cluster suggestions |
| Unresolved contradictions | `.wabblespec/memory/unresolved-contradictions.md` | Escalated contradictions |
| Dream receipt | `.wabblespec/receipts/dream-receipt.md` | I10 compliance |

---

## Workflow

```
1. Check: is active execution in progress?
   -> IF yes: abort, reschedule for session end
   -> IF no: proceed

2. Read Memory index.md (all drawers + staleness states)

3. Apply staleness decay (task 1)

4. Read tracker.json, apply pattern decay (task 2)

5. Cluster evidence by entity overlap + keyword similarity (task 3)

6. Trigger EntityGraph cleanup and confidence update (task 4)

7. Process contradictions from Provenance (task 5)

8. Write dream-clusters.md

9. Write unresolved-contradictions.md if any

10. Write Dream receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — deferred, never during execution |
| `scripts/staleness-decay.py` | Script | Deterministic staleness threshold evaluation |
| `scripts/pattern-decay.py` | Script | tracker.json EMA decay computation |
| `scripts/cluster-detector.py` | Script | Entity overlap and keyword similarity clustering |
| `rules/staleness-thresholds.md` | Rules | Thresholds for each staleness transition |
| `rules/decay-policy.md` | Rules | Pattern decay rate, pruning thresholds |
| `rules/contradiction-escalation.md` | Rules | Age threshold for human escalation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | Dream reads all drawers, writes staleness transitions back |
| Provenance | Dream reads contradictions.md, notifies Provenance of resolved contradictions |
| EntityGraph | Dream triggers EntityGraph cleanup after staleness transitions |
| Instinct | Dream decays tracker.json patterns — shared file, Dream writes, Instinct reads |
| Autopilot | Autopilot schedules Dream after major waves |

---

## Verification Mode

**Observation** — Dream receipt exists, staleness transitions logged, tracker.json updated, EntityGraph notified, no active execution was interrupted.

---

## Receipt Extension Fields

```json
{
  "drawers_processed": "integer",
  "staleness_transitions": "integer",
  "patterns_decayed": "integer",
  "patterns_pruned": "integer",
  "clusters_identified": "integer",
  "contradictions_resolved": "integer",
  "contradictions_escalated": "integer",
  "entitygraph_nodes_removed": "integer"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Dream trigger threshold | 20 new drawers (proposed) vs. configurable | Per-module planning |
| Auto-merge clusters | Never (current — suggest only) vs. merge when confidence > threshold | Per-module planning |
| Contradiction age threshold | 3 Dream runs (proposed) vs. configurable | Per-module planning |
