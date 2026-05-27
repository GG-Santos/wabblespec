# Guard Policy Reference

**Module:** l2/guard  
**Consumed by:** l2/executor (pre-wave), l2/triage (violation resolution), l2/grader (audit), l2/reviewer (SPEC_VIOLATION routing)  
**Purpose:** Quick-reference for Guard's 5-layer validation policy. For full Guard behavior see `modules/l2/guard/SKILL.md`.

---

## When Guard runs

Guard runs before every Executor wave. It cannot be skipped. A wave that proceeds without a Guard PASS receipt is an **I4 violation**, independently enforced by the pre-tool-use hook.

Guard also runs on explicit `/guard <input>` invocation for standalone validation.

---

## The 5 validation layers

Layers run in sequence. A HARD violation stops all subsequent layers and returns immediately.

### Layer 1 — Schema validation

Checks all wave inputs against their declared schemas.

| Finding | Action |
|---|---|
| Missing required fields | HARD — abort wave |
| Malformed input (JSON/YAML parse error) | HARD — abort wave |
| Unknown optional fields | SOFT warning — log to receipt, proceed |

### Layer 2 — Scope constraint (I12)

Verifies the wave task is within `scope.md` boundaries.

| Finding | Action |
|---|---|
| Wave targets a file in "Out of Scope" | SPEC_VIOLATION — halt, route to human |
| Wave expands scope beyond current task card stage | SPEC_VIOLATION — loop back to ScopeFrame |

### Layer 3 — Invariant compliance

| Invariant | Check description | Violation result |
|---|---|---|
| I1 | Locked task card exists | SPEC_VIOLATION |
| I2 | Plan receipt exists before Execute phase | SPEC_VIOLATION |
| I3 | Build target declared in recipe.json | SPEC_VIOLATION |
| I6 | No model names in wave inputs (capability descriptors only) | SPEC_VIOLATION |
| I9 | No EXPIRED evidence in wave inputs | HARD — quarantine |
| I10 | Prior wave receipt exists (wave N needs wave N-1) | DEPENDENCY — pause |
| I11 | Wave writes only to product space (not `.wabblespec/` framework space) | HARD — abort |
| I12 | Task card input not bloated (criteria count reasonable) | SPEC_VIOLATION |

**Memory backend invariants** (added 2026-05-24, enforced when wave plan includes Memory / MemorySearch / MemoryMine / EntityGraph):

| Invariant | Check | Violation result |
|---|---|---|
| `WABBLESPEC_MEMORY_READY` | `WABBLESPEC_MEMORY_PATH` env var set | HARD — abort; "Run bootstrap script" |
| `CHROMADB_EXISTS` | `.wabblespec/memory/chroma.sqlite3` present | HARD — abort; "Run migrate-json-drawers.py" |
| `CLOSET_INDEX_GATE` | Closet indexing only when ChromaDB drawer count ≥ 50 | SPEC_VIOLATION — route to Reviewer |

### Layer 4 — Authority check

Verifies the requesting module has declared authority over its target files via `skill-rules.json`.

| Finding | Action |
|---|---|
| Target path not in `authority.owns` | HARD — abort, log violation |
| Module has no `skill-rules.json` | HARD — abort (I5 violation) |
| `file_path_patterns` declared but no wave files match | SOFT warning — log `misactivation_risk: true`, proceed |

### Layer 5 — Command risk gate

**Only runs when wave plan contains shell commands** (`bash_command`, `shell`, or equivalent fields). Skipped (`layer_5_command_risk: "SKIP"`) for waves with no shell operations.

Classifies shell commands against `.wabblespec/engine/shared/references/command-risk-policy.md`.

| Classification | Action |
|---|---|
| SAFE | Proceed — no annotation required |
| WARN | Proceed — add to `command_warnings` list; Executor must log rationale |
| BLOCK | HARD — abort; return COMMAND_RISK error with safer alternative |

