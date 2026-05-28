# WabbleSpec v6.1

A spec-driven, receipt-gated, hook-enforced SDLC framework for a single-agent runtime. **The framework is the product** — 103 skill modules across layers L0–L8, with `.wabblespec/wabblespec.yaml` as the canonical module registry.

Current version: see [`.wabblespec/VERSION`](.wabblespec/VERSION).

## What it is

WabbleSpec turns an agent's software work into an auditable pipeline: every non-trivial step is grounded in a locked spec, passes a declared verification gate, and emits a receipt. Twelve invariants (e.g. *spec is the single source of truth*, *receipts are operational artifacts*, *framework and product never mix*) are enforced by hooks rather than convention. Full table: [`.wabblespec/engine/shared/references/invariants.md`](.wabblespec/engine/shared/references/invariants.md).

The lifecycle, roughly: **Recipe → ScopeFrame → (Brainstorm/Propose/Interview) → Specify → Decompose → (Reviewer) → Executor → Verifier → Archive**, with an L8 self-improvement chain (Instinct → Synth → Blueprint → Augment → Benchmark → Forge).

## Repository layout

| Path | Contents |
|---|---|
| `.wabblespec/wabblespec.yaml` | Canonical registry of all 103 modules |
| `.wabblespec/engine/modules/` | Skill modules, organized by layer (`l0`–`l8`, `_shared`) |
| `.wabblespec/engine/shared/scripts/` | Pipeline automation (receipts, archive, guard, validation) |
| `.wabblespec/engine/shared/schemas/` | JSON Schema for receipts and artifacts |
| `.wabblespec/engine/shared/references/` | Invariants, staleness states, contracts |
| `.wabblespec/engine/hooks/` | SessionStart, UserPromptSubmit, Statusline, PreToolUse |
| `.wabblespec/engine/docs/` | Architecture and contributor docs |
| `.wabblespec/state/` | **Machine-local runtime state** (receipts, memory, plans) — gitignored, not versioned |
| `CLAUDE.md` | Operating guidance for Claude Code in this repo |

## Getting started

Requirements: Python 3.8+ and `pip install pyyaml duckdb`.

Most automation lives in `.wabblespec/engine/shared/scripts/` — run any with `--help`. To check framework health:

```bash
python .wabblespec/engine/shared/scripts/validate-graph.py        # module registry integrity
python .wabblespec/engine/shared/scripts/quality-floor-check.py   # per-module quality gates
```

## Learn more

- [`CLAUDE.md`](CLAUDE.md) — key scripts, invariants, conventions, state paths
- [`.wabblespec/engine/docs/core/architecture.md`](.wabblespec/engine/docs/core/architecture.md) — architecture
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to add or change modules
