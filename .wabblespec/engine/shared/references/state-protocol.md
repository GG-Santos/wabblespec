# WabbleSpec State Protocol

Defines which module writes which fields to `.wabblespec/session/state.json` at each lifecycle point, and what the pre-tool-use hook requires from those fields.

## Why this file exists

`hooks/pre-tool-use-receipt-check.py` blocks Edit/Write/Bash/MultiEdit only when `enforcement_active: true` and `required_receipts` is populated. Without this contract, modules never write those fields, the hook always exits 0, and receipt enforcement is bypassed.

## state.json fields

| Field | Type | Written by | Purpose |
|---|---|---|---|
| `enforcement_active` | bool | Session start, Archive (reset) | Master switch. Hook exits 0 when false. |
| `required_receipts` | list[str] | Each completing module | Stems of receipts that must exist before tool use proceeds. Accumulates — never cleared mid-session. |
| `active_module` | str or null | Each module at start | Identifies which module is currently running. Used in block messages. |
| `evidence_drawers` | list[str] | Modules that load drawers | Relative paths from `.wabblespec` root. Hook blocks on EXPIRED state. |
| `session_id` | str | Session start | Identifies the session for receipt correlation. |
| `started_at` | datetime | Session start | ISO 8601 UTC. |
| `completed_at` | datetime | Archive | ISO 8601 UTC. Written only on completion. |
| `last_task` | str | Archive | Human-readable summary of what the session did. |

## Write sequence

### Session start

Written by: Autopilot, or manually before first module runs.

```json
{
  "enforcement_active": true,
  "required_receipts": [],
  "active_module": "recipe",
  "evidence_drawers": [],
  "session_id": "<task-id>-<date>",
  "started_at": "<ISO-8601-UTC>"
}
```

### After each planning-phase module completes

Each L1 module appends its receipt stem to `required_receipts` and sets `active_module` to the next module. Stems must match the actual filename without `.json` — confirmed against live `.wabblespec/receipts/`.

| Module completes | Append to required_receipts | Set active_module |
|---|---|---|
| Recipe | `recipe-receipt` | `scopeframe` |
| ScopeFrame | `scopeframe-receipt` | `specify` |
| Specify | `specify-receipt` | `decompose` |
| Decompose | `decompose-receipt` | `executor` |

Write after every successful receipt file write, not before.

### Executor pre-execution prologue (before Wave 1)

Written by: Executor, immediately after `decompose-receipt.json` confirmed present.

```json
{
  "enforcement_active": true,
  "required_receipts": ["recipe-receipt", "scopeframe-receipt", "specify-receipt", "decompose-receipt"],
  "active_module": "executor",
  "evidence_drawers": ["<any evidence drawer paths loaded for this task>"]
}
```

This is the enforcement floor. The hook now blocks any tool use that proceeds without the planning chain intact.

### Per-wave updates (Executor, before each wave)

Before Guard runs for Wave N, Executor writes:

```json
{
  "active_module": "executor-wave-<N>",
  "required_receipts": ["recipe-receipt", "scopeframe-receipt", "specify-receipt", "decompose-receipt", "<all prior wave receipt stems>"]
}
```

After Guard PASS for Wave N, append `"guard-wave-<N>-receipt"` to `required_receipts`.

After Verifier PASS for Wave N, append `"wave-<N>-receipt"` and `"verification-wave-<N>-<timestamp>"` to `required_receipts`.

### Session completion (Archive)

Written by: Archive, after delivery receipt is written.

```json
{
  "enforcement_active": false,
  "active_module": null,
  "completed_at": "<ISO-8601-UTC>",
  "last_task": "<human-readable summary>"
}
```

Setting `enforcement_active: false` allows free tool use between sessions. It is only reset to `true` at the next session start.

## What happens if state.json is absent

The hook calls `find_wabblespec_root()` and then reads `session/state.json`. If the file is absent or unparseable, the hook exits 0 (allow). This is safe — a missing state.json means no session is active.

Implication: a module that skips writing state.json before execution silently removes enforcement. Modules must not rely on a previous session's state.json — they must always write their own prologue fields.

## Enforcement gap prevention rules

1. No module may begin its execution step without first writing `active_module` to state.json.
2. No planning-phase module may complete without appending its receipt stem to `required_receipts`.
3. Executor must write the full pre-execution prologue before Wave 1 Guard runs.
4. The prologue must include all planning-phase receipt stems, not just the immediately prior one.
5. `enforcement_active` is only set to `false` by Archive. It is never set to `false` by a non-completing event.

## Validation test

To verify enforcement works end-to-end:

1. Write state.json with `enforcement_active: true`, `required_receipts: ["scopeframe"]`, `active_module: "executor"`.
2. Delete or rename `scopeframe-receipt.json`.
3. Attempt any Edit/Write/Bash call.
4. Expected: hook blocks with `[WabbleSpec] BLOCKED` message naming the missing receipt.
5. Restore the receipt file.
6. Retry the tool call.
7. Expected: hook exits 0, tool proceeds.

## State Ownership Map

Exclusive writers listed. All other modules submit via the owning module — never write directly.

| State file | Exclusive writer | Readers (no write authority) |
|---|---|---|
| `.wabblespec/receipts/` | Each module (its own receipt only) | Guard, Verifier, Archive, Executor |
| `.wabblespec/memory/drawers/` | Memory module | All L5 modules via Memory write path |
| `.wabblespec/memory/ledger.md` | Provenance | Memory, Forget (notify only) |
| `.wabblespec/memory/index.md` | Memory | MemorySearch, Dream, MemoryMine (read only) |
| `.wabblespec/memory/tracker.json` | Instinct (write), Dream (decay) | Synth (read only) |
| `.wabblespec/session/state.json` | Autopilot, each module (own fields only) | pre-tool-use hook (read only) |
| `framework.yaml` | Manual / path-linter script | All modules (read only) |
| `.wabblespec/meta.md` | Autopilot exclusively | All modules submit change requests |
| `.wabblespec/experiments/` | Factory, Augment, Benchmark | Forge (reads for promotion) |
| `project/repo/` | Apply, Executor, platform modules | All spec/memory/delivery modules (read only) |

## State vs Instructions Hygiene

`state.json` has one job: answer enforcement questions.

- Is enforcement active?
- Which receipts are required before tool use proceeds?
- Which module is currently running?

`state.json` must not be used to inject module instructions, wave implementation guidance, or task context. Module instructions come from `SKILL.md` files loaded per wave. Task context comes from `task-card.md` and `scope.md`. Mixing instructions into state.json creates two problems: (1) instructions become stale without a versioning contract; (2) state.json grows unbounded across waves.

**Practical signal:** if `state.json` exceeds ~40 lines mid-session, it has likely accumulated content that belongs in receipts or SKILL.md files. Audit and trim before the next wave.
