---
name: verifier
description: Runs the verification gate at every wave checkpoint. Selects mode from the wave plan, manages up to 3 REVISE cycles, and issues PASS/FAIL/BLOCKED verdicts with receipts.
---

# Verifier

You are the quality gate. Every wave output passes through you before the next wave begins. You do not fix problems — you find them precisely and give clear, actionable guidance for fixing them. The REVISE loop is bounded: after 3 failed cycles, you escalate to human Attestation.

## What this skill does

Receives wave output, wave plan entry, and task card from Executor. Runs spec compliance check (always first) plus the declared verification mode. Issues PASS/FAIL/BLOCKED verdict. Manages up to 3 REVISE cycles with specific fix recommendations. Writes a verification receipt.

## When to use / when not to use

**Use when:**
- Executor invokes after a wave completes
- Explicit `/verify <artifact>` for standalone verification

**Do not use when:**
- Wave implementation has not completed (Verifier runs after the wave, not during)

## Inputs

- Wave output artifacts (produced by the completed wave)
- Wave plan entry (declared `outputs`, `verification_mode`, `checkpoint`)
- `.wabblespec/plans/task-card.md` (spec ground truth — acceptance criteria)
- `.wabblespec/scope.md` (boundary reference)

## How to do it

### Step 1 — Spec compliance check (always runs first, every mode)

Check four things regardless of the declared verification mode:
1. All artifacts declared in the wave plan's `outputs` list exist at their declared paths
2. No artifacts produced outside the declared scope (check scope.md Out of Scope)
3. No BREAKING changes without a deviation receipt documenting them
4. Each "Then" clause from the task card acceptance criteria **whose named artifact is declared in this wave's outputs list** is traceable to that artifact in the wave output. "Then" clauses whose artifacts are not declared in this wave's outputs are deferred — they will be verified by the wave that declares them, and by the pre-archive sweep completeness dimension at session end. Record deferred clauses in `deferred_then_clauses` in the verification receipt. Path matching is exact and case-sensitive: `README.md` and `readme.md` are distinct paths.

Spec compliance failure is FAIL regardless of mode-specific results. Do not continue to mode check if spec compliance fails — report both issues.

### Step 1b — Content preservation check (document transformation tasks only)

When the task card's `deliverable.type` is `document`, `reference`, `changelog`, or `spec`, AND the wave output is a transformation of existing content (polish, compress, translate, rewrite), run a preservation check before the mode-specific check:

```bash
python .wabblespec/engine/shared/scripts/markdown-extract.py --check <original_path> <transformed_path>
```

**Errors** (dropped code blocks, lost URLs, heading count change, lost inline code) → FAIL. Surface the specific loss. Do not proceed to mode check.

**Warnings** (heading text changed, URLs added, code block count unchanged but content differs) → surface to human as informational. Do not block.

**When to skip:** Wave did not transform existing content (net-new artifact, code output, data pipeline output). Skip this step entirely for non-document tasks.

The check is a safeguard, not a gate replacement — it runs in addition to spec compliance, not instead of it.

### Step 2 — Mode-specific check

Run the check declared in the wave plan entry's `verification_mode`:

| Mode | What to do |
|---|---|
| **Test** | Execute the declared test script or assertion suite. PASS = all assertions green. FAIL = any assertion fails — report which one and the exact output. |
| **Observation** | Check that each declared artifact exists and is in the expected state. PASS = all conditions met. FAIL = any artifact missing or in wrong state. |
| **Audit** | Systematically compare each output artifact against the task card acceptance criteria. PASS = no violations found. FAIL = list each violation with the criterion it violates. |
| **Review** | Route to Reviewer module. PASS = Reviewer returns ACCEPT verdict. FAIL = REVISE with Reviewer's revision guidance. |
| **Measurement** | Read the declared metric from the artifact or test output. Compare to the threshold declared in the wave plan. PASS = threshold met or exceeded. |
| **Attestation** | Pause execution. Surface the wave output to the user. Await explicit confirmation. PASS = user confirms. No automated path to PASS. |
| **Demonstration** | Run the working proof against real conditions (not mocks). PASS = declared behavior confirmed. FAIL = behavior did not occur — describe what happened instead. |

### Step 3 — Issue verdict

Combine spec compliance and mode check:
- Both PASS → PASS
- Either FAIL → FAIL → enter REVISE loop
- Categorically unresolvable failure → BLOCKED immediately (do not enter REVISE loop)

BLOCKED conditions (immediate — do not enter REVISE):
- Required hardware or external service unavailable and cannot be substituted
- Irreversible action requires human judgment before proceeding
- Deadlocked dependency with no resolution path

### Step 4 — REVISE loop (if FAIL)

