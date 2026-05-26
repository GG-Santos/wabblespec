# NEEDS_REVERIFICATION Resolution

**Date:** 2026-05-25
**Reviewer:** Claude (automated spec review)
**Triggered by:** Forge promotions — cold-start-coverage-recipe-gate-v1, acceptance-test-executor-enforcement-v1

---

## Executor dependents (3 modules)

### verifier — CLEARED

Verifier operates per-wave, invoked by executor during wave execution. The new executor acceptance gate fires after all verifier interactions are complete (post-final-wave). Verifier writes wave receipts only; it has no reference to execution-receipt.json or `acceptance_verified`. No spec change required.

### apply — CLEARED

Apply activates per-wave after Guard PASS, writes to project/repo/ only. Acceptance gate is post-final-wave — after apply has completed its routing work. No overlap, no conflict. No spec change required.

### autopilot — CLEARED (with minor update)

Autopilot's error routing table lacked an entry for ACCEPTANCE_NOT_COVERED. Added explicit routing rule: surface missing acceptance file path to human; do not advance to Delivery phase; await Executor re-run. Phase transition check already handles the case correctly (stalls on missing execution-receipt.json), but the explicit routing makes the behavior unambiguous. Update applied to `modules/l2/autopilot/SKILL.md`.

---

## Recipe dependents (16 modules)

**Modules reviewed:** product, enhance, sharpen, scope-frame, scaffold, platform-web, platform-api-service, platform-cli, platform-game, platform-mobile, platform-desktop, platform-iot-embedded, platform-library-package, platform-extension-plugin, platform-data-pipeline, platform-ai-agent

**Finding:** All 16 modules activate after recipe.json is written. The new Step 2d cold-start check runs as a pre-condition to recipe.json being written. From the dependents' perspective, the contract is unchanged: recipe.json either exists (all cold-start files present) or the session has not advanced past recipe (cold-start file missing). No module assumes recipe activates without cold-start verification, because no module previously had visibility into recipe's internal selection logic.

Grep confirmed: none of the 16 modules reference `cold_start_verified`, `MISSING_COLD_START`, or make assumptions about recipe's module selection internals. "Cold-start" references in platform modules refer to application startup performance (CLI startup time, mobile launch time), not WabbleSpec module cold-start files.

**All 16: CLEARED. No spec changes required.**

---

## Summary

| Module | Risk | Action | Status |
|---|---|---|---|
| verifier | Low — no overlap with acceptance gate | None | CLEARED |
| apply | None — different phase of execution | None | CLEARED |
| autopilot | Medium — error routing gap | Added ACCEPTANCE_NOT_COVERED row | CLEARED |
| 16 recipe dependents | None — operate post-recipe.json | None | CLEARED |

**All 19 NEEDS_REVERIFICATION flags resolved.**
