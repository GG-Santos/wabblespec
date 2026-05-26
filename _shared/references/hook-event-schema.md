# Hook Event Schema

**Derived from:** `claude-code-main/src/types/hooks.ts` (production source — read 2026-05-26)
**Consumed by:** l2/guard (pre-tool-use hook validation), l0/recipe (session hook config), all modules authoring hooks, WabbleSpec hook files in `src/hooks/`
**Purpose:** Factual vocabulary for hook event types, payload shapes, response fields, and execution lifecycle. Replaces guesswork in WabbleSpec hook authoring.

---

## Hook Events

Fourteen named events fire at specific lifecycle points. A hook registered for an event receives a typed payload and may return a typed response.

| Event name | When it fires | Blocks execution? |
|---|---|---|
| `SessionStart` | Once per session open | No (informational + context injection) |
| `Setup` | During Claude Code initial setup | No |
| `SubagentStart` | When a subagent spawns | No |
| `UserPromptSubmit` | Before each user prompt is processed | No (informational only) |
| `PreToolUse` | Before any tool call | Yes — can approve or block |
| `PostToolUse` | After tool completes successfully | No |
| `PostToolUseFailure` | After tool fails | No |
| `PermissionRequest` | When runtime asks for permission | Yes — can approve or deny |
| `PermissionDenied` | After a permission is denied | No — can signal retry |
| `Notification` | On system notification events | No |
| `Elicitation` | During structured elicitation prompts | Can accept/decline/cancel |
| `ElicitationResult` | After elicitation completes | No |
| `CwdChanged` | When working directory changes | No — can register new watch paths |
| `FileChanged` | When a watched file changes | No |
| `WorktreeCreate` | When a git worktree is created | No |

---

## Hook Response Shape

Every hook returns a JSON object. Two forms: sync (default) and async.

### Async marker

```json
{ "async": true, "asyncTimeout": 30 }
```

`async: true` tells the runtime this hook is running asynchronously. `asyncTimeout` is optional (seconds). An async hook that does not resolve before the timeout is treated as a non-blocking error.

### Sync response fields

All fields are optional unless noted.

| Field | Type | Default | Purpose |
|---|---|---|---|
| `continue` | boolean | `true` | Whether Claude continues after hook. `false` terminates the request with `stopReason`. |
| `suppressOutput` | boolean | `false` | Hide this hook's stdout from the transcript. |
| `stopReason` | string | — | Message shown to user when `continue: false`. |
| `decision` | `"approve" \| "block"` | — | Explicit approve or block decision for tool-use hooks. |
| `reason` | string | — | Explanation for the decision (written to receipt). |
| `systemMessage` | string | — | Warning message displayed to the user in the UI. |
| `hookSpecificOutput` | object | — | Event-specific output; shape varies by `hookEventName` (see below). |

### hookSpecificOutput by event

`hookSpecificOutput` is a discriminated union keyed on `hookEventName`. Only include the object matching the event firing.

**PreToolUse:**
```json
{
  "hookEventName": "PreToolUse",
  "permissionDecision": "allow | deny | ask",
  "permissionDecisionReason": "string",
  "updatedInput": { "<key>": "<value>" },
  "additionalContext": "string"
}
```

**PostToolUse:**
```json
{
  "hookEventName": "PostToolUse",
  "additionalContext": "string",
  "updatedMCPToolOutput": "<any>"
}
```
`updatedMCPToolOutput` replaces the MCP tool result in the conversation. Only valid for MCP tools.

**PostToolUseFailure:**
```json
{ "hookEventName": "PostToolUseFailure", "additionalContext": "string" }
```

**UserPromptSubmit:**
```json
{ "hookEventName": "UserPromptSubmit", "additionalContext": "string" }
```

**SessionStart:**
```json
{
  "hookEventName": "SessionStart",
  "additionalContext": "string",
  "initialUserMessage": "string",
  "watchPaths": ["/absolute/path"]
}
```
`initialUserMessage` injects a synthetic user message at session open. `watchPaths` registers paths for `FileChanged` events.

**Setup:**
```json
{ "hookEventName": "Setup", "additionalContext": "string" }
```

**SubagentStart:**
```json
{ "hookEventName": "SubagentStart", "additionalContext": "string" }
```

**PermissionRequest:**
```json
{
  "hookEventName": "PermissionRequest",
  "decision": {
    "behavior": "allow",
    "updatedInput": {},
    "updatedPermissions": []
  }
}
```
or
```json
{
  "hookEventName": "PermissionRequest",
  "decision": {
    "behavior": "deny",
    "message": "string",
    "interrupt": false
  }
}
```

**PermissionDenied:**
```json
{ "hookEventName": "PermissionDenied", "retry": true }
```
`retry: true` signals the runtime to re-attempt the permission check.

**Notification:**
```json
{ "hookEventName": "Notification", "additionalContext": "string" }
```

**Elicitation / ElicitationResult:**
```json
{
  "hookEventName": "Elicitation",
  "action": "accept | decline | cancel",
  "content": { "<key>": "<value>" }
}
```

**CwdChanged:**
```json
{ "hookEventName": "CwdChanged", "watchPaths": ["/absolute/path"] }
```

**FileChanged:**
```json
{ "hookEventName": "FileChanged", "watchPaths": ["/absolute/path"] }
```

**WorktreeCreate:**
```json
{ "hookEventName": "WorktreeCreate", "worktreePath": "/absolute/path" }
```

---

## Hook Execution Result

After the runtime processes a hook response, it produces a `HookResult` object (internal — not returned to the hook). Relevant fields that determine downstream behavior:

| Field | Type | Effect |
|---|---|---|
| `outcome` | `"success" \| "blocking" \| "non_blocking_error" \| "cancelled"` | `"blocking"` halts the request |
| `preventContinuation` | boolean | Stops Claude from continuing the current turn |
| `permissionBehavior` | `"ask" \| "deny" \| "allow" \| "passthrough"` | Overrides the permission decision for this tool call |
| `additionalContext` | string | Injected into Claude's context for the current turn |
| `updatedInput` | object | Replaces the tool input before execution |
| `retry` | boolean | Signals the calling layer to retry the permission check |

When multiple hooks fire for the same event, results are aggregated into an `AggregatedHookResult`. Blocking errors from any hook in the set cause the overall outcome to be `"blocking"`.

---

## Silent-fail contract

All hooks must catch errors and return `{}` rather than a non-zero exit code. A hook that exits non-zero causes the runtime to treat the event as a non-blocking error — the session continues. Hook failures must never interrupt a session.

WabbleSpec hook files in `src/hooks/` implement this via try/catch with `process.stdout.write('{}')` as the fallback output.

---

## Prompt elicitation protocol

A hook can request structured input from the user mid-execution using the elicitation protocol:

```json
{
  "prompt": "<request-id>",
  "message": "Question to show the user",
  "options": [
    { "key": "a", "label": "Option A", "description": "optional explanation" }
  ]
}
```

The `prompt` field acts as a discriminator (the value is the request ID). The runtime shows the options to the user and fires an `Elicitation` event with the selected key. The hook receives the result via `ElicitationResult`.

---

## WabbleSpec-specific notes

- `wabblespec-session-start.js` fires on `SessionStart`. It uses `additionalContext` to inject invariant state into the session system prompt.
- `wabblespec-prompt-guard.js` fires on `UserPromptSubmit`. It is informational only — it never sets `continue: false`.
- Neither WabbleSpec hook uses `watchPaths`, `initialUserMessage`, or elicitation.
- Both hooks implement the silent-fail contract with `process.stdout.write('{}')` on error.