**Classification rules:**
1. SAFE patterns checked first — a SAFE match terminates classification for that command.
2. For piped commands, classify each segment independently; highest tier wins.
3. Unresolved shell variables (`$UNKNOWN`, `*` wildcards) in WARN-or-above patterns escalate one tier.
4. Novel commands matching no pattern default to WARN.

**BLOCK error message format:**
```
COMMAND_RISK: "<command>" is classified BLOCK.
Reason: <risk from policy table>
Safer alternative: <alternative from policy table>
Wave cannot proceed. Remove or replace this command before re-submitting.
```

---

## Guard receipt fields

Written to `.wabblespec/receipts/guard-wave-{N}-receipt.json`:

```json
{
  "wave_id": "integer",
  "layer_1_schema": "PASS|FAIL",
  "layer_2_scope": "PASS|FAIL|SPEC_VIOLATION",
  "layer_3_invariants": "PASS|FAIL|SPEC_VIOLATION",
  "layer_4_authority": "PASS|FAIL|WARN",
  "misactivation_risk": "boolean",
  "layer_5_command_risk": "PASS|WARN|BLOCK|SKIP",
  "command_warnings": ["string — WARN-classified commands"],
  "overall": "PASS|FAIL",
  "violations": ["string — description of each violation"]
}
```

---

## Error types Guard emits

| Layer | Error type | Schema routing action |
|---|---|---|
| 1 — schema | HARD | halt |
| 2 — scope (out-of-scope) | SPEC_VIOLATION | loop_back |
| 3 — I9 (expired evidence) | HARD | halt |
| 3 — I10 (missing prior receipt) | DEPENDENCY | pause |
| 3 — I11 (boundary) | HARD | halt |
| 3 — other invariants | SPEC_VIOLATION | loop_back |
| 4 — authority | HARD | halt |
| 5 — command BLOCK | HARD | halt |

All error events conform to `.wabblespec/engine/shared/schemas/error-event.schema.json`. See `.wabblespec/engine/shared/references/error-event-catalog.md` for per-error message templates.

---

## Common failure modes

**1. Skipping Guard because it slows things down.**  
Guard is not optional. The pre-tool-use hook blocks this at the infrastructure level independently of LLM compliance. Bypassing Guard is an I4 violation that the hook enforces.

**2. Fixing violations inside Guard.**  
Guard validates and reports — it does not repair. A Guard that silently repairs inputs produces false PASS receipts and defeats the audit trail. Return the typed error, let the appropriate module resolve it.

**3. Authority matrix out of date.**  
When a new module is added without updating its `skill-rules.json` `authority.owns` list, Guard will HARD block it. Fix the `skill-rules.json`, not Guard's rules.

**4. Memory backend not initialized.**  
If `WABBLESPEC_MEMORY_PATH` is unset or `chroma.sqlite3` is absent, any wave touching Memory HARD errors at Layer 3. Resolution: ensure the bootstrap script ran at session start. The Stop hook handles this automatically after Phase 1 is complete.

**5. SPEC_VIOLATION routing confusion.**  
`SPEC_VIOLATION` routes to `loop_back` — it returns to the module that violated the spec (usually ScopeFrame or Reviewer), not to the human. `HARD` routes to `halt` — that is the human-intervention path.

---

## Cross-references

- `modules/l2/guard/SKILL.md` — full Guard implementation spec
- `.wabblespec/engine/shared/references/invariants.md` — full invariant definitions (I1–I12 and Memory variants)
- `.wabblespec/engine/shared/references/command-risk-policy.md` — SAFE/WARN/BLOCK command classification table
- `.wabblespec/engine/shared/references/error-event-catalog.md` — per-module error event registry with user-facing message templates
- `.wabblespec/engine/shared/schemas/error-event.schema.json` — typed error event schema
- `.wabblespec/engine/shared/schemas/skill-rules.schema.json` — authority declaration schema
