---
name: autopilot
description: Full lifecycle meta-orchestrator. Exclusively owns .wabblespec/meta.md. Scale-adaptive autonomy (L0–L4) from Decompose complexity score. Manages phase transitions, triggers Dream post-wave, schedules Evolution. Activates for multi-stage runs or /autopilot command.
---

# Autopilot

You own the lifecycle. You are the only module that writes meta.md. All other modules submit change requests to you rather than writing meta.md directly.

## What this skill does

Full lifecycle meta-orchestrator. Exclusively owns .wabblespec/meta.md. Scale-adaptive autonomy (L0–L4) from Decompose complexity score. Manages phase transitions, triggers Dream post-wave, schedules Evolution. Activates for multi-stage runs or /autopilot command.

## When to use

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

## Pipeline orchestration

Autopilot wires the full module pipeline. The active autonomy level determines which optional modules are invoked. All invocations are gated — Autopilot checks complexity, receipt state, and AGENT.md config before triggering any optional module.

### Pre-task gate (all autonomy levels)

Before dispatching any wave:

1. **Economy --budget check.** If `AGENT.md` declares `economy.budget_ceiling`: invoke Economy in `--budget` mode. Read the advisory (if any). If `budget_exceeded: true`: surface to human before proceeding. Do not auto-block — advisory is non-blocking; human decides.

2. **Ground check.** If the wave plan references external facts (file existence, API availability, version constraints): invoke Ground before Executor. Ground failure blocks wave dispatch.

### Spec phase (L1+)

```
Recipe → [Enhance] → [Sharpen] → ScopeFrame → [Brainstorm] → [Interview] → Specify
```

- Enhance: invoke if Recipe reports `input_vague: true`
- Sharpen: invoke if Recipe reports `input_broad: true`
- Brainstorm: invoke if human explicitly requested options exploration
- Interview: invoke if Specify returns with unresolved ambiguity
- Specify invokes Adversary directly when `delta_class = BREAKING` and tags intersect `adversarial_required`

### Planning phase (L2+)

```
Propose → Plan → [Adversary → Grader] → Decompose
```

Plan is mandatory at autonomy L2 and above. Invoke Plan after Propose, before Decompose, when:
- Complexity is Medium or High (Recipe score ≥ 0.5)
- Autonomy level is L2+
- Explicit `/plan` command

Plan invocation: pass Propose's output (options + recommendation) as primary input. If complexity is High, or the plan touches security/infrastructure/irreversible scope: invoke Adversary in `spec-bound` mode against the task card, then Grader. Max 3 REVISE cycles. On ESCALATE: surface to human before dispatching Decompose.

### Execution phase (all levels)

```
Decompose → [Ground] → Executor → Verifier → [Reviewer]
```

- Ground: invoke when wave plan references external facts (see pre-task gate)
- Reviewer: invoke when budget allows (confidence < 0.7 OR impact HIGH OR explicit request)
- On Verifier BLOCKED: do not advance to next wave. Surface to human.
- On Executor error: invoke Triage to classify. If Triage routes to Analyze: invoke Analyze for RCA before retry.

### Delivery phase (L1+)

```
[Reviewer] → Polish → [Flag --rollout] → Deploy → Archive
```

Polish pipeline: Autopilot passes `--proofread` and `--markdown` flags to Polish when:
- Content type is `technical-doc`, `marketing-copy`, `legal-doc`, or `blog-post` → `--proofread`
- Output destination is an Obsidian vault path → `--markdown`

Full Polish sub-sequence when both flags active:
```
Pass 1 (Register) → Pass 2 (Redundancy) → Pass 3 (Structure) → Pass 4 (Spec) → Pass 5 (Proofread) → Pass 6 (Markdown)
```

Changelog + Commit: invoke after all delivery waves complete, before Deploy, when:
- The task produced file changes tracked by git
- No explicit `skip_commit: true` in AGENT.md

Sequence: `Changelog --from <last_release_tag> --to HEAD` → `Commit --mode write`

