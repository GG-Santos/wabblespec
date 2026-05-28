# Session Scope

**target:** Framework
**complexity:** High
**locked_at:** 2026-05-28T13:02:20Z
**session_id:** foundation-hardening-20260528

## In Scope

- Build wabblespec-doctor.py consolidating all 28 audit finding checks
- Close schema gaps: recipe.json, wave-queue.json, delivery-receipt, brainstorm options_path, propose receipt builder
- Unify confidence field across receipt builders (additive, back-compat reads of legacy names)
- Fix C1 receipt-index path normalization (.wabblespec/state/receipts/)
- Fix C2 platform skill ID alignment (registry full IDs vs .claude/skills short forms)
- Fix C3 archive.py wabble-sound.py path and C4 CLAUDE.md version/module-count drift
- Fix high tier: CLI flag unification, entity-graph regen, doc/skill path drift, orphan template disposition, memory-bootstrap dedup
- Wire doctor as on_archive daemon job and advisory (non-blocking) Guard layer
- Establish a permanent authority owner for shared framework infrastructure (engine/shared/**, wabblespec.yaml, CLAUDE.md, daemon-config, the Guard module) so Framework self-builds pass Guard Layer 4 (finding #29, surfaced by Executor Wave 1)

## Out of Scope

- Exhaustive resolution of all medium/low tier findings (left for doctor to surface)
- Full unit-test harness for the 42 shared scripts (deferred to fast-follow task card)
- Promoting the doctor Guard layer to blocking (stays advisory until clean across several Archives)
- Any product-space changes (framework self-build only, I11)

## Assumptions

- Brainstorm + Propose artifacts are the source of the 28 findings and Option 2 was human-selected
- Python 3.8+ with pyyaml and duckdb available
- Reviewer gates the Plan stage before Executor since Guard is invariant-enforcing
- H1 confidence unification is done additively with a deprecation window, keeping the overall delta ADDITIVE
- Finding #29's authority bootstrap needs a one-time human Attestation (root of trust cannot be self-granted); rescope makes the owner permanent and scopes the Attestation to a single governance edit

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
| 2026-05-28T14:18:38Z | Added finding #29 (shared-infra authority owner) + AC8 to scope | Executor Wave 1 blocked at Guard Layer 4; human chose Pause + rescope |
