# L3 Framework Extensions Plan

**Date:** 2026-05-26
**Status:** COMPLETE — analysis only; no execution required
**Session:** l3-framework-extensions-plan-v1
**Closes deferred item:** "Development leaf modules (React, Python, Go, etc.)" from phase-integration.md §6

---

## 1. Context

`phase-integration.md` §6 deferred: "Gateway sub-modules (Security leaf modules: Recon, Surface,
Model, Attack, Defend; Development leaf modules: React, Python, Go, etc.) — separate planning
after v4–v5.2 gateway architecture review."

`gateway-leaf.md` resolved the L4 gateway half (aesthetic/design/experience — rules-only, no leaf
modules). This plan resolves the L3 "development leaf modules" half.

The question: do L3 platform modules need framework-specific child modules (React module, Python
module, Go module) or do the existing `_shared/dev/frameworks/` reference files cover the gap?

---

## 2. L3 Framework Extension Audit

### 2.1 Status per module

| Module | Framework routing pattern | Framework-specific files | Status |
|---|---|---|---|
| platform-web | L3-specific spec templates, conditional | nextjs, react, vue, svelte in `spec-template/framework-specific/` | COMPLETE |
| platform-api-service | L3-specific spec templates, conditional | fastapi, fastify-express, grpc, serverless in `spec-template/framework-specific/` | COMPLETE |
| platform-mobile | L3-specific spec templates, conditional | react-native, flutter, swift-uikit, kotlin-compose in `spec-template/framework-specific/` | COMPLETE |
| platform-game | Mixed — L3 engine templates + `_shared/dev/` | godot, unreal in `spec-template/engine-specific/`; unity loads only from `_shared/dev/` | COMPLETE |
| platform-cli | `_shared/dev/` delegation only | cobra, click, clap loaded from `_shared/dev/frameworks/cli/` | SEE §2.2 |
| platform-data-pipeline | `_shared/dev/` delegation only | airflow, dbt, spark loaded from `_shared/dev/frameworks/data/` | SEE §2.2 |
| platform-desktop | `_shared/dev/` delegation only | electron, tauri loaded from `_shared/dev/frameworks/desktop/` | SEE §2.2 |
| platform-ai-agent | `_shared/dev/` delegation only | langchain, openai-sdk loaded from `_shared/dev/frameworks/ai/` | SEE §2.2 |
| platform-library | No framework routing (`conditional_load: []`) | None | SEE §2.3 |
| platform-extension | No framework routing (`conditional_load: []`) | None | ACCEPTABLE — see §2.4 |
| platform-iot | No framework routing (`conditional_load: []`) | None | ACCEPTABLE — see §2.4 |

### 2.2 `_shared/dev/` delegation pattern (cli, data-pipeline, desktop, ai-agent)

These four modules intentionally route to `_shared/dev/frameworks/{domain}/{framework}.md` rather
than L3-specific spec templates. This is the correct design for the following reason:

**When L3-specific spec templates are needed:** The framework choice changes the *spec structure*
— different P0/P1/P2 template shapes, different acceptance criteria patterns, different
architecture documents. Examples:
- React (SPA) vs Next.js (SSR/RSC) vs SvelteKit (filesystem routing): fundamentally different
  rendering architecture with different P2 systems-design documents.
- FastAPI vs gRPC vs serverless: different API contract shapes (OpenAPI vs protobuf vs functions),
  different P0 service-contract structure.

**When `_shared/dev/` delegation is sufficient:** The framework choice affects *implementation
conventions* but not spec structure. The L3 spec-template already covers the universal patterns;
the framework doc adds syntax and library-specific conventions on top.
- Cobra vs Click vs Clap: all CLI frameworks share the same arg/flag/subcommand spec structure.
  The spec-template for CLI args, exit codes, and output contracts is the same. The framework
  difference is syntax choice.
- Airflow vs dbt vs Spark: all data pipeline frameworks share the same DAG/lineage/SLA spec
  structure. The framework-specific file adds scheduling syntax and backfill semantics.
- Electron vs Tauri: both build cross-platform desktop apps with the same UX spec requirements.
  The framework-specific file adds IPC and security sandbox differences.
