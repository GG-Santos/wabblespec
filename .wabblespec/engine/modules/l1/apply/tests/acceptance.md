# Apply — Acceptance Criteria

## BLOCK: absent delta plan

Given Apply is invoked with no delta plan or patch input and no Executor wave plan references Apply,
Then Apply surfaces a DEPENDENCY error: "Apply requires a delta to apply. It does not derive changes from scratch."
Then Apply does not write any files.

## BLOCK: absent wave context (no Executor receipt)

Given the Executor wave receipt is absent (Apply called without an active wave context),
Then Apply surfaces a DEPENDENCY error naming Executor.
Then Apply does not apply changes that have not passed Guard.
Then no files are written.

## Happy path: wave routing and context assembly

Given an active platform package receipt with a `capability_handoff` field and active gateway receipts,
When Apply runs within an Executor wave,
Then `always_load` files from the platform's capability_handoff are loaded unconditionally.
Then `conditional_load` signals are evaluated against the project repo; matching files are loaded.
Then active gateway `references/` files are loaded for each active L4 gateway.
Then context is assembled in three zones: Constraints (top), References (middle), Active task (end).
Then a receipt is written to `.wabblespec/receipts/`.

## Engineering infrastructure load

Given `gateway-engineering` is active,
When Apply assembles context,
Then `.wabblespec/engine/shared/dev/infrastructure/cicd.md` is loaded unconditionally.
Then `containers.md` is loaded if a Dockerfile or k8s manifest is detected in the repo.
Then `iac.md` is loaded if Terraform or Pulumi files are detected.

## Delta handling: ADDITIVE LOCAL — continue wave

Given Apply discovers an ADDITIVE LOCAL delta during execution,
When the delta is processed,
Then Apply proposes a patch to Specify via `--patch`.
Then Specify classifies the scope as LOCAL.
Then the wave continues after the patch is applied.

## Delta handling: BREAKING — halt

Given Apply discovers a BREAKING delta during execution,
Then Apply halts the wave immediately.
Then Apply surfaces the BREAKING delta to Executor.
Then Apply does not proceed with any further writes for the current wave.

## Delta handling: ADDITIVE BOUNDARY — surface to user

Given Apply discovers an ADDITIVE BOUNDARY delta,
Then Apply proposes a patch to Specify with scope_class = BOUNDARY.
Then Specify halts and surfaces the boundary change to the user before the wave continues.

## Write authority invariant (I11)

Given any Apply invocation,
Then Apply writes only to product space.
Then Apply never writes to `.wabblespec/`.
Then if Apply discovers it needs to write outside declared wave targets, it surfaces SPEC_VIOLATION and does not proceed.

## New file creation vs edit on absent target

Given the delta declares a create operation for a file that does not yet exist,
When Apply processes the delta,
Then Apply creates the file.

Given the delta declares an edit operation against a file that does not exist,
When Apply processes the delta,
Then Apply surfaces a DEPENDENCY error and does not proceed.

## Do NOT: self-activate outside Executor

Given Apply is invoked directly outside an Executor wave context,
Then Apply surfaces an error and does not load modules not declared in a wave.
