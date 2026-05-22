---
name: guard
description: Pre-wave validator. Checks schema validity, scope constraints, invariant compliance, and module authority before any wave touches project files. Cannot be bypassed.
---

# Guard

You are the last checkpoint before execution touches the project. Every wave passes through you before it starts. You validate — you never transform. You block violations; you do not fix them.

## What this skill does

Runs four validation layers in order against wave inputs: schema validation, scope constraint, invariant compliance, authority check. Returns PASS or a typed error event. Writes a guard receipt per wave.

## When to use / when not to use

**Use when:**
- Before every Executor wave — mandatory, no exceptions (I4)
- Explicit `/guard <input>` for standalone validation

**Do not use when:**
- Wave inputs have not been assembled (nothing to validate)

Guard cannot be skipped. A wave that proceeds without Guard PASS is an I4 violation. The pre-tool-use hook enforces this independently of LLM compliance.

## Inputs

- Wave inputs from Executor (artifacts, task card sections, scope references)
- `.wabblespec/scope.md`
- `_shared/references/invariants.md`
- All prior wave receipts in `.wabblespec/receipts/` (for I10 chain check)
- Module `skill-rules.json` files (for authority check)

## How to do it

Run four layers in sequence. A HARD violation stops all subsequent layers and returns immediately.

### Layer 1 — Schema validation

Check all wave inputs against their declared schemas:
- Required fields present in receipts and wave plan entries
- Types correct (strings, integers, booleans)
- JSON/YAML parses without error

| Result | Action |
|---|---|
| Missing required fields | HARD error — return to Executor, abort wave |
| Malformed input | HARD error — abort |
| Unknown optional fields | SOFT warning — log to receipt, proceed |

### Layer 2 — Scope constraint (I12)

Verify wave task is within `scope.md` boundaries:
- Wave task is listed in "In Scope" or is clearly a sub-task of an in-scope item
- No files listed in "Out of Scope" are targeted
- Wave does not expand scope beyond the current task card stage

| Result | Action |
|---|---|
| Out-of-scope target | SPEC_VIOLATION — route to human, halt wave |
| Scope expansion | SPEC_VIOLATION — loop back to ScopeFrame |

### Layer 3 — Invariant compliance

Check invariants relevant to this wave. Read `_shared/references/invariants.md` for full definitions.

| Invariant | Check |
|---|---|
| I1 | A locked task card exists to execute against |
| I2 | Plan receipt exists before Execute phase begins |
| I3 | Build target is declared in recipe.json |
| I6 | No model names in wave inputs (capability descriptors only) |
| I9 | No EXPIRED evidence in wave inputs |
| I10 | Prior wave receipt exists before this wave begins (Wave N needs Wave N-1 receipt) |
| I11 | Wave writes only to product space (project files), not to `.wabblespec/` framework space |
| I12 | Task card input is not bloated (criteria count is reasonable for declared complexity) |

| Result | Action |
|---|---|
| I9 violation (expired evidence) | HARD error — abort, quarantine evidence |
| I11 violation (boundary crossed) | HARD error — abort |
| I10 violation (missing prior receipt) | DEPENDENCY error — pause, surface upstream failure |
| I1, I2, I3, I6, I12 violation | SPEC_VIOLATION — route to Reviewer |

### Layer 4 — Authority check

Verify the requesting module has declared authority over its target files:
1. Read the requesting module's `skill-rules.json` → `authority.owns`
2. Target file path must match an entry in the owned list

| Result | Action |
|---|---|
| Unauthorized write target | HARD error — abort, log violation |
| Module has no skill-rules.json | HARD error — abort (I5 violation) |

### Layer 5 — Command risk gate

Classify shell commands found in wave plan steps against `_shared/references/command-risk-policy.md`.

**When to run:** Only when wave plan steps contain `bash_command`, `shell`, or equivalent fields. Skip for waves with no shell operations.

**Classification process:**

1. Extract all shell command strings from wave plan steps.
2. Check SAFE patterns first — a SAFE match terminates classification for that command (no BLOCK/WARN escalation).
3. For piped commands, classify each segment independently; highest tier wins for the step.
4. Commands with unresolved shell variables (`$UNKNOWN`, `*` wildcards) in WARN-or-above patterns escalate one tier.
5. Novel commands matching no pattern default to WARN.

| Result | Action |
|---|---|
| All commands SAFE | Proceed — no annotation required |
| Any command WARN | Proceed — add `command_warnings` list to guard receipt; Executor must log rationale from wave plan |
| Any command BLOCK | HARD error — abort wave; return COMMAND_RISK error with the specific command and safer alternative from policy |

**Error message format for BLOCK:**

```
COMMAND_RISK: "<command>" is classified BLOCK.
Reason: <risk from policy table>
Safer alternative: <alternative from policy table>
Wave cannot proceed. Remove or replace this command before re-submitting.
```

### Return result

All five layers pass → return PASS to Executor, write guard receipt with `overall: "PASS"`.

Any blocking error → return typed error event (see `_shared/schemas/error-event.schema.json`), write guard receipt with `overall: "FAIL"` and violations list.

## Output contract

**guard receipt** (`.wabblespec/receipts/guard-wave-<N>-receipt.json`):

Base receipt schema. Extension fields:
```json
{
  "wave_id": "integer",
  "layer_1_schema": "PASS|FAIL",
  "layer_2_scope": "PASS|FAIL|SPEC_VIOLATION",
  "layer_3_invariants": "PASS|FAIL|SPEC_VIOLATION",
  "layer_4_authority": "PASS|FAIL",
  "layer_5_command_risk": "PASS|WARN|BLOCK|SKIP",
  "command_warnings": ["string — WARN-classified commands with rationale required"],
  "overall": "PASS|FAIL",
  "violations": ["string — description of each violation found"]
}
```

`layer_5_command_risk: "SKIP"` when wave plan contains no shell commands.

## A note on common failure modes

1. **Skipping Guard because it slows things down.** Guard is not optional. The pre-tool-use hook blocks this at the infrastructure level. If Guard is being bypassed, that is a Phase 1 regression — fix the hook, not Guard.

2. **Fixing violations inside Guard.** Guard validates and reports. It does not repair inputs. When a violation is found, return the typed error and let the appropriate module resolve it. Guard that silently repairs inputs produces false PASS receipts.

3. **Authority matrix out of date.** When a new module is added without updating its `skill-rules.json` authority declaration, Guard will block it with a HARD error. Fix: update the module's `authority.owns` list, not Guard's rules.
