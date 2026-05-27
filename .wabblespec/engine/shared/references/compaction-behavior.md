# Compaction Behavior

**Derived from:** `claude-code-main/src/services/compact/autoCompact.ts`, `compact.ts`, `microCompact.ts` (production source — read 2026-05-26)
**Consumed by:** l2/economy (--budget mode), l2/autopilot (context pressure handling), all modules aware of session token state
**Purpose:** Factual description of when and how the runtime compacts conversation context. Replaces abstract references to "compaction" with real trigger thresholds, process steps, and post-compaction state.

---

## Context Window Model

The runtime maintains an effective context window separate from the raw model window:

```
effectiveContextWindow = modelContextWindow - min(maxOutputTokensForModel, 20,000)
```

The 20,000 token reservation protects space for compaction summary output (p99.99 of real compact summaries observed at 17,387 tokens).

Override available via `CLAUDE_CODE_AUTO_COMPACT_WINDOW` env var (caps effective window at a lower value).

---

## Token Warning States

Four threshold states, evaluated on every turn:

| State | Threshold | Visible effect |
|---|---|---|
| Normal | tokenUsage < warningThreshold | No warning |
| Warning | tokenUsage >= (autoCompactThreshold - 20,000) | Yellow warning shown |
| Error | tokenUsage >= (autoCompactThreshold - 20,000) | Red error shown (same threshold as warning) |
| Auto-compact trigger | tokenUsage >= autoCompactThreshold | Auto-compaction fires |
| Blocking | tokenUsage >= (effectiveContextWindow - 3,000) | Session blocks — cannot continue without compaction |

```
autoCompactThreshold = effectiveContextWindow - 13,000
```

Override: `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=<float>` sets threshold as a percentage of effective window (useful for testing).

---

## Auto-Compaction Trigger Conditions

Auto-compaction fires when all of the following are true:

- `tokenUsage >= autoCompactThreshold`
- `DISABLE_COMPACT` env var is not set
- `DISABLE_AUTO_COMPACT` env var is not set
- `userConfig.autoCompactEnabled === true` (user setting)
- `querySource` is not `session_memory` or `compact` (recursion guard)
- CONTEXT_COLLAPSE feature is not active (when enabled, context collapse owns headroom management)
- REACTIVE_COMPACT GrowthBook gate is not active (when enabled, reactive compact handles 413 errors instead)

**Circuit breaker:** After 3 consecutive auto-compaction failures, auto-compaction stops retrying for the rest of the session. Prevents infinite API hammering when context is irrecoverably oversized.

---

## Compaction Process (Full)

### Step 1 — Pre-compact hooks
Execute `PreCompact` hooks with `trigger: "auto"` or `trigger: "manual"`. Hooks may inject custom instructions that influence the summary.

### Step 2 — Session memory compaction (attempted first)
Before full compaction, the runtime tries `trySessionMemoryCompaction`. If session memory compaction succeeds, full compaction is skipped.

### Step 3 — Message preparation
- Strip images from messages: `<img>` blocks → `[image]` text markers, documents → `[document]`
- Strip re-injected attachment types (skill_discovery, skill_listing — they are re-generated post-compact anyway)
- Get only messages after the last compact boundary marker

### Step 4 — Summary request
Send prepared messages plus a compaction prompt to the model (streaming, text only — no tool use during compaction). Compaction agent is denied tool use: `behavior: "deny", reason: "compaction agent should only produce text summary"`.

**Cache-sharing:** The forked compaction agent reuses the main conversation's prompt cache prefix. Falls back to a fresh streaming call if the fork fails.

**Prompt-too-long recovery:** If the compaction request itself hits the context limit:
1. Group messages into API-round groups
2. Drop oldest groups until the token gap is covered (or 20% of groups if gap is unparseable)
3. Prepend a synthetic user marker (`[earlier conversation truncated for compaction retry]`) if the remaining messages start with an assistant message
4. Retry (max 3 attempts)

### Step 5 — Post-compact state
On successful summary:

1. Clear `readFileState` (file content cache)
2. Clear `loadedNestedMemoryPaths`
3. **Do not reset `sentSkillNames`** — re-injecting the full skill listing (~4K tokens) post-compact is wasteful; the model still has SkillTool in schema

