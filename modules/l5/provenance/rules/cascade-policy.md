# Cascade Policy

Governs how Provenance propagates NEEDS_REVERIFICATION when a BREAKING spec change occurs.

---

## Trigger

Cascade triggers only on BREAKING classification. Non-BREAKING spec changes do not cascade.

BREAKING means: a change that alters the meaning, contract, or structural assumption that downstream specs depend on. Examples: interface change, schema rename, invariant removal, acceptance criteria revision.

---

## Cascade algorithm

```
Hop 0: Changed spec artifact (the thing that changed)
Hop 1: All drawers with cited_by containing the changed spec
         -> transition each to NEEDS_REVERIFICATION via Memory
Hop 2: All spec artifacts in those drawers' cited_by lists
         -> mark those specs NEEDS_REVERIFICATION
         (do not recurse further — stop at hop 2)
```

---

## Depth limit: 2 hops

Default depth: 2. Do not cascade beyond hop 2.

If the cascade surface at hop 2 contains more than 10 affected artifacts: log the gap in ledger.md and surface for human review. Do not silently cascade a large blast radius.

---

## What cascade does NOT do

- Does not delete drawers or specs
- Does not automatically re-verify anything
- Does not block execution by itself — the pre-tool-use hook blocks on EXPIRED, not NEEDS_REVERIFICATION
- Does not change confidence scores

---

## Cascade log entry format (ledger.md)

```
| {timestamp} | CASCADE | hop={N} | source={spec_path} | affected={count} | drawers={id_list} |
```

---

## Grace period

After cascade marks a drawer NEEDS_REVERIFICATION:
- If re-verified within 5 execution receipts: transitions to FRESH
- If not re-verified within 15 execution receipts: transitions to EXPIRED

This grace period is checked by `staleness-checker.py`.