- LangChain vs OpenAI SDK: both build AI agents with the same evaluation and safety spec
  requirements. The framework doc adds chain design and token management specifics.

**Decision: No L3-specific framework spec templates needed for these four modules.** The
`_shared/dev/frameworks/` delegation pattern is correct and intentional.

### 2.3 `platform-library` — no conditional routing

Library platform is unique: the *specification* of a library (API contract, compatibility matrix,
semantic versioning policy, documentation requirements) is identical regardless of whether the
implementation is Python/pip, Go/modules, Node/npm, or Rust/crates.

Framework differences affect build toolchain (handled by `engineering/build-toolchain.md`) and
distribution (handled by `engineering/platform-verification.md`) — not the spec-template structure.

**Decision: `conditional_load: []` is correct for library.** No framework routing needed.

### 2.4 `platform-extension` and `platform-iot` — no conditional routing

- **Extension:** Browser extension APIs (Chrome/Firefox) are sufficiently standardized. The
  `spec-template/` covers manifest, popup, options, content scripts uniformly. Framework choice
  (vanilla JS vs React) is a detail inside the implementation spec, not a template-level concern.
- **IoT/Embedded:** Firmware targets (RTOS, bare-metal, Zephyr, ESP-IDF) have wildly different
  toolchains but share the same spec requirements: resource constraints, peripheral contracts,
  safety requirements. No single framework dominates enough to warrant a conditional route.

**Decision: Both are correctly pattern-C (no conditional loading).** No change needed.

---

## 3. Security leaf modules finding

`phase-integration.md` mentioned "Security leaf modules: Recon, Surface, Model, Attack, Defend."

These map directly to `modules/l4/security/references/cycling/`:
- **Recon/Surface** → `security-profile.md` (Phase A Intel: Recon + Surface + Context)
- **Model** → `threat-model.md` (cross-cutting threat model)
- **Attack** → `red-protocol.md` (Phase B Red attack protocol)
- **Defend** → `blue-protocol.md` (Phase C Blue defend protocol)
- **Purple scoring** → `cycle-protocol.md` (9-component evaluation model)

All five are implemented as rules files inside `gateway-security`. Consistent with the rules-only
pattern. No separate skill modules required.

**Decision: Security leaf modules are DONE.** No new modules needed.

---

## 4. Overall finding

| Deferred item | Resolution |
|---|---|
| Security leaf modules (Recon/Attack/Defend) | DONE — cycling protocol files in gateway-security |
| L4 gateway aesthetic/design/experience leaf modules | DONE — gateway-leaf.md 2026-05-24 |
| Development leaf modules (React, Python, Go) | DONE — web/api/mobile have L3 templates; cli/data/desktop/ai delegate to _shared/dev (correct) |
| Library framework routing | DONE — no routing is correct; spec structure is language-agnostic |

**No new files are needed. No SKILL.md edits are needed. No framework.yaml changes are needed.**

The deferred item from `phase-integration.md` §6 is fully resolved. The framework has reached
its intended L3 framework-extension design with no gaps.

---

## 5. What this plan does NOT do

- Does not create new skill modules under `modules/l3/` or `modules/l4/`
- Does not modify any SKILL.md
- Does not create framework-specific spec templates for cli, data-pipeline, desktop, ai-agent,
  library, extension, or iot
- Does not change `conditional_load` declarations in any skill-rules.json

---

## 6. Follow-on candidates (not blocking, optional quality improvements)

These are potential improvements that could follow from this analysis if scope is re-opened:

1. **CLI `spec-template/framework-specific/`** — while not required, a `cobra.md` L3 template
   could add Go-specific CLI acceptance criteria patterns (cobra command tree declarations,
   flag types, persistent flags vs local flags). Low value given `_shared/dev/frameworks/cli/cobra.md`
   already exists. Estimated effort: Low. Estimated value: Low.

2. **Library language-specific build references** — `engineering/build-toolchain.md` in library
   currently covers language-agnostic patterns. Language-specific build guidance (poetry/pyproject,
   cargo publish, go mod tidy) could be added as conditional load from `_shared/dev/languages/`.
   Low value since `_shared/dev/languages/{python,go,rust,node}/reference.md` already exists.
   Estimated effort: Low. Estimated value: Low.

These are acknowledged but not required. The framework is complete without them.