4. Re-inject post-compact attachments (generated in parallel):
   - **Recent files:** up to 5 most-recently-accessed files, 50,000 token total budget, 5,000 tokens per file. Files already present in preserved messages are skipped. Plan files and CLAUDE.md files are excluded.
   - **Async agent status:** status attachments for running or completed-but-unretrieved background agents
   - **Plan attachment:** if a plan file exists for this session
   - **Plan mode attachment:** if currently in plan mode (re-injects plan mode instructions)
   - **Skill attachment:** up to 5 most-recently-invoked skills, 25,000 token budget, 5,000 tokens per skill (head-truncated with marker if over limit)
   - **Deferred tool schemas delta:** re-announce any tool schemas that were active before compaction
   - **MCP instructions delta:** re-announce MCP tool instructions

5. Execute `SessionStart` hooks with `trigger: "compact"` (same hooks that run at session open)

6. Create compact boundary marker (type: `SystemCompactBoundaryMessage`). Boundary carries:
   - `trigger: "auto" | "manual"`
   - `preCompactTokenCount`
   - `uuid` of last pre-compact message
   - `preCompactDiscoveredTools` (set of tool names that were loaded before compaction)

7. Construct summary message (visible in transcript only, marked `isCompactSummary: true`)

8. Execute `PostCompact` hooks

9. Notify prompt-cache break detection (suppresses false-positive cache miss alerts for the next turn)

10. Mark post-compaction state (`markPostCompaction()`)

---

## Post-Compact Message Order

The resulting message array after compaction:

```
[boundaryMarker] [summaryMessages...] [messagesToKeep?] [attachments...] [hookResults...]
```

`messagesToKeep` is only present for partial compaction (user selects a pivot message). Full compaction does not keep any original messages.

---

## Partial Compaction

User-triggered from the message selector UI. Two directions:

| Direction | Summarizes | Keeps |
|---|---|---|
| `from` (default) | Messages after the pivot | Messages before the pivot |
| `up_to` | Messages before the pivot | Messages after the pivot (compact boundaries and summaries stripped) |

Partial compaction uses the same summary request, prompt-too-long recovery, and post-compact attachment logic as full compaction.

---

## Microcompaction (Pre-API-call cleanup)

Microcompaction runs before each API call to trim tool result tokens without a full summarization cycle.

**Time-based trigger:** If the gap since the last main-thread assistant message exceeds a configured threshold (minutes), content-clear all but the N most-recent compactable tool results. Rationale: server prompt cache has expired anyway; clearing old results shrinks what gets rewritten.

**Cached microcompact (internal builds only):** Uses the cache editing API to delete old tool results without invalidating the cached prompt prefix. Does not modify local message content — edits are applied at the API layer. Only runs for the main thread (not forked agents).

**Compactable tool set:** FileRead, Shell tools (Bash, PowerShell), Grep, Glob, WebSearch, WebFetch, FileEdit, FileWrite. Other tools are never microcompacted.

**Image token estimate:** Images and documents inside tool results are estimated at 2,000 tokens each.

---

## Disabling Compaction

| Mechanism | Effect |
|---|---|
| `DISABLE_COMPACT=1` | Disables all compaction (auto, manual, microcompact) |
| `DISABLE_AUTO_COMPACT=1` | Disables auto-compaction only; manual `/compact` still works |
| `autoCompactEnabled: false` in user config | Same as `DISABLE_AUTO_COMPACT=1` |

---

## Implications for WabbleSpec

- Economy's `--budget` mode projects token cost before a wave. The actual auto-compact threshold is `effectiveContextWindow - 13,000`. A projected cost approaching this value is the real risk boundary, not the raw model context window.
- Autopilot should treat compaction as a transparent runtime event — no module action required. The runtime handles context recovery. Modules that maintain important state (file content, skill references) will have that state re-injected automatically post-compact.
- Receipts and task cards are not affected by compaction — they live on disk (`.wabblespec/engine/shared/references/`, `.wabblespec/receipts/`), not in the conversation context. A compacted session retains full receipt chain integrity.
- The `SessionStart` hooks (`wabblespec-session-start.js`) re-run after every compaction. The invariant context they inject is therefore available in every post-compact turn.
- CLAUDE.md memory files are excluded from post-compact file re-injection (they are already loaded via the memory system separately).
