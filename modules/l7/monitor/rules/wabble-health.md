# /wabble-health — Framework Self-Diagnostic Design

Self-diagnosis command for WabbleSpec. Checks framework integrity, not target-project observability. Separate from Monitor's primary SLO-generation function.

**Trigger:** `/wabble-health` command or explicit invocation.

**Output:** `.wabblespec/health-report-<timestamp>.md` + inline summary.

**Status values per check:** PASS | WARN | FAIL | SKIP (SKIP = prerequisite missing, check not applicable).

---

## Health Check Categories

### Category 1 — Schema Integrity

**Check 1.1 — framework.yaml module paths**

Verify every `module_id` declared in `framework.yaml` has a corresponding directory in `modules/`. Flag mismatches.

Known failures (as of 2026-05-22):
- `framework.yaml` declares `archive` at `modules/l2/archive/` — live path is `modules/l7/archive/`
- `framework.yaml` declares `economy` at `modules/l6/economy/` — live path is `modules/l2/economy/`

Status: FAIL if any declared path does not exist in live tree.
Blast radius: affects any tool that reads `framework.yaml` for module routing.

**Check 1.2 — skill-rules.json layer field alignment**

For each `modules/<layer>/<module>/skill-rules.json`: verify `"layer"` field matches the directory layer prefix.

Example: `modules/l2/executor/skill-rules.json` must have `"layer": "L2"`.

Status: FAIL per mismatched file. PASS if all 59 files match.

**Check 1.3 — receipt schema required fields**

Sample up to 10 most recent receipts from `.wabblespec/receipts/`. Validate each against `_shared/schemas/receipt.base.schema.json`.

Status: FAIL if any sampled receipt missing required fields. WARN if receipt count < 3 (too few to sample).

---

### Category 2 — Module Completeness

**Check 2.1 — L8 module folders**

Verify `modules/l8/` exists with at least one module folder.

Known state: L8 planned but absent from live tree. Expected modules: `instinct`, `synth`, `blueprint`, `factory`, `augment`, `benchmark`, `forge`, `feedback`, `retro`.

Status: WARN (not FAIL — L8 is correctly gated on 100+ real receipts). Report count of planned-but-absent L8 modules.

**Check 2.2 — Required shared schemas present**

Verify all four required schemas exist:
- `_shared/schemas/receipt.base.schema.json`
- `_shared/schemas/skill-rules.schema.json`
- `_shared/schemas/error-event.schema.json`
- `_shared/schemas/drawer.schema.json`

Status: FAIL per missing file.

**Check 2.3 — skill-rules.json count vs module directory count**

Count directories in `modules/` that contain a `SKILL.md`. Count `skill-rules.json` files. If count differs by more than 2: flag discrepancy.

Status: WARN if mismatch.

---

### Category 3 — Memory and Staleness

**Check 3.1 — EXPIRED drawer count**

Query Memory for drawers with staleness state EXPIRED or NEEDS_REVERIFICATION. Report count.

Status: PASS if count = 0. WARN if 1–3. FAIL if > 3 (staleness pressure on evidence quality).

**Check 3.2 — Dream log recency**

Read `.wabblespec/memory/dream-log.json`. Report last Dream run date and run count.

Status: PASS if last run within 20 receipts of current receipt count. WARN if Dream has never run. WARN if behavior-change evidence missing after 5+ runs.

**Check 3.3 — Memory drawer count vs MemoryMine gate**

Count total drawers. Report against MemoryMine 50-drawer activation gate.

Status: INFO only — not PASS/FAIL. Reports: "N drawers — MemoryMine gate at 50."

---

### Category 4 — Receipt Chain

**Check 4.1 — Recent receipt chain completeness**

Read `.wabblespec/archive/receipt-index.json` (or equivalent). For the most recent archived task, verify the full chain exists: recipe → scopeframe → specify → decompose → executor → verifier → archive.

Status: FAIL if any link missing. WARN if index is empty (no archived tasks yet).

**Check 4.2 — Hook wired**

Verify `hooks/pre-tool-use-receipt-check.py` exists and is referenced in `.claude/settings.json`.

Status: FAIL if hook file missing. FAIL if not wired in settings. PASS otherwise.

**Check 4.3 — Economy captures directory**

Check if `.wabblespec/captures/` exists. If it exists, report file count.

Status: INFO only. No PASS/FAIL — captures directory absence just means Economy Rule 2 has not fired yet.

---

## Output Format

```markdown
# WabbleSpec Health Report

**Generated:** <ISO-8601>
**WabbleSpec workspace:** <path>

## Summary

| Category | PASS | WARN | FAIL | SKIP |
|---|---|---|---|---|
| Schema Integrity | N | N | N | N |
| Module Completeness | N | N | N | N |
| Memory and Staleness | N | N | N | N |
| Receipt Chain | N | N | N | N |

**Overall:** PASS | WARN | FAIL
(FAIL if any check FAIL. WARN if any check WARN and no FAIL. PASS otherwise.)

## Findings

### FAIL — Check 1.1: framework.yaml module paths
- `archive`: declared `modules/l2/archive/`, live path `modules/l7/archive/`
- `economy`: declared `modules/l6/economy/`, live path `modules/l2/economy/`
Blast radius: framework.yaml consumers cannot route to archive or economy correctly.
Fix: Update framework.yaml paths to match live tree.

### WARN — Check 2.1: L8 module folders absent
9 planned L8 modules not yet built. Gate: 100+ real receipts required before L8 build begins.
Current receipt count: N. Gate opens at: 100.

[... one finding per non-PASS check ...]

## Checks with no findings

[List of PASS checks — one line each]
```

---

## Non-negotiable rules

1. `/wabble-health` reads — never writes. No side effects except the health report file.
2. Every FAIL includes a blast-radius statement and a fix path.
3. Known pre-existing failures (framework.yaml path drift, L8 absent) are reported with context, not silently suppressed.
4. Health report is a receipt-adjacent artifact — cite it in the session's archive receipt when run alongside a task.
