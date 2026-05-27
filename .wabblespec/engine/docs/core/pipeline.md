# Pipeline

The standard WabbleSpec execution pipeline. Every pipeline run produces a receipt at each stage. The run is not complete until Archive writes a delivery receipt.

## Stage sequence

```
Recipe → ScopeFrame → Specify → Decompose → [Gateway] → Executor → Verifier → Archive
```

Each stage is a discrete module invocation. Stages are ordered — a stage does not run until the previous stage's receipt is written and PASS.

## Stage reference

### Recipe (L0)
**Activator:** `/recipe` or session start with a new task description.
**Does:** Captures the raw task request. Detects platform target (CLI, Web, API-Service, etc.). Detects complexity (Low/Medium/High). Sets `input_vague` flag if input needs clarification.
**Writes:** `recipe-receipt-{run-id}.json`
**Branches:** If `input_vague = true` → triggers Enhance (L1) before ScopeFrame.

### ScopeFrame (L1)
**Activator:** After Recipe receipt PASS.
**Does:** Converts the recipe into a bounded scope: what is in, what is out, constraints, success criteria. Locks the scope for the run.
**Writes:** `scopeframe-receipt-{run-id}.json`

### Specify (L1)
**Activator:** After ScopeFrame receipt PASS.
**Does:** Produces the technical specification. Uses the active platform package (L3) to apply platform-specific constraints and templates. Output is a spec the Decompose stage can break into waves.
**Writes:** `specify-receipt-{run-id}.json`
**Variants:** `--patch` for ADDITIVE/COSMETIC changes (skips full spec rewrite).

### Decompose (L1)
**Activator:** After Specify receipt PASS.
**Does:** Breaks the spec into an ordered wave plan. Each wave has a declared checkpoint and rollback target. Assigns a complexity score (1–10) to the overall plan. Writes the wave plan to `.wabblespec/state/plans/wave-current.md`.
**Writes:** `decompose-receipt-{run-id}.json`, `.wabblespec/state/plans/wave-current.md`

### Gateway checks (L4) — conditional
**Activator:** Triggered by platform declaration + task tags. Not every run requires a gateway.
**When required:** Medium/High complexity tasks; targets tagged security, auth, payments, PII, AI/LLM output, or design/UX.
**Does:** Applies domain-specific safety checks. Returns PASS, FLAG, or BLOCK.
**BLOCK:** Executor does not run. Surfaced to human. Execution paused.
**FLAG:** Non-blocking warning. Recorded in delivery receipt.
**Sequence when multiple gateways apply:** security → engineering → AI → aesthetic/design/experience (parallel).
**Writes:** `gateway-{domain}-receipt-{run-id}.json`

### Executor (L2)
**Activator:** After Decompose PASS and all required gateway PASses.
**Does:** Executes the wave plan wave by wave. Each wave modifies product space. Writes a wave receipt after each wave. Halts on wave failure — does not continue to next wave.
**Writes:** `executor-receipt-{run-id}.json`, wave receipts per wave.
**Authority:** Only writes to product space. Never touches `.wabblespec/`.

### Verifier (L2)
**Activator:** After Executor receipt PASS.
**Does:** Validates that the execution produced the declared outcomes. Runs checkpoint assertions from the wave plan. Confirms no scope creep. Produces PASS, PARTIAL, or FAIL verdict.
**PARTIAL:** Escalates to human — partial completion is not silently accepted.
**Writes:** `verifier-receipt-{run-id}.json`

### Archive (L7)
**Activator:** After Verifier receipt PASS (or human override on PARTIAL).
**Does:** Aggregates all receipts from the run into a delivery receipt. Bumps `.wabblespec/VERSION` per semver rules. Appends CHANGELOG entry. Updates receipt index.
**Writes:** `delivery-receipt-{run-id}.json`, bumps `VERSION`, appends to `CHANGELOG.md`.

## Run ID convention

`seed-run-YYYYMMDD{a|b|c...}` for pipeline seed runs.
`{task-slug}-YYYYMMDD` for named task runs.

## Incomplete runs

If a session ends without Archive: the receipt index entry stays `IN_PROGRESS`. On next session, Archive `--sweep` mode detects orphaned entries and surfaces them for human review. Do not auto-resolve — partial state may contain valid work.

## Quality floor gate

Before any wave runs, `quality-floor-check.py` confirms all modules pass both gates:
- `quick_validate`: 8 structural checks (required fields, file existence, schema parse)
- `lint_prompts`: 6 content checks (frontmatter, description length, required sections)

Run: `python .wabblespec/engine/shared/scripts/quality-floor-check.py --framework framework.yaml`
