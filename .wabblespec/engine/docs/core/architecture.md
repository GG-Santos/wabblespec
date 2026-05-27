# Architecture

WabbleSpec v6.1 is a receipt-gated, spec-driven execution framework. Every action is traceable. No task is complete without an Archive receipt.

## Layer map

| Layer | Name | Role | Module count |
|-------|------|------|-------------|
| L0 | Foundation | Session entry, product definition, runtime detection | 5 |
| L1 | Analysis & Planning | Decompose, specify, scope, clean, test, explore | 24 |
| L2 | Execution & Control | Executor, verifier, guard, auditor, autopilot | 13 |
| L3 | Platform | Target-specific constraints and spec templates | 11 |
| L4 | Gateway | Domain safety checks before execution | 6 |
| L5 | Memory | Session memory, entity graph, provenance, dream | 8 |
| L6 | Polish & Delivery | Content quality, translation, documentation, market | 12 |
| L7 | Release | Archive, changelog, commit, deploy, package, release | 8 |
| L8 | Evolution | Benchmark, blueprint, augment, synth, instinct, factory | 9 |
| shared | Reference | Language/DB/API reference collections (not skill modules) | 3 |

**Total: 99 modules** registered in `framework.yaml`.

## Three routing axes

Apply resolves what knowledge to load using three independent axes:

| Axis | Declared by | Resolves to |
|---|---|---|
| Build target (platform) | L3 Platform SKILL.md `capability_handoff` | `.wabblespec/engine/shared/dev/frameworks/{platform}/` files |
| Runtime lane | L2 Orchestration (Autopilot, Executor) | Wave plan and module sequence |
| Capability need (gateway) | L4 Gateway SKILL.md `references/` | Gateway reference files injected at Specify time |

These three axes are independent. Platform determines what frameworks load. Gateways determine what domain knowledge loads. The runtime lane determines execution order.

## Dependency rules

- Higher layers may depend on lower layers.
- No lower layer may depend on a higher layer.
- Cross-layer dependencies are declared in `framework.yaml` under `depends_on`.
- Shared artifacts (`.wabblespec/engine/shared/`) are consumed by any module; consumers are declared in `framework.yaml` under `shared_files[].consumers`.

## Module anatomy

Every module lives at `modules/l{N}/{name}/` and contains:
- `SKILL.md` — instruction set for the AI agent
- `skill-rules.json` — activation rules, authority, verification mode, receipt requirement
- `rules/` — domain-specific rule files (optional)
- `schemas/` — JSON schemas for receipts this module produces (optional)
- `hooks/` — pre/post tool-use hooks (optional, executor only currently)

## Key invariants

| Code | Rule |
|------|------|
| I1 | Every completed task has an Archive receipt. No exceptions. |
| I2 | Receipts are append-only. Written receipts are never modified. |
| I3 | A module writes only to paths listed in its `authority.owns`. |
| I4 | `framework.yaml` is the single source of truth for module registration. |
| I10 | No implied completion. A module that starts a process must complete it, fail explicitly, or escalate. |
| I11 | Apply writes only to product space. Never touches `.wabblespec/`. |
| I12 | Every output token carries information. No decorative prose. |

Full invariant list: `.wabblespec/engine/shared/references/invariants.md`.

## Framework-level infrastructure

| File | Purpose |
|------|---------|
| `framework.yaml` | Module registry — layer, tier, build_status, depends_on, schemas |
| `.wabblespec/VERSION` | Single-line semver. Archive has exclusive write authority. |
| `.wabblespec/receipts/` | All receipt JSON files from every pipeline run |
| `.wabblespec/plans/` | Task cards, wave plans, decision records |
| `.wabblespec/health/` | Health reports from wabble-health.py runs |
| `.wabblespec/memory/` | Session memory: index, tracker, dream log, staleness map |
| `.wabblespec/engine/shared/infrastructure/` | Cross-module policy docs (gateway pattern, guard policy, economy, version tracking) |
| `.wabblespec/engine/shared/schemas/` | Shared JSON schemas (receipt base, etc.) |
| `.wabblespec/engine/shared/scripts/` | Analysis and validation scripts |
| `.wabblespec/engine/shared/templates/` | Shared output templates |
