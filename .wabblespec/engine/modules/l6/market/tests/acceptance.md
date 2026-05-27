# Acceptance Tests — Market (L6)

## AT-MKT-01: Strategy before execution — no execution without positioning

**Given** a Market invocation in `execution` mode
**When** no positioning brief exists
**Then** Market surfaces the gap and does not produce an execution plan — execution always depends on positioning

---

## AT-MKT-02: Three artifacts produced in order for full mode

**Given** a Market invocation in `full` mode
**When** execution runs
**Then** the three artifacts are produced in sequence: positioning brief -> message hierarchy -> execution plan; each depends on the prior

---

## AT-MKT-03: Proof elements must be specific and verifiable

**Given** Market is building a message hierarchy
**When** a proof element is declared
**Then** generic claims ("industry-leading", "best-in-class") are rejected; proof elements must be specific and verifiable (metric, benchmark, version, date)

---

## AT-MKT-04: Positioning without real differentiation is rejected

**Given** Market building a positioning statement
**When** differentiators provided are generic benefits ("easy to use", "saves time")
**Then** Market flags them as non-differentiating and requires specific, defensible differentiation before producing a positioning statement

---

## AT-MKT-05: WARN verdict when assumptions made from missing inputs

**Given** a Market invocation with missing required inputs
**When** Market proceeds with assumptions
**Then** verdict is `WARN` and all assumptions are listed in the output documents

---

## AT-MKT-06: Receipt contains required fields

**Given** a completed Market run
**Then** the receipt at `.wabblespec/state/receipts/market-{timestamp}.json` contains:
- `mode`
- `product_name`
- `positioning_brief_path`
- `message_hierarchy_path`
- `execution_plan_path`
- `icp_defined`
- `market_category`
- `primary_message`
- `channels_recommended`
- `verdict`
