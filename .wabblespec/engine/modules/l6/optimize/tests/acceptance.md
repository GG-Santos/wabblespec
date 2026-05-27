# Acceptance Tests — Optimize (L6)

## AT-OPT-01: Eight sub-modes recognized

**Given** an Optimize invocation
**When** mode is declared
**Then** the following sub-modes are supported: `seo`, `ai-search`, `structured-data`, `performance`, `social`, `local`, `video`, `voice`; `--all` runs all eight in priority order

---

## AT-OPT-02: FAIL verdict on unfixed CRITICAL findings

**Given** an Optimize run that produces a CRITICAL finding
**When** that finding cannot be auto-fixed
**Then** verdict is `FAIL` — a CRITICAL finding that remains unfixed after the optimization pass results in FAIL

---

## AT-OPT-03: Auto-fix only for deterministic, non-destructive findings

**Given** a finding that is deterministic and non-destructive (e.g., missing meta tag, missing alt text)
**When** Optimize processes it
**Then** the fix is applied directly with `fix_applied: true`

**Given** a finding requiring content judgment (keyword choice, FAQ content)
**When** Optimize processes it
**Then** it is surfaced as a finding only — `fix_applied: false`; Optimize does not auto-apply content judgment changes

---

## AT-OPT-04: Schema hallucination prevented

**Given** an Optimize structured-data run on a blog post
**When** Optimize generates JSON-LD
**Then** it does not add Product schema or LocalBusiness schema to a blog post; schema type must match actual page content

---

## AT-OPT-05: Performance findings are proxies, not confirmed regressions

**Given** an Optimize performance run
**When** a performance issue is identified
**Then** findings are labeled as "likely issues requiring measurement" — they are not stated as confirmed regressions without actual measurement data

---

## AT-OPT-06: Receipt contains findings with priority and fix status

**Given** a completed Optimize run
**Then** the receipt at `.wabblespec/receipts/optimize-{timestamp}.json` contains:
- `modes_run`
- `target_path`
- `findings` (each with `mode`, `priority`, `issue`, `fix_applied`, `fix_description`)
- `total_findings`
- `critical_count`
- `fixes_applied`
- `verdict`
