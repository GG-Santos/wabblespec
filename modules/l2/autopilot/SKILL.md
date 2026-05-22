---
name: autopilot
description: Full lifecycle meta-orchestrator. Exclusively owns .wabblespec/meta.md. Scale-adaptive autonomy (L0–L4) from Decompose complexity score. Manages phase transitions, triggers Dream post-wave, schedules Evolution. Activates for multi-stage runs or /autopilot command.
---

# Autopilot

You own the lifecycle. You are the only module that writes meta.md. All other modules submit change requests to you rather than writing meta.md directly.

## When to activate

- Multi-stage runs (complexity > 0.5)
- Explicit `/autopilot` command
- Decompose produces a wave plan requiring phase transition management

## Autonomy levels

| Complexity score | Level | Behavior |
|---|---|---|
| < 0.3 | L0 | Collapse-eligible. Minimal orchestration. Executor directly. |
| 0.3–0.5 | L1 | Single-stage. Executor manages waves. |
| 0.5–0.7 | L2 | Multi-stage. Autopilot routes between stages. |
| 0.7–0.9 | L3 | Full lifecycle. Autopilot manages all phases. |
| > 0.9 | L4 | Complex multi-stage. TeamPlan may activate. |

## meta.md — sole owner

```markdown
# Framework Meta State

**session_id:** string
**active_stage:** P1|P2|P3|P4|Execution|Delivery
**active_wave:** integer
**lifecycle_phase:** Research|Plan|Execute
**complexity_score:** 0.0-1.0
**autonomy_level:** L0|L1|L2|L3|L4
**counter_state:**
  revise_cycles: 0
  waves_completed: 0
  stages_completed: 0
**last_updated:** ISO 8601
```

No other module writes meta.md. Other modules submit: `{ "field": "value", "reason": "string" }` — Autopilot applies or rejects.

## Phase transitions

Before advancing to the next phase, verify:
- All three phase receipts present (Research + Plan + Execute) for the current stage
- No BLOCKED Verifier gates outstanding
- Guard passed for all completed waves

If any check fails: surface to human before advancing.

**Deny-without-mutation rule.** A failed transition check must leave `meta.md` state unchanged. Write a handoff record with `status: failed` and `reason`. Never partially advance. Adapted from oh-my-codex-main multi-state-transition-contract: "Until a combination is explicitly approved, the default rule is deny-without-mutation."

**Standalone-only.** Autopilot does not enter peer-mode with runtime orchestration workflows. A conflicting runtime activation request is denied; current state is preserved unchanged.

## Wave handoff records

Autopilot writes one handoff record per wave dispatch to `.wabblespec/meta.md` under `dispatch_log`. Status is authoritative; timestamp fields are supporting evidence and must not contradict status.

```json
{
  "request_id": "wave-<N>-<timestamp>",
  "target": "executor:wave-<N>",
  "status": "pending | notified | delivered | failed",
  "created_at": "ISO 8601",
  "notified_at": "ISO 8601 or null",
  "delivered_at": "ISO 8601 or null",
  "failed_at": "ISO 8601 or null",
  "reason": "string or null"
}
```

See `_shared/references/orchestration-adapter-boundary.md` for full adapter boundary rules.

## Post-wave triggers

After each major execution wave: trigger Dream (non-blocking — does not wait for completion). After a release cycle: schedule Evolution pipeline check.

## What not to do

- Do not allow other modules to write meta.md directly
- Do not advance phase without all required receipts
- Do not activate TeamPlan without complexity > 0.9 or explicit command
