# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## What This Repository Is

WabbleSpec v6.1: spec-driven, receipt-gated, hook-enforced SDLC framework for single agent runtime. Framework is the product — 99 skill modules across layers L0–L8, `framework.yaml` as canonical module registry.

Current version: **0.7.1** (see `.wabblespec/VERSION`)

## Key Scripts

All scripts require `pip install pyyaml pytest jinja2` (see `.claude/skills/skill-factory/requirements.txt`).

```bash
# Validate the module graph (dependency references, shared file consumers)
python _shared/scripts/validate-graph.py

# Record sha256 witness for all module files (SKILL.md + skill-rules.json)
python _shared/scripts/validate-graph.py --record-witness

# Check module files against recorded witness — emits MODULE_FILE_DRIFT on mismatch
python _shared/scripts/validate-graph.py --check-hashes

# Check all modules against both quality floor gates
python _shared/scripts/quality-floor-check.py
python _shared/scripts/quality-floor-check.py --module <id>    # single module
python _shared/scripts/quality-floor-check.py --verbose        # show all checks
python _shared/scripts/quality-floor-check.py --write          # patch framework.yaml

# Validate EARS-syntax requirements in a spec file
python _shared/scripts/ears-validate.py <spec_file> [--test-dir <path>] [--json]

# Score task complexity (deterministic, 0.0–1.0 → L0–L4)
python _shared/scripts/complexity-scorer.py --task-card <path> [--wave-plan <path>] [--json]

# L8 Instinct pattern detection (read-only except instinct-observations.md)
python modules/l8/instinct/scripts/instinct.py --status
python modules/l8/instinct/scripts/instinct.py --dry-run
python modules/l8/instinct/scripts/instinct.py --activate
```

Skill-factory evaluation scripts: `.claude/skills/skill-factory/scripts/` (mirrored to `.agents/skills/skill-factory/scripts/`). For skill building/evaluation only — not WabbleSpec framework.

## Layer Architecture

Modules activate in sequence per session:

| Layer | Modules | Role |
|---|---|---|
| L0 | recipe, runtime-probe | Session start: selects modules, detects runtime capabilities |
| L1 | specify, interview, propose, migrate, clean, test, triage | Spec and planning |
| L2 | guard, executor, autopilot, model-router | Enforcement, execution, orchestration |
| L3 | cli, web, api-service, library, data-pipeline, mobile, desktop, game, extension, iot | Platform-specific targets |
| L4 | gateway-security, gateway-engineering, gateway-ai, gateway-aesthetic, gateway-design, gateway-experience | Cross-cutting standards loaded per session |
| L5 | memory, provenance | Evidence storage and contradiction tracking |
| L6 | document, polish, and output-oriented modules | Delivery-phase output |
| L7 | (deferred/specialized modules) | Advanced transforms |
| L8 | instinct, synth, blueprint, augment, benchmark, forge, retro, feedback | Self-improvement evolution chain |

## Module File Structure

Every standard module (L0–L8) must have:
- `SKILL.md` — prompt file with frontmatter (`name:`, `description:`), `## What this skill does`, `## When to use`, and an output contract section
- `skill-rules.json` — machine-readable rules with required fields: `module`, `layer`, `tier`, `activators`, `authority` (with `owns` list and `reads` list), `verification_mode`, `receipt_required`
- `rules/cold-start.md` — cold-start procedure (required for all 99 modules)
- `tests/acceptance.md` — acceptance criteria (required before any execution receipt is written)

## Shared Artifacts

`_shared/` artifacts consumed across modules:
- `schemas/` — JSON schemas for receipts, errors, drawers, task cards, graph nodes/edges
- `references/` — lookup tables and policies (invariants, error taxonomy, staleness states, etc.)
- `infrastructure/` — cross-cutting principles (economy, guard policy, gateway pattern, version tracking)
- `scripts/` — shared Python utilities
- `templates/` — reusable output templates (legal, changelog, specs, handoffs)
- `dev/` — language, database, API, and framework reference guides

## The 12 Invariants

Govern all operations. Guard and Verifier enforce. Violations emit typed errors (see `_shared/references/error-taxonomy.md`).

Key for daily work:

- **I1 SPEC IS SINGLE SOURCE OF TRUTH** — Every execution is grounded in spec. P2 blocked until P1 locked; P3 blocked until P2 locked.
- **I4 VERIFICATION IS EXPLICIT** — Every output passes a declared verification gate. Max 3 REVISE cycles; at 3 failures, Attestation required.
- **I6 RUNTIME IS VENDOR-NEUTRAL** — No model names anywhere in framework files. Use capability descriptors only (`code-generation`, `analysis`, `synthesis`, `long-context`).
- **I10 RECEIPTS ARE OPERATIONAL ARTIFACTS** — Every non-trivial execution writes a receipt. Implied completion is prohibited.
- **I11 FRAMEWORK AND PRODUCT NEVER MIX** — `.wabblespec/` is framework space. `project/repo/` is product space. Never cross the boundary. Apply writes only to `project/repo/`.
- **I8 SELF-IMPROVEMENT THROUGH EVIDENCE** — Evolution chain is Execution → Receipt → Instinct → Synth → Blueprint → Augment → Benchmark → Forge. No stage skips. Self-promotion requires Attestation.

Full table: `_shared/references/invariants.md`

## Quality Floor Gates

Both gates required for `quality_floor_passed: true` in `framework.yaml`:

**Gate 1 — quick_validate** (8 structural checks): SKILL.md and skill-rules.json exist and parse; required JSON fields present; `authority.owns` non-empty; `receipt_required` is boolean; activators declared.

**Gate 2 — lint_prompts** (6 content checks): SKILL.md has YAML frontmatter with `name:` and `description:` (≥20 chars); contains `## What this skill does` and `## When to use` headings; has an output contract signal; body ≥200 characters.

Modules tagged `security`, `enforcement`, `receipt`, or `gate` must also contain the word `adversarial` in SKILL.md (warning, not gate fail).

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

Drawer evidence states: `FRESH`, `AGING`, `STALE`, `EXPIRED`, `NEEDS_REVERIFICATION`, `SUPERSEDED`. `EXPIRED` evidence emits `STALENESS_VIOLATION` (I9). Guard pre-tool-use hook enforces. Full rules: `_shared/references/staleness-states.md`.

## L8 Evolution Gate

L8 gate: **MET** (as of 0.7.1). 3 modules promoted through full evolution pipeline. Future cycles use `.wabblespec/experiments/`. Gate conditions: `_shared/references/l8-corpus-gate.md`.

## Hook Architecture

Hook files live in `src/hooks/`. All three are CommonJS modules. `src/hooks/package.json` sets `{"type": "commonjs"}` to prevent ESM/CJS conflict when an ancestor `package.json` declares `"type": "module"`.

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
