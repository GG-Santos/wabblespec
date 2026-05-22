# WabbleSpec v6.1 — Memory

The Memory layer (L5) is WabbleSpec's evidence store. All sourced facts are written here with staleness metadata, provenance records, and entity relationships. Nothing is trusted without a Memory entry backed by a Provenance record. Local-first, plain files. Zero external dependencies.

Memory is not a cache. It is the framework's long-term evidence infrastructure — structured, verifiable, and designed to degrade gracefully as evidence ages.

---

## 1. Design Principles

**Evidence-first.** Every source-derived claim must point to a drawer ID with provenance. Unsupported claims are marked UNVERIFIED. There is no assertion without an anchor.

**Staleness is activity-based, not calendar-based.** A drawer does not expire because time passed — it expires because project activity since its last verification crossed a threshold. A quiet project with old drawers may have perfectly valid FRESH evidence. An active project with recent drawers may have STALE evidence if core specs changed.

**Provenance is append-only.** The ledger.md file is never edited — only appended. Deletion records are permanent entries in the ledger, not erasures. Even after a drawer is removed, evidence of its existence remains.

**Dream consolidates. Forget removes.** These are distinct operations with distinct authority. Dream decays staleness and clusters evidence passively. Forget executes controlled deletion with audit trail. No module conflates these roles.

**MemoryMine explores. MemorySearch retrieves.** MemoryMine is pattern discovery across the full evidence store (no specific query). MemorySearch is targeted retrieval by topic, entity, or relationship. These are separate modules with separate authority.

---

## 2. Storage Structure

```
.wabblespec/memory/
  index.md                   ← drawer registry with staleness states (the source of truth for what exists)
  tracker.json               ← Instinct pattern tracker (Evolution reads this; Dream decays it)
  dream-clusters.md          ← cluster suggestions from Dream/MemoryMine (suggestions only, not auto-merged)
  unresolved-contradictions.md ← contradictions flagged by Dream that require human review
  drawers/                   ← active evidence files
    <drawer-id>.md           ← one file per drawer
  closets/                   ← archived/expired evidence (moved here by Forget, not deleted)
    <drawer-id>-<timestamp>.md
  provenance/
    ledger.md                ← append-only full lineage log (never edited — only appended)
    index.json               ← drawer-id to provenance record map
    contradictions.md        ← active contradiction list
  entity-graph/
    nodes.json               ← entity registry
    edges.json               ← relationship registry
    index.md                 ← human-readable graph summary
```

**Rule:** `drawers/` contains active evidence. `closets/` contains archived evidence. Forget moves files between them — nothing is hard-deleted from the filesystem without a Provenance record.

**Rule:** `ledger.md` is append-only. No line is ever removed. Deletion records written by Forget are permanent entries.

---

## 3. Data Contracts

### 3.1 Drawer File Format

```markdown
# Drawer: <topic>

**id:** <drawer-id>
**staleness:** FRESH|AGING|STALE|EXPIRED|NEEDS_REVERIFICATION|SUPERSEDED
**last_verified:** <ISO 8601 timestamp>
**source_module:** <module that wrote this>
**confidence:** 0.0-1.0

## Evidence

<evidence content — sourced, specific, not vague>

## Provenance

- Source: <source file path, URL, or internal computation reference>
- Written: <ISO 8601 timestamp>
- Written by: <module name>
- Contradiction: none|<contradicting drawer id>
- Superseded by: none|<superseding drawer id>
```

---

### 3.2 Index Format

```markdown
# Memory Index

| drawer-id | topic | staleness | last_verified | confidence | source_module |
|---|---|---|---|---|---|
| <id> | <topic> | FRESH | <timestamp> | 0.9 | <module> |
```

Index is kept compact — one row per drawer. Full content lives in the drawer file.

---

### 3.3 Provenance Record

