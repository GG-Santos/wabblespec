# Cascade Policy

Governs how Provenance propagates NEEDS_REVERIFICATION when a BREAKING spec change occurs.

---

## Change classification

Every spec change arriving at Provenance must declare a `change_class`. This determines whether cascade fires.

| `change_class` | Cascade action | Examples |
|---|---|---|
| `BREAKING` | Cascade fires — mark affected drawers NEEDS_REVERIFICATION | Interface change, schema rename, invariant removal, acceptance criteria revision, required field dropped |
| `NON_BREAKING` | No cascade — log to ledger.md only | Wording clarification, example added, non-normative note |
| `ADDITIVE` | No cascade — log to ledger.md only | New optional field, new subcommand with no existing contract change |

If `change_class` is absent from the incoming event: default to `BREAKING` and log the absence. Never silently skip cascade on an unclassified change.

Source hash change detection: before accepting `change_class` from the caller, compare `source_hash` in the provenance record against the current hash of the source file. If hashes differ AND the caller declares `NON_BREAKING` or `ADDITIVE`, log a warning in ledger.md: "source_hash mismatch — caller classified as {change_class} but source content changed." Do not override caller's classification; surface the discrepancy.

## Trigger

Cascade triggers only on `BREAKING` classification. `NON_BREAKING` and `ADDITIVE` changes do not cascade.

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
| {timestamp} | CASCADE | change_class=BREAKING | hop={N} | source={spec_path} | affected_drawers={count} | affected_specs={comma_separated_paths} | drawers={id_list} |
```

`affected_specs` lists the spec artifact paths marked NEEDS_REVERIFICATION at hop 2. Empty string if cascade stopped at hop 1 (no specs in cited_by of affected drawers). This field populates `cascade_events[].affected_specs` in each drawer's provenance record.

---

## Grace period

After cascade marks a drawer NEEDS_REVERIFICATION:
- If re-verified within 5 execution receipts: transitions to FRESH
- If not re-verified within 15 execution receipts: transitions to EXPIRED

This grace period is checked by `staleness-checker.py`.