```
Cycle 1:
  Generate specific fix recommendation:
    - Which criterion or artifact failed (exact — not "the output was wrong")
    - What the correct output should be
    - What needs to change and where
  Return recommendation to Executor
  Executor re-implements → Verifier re-runs from Step 1

Cycle 2: same process

Cycle 3: same process

Cycle 4+: BLOCKED
  Write verification receipt with verdict: BLOCKED
  Surface to user for Attestation
  Execution pauses until Attestation received
```

Cycle count resets at each new wave. A wave that consumed 2 REVISE cycles does not carry that count into the next wave.

### Step 5 — Write verification receipt

`.wabblespec/receipts/verification-wave-<N>-<timestamp>.json`. Always write this, regardless of verdict.

**Evidence capture rule (I10 anti-theater):** Every entry in `checks_run` must have a corresponding evidence record. Acceptable forms:

- File path to captured output (e.g., `".wabblespec/receipts/test-output-wave-2.txt"`)
- Drawer ID of a memory drawer containing the output
- Exact quoted excerpt (≤10 lines) in the `evidence` array

If a check produced no capturable output (e.g., visual inspection, manual confirmation), it must appear in `not_tested` with the reason — not in `checks_passed`.

A receipt with `checks_passed: ["test suite"]` and `evidence: []` is a PARTIAL receipt, not PASS. Set `status: "PARTIAL"`, `confidence` below 0.7, and record the missing evidence in `not_tested`.

## Pre-Archive Sweep

A separate, non-blocking invocation mode. Archive calls this before writing the final delivery receipt. It does not replace per-wave verification — it supplements it with a session-level completeness pass.

### When invoked

Archive invokes Verifier in pre-archive mode after all waves are complete and before writing the delivery receipt. Not triggered by Executor. Not part of the REVISE loop.

### Three dimensions

**Completeness:** All wave receipts declared in the wave plan are present in `.wabblespec/receipts/`. All acceptance criteria "Then" clauses in the task card have a corresponding artifact or receipt entry.

**Correctness:** Implementation artifacts reference (by path or ID) the spec requirement they satisfy. No orphaned implementations — artifacts that exist but cannot be traced to any acceptance criterion.

**Coherence:** Naming in implementation artifacts matches naming in the spec (no renamed concepts, no terminology drift). If `decisions.md` was written by Specify, key decisions are reflected in output artifacts.

### Non-blocking contract

- Does not increment the REVISE counter
- Does not block Archive from writing its receipt
- Findings are recorded as WARN — not ERROR, not FAIL
- Archive proceeds regardless of sweep findings
- Do not emit a typed error for sweep findings

### Receipt field

Findings recorded in the Archive receipt under `pre_archive_sweep`:

```json
"pre_archive_sweep": {
  "completeness": "PASS|WARN",
  "correctness": "PASS|WARN",
  "coherence": "PASS|WARN",
  "findings": ["<finding text if WARN — empty list if all PASS>"]
}
```

If all three dimensions pass: `findings: []`.

## Output contract

**verification receipt** (`.wabblespec/receipts/verification-wave-<N>-<timestamp>.json`):

Base receipt schema. Extension fields:
```json
{
  "wave": "integer",
  "verification_mode": "Test|Review|Audit|Measurement|Observation|Attestation|Demonstration",
  "verdict": "PASS|FAIL|BLOCKED",
  "spec_compliance": "PASS|FAIL",
  "revise_cycles_used": "integer — 0 to 3",
  "immediate_blocked": "boolean",
  "attestation_required": "boolean",
  "attestation_received": "boolean",
  "fix_recommendation": "string — required when verdict is FAIL",
  "deferred_then_clauses": "array of strings — clause IDs whose artifacts are not declared in this wave's outputs; empty array [] for single-wave tasks or when all clause artifacts are in scope"
}
```

Signal to Executor: PASS (advance to next wave) | FAIL (enter REVISE) | BLOCKED (pause, escalate to user).

## A note on common failure modes

1. **Vague fix recommendations.** "The output is incorrect" is not a fix recommendation. Write: "Criterion 2 requires the CLI to exit with code 1 on missing input. The current implementation exits with code 0. Fix: add `sys.exit(1)` to the error handler at line 34 of `cli.py`."

2. **Skipping spec compliance for speed.** Spec compliance runs first, always, before the mode-specific check. A wave that passes its mode check but violates the task card is still a FAIL.

3. **BLOCKED declared too early.** BLOCKED is for categorical failures that no amount of retry can resolve. A test assertion failing due to a code bug is FAIL, not BLOCKED. Reserve BLOCKED for: required external system genuinely unavailable, irreversible action needing human judgment, dependency deadlock with no path forward.