```json
{
  "drawer_id": "string",
  "topic": "string",
  "source": {
    "path": "string",
    "type": "framework-reference|project-file|external-doc|internal-computation",
    "trust_level": "HIGH|MEDIUM|LOW"
  },
  "written_by": "module name",
  "written_at": "ISO 8601",
  "confidence": 0.0,
  "staleness_state": "FRESH|AGING|STALE|EXPIRED|NEEDS_REVERIFICATION|SUPERSEDED",
  "last_verified": "ISO 8601",
  "superseded_by": "drawer_id or null",
  "contradiction_with": ["drawer_id"],
  "cited_by": ["spec artifact paths"],
  "deletion": {
    "deleted": false,
    "deleted_at": null,
    "deleted_by": null,
    "reason": null,
    "archived_to": null
  }
}
```

---

### 3.4 EntityGraph Node

```json
{
  "id": "entity-id",
  "name": "entity name",
  "type": "module|file|person|service|concept|standard|technology",
  "drawer_refs": ["drawer-id-1", "drawer-id-2"],
  "first_seen": "ISO 8601",
  "last_updated": "ISO 8601",
  "confidence": 0.0
}
```

---

### 3.5 EntityGraph Edge

```json
{
  "id": "edge-id",
  "from": "entity-id",
  "to": "entity-id",
  "relationship": "depends-on|implements|calls|extends|replaces|contradicts|cites",
  "drawer_refs": ["drawer-id"],
  "confidence": 0.0,
  "first_seen": "ISO 8601"
}
```

---

### 3.6 MemorySearch Result Format

```markdown
## MemorySearch Results

**query:** <query text>
**query_type:** topic|entity|relationship|recency|staleness|full-text
**timestamp:** <when queried>

| rank | drawer_id | topic | staleness | confidence | snippet |
|---|---|---|---|---|---|
| 1 | <id> | <topic> | FRESH | 0.9 | <first 100 chars> |
```

---

## 4. Staleness State Machine

Staleness is **not** calendar-time-based. It is driven by:
- Project activity (file changes since last verification)
- Spec change events (BREAKING classification triggers NEEDS_REVERIFICATION)
- Explicit invalidation by Provenance or Dream

```
FRESH
  -> AGING              activity threshold crossed, no re-verification
  -> NEEDS_REVERIFICATION  BREAKING spec change in a spec that cited this drawer

AGING
  -> STALE              further activity or time fallback threshold
  -> NEEDS_REVERIFICATION  BREAKING spec change

STALE
  -> EXPIRED            max staleness limit reached
  -> FRESH              re-verified from source (valid path back)
  -> NEEDS_REVERIFICATION  BREAKING spec change

EXPIRED
  -> closets/           archived by Forget (with Provenance record) or Dream (suggestion)
  -> FRESH              re-verified from source (only valid path back from EXPIRED)

NEEDS_REVERIFICATION
  -> FRESH              re-verified
  -> EXPIRED            not re-verified within grace period

SUPERSEDED
  -> closets/           archived (newer drawer exists on same topic)
```

### Staleness in MemorySearch

| State | MemorySearch behavior |
|---|---|
| FRESH | Return normally |
| AGING | Return with AGING flag |
| STALE | Return with STALE flag — caller must acknowledge before using |
| EXPIRED | Exclude from results. STALENESS_VIOLATION if explicitly requested. |
| NEEDS_REVERIFICATION | Return with flag — surface for human check |
| SUPERSEDED | Redirect to superseding drawer automatically |

---

## 5. Module Inventory

| Module | Tier | Role |
|---|---|---|
| Memory | 1 — CRITICAL | Primary evidence store coordinator. Write path, read path, staleness state machine. |
| MemorySearch | 2 — CORE | Targeted retrieval by topic, entity, or relationship. Runs in every Research phase. |
| EntityGraph | 3 — SUPPORTING | Entity and relationship index. Deterministic pattern extraction. Enables relationship queries. |
| Provenance | 2 — CORE | Source lineage, cascade computation, contradiction detection, deletion records. |
| Dream | 3 — SUPPORTING | Background consolidation. Staleness decay, pattern decay, clustering. Never during execution. |
| MemoryMine | 3 — SUPPORTING | Deep pattern mining. Gap detection, cluster scoring, pattern extraction, staleness distribution. |
| Forget | 3 — SUPPORTING | Controlled deletion. Sole authorized deleter. Provenance record before every removal. |

