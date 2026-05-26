# Autopilot — Acceptance Criteria

## BLOCK: multi-stage run without decompose receipt

Given Autopilot is invoked for a multi-stage run but no decompose receipt exists,
Then Autopilot surfaces: "Autopilot requires a decompose receipt before dispatching waves."
Then no waves are dispatched.
Then meta.md is not modified.

## Cold start: creates state.json and meta.md

Given Autopilot is invoked and neither `.wabblespec/session/state.json` nor `.wabblespec/meta.md` exist,
When Autopilot performs cold start,
Then state.json is created with `enforcement_active: true`.
Then meta.md is created from scratch with all required fields populated.
Then `active_stage`, `lifecycle_phase`, `complexity_score`, and `autonomy_level` are set correctly.

## Autonomy level derivation

Given a Decompose complexity score,
When Autopilot assigns autonomy level,
Then score < 0.3 maps to L0 (collapse-eligible, minimal orchestration).
Then score 0.3–0.5 maps to L1 (single-stage, Executor manages waves).
Then score 0.5–0.7 maps to L2 (multi-stage, Autopilot routes stages).
Then score 0.7–0.9 maps to L3 (full lifecycle, Autopilot manages all phases).
Then score > 0.9 maps to L4 (TeamPlan may activate).

## meta.md sole ownership

Given any other module attempts to write meta.md directly,
When Autopilot enforces ownership,
Then the write is blocked.
Then the requesting module is required to submit a change request `{ "field": "value", "reason": "string" }`.
Then Autopilot applies or rejects the request.

## Economy --budget pre-task check

Given `AGENT.md` declares `economy.budget_ceiling`,
When Autopilot runs the pre-task gate,
Then Economy is invoked in `--budget` mode before dispatching any wave.
Then if `budget_exceeded: true` in the advisory, Autopilot surfaces to human before proceeding.
Then the advisory is non-blocking — the human decides whether to proceed.

## Phase transition: all receipts required

Given Autopilot attempts to advance to the next phase,
When the phase transition check runs,
Then Autopilot verifies all three phase receipts are present (Research + Plan + Execute) for the current stage.
Then Autopilot verifies no BLOCKED Verifier gates are outstanding.
Then Autopilot verifies Guard passed for all completed waves.
Then if any check fails, Autopilot surfaces to human before advancing.

## Deny-without-mutation on failed transition

Given a phase transition check fails,
When Autopilot handles the failure,
Then meta.md state is left unchanged.
Then a handoff record is written with `status: "failed"` and a reason.
Then Autopilot never partially advances phase state.

## Wave handoff records

Given Autopilot dispatches a wave,
When the handoff record is written to meta.md dispatch_log,
Then the record contains: `request_id`, `target`, `status`, `created_at`, `notified_at`, `delivered_at`, `failed_at`, `reason`.
Then status values are: pending, notified, delivered, or failed.
Then timestamp fields never contradict status.

## Dream triggered post-archive

Given Archive completes a major execution wave,
When Autopilot handles the post-archive phase,
Then Dream is triggered non-blocking — Autopilot does not wait for Dream completion.
Then Shift check is performed: if `shift_triggered: true` in Archive receipt and change_class is BREAKING, surface to human before marking task complete.

## Evolution scheduled post-release

Given Deploy + Archive both return PASS,
When Autopilot handles the post-release phase,
Then Autopilot schedules Evolution pipeline check (Instinct → [Synth] if gate allows).

## Verifier BLOCKED: halt wave

Given Verifier returns BLOCKED during a wave,
When Autopilot handles the error,
Then the wave is halted.
Then the blocked state is surfaced to human immediately.
Then Autopilot does not advance to the next wave.

## Reviewer ESCALATE at cycle 3

Given Reviewer reaches cycle 3 with no ACCEPT,
When Autopilot handles the escalation,
Then Autopilot surfaces to human and awaits instruction.
Then no further waves are dispatched until human responds.

## TeamPlan activation gate

Given complexity score is <= 0.9 or no explicit TeamPlan command was issued,
When Autopilot evaluates module selection,
Then TeamPlan is not activated.
Then single-agent Executor handles execution.

## Do NOT

Given any Autopilot run,
Then Autopilot does not allow other modules to write meta.md directly.
Then Autopilot does not advance phase without all required receipts.
Then Autopilot does not activate TeamPlan without complexity > 0.9 or explicit command.
Then Autopilot does not enter peer-mode with runtime orchestration workflows.

## Receipt fields

Given any successful Autopilot run,
Then a receipt is written to `.wabblespec/receipts/`.
Then meta.md records the completed session_id, final autonomy_level, waves_completed, stages_completed, and last_updated timestamp.
