# WabbleSpec v6.1 Planning Index

Planning authority for v6.1. All documents in this directory are the result of granular planning sessions that use v5.3 as the base and selectively integrate valid v6 novel features.

## Source Truth Hierarchy

1. v5.3 source: `C:\Vaults\WabbleSpec v5\WabbleSpec v5\` — ground truth for module detail and pipeline mechanics
2. v6.1 planning: this directory — decisions made in planning sessions
3. v6 canonical: `../canonical/` — reference only, treat as AI-generated draft, verify before trusting

## Planning Documents

| File | Contents | Status |
|---|---|---|
| `01-INVARIANTS.md` | All 12 invariants (8 from v5.3 expanded + 4 new) | Locked |
| `02-ARCHITECTURE.md` | Full v6.1 architecture: layers, gateways, directory layout, loading gates, data flow | Locked |
| `03-CORE-FEATURES.md` | 14 core feature groups with full detail | Locked |
| `04-SKILLS-FLOW.md` | 10 operational flow diagrams: activation, spec, three-phase, execution, verification, runtime, memory, evolution, error, delivery | Locked |
| `05-MODULE-IMPORTANCE.md` | Tier 1-5 classification, dependency chains, per-module planning order, v5.3 carry-forward decisions | Locked |

## Key Decisions Locked in This Planning Session

- v6 was treated as AI-generated hallucination. v5.3 is base.
- 12 invariants (8 expanded from v5.3, 4 new: Evidence Expiry, Receipts as Operational Artifacts, Framework-Product Separation, Spec Quality over Volume)
- Development gateway fully distributed across platform packages and `_shared/dev/`
- Engineering and Security gateways split: platform-specific portions go to L3, cross-cutting stays at L4
- AI gateway restored at L4 (distinct from AI/Agent build target at L3)
- 11 build targets (vs 6 in v6): Web, API/Service, Game, Mobile, Desktop, CLI, IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, AI/Agent
- WabbleFlow removed
- MCPBridge removed — no MCP in v6.1
- Runtime is vendor-neutral — no hardcoded model names
- Research is a phase (ReferenceLoad + MemorySearch + Explore), not a standalone module
- Compression (Economy) and expression (Homowabian) are separate concerns
- Adversarial challenge lives in Reviewer module, not a standalone invariant
- Error taxonomy carries forward from v5.3 with STALENESS_VIOLATION added

## Planning Stages Remaining

1. Per-module planning (priority order in `05-MODULE-IMPORTANCE.md`)
2. Long-form documentation (after all modules planned)

## Planning Order for Per-Module Work

See `05-MODULE-IMPORTANCE.md` section "Per-Module Planning Order" for the 15-priority sequence.