---

## 6. Module Deep Definitions

### 6.1 Memory

**Layer:** L5  
**Tier:** 1 — CRITICAL  
**v5.3 origin:** Memory module — expanded with staleness states and Evidence Expiry invariant (I9)

**Purpose:** Primary evidence store. Owns the write path, read path, and staleness state machine. Coordinates all other L5 modules.

---

#### Write Path

```
1. Receive evidence item (content, source, confidence, topic)
2. Check index.md for existing drawer on this topic
   -> IF exists: check staleness state
      -> IF SUPERSEDED or EXPIRED: write new drawer, archive old to closets/
      -> IF FRESH/AGING/STALE: update existing drawer, bump confidence
   -> IF not exists: create new drawer in drawers/
3. Assign staleness state = FRESH
4. Notify Provenance (writes lineage record to provenance/index.json and ledger.md)
5. Notify EntityGraph (scans new drawer for entity extraction)
6. Update index.md
7. Write receipt
```

---

#### Read Path

```
1. Receive drawer-id or topic from MemorySearch
2. Read drawer file from drawers/
3. Check staleness state
   -> FRESH/AGING: return content + state
   -> STALE: return content + STALE flag (caller must acknowledge)
   -> EXPIRED: return STALENESS_VIOLATION error, do not return content
   -> NEEDS_REVERIFICATION: return content + NEEDS_REVERIFICATION flag
   -> SUPERSEDED: redirect to superseding drawer
4. Log access to drawer file
```

---

#### Staleness Transition Path

```
1. Receive transition event (source: spec change, Dream, Provenance, explicit)
2. Find affected drawers (by source reference or topic)
3. Apply transition rule from state machine
4. Update drawer file staleness field
5. Update index.md
6. IF transition to NEEDS_REVERIFICATION:
   -> Notify Provenance
   -> Provenance cascades to all specs in cited_by
7. Write transition log entry
```

---

#### Sub-Components

| Component | Purpose |
|---|---|
| `SKILL.md` | Orchestration: write, read, transition workflows |
| `skill-rules.json` | Activation patterns, authority over `drawers/` and `index.md` |
| `schemas/drawer.schema.json` | Drawer file structure validation |
| `scripts/staleness-checker.py` | Deterministic staleness threshold evaluation |
| `rules/staleness-thresholds.md` | What triggers AGING, STALE, EXPIRED transitions |
| `rules/drawer-naming.md` | Drawer ID generation convention |

---

#### Integration Points

| Module | Relationship |
|---|---|
| MemorySearch | Queries Memory for evidence. Memory retrieves; MemorySearch filters and ranks. |
| Provenance | Memory notifies Provenance on every write and delete. |
| Dream | Dream reads all drawers, writes staleness transitions back. |
| Forget | Moves drawers from `drawers/` to `closets/` with deletion provenance. |
| EntityGraph | Notified on every write to extract entities. |
| MemoryMine | Reads drawers for pattern mining. Writes mining outputs. |
| ReferenceLoad | Writes fetched external evidence as drawers. |
| Instinct | Reads `tracker.json` co-located in memory/. |

**Verification Mode:** Observation — drawer exists, staleness state set, index.md updated, Provenance notified.

---

### 6.2 MemorySearch

**Layer:** L5  
**Tier:** 2 — CORE  
**v5.3 origin:** Memory module search behavior — formalized as standalone module

**Purpose:** Query interface for the evidence store. Finds evidence by topic, entity, or relationship. Returns ranked results with staleness states. Runs in every Research phase of the three-phase model.

---

#### Query Types

