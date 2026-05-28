# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## What This Repository Is

WabbleSpec v6.1: spec-driven, receipt-gated, hook-enforced SDLC framework for single agent runtime. Framework is the product — 100 skill modules across layers L0–L8, `.wabblespec/wabblespec.yaml` as canonical module registry.

Current version: **0.39.0** (see `.wabblespec/VERSION`)

## Key Scripts

All scripts in `.wabblespec/engine/shared/scripts/`; run any with `--help`. Required deps: `pip install pyyaml duckdb` (duckdb for receipt-db.py).

**Pipeline automation (all sessions):**
- `archive.py` — CHANGELOG + VERSION + delivery receipt + receipt-index (replaces manual Archive steps)
- `receipt-writer.py` — 17 receipt types; auto-upserts into DuckDB if DB exists; use `--no-db` to skip
- `guard-check.py` — Layers 4+5 (authority + command risk + receipt chain via `chain` subcommand)

**Session lifecycle:**
- `session-state.py` — init/show/set/complete/clear session state.json
- `session-registry.py` — create/list/close/purge namespaced session directories
- `recipe-writer.py` — write recipe.json
- `task-card-writer.py` — write task-card.md from CLI args
- `wave-plan-writer.py` — write current-wave-plan.md from wave JSON
- `scope-writer.py` — write scope.md from CLI args

**Receipt store:**
- `receipt-db.py` — DuckDB store; `init`, `import`, `query`, `stats`, `export` subcommands
- `wave-queue.py` — file-locked parallel wave task queue

**Analysis and validation:**
- `quality-floor-check.py` — Gate 1 + Gate 2 for all 100 modules; `--verbose` for full detail
- `validate-graph.py` — module registry integrity
- `agent-output-validator.py` — validate JSON output from skill subagents

**Memory layer:**
- `drawer-writer.py` — write file-based drawer JSON
- `provenance-append.py` — append to provenance ledger

**Background scripts (fired by stop-hook via daemon-config.json):**
- `dream.py` — EMA decay + gap-map + staleness-map (on_stop)
- `quality-floor-check.py` — regression check (on_archive)
- `index-update.py` — regenerate INDEX.md managed sections (on_archive)
- `receipt-db.py import` — sync JSON receipts to DuckDB (on_archive)
- `memory-mine.py` — closet indexing (on_stop, enabled at 50+ drawers)
- `entity-graph.py` — graph update (on_stop)

**Engine scripts (not in shared/scripts/):**
- `.wabblespec/engine/scripts/wabblespec-sync-skills.py` — sync engine/modules/ → .claude/skills/; use `--filter-recipe .wabblespec/state/recipe.json` to sync only the skills declared in `active_skills:` (run without flag to restore all)
- `.wabblespec/engine/scripts/stop-hook.py` — Stop hook orchestrator

**Selective skill preloading:**
Add `--skills <name>` (repeatable) to `recipe-writer.py` to declare which skills are active for the session. This writes `active_skills: [...]` to recipe.json. Then run sync with `--filter-recipe` to limit `.claude/skills/` to only those skills. Run sync without `--filter-recipe` at session end to restore all 100 skills. Sessions that omit `--skills` default to all skills.

## The 12 Invariants

Full table: `.wabblespec/engine/shared/references/invariants.md`. Key session rules:

- **I1 SPEC IS SINGLE SOURCE OF TRUTH** — Every execution is grounded in spec. P2 blocked until P1 locked; P3 blocked until P2 locked.
- **I4 VERIFICATION IS EXPLICIT** — Every output passes a declared verification gate. Max 3 REVISE cycles; at 3 failures, Attestation required.
- **I6 RUNTIME IS VENDOR-NEUTRAL** — No model names anywhere in framework files. Use capability descriptors only (`code-generation`, `analysis`, `synthesis`, `long-context`).
- **I10 RECEIPTS ARE OPERATIONAL ARTIFACTS** — Every non-trivial execution writes a receipt. Implied completion is prohibited.
- **I11 FRAMEWORK AND PRODUCT NEVER MIX** — `.wabblespec/` is framework space. Project root (excluding `.wabblespec/`, `.claude/`, `.git/`) is product space. Never cross the boundary. Apply writes only to product space.
- **I8 SELF-IMPROVEMENT THROUGH EVIDENCE** — Evolution chain is Execution → Receipt → Instinct → Synth → Blueprint → Augment → Benchmark → Forge. No stage skips. Self-promotion requires Attestation.

