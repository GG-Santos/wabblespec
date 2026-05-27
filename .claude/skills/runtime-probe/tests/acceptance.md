# RuntimeProbe — Acceptance Criteria

## Happy path: nine capabilities written

Given RuntimeProbe is invoked with no existing runtime-state.json,
When detection completes,
Then runtime-state.json is written to `.wabblespec/runtime/runtime-state.json`.
Then the file contains all nine capability descriptors: code-generation, analysis, synthesis, instruction-following, reasoning, tool-use, vision, embedding, context7.
Then `probed_at` is a valid ISO 8601 timestamp.
Then `overrides_applied` is false and `override_source` is null.

## Capability detection: binary result

Given RuntimeProbe runs detection for any capability,
When the detection signal is present,
Then `available: true` is recorded with confidence >= 0.7.

Given RuntimeProbe runs detection for any capability,
When the detection signal is absent,
Then `available: false` is recorded with confidence >= 0.7.

Given detection is uncertain,
When RuntimeProbe records the capability,
Then `available: true` is recorded with confidence < 0.7 and no error is emitted.

## context7: MCP detection

Given the Claude Code tool context includes `resolve-library-id` or `get-library-docs`,
When RuntimeProbe detects context7,
Then `context7.available: true` is recorded.
Then `context7.detection: "mcp"` is recorded.

## context7: CLI detection

Given `ctx7` binary is on PATH,
And `resolve-library-id` / `get-library-docs` are not in available tools,
When RuntimeProbe detects context7,
Then `context7.available: true` is recorded.
Then `context7.detection: "cli"` is recorded.

## context7: MCP preferred over CLI

Given both `ctx7` CLI is on PATH and MCP tools are present,
When RuntimeProbe detects context7,
Then `context7.detection: "mcp"` is recorded (not "cli").

## context7: unavailable

Given `ctx7` is not on PATH,
And `resolve-library-id` / `get-library-docs` are not in available tools,
When RuntimeProbe detects context7,
Then `context7.available: false` is recorded.
Then `context7.detection: "none"` is recorded.
Then no error is emitted and detection continues for other capabilities.

## No model names in output

Given RuntimeProbe completes detection,
When runtime-state.json is written,
Then no model name, provider name, or API version identifier appears in the file.

## Overrides applied

Given `.wabblespec/runtime/runtime.json` exists with an override for a capability,
When RuntimeProbe reads overrides and writes runtime-state.json,
Then the overridden capability reflects the declared value, not the probed value.
Then `overrides_applied: true` and `override_source: "runtime.json"` are recorded.
Then non-overridden capabilities reflect probed values.

## Reuse fresh state

Given runtime-state.json exists and is FRESH (within staleness threshold),
When RuntimeProbe is invoked,
Then RuntimeProbe does not re-probe — it reuses the existing file.
Then no new runtime-state.json write occurs.

## Do NOT

Given any RuntimeProbe run,
Then RuntimeProbe does not write model names or provider names anywhere.
Then RuntimeProbe does not skip detection and assume capabilities.
Then RuntimeProbe does not block session start if runtime-state.json is already FRESH.
