# Migration Gate — Migrate

## Phase 2 is gated — no auto-advance

Phase 2 (removal) does not execute automatically after Phase 1 completes. A human must explicitly confirm the gate before Phase 2 is routed to Executor.

## Gate confirmation

Gate confirmation consists of a human declaration that:
1. All known consumers of the deprecated interface have migrated to the new interface
2. No active references to the deprecated interface remain in any consumer
3. The automated migration script (if generated) has been run and verified

This declaration is recorded in the Migrate receipt as `phase2_gate_confirmed: true`.

## Gate failure

If any known consumer has not migrated when Phase 2 is requested:
- Do not proceed with Phase 2
- Surface the unconverted consumers to the human
- Wait for explicit re-confirmation after consumers are migrated

## Unknown consumers

If external consumers exist that cannot be enumerated (public API):
- Phase 2 requires a deprecation timeline — a public notice period
- Migrate records the notice period as part of the migration plan
- Phase 2 gate confirmation includes acknowledgment that the notice period has elapsed

## Verifier role

Verifier audits Phase 1 completion before Phase 2 is authorized. Verifier checks:
- New interface present and functional
- Old interface marked deprecated (not removed)
- No Phase 1 acceptance criteria failures

Phase 2 cannot be routed to Executor until Verifier Phase 1 audit passes.