## Quality Floor Gates

Both gates enforced by `quality-floor-check.py`. Details in that script's output (`--verbose` for full check list).

## Framework State (`.wabblespec/`)

**Do not write to `.wabblespec/` from product-space tasks (I11).** Framework modules own all writes here.

Key paths:
- `.wabblespec/wabblespec.yaml` — canonical module registry; source of truth for all 99 modules
- `.wabblespec/state/receipts/` — individual seed run receipts (100 accumulated)
- `.wabblespec/state/archive/receipt-index.json` — completed task receipt index
- `.wabblespec/state/memory/` — drawers, entity graph, gap-map, instinct observations
- `.wabblespec/state/experiments/` — L8 evolution cycle artifacts (candidates, blueprints, augments, fixtures, tracker.json)
- `.wabblespec/state/plans/` — active task card and wave plan
- `.wabblespec/state/session/state.json` — session enforcement state (active only during open task)

**Canonical session state paths** (do not use root-level copies):
- `.wabblespec/state/scope.md` — active session scope (not `.wabblespec/scope.md`)
- `.wabblespec/state/recipe.json` — active session recipe (not `.wabblespec/recipe.json`)

Root-level `scope.md` and `recipe.json` are legacy artefacts from earlier skill versions. Skills and scripts SHALL read from `state/` paths. Root copies are written only for backward compatibility during the Phase 2 migration window.

## Receipt Chain

Every non-trivial task: Research receipt → Plan receipt → Execution receipt → Verifier receipt → Archive receipt. Each phase reads the prior phase's receipt. Skip requires `collapse_eligible: true` in recipe.json plus complexity below threshold.

## Staleness States

Drawer evidence states and decay rules: `.wabblespec/engine/shared/references/staleness-states.md`. `EXPIRED` evidence emits `STALENESS_VIOLATION` (I9) — Guard pre-tool-use hook enforces.

## L8 Evolution Gate

Gate: **MET** (as of 0.23.0). Gate conditions and current status: `.wabblespec/engine/shared/references/l8-corpus-gate.md`.

## Hook Architecture

Hook files live in `.wabblespec/engine/hooks/`. All four JS files are CommonJS modules. `hooks/package.json` sets `{"type": "commonjs"}` to prevent ESM/CJS conflict when an ancestor `package.json` declares `"type": "module"`.

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

## Skill Authoring Conventions

**Tool references in SKILL.md files use capability placeholders, not provider names (extends I6).**

When a SKILL.md references an external tool by capability — an MCP server, external API, CLI tool, or data connector — use the `~~capability-name` placeholder form rather than hardcoding a provider name or tool prefix. Examples:

- `~~search-console` (not `mcp__google__searchConsole` or `gcloud`)
- `~~vector-store` (not `mcp__chroma__*` or a hardcoded ChromaDB path)
- `~~code-runner` (not `bash` or a specific interpreter name)

The shared skill preamble or Guard resolves `~~capability-name` to the active provider at runtime. Skills written this way work with any conforming provider and never require edits when a backend changes.

**Reference routing over inline documentation.** When a SKILL.md section has a dedicated reference document, add a `## Reference Routing` table and route the situation to that file rather than duplicating the content inline. Each routing entry replaces (not supplements) the corresponding inline block — SKILL.md line counts must go down when routing tables are added.
