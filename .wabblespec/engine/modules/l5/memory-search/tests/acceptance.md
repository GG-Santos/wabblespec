# Acceptance Tests — MemorySearch (L5)

## AT-MSEARCH-01: MemorySearch has no write authority

**Given** a MemorySearch invocation of any query type
**When** execution completes
**Then** no drawer is written, no staleness state is modified, and the receipt records `write_operations: 0`

---

## AT-MSEARCH-02: EXPIRED drawers never appear in results

**Given** a query that would match an EXPIRED drawer
**When** MemorySearch applies the mandatory staleness post-filter
**Then** the EXPIRED drawer is excluded from all results regardless of semantic score

---

## AT-MSEARCH-03: Staleness post-filter is mandatory

**Given** any semantic or topic query
**When** results are ranked
**Then** STALE drawers have their score decremented by 0.3 and NEEDS_REVERIFICATION drawers have their score decremented by 0.5 before ranking; EXPIRED drawers are removed entirely

---

## AT-MSEARCH-04: Confidence boost applied in ranking

**Given** a drawer with confidence value C
**When** ranking is computed
**Then** the drawer's ranking score includes `+ confidence * 0.1` as a positive adjustment

---

## AT-MSEARCH-05: Deduplication by drawer ID

**Given** a query that retrieves multiple results with the same `wabblespec_drawer_id`
**When** results are returned
**Then** only one result per `wabblespec_drawer_id` is included (exact duplicate removed)

---

## AT-MSEARCH-06: Traversal query type follows relationship edges

**Given** a `traverse` query with a starting drawer ID
**When** MemorySearch executes
**Then** it follows typed relationship edges and returns connected drawers, not just the seed drawer

---

## AT-MSEARCH-07: Receipt contains query metadata

**Given** a completed MemorySearch run
**Then** the receipt at `.wabblespec/receipts/memorysearch-{timestamp}.json` contains:
- `query_type`
- `query_terms`
- `results_count`
- `staleness_filtered_count`
- `drawers_returned`