| Query Type | Input | Returns |
|---|---|---|
| Topic | keyword or phrase | Drawers matching topic, ranked by relevance + confidence |
| Entity | entity name | Drawers referencing that entity, via EntityGraph |
| Relationship | entity A + relationship + entity B | Drawers confirming or denying relationship |
| Recency | timestamp range | Drawers written/updated in period |
| Staleness | staleness state filter | Drawers in specified state (e.g., all NEEDS_REVERIFICATION) |
| Full-text | arbitrary text | Drawers containing matching content |

---

#### Retrieval Workflow

```
1. Receive query (type + parameters)
2. Read Memory index.md for drawer list + staleness states
3. Apply staleness filter:
   -> Exclude EXPIRED (emit STALENESS_VIOLATION if explicitly requested)
   -> Flag STALE and NEEDS_REVERIFICATION in results
4. Execute query against drawer files
5. Rank results:
   -> Primary: confidence score
   -> Secondary: staleness (FRESH > AGING > STALE)
   -> Tertiary: recency (newer ranks higher)
6. Return ranked result list with staleness flags
7. Write MemorySearch receipt
```

---

#### Sub-Components

| Component | Purpose |
|---|---|
| `SKILL.md` | Orchestration |
| `skill-rules.json` | Activation — runs in every Research phase; no write authority |
| `scripts/search-index.py` | Deterministic full-text search across drawer files |
| `schemas/search-result.schema.json` | Result format validation |

---

#### Integration Points

| Module | Relationship |
|---|---|
| Memory | Reads from Memory drawers. No write authority. |
| EntityGraph | Delegates entity and relationship queries to EntityGraph |
| Research phase | Every Research phase runs MemorySearch before Plan begins |
| Specify | Reads MemorySearch results to populate spec with prior evidence |
| Provenance | Reads provenance records for trust metadata in results |

**Verification Mode:** Observation — results returned, staleness states on all results, EXPIRED excluded, receipt written.

---

### 6.3 EntityGraph

**Layer:** L5  
**Tier:** 3 — SUPPORTING  
**v5.3 origin:** Nexus (partial) — relationship index formalized

**Purpose:** Track entities and relationships across the project lifetime. Enables relationship-based evidence retrieval. Entities are extracted from Memory drawer content by deterministic pattern matching — not LLM inference.

---

#### Entity Extraction

EntityGraph extracts entities from drawer content using deterministic pattern matching:

| Entity type | Detection signals |
|---|---|
| module | Module name patterns, SKILL.md references |
| file | File paths (`src/`, `.ts`, `.py`, `.go`, etc.) |
| service | Service names, API endpoints, external integrations |
| concept | Key terms from spec artifacts |
| standard | Named standards (OWASP, EARS, semver, WCAG, etc.) |
| technology | Framework/language names from project detection |

Low-confidence entities are included with `confidence < 0.5` — not excluded. Exclusion requires human confirmation via Dream or Forget.

---

#### Graph Operations

**On Memory write:**
```
1. Read new drawer content
2. Extract entities using pattern matching
3. For each entity:
   -> Check nodes.json: exists? update drawer_refs + confidence
   -> Not exists? create new node
4. Detect relationships between entities in same drawer
5. Update edges.json
6. Update index.md
```

**On MemorySearch entity query:**
```
1. Find entity node in nodes.json
2. Return all drawer_refs for that entity
3. Traverse edges for related entities (configurable depth)
4. Return entity + related entities + drawer refs
```

**On Dream consolidation:**
```
1. Remove nodes with no drawer_refs (orphaned)
2. Update confidence scores based on co-occurrence
3. Flag contradicting relationships (contradicts edges)
```

---

#### Integration Points

| Module | Relationship |
|---|---|
| Memory | Notified on every Memory write to scan new drawers |
| MemorySearch | Delegates entity and relationship queries to EntityGraph |
| Dream | Triggers EntityGraph cleanup after staleness transitions |
| Provenance | Reads Provenance records for entity source trust |
| Explore | Reads EntityGraph for project-map relationship context |

