# Contradiction Policy

Governs when Provenance flags a contradiction and how it is resolved.

---

## When to flag a contradiction

Flag when a new drawer is written on a topic where an existing drawer already exists with staleness_state in [FRESH, AGING, STALE] AND the new drawer's `source` differs from the existing drawer's source.

Do not flag contradiction if:
- Existing drawer is SUPERSEDED or EXPIRED (it is already replaced)
- New drawer explicitly sets `superseded_by` pointing to the existing drawer (this is an intentional replacement, not a contradiction)
- Topics are similar but distinct enough to be separate facts

---

## What flagging does

1. Append entry to `contradictions.md`:
   ```
   | {timestamp} | {drawer_a} | {drawer_b} | {topic} | unresolved |
   ```
2. Set `contradiction_with` on both provenance records
3. Do NOT block the write — contradiction is surfaced, not enforced
4. Dream resolves contradictions during consolidation

---

## Auto-resolution (never)

Contradictions are never auto-resolved by Provenance. Resolution requires:
- Human decision, OR
- Dream consolidation run that surfaces the contradiction with context
- Resolution must be recorded: one drawer set to SUPERSEDED, the other confirmed FRESH

---

## Contradiction aging

A contradiction that remains unresolved for 10+ execution receipts (since it was flagged) is escalated: both drawers transition to NEEDS_REVERIFICATION via Memory.

This is checked by `staleness-checker.py`, not by Provenance directly.
