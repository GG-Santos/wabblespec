# Permission Flow

**Derived from:** `claude-code-main/src/types/permissions.ts` (production source — read 2026-05-26)
**Consumed by:** l2/guard (Layer 5 command risk), l4/gateway-security (enforcement description), l4/gateway-engineering (tool call safety), l2/executor (tool dispatch)
**Purpose:** Factual description of the runtime permission decision tree. Replaces abstract descriptions of "the permission system" with the actual types and decision sequence.

---

## Permission Modes

Five external (user-addressable) modes, set via `settings.json defaultMode` or `--permission-mode` CLI flag:

| Mode | Behavior |
|---|---|
| `default` | Standard. All tool calls evaluated against rules and mode. |
| `acceptEdits` | File edits auto-approved. Other tools still evaluated. |
| `dontAsk` | All tool calls auto-approved. Equivalent to bypassing the ask step. |
| `plan` | File-write operations trigger ask. File-read and shell read-only are allowed. |
| `bypassPermissions` | All tool calls auto-approved, including destructive operations. Requires explicit activation. |

Two internal-only modes:

| Mode | Behavior |
|---|---|
| `auto` | Uses a transcript classifier to evaluate tool safety. Feature-gated (TRANSCRIPT_CLASSIFIER). Not user-addressable in standard builds. |
| `bubble` | Internal propagation mode. Not user-addressable. |

---

## Permission Rules

A permission rule has three parts:

```
source: where the rule came from
ruleBehavior: "allow" | "deny" | "ask"
ruleValue: { toolName: string, ruleContent?: string }
```

**Rule sources** (evaluated in priority order, highest first):

| Source | Origin |
|---|---|
| `policySettings` | Enterprise MDM/policy deployment |
| `flagSettings` | Feature flags |
| `cliArg` | `--permission-mode` and related CLI flags |
| `command` | Command-level permission grants |
| `session` | Runtime grants made during the current session |
| `localSettings` | `.claude/settings.local.json` (project-local, not checked in) |
| `projectSettings` | `.claude/settings.json` (project-level, checked in) |
| `userSettings` | `~/.claude/settings.json` (user-global) |

`policySettings` has highest authority and cannot be overridden by user or project rules.

---

## Decision Tree

For each tool call, the runtime evaluates in this order:

1. **Always-deny rules first.** If any `ruleBehavior: "deny"` rule matches the tool and optional content pattern — deny immediately. `decisionReason: { type: "rule", rule }`.

2. **Always-allow rules.** If any `ruleBehavior: "allow"` rule matches — allow. `decisionReason: { type: "rule", rule }`.

3. **Mode evaluation.**
   - `bypassPermissions` → allow all.
   - `dontAsk` → allow all non-policy-blocked.
   - `plan` → ask for file-write operations; allow reads and shell.
   - `default` / `acceptEdits` → continue to step 4.

4. **Safety check.** Checks for security-critical patterns (path traversal, shell injection, Windows path bypass). Non-`classifierApprovable` patterns → deny. `classifierApprovable` patterns → may proceed to classifier in `auto` mode.

5. **Working directory constraint.** File paths outside the declared working directory set → deny. `decisionReason: { type: "workingDir" }`.

6. **Hook decision.** `PreToolUse` hooks may return `permissionDecision: "allow" | "deny"`. If a hook decides — use that result. `decisionReason: { type: "hook" }`.

7. **Classifier (auto mode only).** A transcript-aware classifier evaluates the tool call in context. Returns a `ClassifierResult` with `matches`, `confidence: "high" | "medium" | "low"`, and `reason`. Classifier result maps to allow/deny/ask. `decisionReason: { type: "classifier" }`.
   - The classifier may run asynchronously (`pendingClassifierCheck`) — the dialog may appear before the classifier resolves, and the classifier may auto-close it.

8. **Ask (user dialog).** None of the above produced a terminal decision → show a permission dialog. User can approve, deny, or approve-and-remember (which writes a new rule to the appropriate destination).

---

## Decision Result Types

**Allow:**
```
behavior: "allow"
updatedInput?: object        -- hook may have modified tool input
userModified?: boolean       -- user edited input in the dialog
decisionReason?: ...
```

**Ask:**
```
behavior: "ask"
message: string              -- shown in the dialog
pendingClassifierCheck?: {   -- classifier running async; may resolve before user acts
  command: string
  cwd: string
  descriptions: string[]
}
suggestions?: PermissionUpdate[]  -- offered "remember this" options
```

**Deny:**
```
behavior: "deny"
message: string
decisionReason: ...
```

**Passthrough:**
```
behavior: "passthrough"     -- no decision at this layer; propagate to next
```

---

## Permission Updates

When a user approves-and-remembers in the dialog, the runtime writes a `PermissionUpdate` to the declared destination:

| Operation | Effect |
|---|---|
| `addRules` | Append allow/deny/ask rules for specified tools |
| `replaceRules` | Replace existing rules for specified tools |
| `removeRules` | Remove matching rules |
| `setMode` | Change the active permission mode |
| `addDirectories` | Add paths to the working directory set |
| `removeDirectories` | Remove paths from working directory set |

Destination choices: `userSettings`, `projectSettings`, `localSettings`, `session`, `cliArg`.

`session` destination is ephemeral — it lasts only the current session and is not persisted to disk.

---

## Classifier Detail

The auto-mode classifier (`YoloClassifierResult`) is a two-stage evaluator:

- **Stage 1 (fast):** Quick model call. If confidence is high, terminates.
- **Stage 2 (thinking):** Extended reasoning model call. Runs when stage 1 is uncertain.

Fields relevant to Guard and gateway-security:

| Field | Meaning |
|---|---|
| `shouldBlock` | Whether the classifier recommends blocking |
| `reason` | Natural-language explanation |
| `confidence: "high" \| "medium" \| "low"` | Certainty of the decision |
| `transcriptTooLong` | Context window exceeded — fall back to normal prompting (not retry/fail-closed) |
| `unavailable` | API error — fall back, do not treat as block |

The classifier is not available in external builds. `auto` mode is excluded from `INTERNAL_PERMISSION_MODES` unless `TRANSCRIPT_CLASSIFIER` feature is compiled in.

---

## Tool Permission Context

At decision time, the runtime passes a read-only `ToolPermissionContext`:

```
mode: PermissionMode
additionalWorkingDirectories: Map<string, AdditionalWorkingDirectory>
alwaysAllowRules: { [source]: string[] }
alwaysDenyRules: { [source]: string[] }
alwaysAskRules: { [source]: string[] }
isBypassPermissionsModeAvailable: boolean
strippedDangerousRules?: ...      -- rules removed due to policy constraints
shouldAvoidPermissionPrompts?: boolean
awaitAutomatedChecksBeforeDialog?: boolean
```

`awaitAutomatedChecksBeforeDialog: true` means the classifier runs before showing the dialog. `false` means the dialog appears immediately while the classifier runs in parallel.

---

## Implications for WabbleSpec

- Guard Layer 5 (command risk) operates before the runtime permission system. A BLOCK from Guard prevents the wave from reaching the runtime permission check.
- The runtime permission system applies after Guard PASS — it evaluates individual tool calls at execution time, not at wave plan time.
- Hook-based decisions (`type: "hook"`) map to WabbleSpec hook files. `wabblespec-prompt-guard.js` does not make permission decisions — it is informational. A hook that makes real decisions would use `hookSpecificOutput.permissionDecision`.
- `policySettings` authority cannot be overridden by any WabbleSpec rule or session grant. Enterprise deployment constraints are terminal.
