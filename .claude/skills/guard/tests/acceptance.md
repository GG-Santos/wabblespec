# Guard — Acceptance Criteria

## BLOCK: no wave inputs

Given Guard is invoked with no wave inputs assembled,
Then Guard surfaces: "Guard requires assembled wave inputs to validate."
Then Guard does not proceed to any validation layer.
Then no guard receipt is written.

## Layer 1 — Checkpoint detection on Wave 1

Given Guard is invoked for Wave 1 of a task,
And `.wabblespec/session/checkpoints/checkpoint-wave-*.json` files exist,
When Guard runs Layer 1,
Then Guard surfaces the most recent checkpoint to Executor with wave_index, wave_label, timestamp, and receipts_written.
Then Guard pauses (SOFT) and awaits Executor confirmation before continuing Layer 2.
Then this is not a HARD abort — it is a recovery-awareness check.

Given Guard is invoked for Wave 1,
And the checkpoint's `session_id` does not match the current session,
When Guard surfaces the checkpoint,
Then Guard notes the session_id mismatch as informational.
Then Guard does not block on session_id mismatch alone.

Given Guard is invoked for Wave N where N > 1,
When Guard runs Layer 1,
Then Guard does not check for checkpoint files.
Then no checkpoint detection pause occurs.

Given Guard is invoked for Wave 1 and no checkpoint files exist,
When Guard runs Layer 1,
Then checkpoint detection is a no-op.
Then Guard proceeds to Layer 2 without pausing.

## Layer 1 — Schema validation: HARD error

Given a wave input has missing required fields or malformed JSON/YAML,
When Guard runs Layer 1,
Then Guard returns a HARD error and aborts the wave immediately.
Then no subsequent layers run.
Then the guard receipt records `layer_1_schema: "FAIL"` and the violation in `violations`.

## Layer 1 — Schema validation: SOFT warning

Given a wave input contains unknown optional fields,
When Guard runs Layer 1,
Then Guard logs a SOFT warning to the receipt and proceeds to Layer 2.
Then the wave is not aborted.

## Layer 2 — Scope violation

Given a wave targets a file listed in scope.md Out of Scope,
When Guard runs Layer 2,
Then Guard returns a SPEC_VIOLATION error and routes to human.
Then the wave halts.
Then `layer_2_scope: "SPEC_VIOLATION"` is recorded in the receipt.

## Layer 3 — I9 invariant (expired evidence)

Given a wave input contains evidence marked EXPIRED,
When Guard runs Layer 3,
Then Guard returns a HARD error, aborts the wave, and quarantines the expired evidence.
Then `layer_3_invariants: "FAIL"` is recorded.

## Layer 3 — I11 invariant (boundary violation)

Given a wave attempts to write to `.wabblespec/` framework space rather than project space,
When Guard runs Layer 3,
Then Guard returns a HARD error and aborts the wave.
Then `layer_3_invariants: "FAIL"` is recorded.

## Layer 3 — I10 invariant (missing prior receipt)

Given Wave N begins but Wave N-1 receipt does not exist,
When Guard runs Layer 3,
Then Guard returns a DEPENDENCY error and pauses execution.
Then the upstream failure is surfaced.
Then the wave does not proceed.

## Layer 3 — Memory backend invariants

Given any wave plan includes a Memory, MemorySearch, MemoryMine, or EntityGraph module,
When Guard runs Layer 3,
Then Guard checks that `WABBLESPEC_MEMORY_PATH` env var is set (WABBLESPEC_MEMORY_READY invariant).
Then Guard checks that `.wabblespec/memory/chroma.sqlite3` exists (CHROMADB_EXISTS invariant).
Then if either check fails, Guard returns a HARD error with actionable resolution message.
Then Guard checks that ChromaDB drawer count >= 50 before any closet indexing (CLOSET_INDEX_GATE).

## Layer 4 — Unauthorized write target

Given a module's wave targets a file not in its `skill-rules.json` authority.owns list,
When Guard runs Layer 4,
Then Guard returns a HARD error and aborts the wave.
Then the violation is logged in the receipt.

## Layer 4 — Missing skill-rules.json

Given the requesting module has no skill-rules.json,
When Guard runs Layer 4,
Then Guard returns a HARD error (I5 violation) and aborts the wave.
Then `layer_4_authority: "FAIL"` is recorded.

## Layer 4 — Misactivation risk (SOFT)

Given a module's file_path_patterns are declared but no wave files match those patterns,
When Guard runs Layer 4,
Then Guard logs `misactivation_risk: true` to the receipt and proceeds.
Then the wave is not blocked.

## Layer 5 — BLOCK-classified command

Given a wave plan step contains a shell command classified BLOCK in command-risk-policy.md,
When Guard runs Layer 5,
Then Guard returns a HARD error and aborts the wave.
Then the error message names the specific command, the risk reason, and the safer alternative.
Then `layer_5_command_risk: "BLOCK"` is recorded.

## Layer 5 — WARN-classified command

Given a wave plan step contains a shell command classified WARN,
When Guard runs Layer 5,
Then Guard proceeds and adds the command to `command_warnings` in the receipt.
Then Executor must log a rationale from the wave plan.
Then `layer_5_command_risk: "WARN"` is recorded.

## Layer 5 — No shell commands (SKIP)

Given a wave plan contains no shell command fields,
When Guard runs Layer 5,
Then Guard records `layer_5_command_risk: "SKIP"` and issues no warnings.

## Happy path: all layers PASS

Given all five layers pass,
When Guard returns,
Then `overall: "PASS"` is returned to Executor.
Then a guard receipt is written to `.wabblespec/receipts/guard-wave-<N>-receipt.json`.

## Guard cannot be bypassed

Given any wave attempts to proceed without a Guard PASS receipt,
Then an I4 invariant violation is triggered.
Then the pre-tool-use hook blocks the wave independently of LLM compliance.
Then Guard does not fix violations — it reports them and lets the appropriate module resolve.

## Do NOT

Given any Guard run,
Then Guard does not repair or transform inputs.
Then Guard does not silently suppress violations and return false PASS receipts.
Then Guard does not skip layers for speed.

## Receipt fields

Given any successful Guard run,
Then the receipt contains: `wave_id`, `layer_1_schema`, `layer_2_scope`, `layer_3_invariants`, `layer_4_authority`, `misactivation_risk`, `layer_5_command_risk`, `command_warnings`, `overall`, `violations`.
