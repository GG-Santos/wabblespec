# WabbleSpec Staleness States — Reference

Lookup table. Consumers: memory, memory-search, provenance, guard.
Governed by Invariant 9 (I9).

---

## States

| State | Meaning | Action |
|---|---|---|
| FRESH | Recently verified. Fully trusted. | Use freely. |
| AGING | Approaching staleness threshold. Still usable. | Use with awareness. Flag in receipt if critical. |
| STALE | Past threshold. Credibility degraded. | Flag before use. Document in receipt evidence. Do not treat as verified. |
| EXPIRED | Do not use. Past hard expiry. | Block use. Emit STALENESS_VIOLATION if used. Quarantine. Trigger re-fetch. |
| NEEDS_REVERIFICATION | Upstream dependency changed (BREAKING mutation). Evidence may still be structurally valid but is untrusted until re-checked. | Block use. Reverify before proceeding. |
| SUPERSEDED | Replaced by newer evidence for the same fact. Content no longer authoritative. | Do not use. Refer to superseding drawer. |

---

## Propagation Rules

When a source changes with BREAKING classification:
- All drawers and spec artifacts citing that source are marked NEEDS_REVERIFICATION
- They do not auto-update
- They do not auto-revert to FRESH
- Human or module action required to move to FRESH

When a source expires:
- Drawers citing it are marked EXPIRED if they have no independent verification
- STALENESS_VIOLATION is emitted if expired evidence is used in execution

---

## Staleness Decay (Dream module)

Dream applies EMA decay to staleness confidence scores:

```
new_confidence = old_confidence * 0.9 + base_freshness * 0.1
```

Dream runs when invoked (not as background daemon). Outputs:
- `gap-map.md` — drawers with AGING or worse states
- `staleness-map.md` — full staleness overview

---

## Drawer Metadata Fields

Every drawer JSON must include:

```json
{
  "staleness_state": "FRESH | AGING | STALE | EXPIRED | NEEDS_REVERIFICATION | SUPERSEDED",
  "written_at": "<ISO 8601 UTC>",
  "expires_at": "<ISO 8601 UTC> | null",
  "source": "<reference string>",
  "confidence": 0.0
}
```

`expires_at: null` = no hard expiry, subject to decay only.

---

## Temporal Tiers

Drawers are implicitly scoped to a temporal tier based on their subject. Tier informs expected staleness decay rate and appropriate `expires_at` values:

| Tier | Scope | Decay expectation | Drawer types |
|---|---|---|---|
| Long-term (Global) | Persists across projects and versions | Slow — years | Instinct observations, entity graph nodes, evolution artifacts |
| Medium-term (Project) | Active while the project evolves | Moderate — weeks/months | Architecture decisions, API contracts, module receipts, reference evals |
| Short-term (Session) | Valid for the duration of a task cycle | Fast — days | Active wave plan state, session receipts, scope boundaries |
| Ephemeral (Task) | Valid only within a single wave | Very fast — hours | Active evidence drawers loaded per wave, intermediate outputs |

Temporal tier does not replace `staleness_state` — it is a planning lens for choosing `expires_at` when writing a new drawer.

---

## Hook Enforcement

Pre-tool-use hook checks staleness state of evidence listed in the active module's receipt inputs. If any `staleness_state` is EXPIRED, hook blocks and emits STALENESS_VIOLATION error.