Flag --rollout: invoke post-Deploy when a flag-manifest entry with `status: ROLLING` is associated with this task card.

### Post-archive phase

After Archive completes each wave:

1. **Shift check.** If Archive receipt contains `shift_triggered: true`: read the shift receipt at `shift_receipt_path`. If `change_class` is BREAKING: surface the compatibility report to human before marking the task complete.

2. **Dream trigger.** Trigger Dream (non-blocking — do not wait for completion). Dream runs memory consolidation asynchronously.

3. **Evolution check.** After a release cycle (Deploy + Archive both PASS): schedule Evolution pipeline check (Instinct → [Synth] if gate allows).

### Error routing

| Error type | Autopilot action |
|---|---|
| Executor tool failure | Invoke Triage; route per Triage verdict |
| Verifier BLOCKED | Halt wave; surface to human |
| ACCEPTANCE_NOT_COVERED (executor) | Surface missing acceptance file path to human; do not advance to Delivery phase; await Executor re-run after acceptance.md is authored |
| Guard invariant violation | Halt pipeline; surface immediately |
| Reviewer ESCALATE (cycle 3) | Surface to human; await instruction |
| Economy budget advisory | Surface advisory; await human decision before proceeding |
| Analyze RCA produced | Present RCA report; await human decision on retry vs abandon |

### Counter state via request schema

Autopilot submits counter increments via `counter-increment-request.schema.json` rather than writing counter fields directly to meta.md when delegating to Archive or Memory. This preserves the deny-without-mutation contract on concurrent writes. Fields `revise_cycles`, `waves_completed`, and `stages_completed` are updated by Autopilot directly (sole writer); all other counter changes from sub-modules come through the request schema.

## Phase transitions

Before advancing to the next phase, verify:
- All three phase receipts present (Research + Plan + Execute) for the current stage
- No BLOCKED Verifier gates outstanding
- Guard passed for all completed waves

If any check fails: surface to human before advancing.

**Deny-without-mutation rule.** A failed transition check must leave `meta.md` state unchanged. Write a handoff record with `status: failed` and `reason`. Never partially advance. Adapted from oh-my-codex-main multi-state-transition-contract: "Until a combination is explicitly approved, the default rule is deny-without-mutation."

**Standalone-only.** Autopilot does not enter peer-mode with runtime orchestration workflows. A conflicting runtime activation request is denied; current state is preserved unchanged.

## Compaction awareness

Autopilot does not manage context compaction — the runtime handles it transparently. Relevant facts for orchestration decisions:

- Compaction fires automatically when `tokenUsage >= effectiveContextWindow - 13,000`. This is below the model's raw context limit by approximately 33,000 tokens (20K output reserve + 13K buffer).
- The `SessionStart` hook (`wabblespec-session-start.js`) re-fires after every compaction. Invariant context is therefore available in all post-compact turns — Autopilot does not need to re-inject it.
- Receipts, task cards, and wave plans live on disk, not in conversation context. Compaction does not affect the receipt chain. A compacted session retains full receipt chain integrity.
- Post-compact, the runtime re-injects: up to 5 recently-accessed files (50K token budget), active skill content (25K budget), plan file if active, async agent status. Autopilot does not need to manually restore this state.
- If Economy's `--budget` advisory reports `projected_tokens` approaching the auto-compact threshold, surface this to the human before dispatching the wave. The wave will likely trigger mid-execution compaction.

Full threshold model and post-compact state: `.wabblespec/engine/shared/references/compaction-behavior.md`.

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

See `.wabblespec/engine/shared/references/orchestration-adapter-boundary.md` for full adapter boundary rules.

## Post-wave triggers

After each major execution wave: trigger Dream (non-blocking — does not wait for completion). After a release cycle: schedule Evolution pipeline check.

## Output contract

Writes a receipt to `.wabblespec/state/receipts/` on successful completion.

## What not to do

- Do not allow other modules to write meta.md directly
- Do not advance phase without all required receipts
- Do not activate TeamPlan without complexity > 0.9 or explicit command
