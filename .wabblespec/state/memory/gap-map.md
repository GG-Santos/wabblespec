# Gap Map

> Generated: 2026-05-30T14:46:17.130155+00:00
> Drawers scanned: 97
> Findings: 1

## MEDIUM (1)

### 1. [COVERAGE_GAP] unknown/unknown

**Finding:** Room unknown/unknown has no FRESH or AGING drawers (states present: )

**Action:** Run MemorySearch to identify what needs documenting in unknown/unknown. Write at least one new drawer from a verified source.

---

## How to close a finding

1. Pick highest-severity finding.
2. Follow the Action instruction.
3. After updating the drawer, run `staleness-checker.py` to confirm state.
4. Re-run `dream.py` to verify this finding no longer appears.
5. Record the closure in the drawer's provenance log.
