# Query Types

Four canonical query types. Map every incoming query to exactly one before traversal begins.

## why-query

**Signal words:** "why", "rationale", "reason", "decided", "chose", "motivation"

**What it answers:** Historical decision provenance — why a design exists as it does.

**Traversal:** Find entity matching domain. Follow provenance edges backward (which drawers reference this entity as an origin decision point?). Surface top 3–5 drawers by relevance. Extract narrative from those drawers.

**Output includes:** Decision timeline, drawer IDs as evidence, confidence that the traversal is complete.

---

## blast-radius

**Signal words:** "what breaks", "impact", "affects", "depends on", "downstream", "if I change"

**What it answers:** Forward reachability — which other entities are affected if this entity changes.

**Traversal:** Find the entity. Run `scripts/blast-radius.py --entity <eid>`. Compute all entities reachable via dependency edges. Rank by hop distance.

**Output includes:** Affected entity list, hop distances, drawer IDs evidencing each dependency relationship.

---

## pattern-discovery

**Signal words:** "recurring", "pattern", "seen before", "similar", "common", "repeated", "trend"

**What it answers:** Co-occurrence clusters — problems or design patterns that appear repeatedly across sessions.

**Traversal:** Run `scripts/pattern-matcher.py --domain <domain>`. Find co-occurrence clusters with frequency counts. Rank by frequency.

**Output includes:** Top patterns, frequency counts, example drawers for each pattern.

---

## what-changed

**Signal words:** "changed", "recent", "since", "timeline", "history", "last week", "between"

**What it answers:** Entity change timeline — what was modified and when, across sessions.

**Traversal:** Filter graph edges by timestamp range. Sort by recency. Return entities that gained new edges in range.

**Output includes:** Chronological change list, entities modified, drawer IDs that introduced each change.

---

## Ambiguous query handling

If the query matches two types, pick the one with higher specificity:
- Specific artifact named → prefer blast-radius or why-query over pattern-discovery
- Time range mentioned → prefer what-changed
- Still ambiguous → resolve with why-query (most information-dense traversal)
