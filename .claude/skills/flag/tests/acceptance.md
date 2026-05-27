# Flag — Acceptance Criteria

## BLOCK: absent flag management system

Given Flag is invoked but no flag management system is declared (no LaunchDarkly, Unleash, env variable strategy, or other),
Then Flag surfaces: "Flag requires a declared flag management system. Specify: LaunchDarkly, Unleash, environment variable, database-backed, or other."
Then Flag does not implement a flag without knowing where it lives.
Then no receipt is written.

## Mode: --create

Given `--create` is specified with a unique flag ID, owner, and description,
When Flag runs in create mode,
Then a new flag entry is written to `.wabblespec/flags/manifest.json` with state `DRAFT`.
Then `created_at` is set to the current timestamp.
Then the flag is not activated at creation — it starts DRAFT.
Then `previous_state` in the receipt is null and `new_state` is DRAFT.

Given `--create` is specified for a flag ID already in the manifest,
Then Flag surfaces a duplicate ID error.
Then no new entry is written.

## Mode: --create without removal date

Given a flag is being created with no declared removal date or cleanup condition,
When Flag runs,
Then Flag flags: "Feature flag has no declared removal date or cleanup condition."
Then Flag requires a removal date, removal trigger, or explicit 'permanent flag' justification before proceeding.
Then the flag creation is not silently allowed without this declaration.

## Mode: --rollout

Given `--rollout` is specified and the rollout gate passes,
When Flag runs in rollout mode,
Then the flag state transitions per the state machine: DRAFT → ACTIVE, or ACTIVE → ROLLING with a declared percentage.
Then `rollout_gate_passed` in the receipt is true.
Then `rollout_percentage` and `rollout_target` are set for ROLLING state.

Given the rollout gate does not pass,
Then the flag state does not change.
Then `rollout_gate_passed` is false.

## Mode: --audit

Given `--audit` is specified,
When Flag runs in audit mode,
Then DRAFT flags older than 30 days are identified as stale.
Then ROLLING flags with no percentage update in 14 days are identified as stuck.
Then ACTIVE flags with no associated task card are identified as orphaned.
Then flags with no owner are identified and reported.

## Mode: --retire

Given `--retire` is specified for an existing flag,
When Flag runs in retire mode,
Then the flag state transitions to RETIRED.
Then `retired_at` and `retirement_reason` are recorded in the manifest.
Then the flag entry is NOT deleted from the manifest — retired flags persist.
Then deletion requires an explicit `--purge` flag, not the default retire operation.

## State machine enforcement

Given a flag is in DRAFT state,
When a direct transition to ROLLING is attempted without passing through ACTIVE,
Then Flag rejects the transition and surfaces the required path.

## Absent rules files: fallback

Given `rules/flag-lifecycle.md` is missing,
When Flag runs,
Then Flag applies SKILL.md flag lifecycle rules.
Then the receipt logs: "flag-lifecycle.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Flag run,
Then the receipt contains: `mode`, `flag_id`, `previous_state`, `new_state`, `rollout_gate_passed`, `flag_manifest_path`.
Then `flag_manifest_path` is `.wabblespec/flags/manifest.json`.
