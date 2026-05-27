---
name: orchestration-adapter-boundary
description: Declares the thin adapter boundary between WabbleSpec orchestration modules (Autopilot, ModelRouter, Ensemble, TeamPlan) and the underlying runtime (OMX/Codex/Claude Code). WabbleSpec stays on its side; runtime stays on its side. Adapted from oh-my-codex-main docs/contracts/.
---

# Orchestration Adapter Boundary

WabbleSpec runs inside an orchestration runtime (currently OMX/Codex or Claude Code). This document declares what WabbleSpec owns, what the runtime owns, and the boundary rules that prevent identity collapse.

## WabbleSpec owns

| Artifact | Owner module | Notes |
|---|---|---|
| `.wabblespec/meta.md` | Autopilot | Sole writer. No runtime may write this file. |
| `.wabblespec/receipts/*.json` | Per-module authority | Runtime has no receipt authority. |
| Phase transitions (Research → Plan → Execute → Delivery) | Autopilot | Transition rules defined in Autopilot SKILL.md. |
| Capability routing decisions | ModelRouter | Runtime provides capabilities; ModelRouter selects. |
| Wave dispatch records | Autopilot | Handoff records in `.wabblespec/meta.md` dispatch log. |
| Guard, Verifier, Archive gates | Respective modules | Runtime cannot bypass WabbleSpec receipt gates. |
| Command risk classification | Guard Layer 5 | Runtime shell access does not bypass command-risk policy. |

## Runtime owns

| Artifact | Runtime responsibility | Notes |
|---|---|---|
| `.wabblespec/runtime/runtime-state.json` | RuntimeProbe (writes), Runtime (provides capabilities) | WabbleSpec reads but does not write capability descriptors. |
| Tool execution (Edit, Write, Bash) | Runtime | WabbleSpec describes what to do; runtime executes. |
| Session continuity, context compression | Runtime | WabbleSpec does not manage token window directly. |
| MCP server connections | Runtime | WabbleSpec uses MCP tools but does not configure the MCP server. |
| tmux/multiplexer management | Runtime | WabbleSpec does not write to tmux panes or manage processes. |

## Adapter rules

1. **WabbleSpec receipt gates are not bypassed by runtime convenience.** If the runtime offers a shortcut that would skip a Guard or Verifier gate, the shortcut is refused.

2. **Runtime capability descriptors flow one way.** RuntimeProbe reads capabilities and writes `runtime-state.json`. ModelRouter reads `runtime-state.json`. Neither module calls runtime internals directly.

3. **Autopilot is standalone-only.** It does not enter peer-mode with runtime orchestration workflows. Autopilot activation clears any conflicting runtime state; conflicting runtime state does not override Autopilot.

4. **Dispatch status is authoritative; timestamps are supporting evidence.** A wave handoff record's `status` field determines routing. Timestamp fields (`notified_at`, `delivered_at`) are supporting metadata and cannot contradict `status`. Adapted from oh-my-codex-main `crates/omx-runtime-core/src/dispatch.rs` DispatchRecord contract.

5. **Deny-without-mutation.** Invalid Autopilot phase transitions must leave state unchanged. A failed transition attempt is logged to the handoff record with `status: failed` and `reason`. It does not partially advance state.

6. **Identity preservation.** WabbleSpec modules do not adopt runtime naming, skill structures, or identity. OMX skills are not imported as WabbleSpec modules. The runtime is an execution surface, not an authority layer.

## What this boundary prevents

- Runtime triggering a wave without Guard PASS (bypass attempt)
- Runtime writing `.wabblespec/meta.md` directly (state corruption)
- WabbleSpec claiming runtime capabilities it does not have (false vendor-neutral claims)
- Autopilot phase advancing on partial evidence (deny-without-mutation rule)
- Timestamp evidence overriding authoritative dispatch status (state consistency)
