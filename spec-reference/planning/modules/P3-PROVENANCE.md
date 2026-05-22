# Module Plan — Provenance (L5)

**Tier:** 2 — CORE
**Layer:** L5 Memory
**v5.3 origin:** Memory subsystem (provenance was embedded) — formalized as standalone module in v6.1

---

## Purpose

Record and maintain evidence lineage. Every piece of evidence in Memory has a Provenance record: source path, confidence, freshness, contradiction status, and deletion path. Provenance is the trust infrastructure for I9 (Evidence Has Expiry). Without Provenance, staleness propagation has no target list.

---

## Activation

`skill-rules.json` triggers:
- Any Memory write (notified by Memory module)
- Any Memory deletion (Forget notifies Provenance)
- BREAKING spec change event (triggers cascade computation)
- Explicit provenance query from any module

---

## Storage Structure

```
.wabblespec/memory/provenance/
  ledger.md                  <- full lineage log (append-only)
  index.json                 <- drawer-id to provenance record map
  contradictions.md          <- active contradiction list
```

### Provenance Record (per drawer)

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
  "written_at": "timestamp",
  "confidence": 0.0,
  "staleness_state": "FRESH|AGING|STALE|EXPIRED|NEEDS_REVERIFICATION|SUPERSEDED",
  "last_verified": "timestamp",
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

## Core Responsibilities

### 1. Lineage Recording

On every Memory write: Provenance receives source, module, confidence, timestamp. Creates or updates provenance record. Appends to ledger.md.

### 2. Cascade Computation

When a spec changes with BREAKING classification:
- Identify all drawers cited by affected spec (via `cited_by` list)
- Mark each drawer NEEDS_REVERIFICATION
- Identify all other specs that cite those drawers
- Mark those specs NEEDS_REVERIFICATION
- Write cascade log entry to ledger.md

### 3. Contradiction Detection

When a new drawer is written on a topic that already has a FRESH/AGING drawer:
- Flag potential contradiction
- Write to contradictions.md with both drawer IDs
- Set `contradiction_with` on both records
- Surface to Dream for resolution during consolidation

### 4. Deletion Provenance

When Forget archives a drawer:
- Record deletion event in provenance record
- Record reason, timestamp, requesting module
- Mark archived_to path
- Trigger NEEDS_REVERIFICATION on all specs citing deleted drawer

### 5. Citation Tracking

When Specify or any spec-writing module references a drawer:
- Provenance records the spec artifact path in `cited_by`
- Enables cascade computation when drawer expires

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Provenance records | `.wabblespec/memory/provenance/index.json` | Machine-readable lineage |
| Ledger entries | `.wabblespec/memory/provenance/ledger.md` | Human-readable append-only log |
| Contradiction list | `.wabblespec/memory/provenance/contradictions.md` | Active contradictions for Dream |
| Cascade notifications | Sent to Memory (staleness transitions) | NEEDS_REVERIFICATION propagation |
| Provenance receipt | `.wabblespec/receipts/provenance-receipt.md` | I10 compliance |

---

## Workflow

### On Memory Write

```
1. Receive: drawer_id, source, module, confidence, timestamp
2. Create or update provenance record in index.json
3. Check for existing drawer on same topic -> contradiction check
4. Append write event to ledger.md
5. Confirm to Memory (write proceeds)
```

### On BREAKING Spec Change

```
1. Receive: changed spec artifact path
2. Query index.json for all drawers with cited_by containing that spec
3. For each drawer:
   a. Transition staleness to NEEDS_REVERIFICATION (via Memory)
   b. Find all other specs in cited_by for that drawer
   c. Mark those specs NEEDS_REVERIFICATION (notify Specify)
4. Log cascade to ledger.md
5. Write Provenance receipt
```

### On Deletion (Forget)

```
1. Receive: drawer_id, reason, requesting module
2. Update provenance record: deletion fields
3. Trigger NEEDS_REVERIFICATION cascade for cited_by specs
4. Append deletion event to ledger.md
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over provenance/ directory |
| `schemas/provenance-record.schema.json` | Schema | Provenance record validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |
| `rules/contradiction-policy.md` | Rules | When contradictions auto-resolve vs. surface to Dream |
| `rules/cascade-policy.md` | Rules | Cascade depth limits, grace periods |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | Provenance is notified on every Memory write/delete. Provenance triggers staleness transitions back to Memory. |
| Forget | Forget notifies Provenance before archiving. Provenance records deletion. |
| Dream | Reads contradictions.md during consolidation to resolve or flag. |
| Specify | Provenance tracks which drawers are cited by which specs (cited_by). |
| ReferenceLoad | Notifies Provenance on every reference load. |
| Verifier | Can query Provenance to confirm evidence trust level before gate check. |

---

## Verification Mode

**Audit** — every Memory drawer has a provenance record. Ledger is append-only (no deletions from ledger). All cited_by relationships are bidirectional. No contradiction older than grace period without Dream resolution.

---

## Receipt Extension Fields

```json
{
  "records_created": "integer",
  "records_updated": "integer",
  "cascade_triggered": "boolean",
  "cascade_depth": "integer",
  "contradictions_flagged": "integer",
  "deletions_recorded": "integer"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Cascade depth limit | Unlimited vs. max N hops | Per-module planning |
| Contradiction auto-resolution | Never (always surface to Dream) vs. auto-resolve if confidence differential > threshold | Per-module planning |
| Ledger format | Markdown append-only (current) vs. JSON event log | Per-module planning |
| cited_by population | Spec-write triggers Provenance vs. Provenance scans spec files | Per-module planning |
