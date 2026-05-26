# WabbleSpec v6.1 — Documentation Index

Receipt-gated, spec-driven execution framework. 99 modules across 9 active layers.

**Version:** See `.wabblespec/VERSION`
**Module registry:** `framework.yaml`
**Changelog:** `.wabblespec/CHANGELOG.md`

---

## Core

Framework fundamentals — start here for orientation.

| Document | What it covers |
|----------|---------------|
| [Architecture](core/architecture.md) | Layer map, module count, dependency rules, key invariants, file layout |
| [Pipeline](core/pipeline.md) | Recipe → ScopeFrame → Specify → Decompose → Gateway → Executor → Verifier → Archive |
| [Receipts and Gates](core/receipts-and-gates.md) | Receipt schema, quality floor gates, L8 gate, integration gate, validate-graph |
| [Guard and Economy](core/guard-and-economy.md) | Risk tiers, scope boundaries, completion promise, token economy, version tracking |
| [Contributing](core/contributing.md) | How to add a module, pass quality floor, run a seed run |
| [Handover](core/handover.md) | Clean-slate briefing for resuming work in a new session |

---

## Layers

One document per layer. Each covers modules in that layer, key behaviors, and layer rules.

| Layer | Document | Module count |
|-------|----------|-------------|
| L0 — Foundation | [L0-foundation.md](layers/L0-foundation.md) | 5 |
| L1 — Analysis & Planning | [L1-analysis-planning.md](layers/L1-analysis-planning.md) | 24 |
| L2 — Execution & Control | [L2-execution-control.md](layers/L2-execution-control.md) | 13 |
| L3 — Platforms | [L3-platforms.md](layers/L3-platforms.md) | 11 |
| L4 — Gateways | [L4-gateways.md](layers/L4-gateways.md) | 6 |
| L5 — Memory | [L5-memory.md](layers/L5-memory.md) | 8 |
| L6 — Polish & Delivery | [L6-polish-delivery.md](layers/L6-polish-delivery.md) | 12 |
| L7 — Release | [L7-release.md](layers/L7-release.md) | 8 |
| L8 — Evolution | [L8-evolution.md](layers/L8-evolution.md) | 9 |

For individual module skill files: `modules/l{N}/{name}/SKILL.md`

---

## Gateways

L4 safety and quality checks. Each gateway runs before Executor for its domain.

| Gateway | Document | Domain |
|---------|----------|--------|
| security | [gateway-security.md](gateways/gateway-security.md) | Cross-platform threats: secrets, SAST, weak crypto |
| engineering | [gateway-engineering.md](gateways/gateway-engineering.md) | Build quality, standards, architecture |
| ai | [gateway-ai.md](gateways/gateway-ai.md) | LLM safety, prompt injection, eval |
| aesthetic | [gateway-aesthetic.md](gateways/gateway-aesthetic.md) | Visual brand, style, color, typography |
| design | [gateway-design.md](gateways/gateway-design.md) | UX, interaction design, user flows |
| experience | [gateway-experience.md](gateways/gateway-experience.md) | Accessibility, performance, delight |

Gateway sequencing and routing protocol: `_shared/infrastructure/gateway-pattern.md`

---

## Platforms

L3 platform packages. Each loads target-specific spec templates, engineering rules, and security controls.

| Platform | Document | Target |
|----------|----------|--------|
| CLI | [platform-cli.md](platforms/platform-cli.md) | Command-line tools |
| Web | [platform-web.md](platforms/platform-web.md) | Web applications, SPAs, SSR |
| API Service | [platform-api-service.md](platforms/platform-api-service.md) | REST / GraphQL APIs, microservices |
| Mobile | [platform-mobile.md](platforms/platform-mobile.md) | iOS and Android apps |
| Desktop | [platform-desktop.md](platforms/platform-desktop.md) | Desktop GUI apps (Electron, Tauri, native) |
| Data Pipeline | [platform-data-pipeline.md](platforms/platform-data-pipeline.md) | ETL, batch, stream processing |
| AI Agent | [platform-ai-agent.md](platforms/platform-ai-agent.md) | LLM apps, agents, RAG systems |
| Library / Package | [platform-library-package.md](platforms/platform-library-package.md) | npm, pip, gem, crate packages |
| Game | [platform-game.md](platforms/platform-game.md) | Games (PC, console, mobile) |
| IoT / Embedded | [platform-iot-embedded.md](platforms/platform-iot-embedded.md) | Firmware, embedded, IoT devices |
| Extension / Plugin | [platform-extension.md](platforms/platform-extension.md) | Browser extensions, editor plugins |

---

## Key tools

```bash
# Quality floor: all modules must pass before any pipeline run
python _shared/scripts/quality-floor-check.py --framework framework.yaml

# Framework graph validation: A7 rule — no script paths in consumers
python _shared/scripts/validate-graph.py --framework framework.yaml

# Single module check with detail
python _shared/scripts/quality-floor-check.py --framework framework.yaml --module {id} --verbose
```

## Current status

| Gate | Status |
|------|--------|
| Quality floor | 96/96 PASS |
| L8 evolution gate | 19/100 receipts — NOT cleared |
| Integration Phase 5-6 | 3/10 runs — NOT cleared |
| build_status: deferred | 0 |
