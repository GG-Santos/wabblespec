---
name: gateway-engineering
description: Engineering capability gateway. Cross-cutting build standards, code quality floors, CI/CD requirements, and dependency hygiene that apply regardless of platform. Activates alongside any platform package. Catches quality gaps that platform engineering modules do not surface — test coverage floor, dependency freshness, documentation standards, code complexity limits, and universal CI requirements.
---

# Gateway: Engineering

You are the cross-cutting engineering quality layer. You activate on top of the active platform package. Platform modules handle platform-specific build toolchains and performance budgets. This gateway handles quality standards that apply regardless of platform: test coverage, code complexity, CI pipeline requirements, dependency freshness, documentation completeness, and versioning conventions.

## What this skill does

| Concern | Covered by L3 platform | Covered by L4 gateway |
|---|---|---|
| Platform-specific build toolchain | CLI/Web/API platform | — |
| Platform-specific performance budgets | CLI/Web/API platform | — |
| Platform-specific distribution | CLI/Web/API platform | — |
| Test coverage floor (universal) | No L3 module | Yes |
| Code complexity limits (cyclomatic, cognitive) | No L3 module | Yes |
| CI pipeline requirements (universal) | No L3 module | Yes |
| Dependency freshness (outdated major versions) | No L3 module | Yes |
| EOL runtime detection | No L3 module | Yes |
| README completeness | No L3 module | Yes |
| CHANGELOG convention | No L3 module | Yes |
| Code review standards (reviewer count, what to check) | No L3 module | Yes |
| Technical debt density (TODO/FIXME limits) | No L3 module | Yes |

## When to use

- Any target at Medium complexity or higher (declared by Recipe)
- Any target approaching production deployment
- Budget-gated for Low complexity: activate quality-gates.md only, skip full gateway

## Activation sequence

### Phase A (Specify time — knowledge injection)

```
1. Confirm platform package (L3) has already activated and written its receipt
2. Load references/ directory into Specify context:
   - references/quality-patterns.md (ADRs, test strategy, breaking change classification)
   - references/architecture.md (circular deps, API versioning, backwards compatibility)
3. Load .wabblespec/engine/shared/dev/infrastructure/ files based on project signals:
   - infrastructure/cicd.md (always)
   - infrastructure/containers.md (if Dockerfile or k8s manifests detected)
   - infrastructure/iac.md (if Terraform/Pulumi files detected)
   - infrastructure/observability.md (if metrics/tracing config detected or declared in spec)
4. Write gateway-spec-receipt (Phase A)
```

### Phase B (pre-Executor — verdict)

```
1. Load build-standards.md (universal CI/CD requirements)
2. Load code-quality.md (linting, coverage, complexity standards)
3. Load dependency-standards.md (freshness, EOL, audit)
4. Register quality-gates.md with Verifier (supplements platform gates)
5. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Type Design Quality Gate

When a wave produces new types, interfaces, or data models, gateway-engineering runs a 4-dimension type design assessment before issuing its verdict:

| Dimension | Question | Score 1–10 |
|---|---|---|
| Encapsulation | Are internal state and invariants hidden from consumers? | |
| Invariant expression | Does the type's structure make illegal states unrepresentable? | |
| Usefulness | Is the type actually used — not just passed through as `any` or `object`? | |
| Invariant enforcement | Are invariants enforced at the boundary (constructor/factory), not in each method? | |

**Gate condition:** Any dimension scoring below 5/10 triggers a FLAG in the gateway verdict. The type must be redesigned or the rationale documented before proceeding. A score below 3/10 on Invariant expression or Encapsulation is a BLOCK — these represent types that create silent coupling or make refactoring unsafe.

Record dimension scores in the gateway verdict receipt under `type_design_scores[]`. Omit this check when the wave produces no new types.

## LSP and Serena Integration

When LSP plugins or Serena MCP are active, gateway-engineering can use semantic tools to augment its standard checks:

| Check | Without LSP/Serena | With LSP/Serena |
|---|---|---|
| Rename propagation | grep-based caller search | `serena_find_references` — authoritative call graph |
| Dead code detection | static grep for unused exports | LSP "no references" signal — confirmed unused |
| Public API surface | read interface files | `serena_list_symbols` — extracted symbol list |
| Deletion safety | grep for references | LSP reference count — exact caller count before delete |

Rule: if `serena_find_references` returns references for a symbol marked for deletion, the deletion is a BREAKING change requiring human confirmation regardless of grep results. The reference graph is Tier 1 evidence (see verifier Evidence Hierarchy).

Record `lsp_augmented: boolean` and `serena_augmented: boolean` in the gateway verdict receipt.

## Reference Routing

| Situation | Reference |
|---|---|
| engineering receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type gateway-spec` / `gateway-verdict` (two-phase) |
| LSP workspace symbol checks and semantic augmentation | `engine/shared/references/lsp-integration.md` → Gateway-engineering section |
| Serena MCP call patterns | `engine/shared/references/mcp-servers-integration.md` → Serena section |

## Output contract

- Code quality report (coverage, complexity, lint findings)
- Dependency freshness report
- CI pipeline compliance check
- Gateway activation receipt with all gate results

## Files loaded by this module

```
modules/l4/engineering/
  build-standards.md
  code-quality.md
  dependency-standards.md
  quality-gates.md
```
