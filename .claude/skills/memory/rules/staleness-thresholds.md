# Staleness Thresholds

Governs automatic transitions applied by `scripts/staleness-checker.py`.
Activity proxy: count of execution receipts written after drawer's `written_at`.

---

## Activity-Based Thresholds (primary)

| Transition | Trigger |
|---|---|
| FRESH → AGING | 5 execution receipts since `written_at` |
| AGING → STALE | 10 execution receipts since `written_at` |
| STALE → EXPIRED | 20 execution receipts since `written_at` |

"Execution receipt" = any `.json` receipt in `.wabblespec/receipts/` with `timestamp` after the drawer's `written_at`.

---

## Hard-Expiry Threshold (secondary)

If `expires_at` is set on a drawer and current UTC time is past `expires_at`, the drawer transitions directly to EXPIRED regardless of receipt count.

`expires_at: null` means no hard expiry — activity-based decay only.

---

## Re-verification Reset

Any state can return to FRESH via explicit re-verification:
- Source must be re-read or re-confirmed
- Re-verification must be documented in the drawer's provenance log
- `last_verified` timestamp must be updated
- staleness-checker will not override a manually set FRESH state until thresholds are crossed again from the new `last_verified` date

---

## NEEDS_REVERIFICATION (event-driven — not threshold)

Triggered by Provenance when upstream source changes with BREAKING classification.
Not triggered by receipt count.
Must be resolved by human or module action before the drawer can return to FRESH.

---

## SUPERSEDED (explicit only)

Set only when a new drawer explicitly replaces this one.
Never triggered by staleness-checker automatically.

---

## Threshold Adjustment

These defaults are intentionally conservative for early-stage use (Phase 3).
Adjust after 50+ real drawers exist and decay patterns are visible.
To change: edit this file. staleness-checker reads no external config — thresholds live in `THRESHOLDS` dict in `scripts/staleness-checker.py`. Keep both files in sync.