**Verification Mode:** Observation — nodes.json and edges.json exist and parse, entity extraction attempted for all drawers, orphans cleaned by Dream.

---

### 6.4 Provenance

**Layer:** L5  
**Tier:** 2 — CORE  
**v5.3 origin:** Memory subsystem (embedded) — formalized as standalone module

**Purpose:** Record and maintain evidence lineage. Every Memory drawer has a Provenance record. Provenance is the trust infrastructure for I9 (Evidence Has Expiry). Without Provenance, staleness cascade has no target list.

**Critical invariant:** `ledger.md` is append-only (I7). No entry is ever removed — only appended.

---

#### Core Responsibilities

**Lineage Recording:** On every Memory write, Provenance receives source, module, confidence, timestamp. Creates or updates provenance record. Appends to ledger.md.

**Cascade Computation:** When a spec changes with BREAKING classification:
```
1. Query index.json for all drawers cited by the changed spec (via cited_by list)
2. For each affected drawer:
   a. Transition staleness to NEEDS_REVERIFICATION (via Memory)
   b. Find all other specs in cited_by for that drawer
   c. Mark those specs NEEDS_REVERIFICATION (notify Specify)
3. Log cascade to ledger.md
```

**Contradiction Detection:** When a new drawer is written on a topic that already has a FRESH/AGING drawer:
- Flag potential contradiction
- Write to contradictions.md with both drawer IDs
- Set `contradiction_with` on both records
- Surface to Dream for resolution during consolidation

**Deletion Provenance:** When Forget archives a drawer:
- Record deletion event in provenance record
- Record reason, timestamp, requesting module
- Mark `archived_to` path
- Trigger NEEDS_REVERIFICATION cascade for all specs in `cited_by`

**Citation Tracking:** When Specify or any spec-writing module references a drawer, Provenance records the spec artifact path in `cited_by`. This enables cascade when the drawer expires.

---

#### Integration Points

| Module | Relationship |
|---|---|
| Memory | Notified on every write/delete. Triggers staleness transitions back to Memory. |
| Forget | Forget notifies Provenance before archiving. Provenance records deletion. |
| Dream | Reads contradictions.md during consolidation to resolve or flag. |
| Specify | Provenance tracks which drawers are cited by which specs. |
| Verifier | Can query Provenance to confirm evidence trust level before gate check. |

**Verification Mode:** Audit — every Memory drawer has a provenance record. Ledger is append-only. All `cited_by` relationships are bidirectional. No contradiction older than grace period without Dream resolution.

---

### 6.5 Dream

**Layer:** L5  
**Tier:** 3 — SUPPORTING  
**v5.3 origin:** Dream consolidation concept from v5.3 memory architecture

**Purpose:** Background Memory consolidation. Runs at zero active-session cost — never during active execution. Keeps Memory healthy without user intervention.

**Critical constraint:** Dream NEVER runs during active execution. If triggered during execution, it aborts and reschedules for session end.

---

#### Consolidation Tasks

**1. Staleness Decay**

Read all drawers in Memory index. Apply staleness transitions:
```
FRESH -> AGING     activity threshold crossed
AGING -> STALE     further activity or time fallback
STALE -> EXPIRED   max staleness limit reached
```
Write transitions to Memory. Notify Provenance of each transition.

**2. Pattern Decay in tracker.json**

Read Instinct tracker.json. For patterns with no new observations since last Dream:
```
confidence_new = 0.9 * confidence_old + 0.1 * 0  (zero outcome signal = decay)
```
Patterns below confidence 0.2 AND count below 2: prune from tracker.json. Log pruned patterns to Dream receipt.

**3. Evidence Clustering**

Identify drawers on related topics by entity overlap (EntityGraph) and keyword similarity. Flag clusters for potential consolidation — do NOT auto-merge. Write cluster suggestions to `dream-clusters.md` for MemoryMine or human review.

**4. EntityGraph Update**

