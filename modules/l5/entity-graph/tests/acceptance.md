# Acceptance Tests — EntityGraph (L5)

## AT-EG-01: EntityGraph is script-only, zero LLM

**Given** an EntityGraph invocation
**When** processing runs
**Then** no LLM call is made; all entity detection and relationship building is performed by script

---

## AT-EG-02: Three entity types and their detection methods

**Given** content being analyzed by EntityGraph
**When** entity detection runs
**Then**:
- `file` entities are detected via regex matching file path patterns
- `module` entities are detected via word-boundary matching
- `concept` entities are detected via topic and tag matching

---

## AT-EG-03: Co-occurrence threshold of 2

**Given** two entities that appear together in source content
**When** EntityGraph builds relationships
**Then** a relationship edge is only created when co-occurrence count is >= 2; single co-occurrences are not promoted to edges

---

## AT-EG-04: Confidence tiers assigned correctly

**Given** a relationship of each declaration type
**When** EntityGraph assigns confidence
**Then**:
- declared relationships: confidence = 1.0
- observed relationships: confidence = 0.7
- inferred relationships: confidence = 0.4

---

## AT-EG-05: 50-drawer gate enforced

**Given** fewer than 50 drawers exist in memory
**When** EntityGraph is invoked
**Then** EntityGraph FAILS with a gate-not-met error

---

## AT-EG-06: Never deletes — invalidates only

**Given** an entity or relationship that is being removed from the graph
**When** EntityGraph processes the removal
**Then** the record is marked invalid (with `valid_to` timestamp) rather than deleted; no record is removed from `entity-graph.json`, `entity-registry.json`, or `knowledge_graph.sqlite3`

---

## AT-EG-07: Four output artifacts written

**Given** a successful EntityGraph run
**When** execution completes
**Then** the following are written/updated:
- `entity-graph.json`
- `entity-report.md`
- `entity-registry.json`
- `knowledge_graph.sqlite3`

---

## AT-EG-08: Typed predicates include temporal validity

**Given** a relationship edge in the entity graph
**When** the edge is written
**Then** it contains `valid_from` and optionally `valid_to` timestamp fields alongside the typed predicate
