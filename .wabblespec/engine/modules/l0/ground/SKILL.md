---
name: ground
description: Pre-execution hallucination check. Verifies EARS/GWT requirements against actual repo state before Executor begins. Flags claims that cannot be confirmed in files. Runs after Decompose, before Executor wave 1. Produces ground receipt with verified/unverified/missing classifications.
---

# Ground

You run before the first wave. You verify that what the spec claims about the current codebase is actually true. Unverified claims are not rejected — they are flagged as NOT_GROUNDED so Executor and Verifier know they are operating on unconfirmed assumptions.

## What this skill does

Reads the locked task card and wave plan. For each claim about current state (file exists, API exists, function exists, behavior currently works), checks the actual repo. Flags claims that cannot be confirmed. Writes ground receipt with three buckets: VERIFIED (confirmed in files), UNVERIFIED (cannot confirm — treat as assumption), MISSING (claim depends on artifact that does not exist).

## When to use / when not to use

**Use when:**
- Before Executor wave 1 on any Medium or High complexity task
- Explicit `/ground` command
- Recipe marks target as requiring ground check (AI/Agent, Data/Pipeline targets always require it)

**Do not use when:**
- Task card is COSMETIC only (no behavioral claims to verify)
- Scope is L0 (trivial — no prior state claimed)
- Ground receipt already exists and is FRESH for this task card

## Inputs

- `.wabblespec/plans/task-card.md` (locked)
- `.wabblespec/plans/wave-plan.md` (wave 1 declaration)
- product space (actual codebase to verify against)

## How to do it

### Step 1 — Extract state claims

Read task card and wave plan. Extract every claim about current state:
- "File X exists at path Y"
- "Function F exists in module M"
- "API endpoint /path returns schema S"
- "Configuration key K is set in file F"
- "Test T currently passes"
- "Behavior B currently works"
- "Dependency D is installed at version V"

State claims are statements about WHAT IS NOW, not what will be after execution.

### Step 2 — Classify each claim

| Claim type | Verification method |
|---|---|
| File existence | `Path.exists()` check |
| Function/class existence | Grep for symbol in declared file |
| API endpoint | Check route file for path declaration |
| Config key | Read config file, check for key |
| Dependency | Check package manifest for dependency |
| Behavioral claim | Mark UNVERIFIABLE — cannot run code |
| Test claim | Check test file for test name, mark UNVERIFIABLE for pass/fail |

### Step 3 — Verify each claim

For VERIFIABLE claims: check the actual file. Record result.
For UNVERIFIABLE claims: mark as ASSUMED — flag in receipt but do not block.

### Step 4 — Write ground receipt

Three buckets:
- `verified`: claims confirmed against actual files (with file path evidence)
- `unverified`: claims that could not be confirmed (file not found, symbol absent)
- assumed: claims that are structurally unverifiable (behavior, runtime state) — flagged but not errors
- `missing`: claims that require artifacts that do not exist at all

## Output contract

**Ground receipt** at `.wabblespec/receipts/ground-receipt.json` with:

```json
{
  "module": "ground",
  "layer": "L0",
  "task_card_path": ".wabblespec/plans/task-card.md",
  "status": "PASS|PARTIAL|BLOCK",
  "claims_total": 0,
  "verified": [],
  "unverified": [],
  "assumed": [],
  "missing": [],
  "block_reason": null,
  "grounded_at": "ISO-8601"
}
```

**Status rules:**
- `PASS`: all verifiable claims confirmed, no missing artifacts
- `PARTIAL`: some claims unverified — Executor proceeds with UNVERIFIED flags on affected criteria
- `BLOCK`: missing artifacts that are declared prerequisites for wave 1 — Executor halted until resolved

## What not to do

- Do not run the codebase (no `exec`, no subprocess calls to test runners)
- Do not modify any file — read only
- Do not block on UNVERIFIABLE claims — only on MISSING prerequisites
- Do not skip PARTIAL results — every unverified claim must appear in receipt
- Do not invent file contents — verify only what can be confirmed by reading

## Integration

| Module | Relationship |
|---|---|
| Decompose | Ground reads wave plan produced by Decompose |
| Executor | Executor reads ground receipt before wave 1; BLOCK halts wave 1 |
| Verifier | Verifier reads ground receipt to know which criteria were pre-confirmed vs assumed |
| Provenance | Provenance notified of MISSING claims — marks affected drawers NEEDS_REVERIFICATION |
| Triage | BLOCK status routes to Triage for resolution |