After staleness transitions: remove nodes whose only `drawer_refs` are now EXPIRED. Recalculate confidence scores for remaining nodes. Remove orphaned edges.

**5. Contradiction Resolution**

Read `provenance/contradictions.md`. For each flagged contradiction:
- One drawer now EXPIRED or SUPERSEDED → auto-resolve
- Both still FRESH and age counter exceeded threshold → escalate to `unresolved-contradictions.md`

---

#### Dream Workflow

```
1. Check: active execution in progress?
   -> IF yes: abort, reschedule for session end
   -> IF no: proceed

2. Read Memory index.md (all drawers + staleness states)

3. Apply staleness decay (task 1)

4. Read tracker.json, apply pattern decay (task 2)

5. Cluster evidence by entity overlap + keyword similarity (task 3)

6. Trigger EntityGraph cleanup (task 4)

7. Process contradictions from Provenance (task 5)

8. Write dream-clusters.md

9. Write unresolved-contradictions.md if any

10. Write Dream receipt
```

---

#### Integration Points

| Module | Relationship |
|---|---|
| Memory | Reads all drawers, writes staleness transitions |
| Provenance | Reads contradictions.md, notifies Provenance of resolved contradictions |
| EntityGraph | Triggers cleanup after staleness transitions |
| Instinct | Decays tracker.json patterns — shared file |
| Autopilot | Autopilot schedules Dream after major execution waves |

**Verification Mode:** Observation — Dream receipt exists, staleness transitions logged, tracker.json updated, EntityGraph notified, no active execution interrupted.

---

### 6.6 MemoryMine

**Layer:** L5  
**Tier:** 3 — SUPPORTING  
**v5.3 origin:** New in v6.1 — deep pattern mining beyond surface MemorySearch

**Purpose:** Deep pattern mining across the full evidence store. MemorySearch handles targeted retrieval (find drawers about X). MemoryMine handles exploratory discovery (find patterns, gaps, and clusters across all evidence without a specific query).

**Critical constraint:** Never runs during active execution — same constraint as Dream.

---

#### Mining Operations

**Gap Detection:** Cross-reference spec artifacts (P1-P4) against EntityGraph nodes and drawer topics. Flag declared concepts with no supporting evidence. Output: `gap-map.md`.

**Cluster Detection:** Identify drawers sharing ≥ 2 EntityGraph nodes. Score cluster coherence (high/medium/low). Flag for potential consolidation — do NOT auto-merge. Output: `mine-clusters.md` (passed to Dream).

**Pattern Extraction:** Identify recurring structures:
- Repeated decision patterns (same trade-off in multiple drawers)
- Recurring constraints (same rule cited across contexts)
- Contradiction clusters (contradicts edges in EntityGraph with multiple drawers)
Output: `pattern-summary.md`.

**Staleness Map:** Aggregate staleness states across all drawers. Identify EXPIRED drawers still referenced by EntityGraph nodes (orphan risk). Output: `staleness-map.md`.

---

#### Outputs

| Output | Location | Purpose |
|---|---|---|
| Gap map | `.wabblespec/memory/gap-map.md` | Evidence gaps vs. spec declarations |
| Cluster candidates | `.wabblespec/memory/mine-clusters.md` | Passed to Dream for consolidation |
| Pattern summary | `.wabblespec/memory/pattern-summary.md` | Recurring structures for Synth |
| Staleness map | `.wabblespec/memory/staleness-map.md` | Staleness distribution for Dream |

---

#### Integration Points

| Module | Relationship |
|---|---|
| Dream | Dream delegates cluster detection to MemoryMine; reads mine-clusters.md |
| Synth | Synth reads pattern-summary.md before generating improvement proposals |
| EntityGraph | MemoryMine reads EntityGraph for cluster and orphan detection |
| Autopilot | Autopilot schedules MemoryMine runs after large Memory growth (default: 50 new drawers) |

**Verification Mode:** Observation — all four mining operations complete, all output files written, no active execution interrupted, receipt written.

---

