# Acceptance Tests — Nexus (L5)

## AT-NEXUS-01: Four query types operate correctly

**Given** a Nexus invocation
**When** query type is declared
**Then** the following are supported and correctly routed:
- `why-query` — traces provenance backward from a drawer
- `blast-radius` — traces dependency forward from a changed artifact
- `pattern-discovery` — clusters co-occurrences across drawers
- `what-changed` — filters graph by timestamp range

---

## AT-NEXUS-02: Graph freshness check before query

**Given** a Nexus invocation
**When** Nexus begins execution
**Then** it checks graph freshness before querying; a stale or uninitialized graph causes Nexus to surface this as a warning before returning results

---

## AT-NEXUS-03: Every claim cites a drawer

**Given** Nexus returns a response with findings
**When** the response is inspected
**Then** every factual claim in the response cites a specific `drawer_id` as its source; uncited claims are not included

---

## AT-NEXUS-04: Receipt contains traversal metadata

**Given** a completed Nexus run
**Then** the receipt at `.wabblespec/state/receipts/nexus-receipt-{timestamp}.json` contains:
- `query_type`
- `domain`
- `drawers_queried`
- `relationships_found`
- `entities_traversed`
- `response_path`
- `graph_freshness`
- `entity_graph_used`

---

## AT-NEXUS-05: blast-radius traversal is forward-only

**Given** a `blast-radius` query starting from a changed artifact
**When** Nexus traverses the dependency graph
**Then** it only follows edges in the forward direction (what depends on this) and does not traverse backward (what this depends on)

---

## AT-NEXUS-06: what-changed query requires timestamp filter

**Given** a `what-changed` query
**When** no timestamp range is declared
**Then** Nexus FAILS with a missing-parameter error — timestamp filtering is required for this query type
