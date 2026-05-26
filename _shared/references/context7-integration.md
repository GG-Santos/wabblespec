# Context7 Optional Integration

Optional documentation retrieval capability. Consumers: executor, runtime-probe, autopilot.

---

## What context7 provides

Context7 resolves up-to-date library and framework documentation on demand. Two operations:

- `resolve-library-id` — converts a library name (e.g. `react`, `fastapi`) to a context7 canonical ID
- `get-library-docs` — fetches current documentation for a library ID and optional version

Both operations are optional enrichment. If context7 is unavailable, execution proceeds with available spec artifacts and `_shared/dev/` reference guides. Progress never gates on context7 availability.

---

## Availability check

Read `context7.available` from `.wabblespec/runtime/runtime-state.json`. This field is written by RuntimeProbe.

If runtime-state.json is absent, stale, or the `context7` key is missing: treat as unavailable. Do not block.

---

## Detection (RuntimeProbe responsibility)

RuntimeProbe sets `context7.available` using the following detection logic:

1. Check if Claude Code's tool context includes `resolve-library-id` or `get-library-docs` — if present, set `detection: "mcp"`
2. Check if `ctx7` binary is on PATH (`where ctx7` on Windows, `which ctx7` on POSIX) — if found, set `detection: "cli"`
3. If both MCP and CLI are present: prefer MCP (`detection: "mcp"`) — more capable
4. If neither: `available: false`, `detection: "none"`, `confidence: 0.95`

---

## Call pattern — MCP

When `detection: "mcp"`:

```
1. resolve-library-id with libraryName: "<library>"
2. get-library-docs with context7CompatibleLibraryID: "<resolved ID>", topic: "<specific API surface needed>"
```

Load only the sections relevant to the current implementation step. Do not load full library docs into context — target the specific API surface the wave plan names.

## Call pattern — CLI

When `detection: "cli"`:

```
ctx7 <library-name>
```

Pipe or search for the relevant section. Same constraint: targeted section only, not full output.

---

## Failure handling

Any context7 error (timeout, library not found, MCP unavailable mid-session, rate limit) is informational only:

- Log in wave receipt under `context7_enrichment` with `status: "failed"` and the reason
- Executor continues with available spec artifacts
- Never emit a typed error event for context7 failure
- Never increment the REVISE counter for context7 failure

---

## When to use

Context7 enrichment is appropriate when:
- The wave implementation involves a named library or framework
- That library is not covered by the relevant `_shared/dev/` reference guide
- The implementation step requires precise API signatures, version-specific behavior, or deprecation status

Context7 enrichment is NOT appropriate when:
- The `_shared/dev/` guide covers the library adequately
- The wave plan does not reference a specific external library
- Context budget tier is DEGRADING or POOR — in those tiers, do not add optional context loads

---

## Receipt field

If context7 was used during a wave, record in the wave receipt:

```json
"context7_enrichment": {
  "status": "used | skipped | failed",
  "library": "<name if used>",
  "detection": "mcp | cli | none"
}
```

This field is optional. If context7 was not checked at all, omit the field. Do not write a receipt field solely to record that context7 is unavailable.

---

## I6 compliance

`context7` in runtime-state.json is a capability descriptor, not a vendor or model identifier. It records tool availability — not the underlying provider or model behind the documentation service. This is consistent with the vendor-neutral capability model (I6).