### 6.7 Forget

**Layer:** L5  
**Tier:** 3 — SUPPORTING  
**v5.3 origin:** Memory deletion concept — formalized with Provenance integration

**Purpose:** Controlled deletion of Memory drawers. Forget is the ONLY module authorized to delete drawers. Dream decays staleness — Forget removes. Every deletion is recorded in Provenance before the file is touched. Deleted drawers are not silently purged — a deletion record in `ledger.md` persists permanently even after the drawer content is gone.

---

#### Deletion Types

| Type | Trigger | Confirmation required |
|---|---|---|
| Single drawer | Explicit `/forget <drawer-id>` | Confirmation prompt (show drawer summary before delete) |
| Bulk (EXPIRED) | Dream suggestion or Archive --sweep | Attestation required |
| Bulk (topic scope) | Explicit `/forget --scope <filter>` | Attestation required |
| Compliance (GDPR) | Legal request + explicit command | Attestation + documented reason |

---

#### Deletion Process

Forget does NOT hard-delete without trace. Process for every deletion:

```
1. Write Provenance deletion record (drawer ID, reason, timestamp, authorized by)
2. Move drawer file from drawers/ to closets/ (not deleted from filesystem)
3. Remove drawer from Memory index.md
4. Notify EntityGraph: remove drawer_refs for deleted drawer, trigger orphan check
5. Notify Provenance: cascade — any drawer citing deleted drawer flagged NEEDS_REVERIFICATION
6. Write Forget receipt with list of deleted drawer IDs
```

---

#### Bulk Deletion Guard

Before bulk deletion executes:
```
1. Display: count of drawers to be deleted, staleness breakdown, topic distribution
2. Require Attestation
3. Write Provenance deletion record for each drawer
4. Execute deletion (move to closets/)
5. Write Forget receipt with full list of deleted drawer IDs
```

No bulk deletion proceeds without showing scope summary first.

---

#### Compliance Deletion (GDPR / Right to Erasure)

When compliance deletion is requested:
- Reason declared: `compliance` with legal basis noted
- Scope: all drawers referencing the data subject
- EntityGraph: all nodes referencing deleted drawers removed
- Provenance: deletion record notes legal basis (not the deleted content)
- Receipt: flagged as compliance deletion for audit trail

---

#### Integration Points

| Module | Relationship |
|---|---|
| Memory | Forget is sole authorized deleter of Memory drawers |
| Provenance | Forget writes deletion record to `ledger.md` before every deletion |
| EntityGraph | Forget notifies EntityGraph to remove drawer_refs and check orphans |
| Dream | Dream flags EXPIRED drawers as Forget candidates (suggestion only) |
| Archive | Archive --sweep delegates EXPIRED drawer removal to Forget |
| MemoryMine | MemoryMine identifies EXPIRED orphan risks; Forget executes removal |

**Verification Mode:** Attestation — Attestation required for bulk deletions, Provenance deletion record written before file moved, EntityGraph notified, receipt written with full deletion list.

---

## 7. Memory Workflows in Practice

### 7.1 Before Repeating Research

Every Research phase runs MemorySearch first. Before any module re-derives prior decisions:

```
1. Run MemorySearch with topic or entity query
2. Check staleness states on results
3. IF results are FRESH/AGING: use as evidence, cite drawer IDs
4. IF results are STALE: use with explicit STALE acknowledgment
5. IF results are EXPIRED: do not use — run re-verification or flag as gap
6. IF no results: evidence gap — new research needed
```

### 7.2 After Major Decisions

After any decision that future modules will need:

```
1. Write evidence to Memory (drawer file)
2. Memory notifies Provenance (lineage recorded)
3. Memory notifies EntityGraph (entities extracted)
4. Memory receipt written
5. Downstream modules can now retrieve via MemorySearch
```

### 7.3 After Spec Change (BREAKING)

When Specify writes a BREAKING spec change:

