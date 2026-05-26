# Two-Phase Migration Policy — Migrate

## Default: two-phase required

Every BREAKING change uses two-phase migration unless a documented exception applies. The two-phase pattern is sourced from the Engineering gateway.

**Phase 1 — Additive:**
- New interface added alongside old
- Old marked deprecated, still functional
- Safe to deploy — consumers not broken
- Must pass Verifier before Phase 2 authorized

**Phase 2 — Removal:**
- Old interface removed
- Requires migration gate confirmation before Executor runs
- Gate: human declares all known consumers have migrated

## Single-phase exceptions

Single-phase (immediate removal) is only permitted when:

| Exception | Condition |
|---|---|
| All-internal consumers | No external API, no third-party consumers — all consumers are within project/repo/ |
| Security-critical | The breaking change fixes a vulnerability that cannot wait for two-phase timing |

Both exceptions require documented justification in the migration plan (`single_phase_justification` field). If justification is absent, default to two-phase.

## Mixed consumer case

If consumers include both internal and external: two-phase required. The presence of any external consumer overrides the all-internal exception.

## Phase 1 minimum

Phase 1 must exist even if the deprecation window is short. "We control all consumers" is not sufficient to skip Phase 1 — use the all-internal single-phase exception instead if that is the intent.
