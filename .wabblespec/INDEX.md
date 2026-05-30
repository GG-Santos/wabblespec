# WabbleSpec Index

Initialized: 2026-05-21T07:42:31.889328+00:00

Module registry and session index.

## Active Modules

<!-- auto-updated: index-update.py -->
111 modules registered in `framework.yaml`. See `framework.yaml` for canonical registry — this file tracks session-level state only.
<!-- end auto-updated -->

## Session State

Current session state: `session/state.json`. Enforcement active only during an open task session.

## Receipt Archive

<!-- auto-updated: index-update.py -->
Completed tasks: `.wabblespec/state/archive/receipt-index.json` (65 entries).

Seed pipeline receipts: `.wabblespec/state/receipts/` — 478 individual receipts accumulated.
<!-- end auto-updated -->

## Research Outputs

Feature-scoped research lives in `research/{feature-slug}/research.md` (written when `spec_binding` present in research-log call). Session receipts at `.wabblespec/receipts/research-log-{timestamp}.json`.

## L8 Gate

**L8 corpus gate: MET (2026-05-25).** All conditions satisfied: receipt corpus 100/100 CLEARED; 3 human-validated Instinct patterns confirmed in `.wabblespec/memory/instinct-observations.md`; benchmark schema CONFIRMED; contradictions CONFIRMED zero. Synth is now authorized. See `_shared/references/l8-corpus-gate.md`.

## Cold-Start Coverage

All 99 modules across L0-L8 have `rules/cold-start.md`. Coverage complete as of VERSION 0.4.4.

(Note: VERSION 0.4.1 overclaimed 81/81; corrected to 99/99 in seed-run-20260524k.)

## Quality Floor

<!-- auto-updated: index-update.py -->
Quality floor status: see `quality-floor-check.py` output. (111 modules registered)
<!-- end auto-updated -->

## Witness

<!-- auto-updated: index-update.py -->
Module file integrity witness recorded at `.wabblespec/state/archive/witness.json` (97 modules, 2026-05-26). Re-record after any intentional module file change with `python .wabblespec/engine/shared/scripts/validate-graph.py --record-witness`. Check drift with `--check-hashes`.
<!-- end auto-updated -->

## Evolution Experiments

First evolution cycle complete (2026-05-25). Infrastructure at `.wabblespec/experiments/`: candidates, blueprints, augments, fixtures, archive, tracker.json. Three modules promoted: recipe (L0), executor (L2), document (L6). tracker.json: 3 entries, all PASS.

## Planned Tasks

`WAVE-CHECKPOINT-TASK-CARD.md` in `.wabblespec/plans/` — wave-level state persistence for Executor. Status: PLANNED, awaiting Specify pass.

## Hook System

Hook files at `src/hooks/`: `wabblespec-config.js`, `wabblespec-session-start.js`, `wabblespec-prompt-guard.js`, `wabblespec-statusline.ps1`. Wired in `.claude/settings.json`. SessionStart emits invariant context on open; UserPromptSubmit nudges for wave drift and missing session. Flag channel: `~/.claude/.wabblespec-session`.

## OMC Extractions

Six extractions from the oh-my-claudecode v4.14.2 evaluation (2026-05-25). Three reasoning patterns (pre-commitment prediction, self-audit, realist check) added to `reasoning-patterns.md`. Three execution discipline rules (prefer deletion, keep changes small, no new deps) added to `guard-policy.md`. No new shared files; no module changes. See CHANGELOG [0.7.7].

## OpenSpec Extractions

Four extractions from the OpenSpec v3.0 evaluation (2026-05-25). Delta spec marker conventions added to `delta-spec-patterns.md`. Verifier pre-archive sweep (non-blocking, three dimensions) added to Verifier SKILL.md and acceptance criteria. State vs instructions hygiene note added to `state-protocol.md`. Wave dependency metadata gap entry added to `gap-map.md`. See CHANGELOG [0.7.6].

## GSD Extractions

Context budget tiers and error taxonomy gate types extracted from GSD reference evaluation (2026-05-25). `_shared/references/context-budget.md` and gate_type annotations in `error-taxonomy.md`. Context7 optional capability added to RuntimeProbe as ninth descriptor. See CHANGELOG [0.7.4].

## Agent OS Extractions

Reference authoring discipline, Specify decisions artifact, ReferenceLoad pointer mode, and references index from Agent OS v3.0 evaluation (2026-05-25). `_shared/references/reference-authoring.md`, `_shared/references/index.yml`, Specify Step 5b, ReferenceLoad `output_mode` parameter. See CHANGELOG [0.7.5].

## Version

<!-- auto-updated: index-update.py -->
Current: 0.49.0
<!-- end auto-updated -->
