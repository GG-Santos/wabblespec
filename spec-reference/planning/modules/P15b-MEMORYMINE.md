# Module Plan — MemoryMine (L5)

**Tier:** 3 — SUPPORTING
**Layer:** L5 Memory
**v5.3 origin:** MemoryMine — deep pattern mining beyond surface MemorySearch

---

## Purpose

Deep pattern mining across the full Memory evidence store. MemorySearch handles targeted retrieval (find drawers about X). MemoryMine handles exploratory discovery (find patterns, gaps, and clusters across all evidence without a specific query). Produces: pattern summaries, evidence gap maps, cluster suggestions. Writes findings to Memory. Primary input to Dream's evidence clustering task and Synth's proposal generation.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/memorymine <scope>` command
- Dream consolidation triggers MemoryMine for cluster detection (Dream delegates clustering to MemoryMine)
- Synth requests evidence mining before proposal generation
- Scheduled by Autopilot after large Memory growth (configurable threshold, default 50 new drawers)

MemoryMine never runs during active execution — same constraint as Dream.

---

## Mining Operations

### 1. Gap Detection

Scan Memory index for topics declared in spec artifacts but absent from Memory evidence:
- Read spec artifacts (P1-P4) for declared concepts, entities, requirements
- Cross-reference against EntityGraph nodes and drawer topics
- Flag: declared concepts with no supporting evidence
- Output: gap-map.md (topics needing evidence collection)

### 2. Cluster Detection

Identify drawers on related topics using entity overlap and keyword similarity:
- Group drawers sharing >= 2 EntityGraph nodes
- Score cluster coherence: high (many shared entities), medium (some), low (few)
- Flag clusters for potential consolidation — do not auto-merge
- Output: cluster candidates (passed to Dream for dream-clusters.md)

### 3. Pattern Extraction

Identify recurring structures across evidence:
- Repeated decision patterns (same trade-off appearing in multiple drawers)
- Recurring constraints (same rule cited across contexts)
- Contradiction clusters (contradicts edges in EntityGraph with multiple drawers)
- Output: pattern-summary.md

### 4. Staleness Map

Produce a staleness distribution across all Memory drawers:
- Count per staleness state (FRESH/AGING/STALE/EXPIRED/NEEDS_REVERIFICATION/SUPERSEDED)
- Identify: largest staleness concentration by topic area
- Flag: EXPIRED drawers that EntityGraph still references (orphan risk)
- Output: staleness-map.md (input to Dream for prioritized decay processing)

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Gap map | `.wabblespec/memory/gap-map.md` | Evidence gaps vs. spec declarations |
| Cluster candidates | `.wabblespec/memory/mine-clusters.md` | Passed to Dream for consolidation |
| Pattern summary | `.wabblespec/memory/pattern-summary.md` | Recurring structures for Synth |
| Staleness map | `.wabblespec/memory/staleness-map.md` | Staleness distribution for Dream |
| MemoryMine receipt | `.wabblespec/receipts/memorymine-receipt.md` | I10 compliance |

---

## Workflow

```
1. Check: active execution in progress?
   -> IF yes: abort, reschedule

2. Read Memory index (all drawer IDs, topics, staleness states)

3. Run gap detection:
   -> Read spec artifacts
   -> Cross-reference EntityGraph
   -> Write gap-map.md

4. Run cluster detection:
   -> Analyze EntityGraph node overlap per drawer pair
   -> Score clusters
   -> Write mine-clusters.md

5. Run pattern extraction:
   -> Traverse EntityGraph for recurring edges and contradictions
   -> Write pattern-summary.md

6. Run staleness map:
   -> Aggregate staleness states
   -> Flag EntityGraph orphan risks
   -> Write staleness-map.md

7. Write MemoryMine receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — never during execution |
| `scripts/gap-detector.py` | Script | Spec-vs-evidence gap analysis |
| `scripts/cluster-scorer.py` | Script | Entity overlap cluster scoring |
| `scripts/pattern-extractor.py` | Script | Recurring structure detection |
| `scripts/staleness-mapper.py` | Script | Staleness distribution aggregation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Dream | Dream delegates cluster detection to MemoryMine; reads mine-clusters.md |
| Synth | Synth reads pattern-summary.md before generating improvement proposals |
| EntityGraph | MemoryMine reads EntityGraph for cluster and orphan detection |
| Memory | MemoryMine reads all drawers; writes gap-map, clusters, pattern summary |
| Autopilot | Autopilot schedules MemoryMine runs after large Memory growth |

---

## Verification Mode

**Observation** — all four mining operations complete, all output files written, no active execution interrupted, receipt written.

---

## Receipt Extension Fields

```json
{
  "drawers_analyzed": "integer",
  "gaps_detected": "integer",
  "clusters_identified": "integer",
  "patterns_extracted": "integer",
  "expired_orphans_flagged": "integer",
  "staleness_distribution": {
    "FRESH": "integer",
    "AGING": "integer",
    "STALE": "integer",
    "EXPIRED": "integer",
    "NEEDS_REVERIFICATION": "integer",
    "SUPERSEDED": "integer"
  }
}
```