```
1. Provenance receives change event with spec path
2. Provenance queries index.json for drawers cited_by that spec
3. Each affected drawer: staleness → NEEDS_REVERIFICATION (via Memory)
4. Each spec cited by those drawers: also flagged NEEDS_REVERIFICATION
5. Cascade logged to ledger.md
6. Reviewer or human decision required before using affected evidence
```

### 7.4 After Large Memory Growth

When 50+ new drawers have been written since last MemoryMine run:

```
1. Autopilot schedules MemoryMine (if not during active execution)
2. MemoryMine runs: gap detection, cluster detection, pattern extraction, staleness map
3. dream-clusters.md and mine-clusters.md available for Dream
4. pattern-summary.md available for Synth
5. staleness-map.md available for Dream prioritized processing
```

### 7.5 Session End Consolidation

At session end or explicit `/dream` trigger (not during execution):

```
1. Dream checks: active execution? → abort if yes
2. Dream: staleness decay for all drawers
3. Dream: pattern decay in tracker.json
4. Dream: cluster evidence
5. Dream: EntityGraph cleanup
6. Dream: contradiction resolution
7. Dream receipt written
```

---

## 8. Invariants Enforced

| Invariant | Memory enforcement |
|---|---|
| I7 — Provenance is Append-Only | `ledger.md` never has lines removed. Deletion records are permanent. |
| I9 — Evidence Has Expiry | EXPIRED drawers return STALENESS_VIOLATION. Never silently used. |
| I10 — Receipts as Operational Artifacts | Every Memory operation writes a receipt (write, read, search, dream, forget). |

---

## 9. Error Types Emitted

| Error | Trigger |
|---|---|
| STALENESS_VIOLATION | Caller requested EXPIRED drawer explicitly |
| SPEC_VIOLATION | Module attempted to write to drawers/ without going through Memory write path |
| DEPENDENCY | Provenance was not reachable during write (blocks write) |
| HARD | ledger.md is corrupt or missing |

---

## 10. Receipt Extension Fields

**Memory write receipt:**
```json
{
  "drawer_id": "string",
  "operation": "write|read|transition|archive",
  "topic": "string",
  "staleness_before": "string",
  "staleness_after": "string",
  "provenance_notified": "boolean",
  "entitygraph_notified": "boolean",
  "cascade_count": "integer"
}
```

**MemorySearch receipt:**
```json
{
  "query_type": "string",
  "results_returned": "integer",
  "results_excluded_expired": "integer",
  "results_flagged_stale": "integer",
  "results_flagged_needs_reverification": "integer",
  "entity_graph_traversed": "boolean"
}
```

**Dream receipt:**
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

**MemoryMine receipt:**
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

**Forget receipt:**
```json
{
  "deletion_type": "single|bulk|compliance",
  "drawers_deleted": "integer",
  "deleted_ids": ["string"],
  "provenance_records_written": "integer",
  "entitygraph_notified": "boolean",
  "cascaded_reverification": "integer",
  "attestation_received": "boolean",
  "compliance_reason": "string"
}
```

---

## 11. v5.3 Mapping

| v5.3 | v6.1 |
|---|---|
| Memory (evidence store) | Memory (expanded with staleness states and Provenance integration) |
| Memory search behavior | MemorySearch (standalone module) |
| Nexus (partial) | EntityGraph (standalone, deterministic extraction) |
| Embedded provenance | Provenance (standalone, append-only ledger, cascade computation) |
| Dream consolidation | Dream (expanded with EMA decay, formal contradiction resolution) |
| Memory deletion | Forget (standalone, Attestation for bulk, permanent deletion record) |
| No deep mining | MemoryMine (new — gap detection, cluster scoring, pattern extraction, staleness map) |
| No formal staleness states | 6 states: FRESH, AGING, STALE, EXPIRED, NEEDS_REVERIFICATION, SUPERSEDED |
| No STALENESS_VIOLATION error | STALENESS_VIOLATION added to error taxonomy |
| Activity-based staleness concept | Formalized with threshold rules and state machine |
