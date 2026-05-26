# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## What This Repository Is

WabbleSpec v6.1: spec-driven, receipt-gated, hook-enforced SDLC framework for single agent runtime. Framework is the product — 99 skill modules across layers L0–L8, `framework.yaml` as canonical module registry.

Current version: **0.23.0** (see `.wabblespec/VERSION`)

## Key Scripts

All scripts require `pip install pyyaml pytest jinja2` (see `.claude/skills/skill-factory/requirements.txt`). All scripts in `_shared/scripts/`; run any with `--help` for flags.

## The 12 Invariants

Full table: `_shared/references/invariants.md`. Key session rules:

- **I1 SPEC IS SINGLE SOURCE OF TRUTH** — Every execution is grounded in spec. P2 blocked until P1 locked; P3 blocked until P2 locked.
- **I4 VERIFICATION IS EXPLICIT** — Every output passes a declared verification gate. Max 3 REVISE cycles; at 3 failures, Attestation required.
- **I6 RUNTIME IS VENDOR-NEUTRAL** — No model names anywhere in framework files. Use capability descriptors only (`code-generation`, `analysis`, `synthesis`, `long-context`).
- **I10 RECEIPTS ARE OPERATIONAL ARTIFACTS** — Every non-trivial execution writes a receipt. Implied completion is prohibited.
- **I11 FRAMEWORK AND PRODUCT NEVER MIX** — `.wabblespec/` is framework space. `project/repo/` is product space. Never cross the boundary. Apply writes only to `project/repo/`.
- **I8 SELF-IMPROVEMENT THROUGH EVIDENCE** — Evolution chain is Execution → Receipt → Instinct → Synth → Blueprint → Augment → Benchmark → Forge. No stage skips. Self-promotion requires Attestation.

## Quality Floor Gates

Both gates enforced by `quality-floor-check.py`. Details in that script's output (`--verbose` for full check list).

## Framework State (`.wabblespec/`)

**Do not write to `.wabblespec/` from product-space tasks (I11).** Framework modules own all writes here.

Key paths:
- `framework.yaml` — canonical module registry; source of truth for all 99 modules
- `.wabblespec/receipts/` — individual seed run receipts (100 accumulated)
- `.wabblespec/archive/receipt-index.json` — completed task receipt index
- `.wabblespec/memory/` — drawers, entity graph, gap-map, instinct observations
- `.wabblespec/experiments/` — L8 evolution cycle artifacts (candidates, blueprints, augments, fixtures, tracker.json)
- `.wabblespec/plans/` — active task card and wave plan
- `.wabblespec/session/state.json` — session enforcement state (active only during open task)

## Receipt Chain

Every non-trivial task: Research receipt → Plan receipt → Execution receipt → Verifier receipt → Archive receipt. Each phase reads the prior phase's receipt. Skip requires `collapse_eligible: true` in recipe.json plus complexity below threshold.

## Staleness States

Drawer evidence states and decay rules: `_shared/references/staleness-states.md`. `EXPIRED` evidence emits `STALENESS_VIOLATION` (I9) — Guard pre-tool-use hook enforces.

## L8 Evolution Gate

Gate: **MET** (as of 0.23.0). Gate conditions and current status: `_shared/references/l8-corpus-gate.md`.

## Hook Architecture

Hook files live in `hooks/`. All four JS files are CommonJS modules. `hooks/package.json` sets `{"type": "commonjs"}` to prevent ESM/CJS conflict when an ancestor `package.json` declares `"type": "module"`.

**SessionStart** (`wabblespec-session-start.js`): Runs once per session open. Writes a session flag to `~/.claude/.wabblespec-session`. Emits invariant context and active task state as stdout — Claude Code injects this as a system prompt addendum, so invariants don't need re-stating per turn.

**UserPromptSubmit** (`wabblespec-prompt-guard.js`): Runs before every user prompt. Two informational nudges only — never blocks:
- If active session with completed waves: emits wave progress to prevent Executor drift.
- If no active session and prompt looks like a task-start phrase: reminds to run Recipe first.

**Statusline** (`wabblespec-statusline.ps1`): Reads the flag file and outputs a badge (`[WS idle]` or `[WS task-id w:N/M]`).

**Flag file channel** (`~/.claude/.wabblespec-session`): Shared state between SessionStart hook and statusline. Written by SessionStart via `safeWriteFlag()` (atomic temp+rename, mode 0600, refuses symlinks). Never written by prompt-guard.

**Silent-fail contract**: All hooks catch errors and emit `{}` rather than non-zero exit. Hook failures must not interrupt the session.

## Tool Call Batching

Claude Code executes independent tool calls in parallel. Real effect on seed run speed — use it.

**Rules:**
- All file reads that do not depend on each other go in one response turn.
- All file writes/edits that do not conflict go in one response turn.
- Script executions that are independent (validate-graph + quality-floor-check + complexity-scorer) can be issued as parallel Bash calls.
- Do not chain `Read → Edit → Read` when the second Read is only to confirm — `Edit` succeeds or errors; a re-read is wasted.

**What cannot be parallel:**
- A write that depends on the content of a prior read in the same turn.
- A script whose input is the output of another script in the same turn.
- Receipt writes: each phase's receipt depends on the prior phase's receipt content.

Applies to framework authoring (seed runs, module builds) and product-space tasks equally.
