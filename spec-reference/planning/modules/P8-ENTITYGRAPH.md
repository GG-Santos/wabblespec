# Module Plan — EntityGraph (L5)

**Tier:** 3 — SUPPORTING
**Layer:** L5 Memory
**v5.3 origin:** Nexus (partial) — EntityGraph is the structural relationship index, formalized in v6.1

---

## Purpose

Track entities, relationships, and changes across project lifetime. Enables relationship-based evidence retrieval via MemorySearch. Entities are extracted from Memory drawer content — not manually declared. Graph is queryable: find all entities related to X, find all drawers referencing entity Y.

---

## Activation

`skill-rules.json` triggers:
- Memory write (EntityGraph scans new drawer for entities)
- MemorySearch entity or relationship query
- Dream consolidation run (EntityGraph updated as part of consolidation)
- Explicit `/entity-graph` query command

---

## Storage Structure

```
.wabblespec/memory/entity-graph/
  nodes.json          <- entity registry
  edges.json          <- relationship registry
  index.md            <- human-readable summary
```

### Node format

```json
{
  "id": "entity-id",
  "name": "entity name",
  "type": "module|file|person|service|concept|standard|technology",
  "drawer_refs": ["drawer-id-1", "drawer-id-2"],
  "first_seen": "timestamp",
  "last_updated": "timestamp",
  "confidence": 0.0
}
```

### Edge format

```json
{
  "id": "edge-id",
  "from": "entity-id",
  "to": "entity-id",
  "relationship": "depends-on|implements|calls|extends|replaces|contradicts|cites",
  "drawer_refs": ["drawer-id"],
  "confidence": 0.0,
  "first_seen": "timestamp"
}
```

---

## Entity Extraction

EntityGraph extracts entities from drawer content using pattern matching:

| Entity type | Detection signals |
|---|---|
| module | Module name patterns, SKILL.md references |
| file | File paths (`src/`, `.ts`, `.py`, etc.) |
| service | Service names, API endpoints, external integrations |
| concept | Key terms from spec artifacts |
| standard | Named standards (OWASP, EARS, semver, etc.) |
| technology | Framework/language names from project-map.md |

Extraction is deterministic pattern matching — not LLM inference. Low-confidence entities are included with confidence < 0.5, not excluded.

---

## Workflow

```
1. ON Memory write:
   a. Read new drawer content
   b. Extract entities using pattern matching
   c. For each entity:
      -> Check nodes.json: exists? update drawer_refs + confidence
      -> Not exists? create new node
   d. Detect relationships between entities in same drawer
   e. Update edges.json
   f. Update index.md

2. ON MemorySearch entity query:
   a. Find entity node in nodes.json
   b. Return all drawer_refs for that entity
   c. Traverse edges for related entities (configurable depth)
   d. Return entity + related entities + drawer refs

3. ON Dream consolidation:
   a. Remove nodes with no drawer_refs (orphaned)
   b. Update confidence scores based on co-occurrence
   c. Flag contradicting relationships (contradicts edges)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over entity-graph/ directory |
| `scripts/entity-extractor.py` | Script | Deterministic entity extraction from drawer content |
| `scripts/graph-traverse.py` | Script | Relationship traversal (shared with Explore) |
| `schemas/nodes.schema.json` | Schema | Node format validation |
| `schemas/edges.schema.json` | Schema | Edge format validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Memory | EntityGraph is notified on every Memory write to scan new drawers |
| MemorySearch | MemorySearch delegates entity and relationship queries to EntityGraph |
| Dream | Dream triggers EntityGraph cleanup and confidence updates during consolidation |
| Provenance | EntityGraph reads Provenance records for entity source trust |
| Explore | Explore reads EntityGraph for project-map relationship context |

---

## Verification Mode

**Observation** — nodes.json and edges.json exist and parse, all Memory drawers have at least attempted entity extraction, orphaned nodes cleaned by Dream.

---

## Receipt Extension Fields

```json
{
  "nodes_total": "integer",
  "nodes_added": "integer",
  "edges_total": "integer",
  "edges_added": "integer",
  "orphaned_removed": "integer",
  "contradictions_flagged": "integer"
}
```
