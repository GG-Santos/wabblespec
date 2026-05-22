# Module Plan — L3 Platform Packages (All 11 Targets)

**Tier:** 1 — CRITICAL ROUTING
**Layer:** L3 Platform
**v5.3 origin:** Development gateway (distributed), Engineering gateway (split), Security gateway (split)

---

## Common Structure

Every platform package follows this layout:

```
.wabblespec/platforms/<target>/
  SKILL.md                      <- routing logic, module load order, platform rules
  skill-rules.json              <- Recipe activation signals for this target
  spec-template/
    design-document.md          <- target-specific P1 spec template variant
    systems-design.md           <- target-specific P2 template
    technical-spec.md           <- target-specific P3 template
  dev/                          <- platform-specific dev modules (absorbed from v5.3)
    <framework-or-lang>/
      references/
      rules/
  engineering/                  <- platform-specific engineering modules
    build-toolchain.md
    performance-budgets.md
    platform-verification.md
  security/                     <- platform-specific security modules
    threat-model.md
    platform-controls.md
  verification/
    gates.md                    <- checkable verification gates for this target
  schemas/
    receipt.schema.json
```

Platform packages do not orchestrate across platforms. Each is self-contained. Apply reads the active platform package's routing logic. Executor executes within the declared scope.

---

## 1. Web

**Recipe signals:** `package.json` with react/next/vue/svelte/angular/astro/vite, `*.tsx`/`*.jsx`, `next.config.*`, `vite.config.*`, `index.html` at root

### Dev modules absorbed

| Module | Content |
|---|---|
| React | Component patterns, hooks, state management (Zustand/Jotai/Redux), prop drilling avoidance |
| NextJS | App router vs. pages router, SSR/SSG/ISR patterns, route handlers, middleware |
| Vue | Composition API, Pinia, SFC structure, Vue Router |
| Svelte | Stores, reactive declarations, SvelteKit routing |
| Angular | Standalone components, signals, RxJS patterns, NgRx |
| HTML/CSS | Semantic HTML, ARIA roles, CSS custom properties, no-framework patterns |
| Styling | CSS Modules, Tailwind, CSS-in-JS — module declares active system |
| PWA | Service worker, manifest.json, offline strategy, install prompt |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Vite (default), Webpack (legacy only with justification), Turbopack (Next 13+)
- Bundle analysis: bundle size tracked per build, budget declared in config
- Tree shaking: verified via bundle analysis

`engineering/performance-budgets.md`:
- Core Web Vitals targets: LCP < 2.5s, CLS < 0.1, INP < 200ms
- JS bundle: initial load < 200KB gzipped (configurable per project)
- Image: next/image or equivalent lazy loading required

### Platform-specific security

`security/platform-controls.md`:
- CSP header required for all production deployments
- XSS: no dangerouslySetInnerHTML without sanitization, no eval()
- CORS: explicit allowlist, no wildcard in production
- Subresource integrity: SRI on externally hosted scripts

### Spec template variant

P1 template sections: Target Users, Key Journeys, Visual Direction, Accessibility Requirements, Browser Support Matrix, Performance Budget

### Verification gates

- Lighthouse CI: CWV pass required before Delivery
- Accessibility: axe-core or equivalent scan, zero critical violations
- Bundle budget: enforced in CI

---

## 2. API/Service

**Recipe signals:** `server.ts`/`server.py`/`main.go`, `Dockerfile` with port EXPOSE, `openapi.yaml`/`swagger.json`, framework-specific entry (fastapi, express, gin, actix, spring-boot, nestjs)

### Dev modules absorbed

| Module | Content |
|---|---|
| REST server | Express/Fastify/Gin/FastAPI/Actix route patterns, middleware, request validation |
| GraphQL server | Apollo Server, Strawberry, gqlgen — schema-first patterns, resolver design |
| gRPC server | Proto service definitions, interceptor patterns, server reflection |
| Realtime server | Socket.io, ws server, SSE endpoint patterns |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Containerization: Dockerfile multi-stage build (builder + runtime image)
- Health check: /health and /ready endpoints required
- Graceful shutdown: SIGTERM handler, drain in-flight requests

`engineering/performance-budgets.md`:
- p99 latency target declared per endpoint type (REST: 200ms, gRPC: 50ms default)
- Throughput baseline: RPS target declared in spec
- Connection pool sizing: declared, not defaulted

### Platform-specific security

`security/threat-model.md`:
- Authentication: every endpoint declares auth requirement (or explicit public)
- Authorization: RBAC or ABAC pattern declared
- Input validation: all external inputs validated at boundary (Zod, Pydantic, etc.)
- Rate limiting: required for public-facing endpoints

`security/platform-controls.md`:
- Secrets: env vars only, no config files in repo
- TLS: required in production, minimum TLS 1.2
- OWASP API Security Top 10: checklist in verification gates

### Spec template variant

P1 template sections: API Contract (OpenAPI/proto), Auth Model, Rate Limits, SLA, Error Response Format, Versioning Strategy

### Verification gates

- Contract test: generated client against server passes
- Auth coverage: every endpoint has auth test (authenticated + unauthorized)
- Load test: baseline RPS target met before Delivery

---

## 3. Game

**Recipe signals:** `unity/`, `godot.project`, `*.gd`, `bevy` in Cargo.toml, `phaser` in package.json, `unreal` project file

### Dev modules absorbed

| Module | Content |
|---|---|
| Engine | Unity, Godot, Bevy, Unreal — project structure, scene management, asset pipeline |
| TwoD | Sprite, tilemap, 2D physics (Box2D/Rapier), camera patterns |
| ThreeD | Mesh, material, PBR lighting, 3D physics, LOD |
| GamePhysics | Collision layers, rigidbody patterns, trigger vs. collider distinction |
| GameAudio | AudioSource pooling, spatial audio, music/sfx separation, audio bus management |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Build targets: platform-specific export (Web/GL, PC, Console, Mobile) declared in spec
- Asset pipeline: atlas packing, compression settings, streaming strategy
- Version: engine version pinned in project config

`engineering/performance-budgets.md`:
- Frame budget: target framerate declared (30/60/120fps), frame time budget derived
- Draw calls: budget per scene type declared
- Memory: texture memory, audio memory, GC allocation budgets

### Platform-specific security

`security/platform-controls.md`:
- Anti-cheat scope: server-authoritative for multiplayer, client-side only for single-player
- Save data: local save encryption if sensitive progression
- Network: dedicated server vs. P2P — security model declared per choice

### Spec template variant

P1 template sections: Game Loop, Core Mechanics, Platform Targets, Input Scheme, Monetization Model (if any), Target Framerate

### Verification gates

- Frame rate: profiler baseline on target hardware before Delivery
- Input: tested on all declared input schemes
- Crash: no crash in 10-minute smoke test on each target platform

---

## 4. Mobile

**Recipe signals:** `ios/` directory, `android/` directory, `*.swift`, `*.kt`, `react-native.config.js`, `pubspec.yaml` (Flutter), `Podfile`

### Dev modules absorbed

| Module | Content |
|---|---|
| iOS | Swift patterns, UIKit vs. SwiftUI, Xcode project structure, App Store review requirements |
| Android | Kotlin patterns, Jetpack Compose, Gradle module structure, Play Store requirements |
| ReactNative | Bridge vs. JSI, Metro bundler, EAS Build, platform-specific code (`Platform.OS`) |
| Flutter | Widget tree, state management (Riverpod/Bloc), Dart null safety, platform channels |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- iOS: Xcode + fastlane, code signing via Xcode Automatic or manual (declared)
- Android: Gradle wrapper committed, keystore in CI secrets
- RN/Flutter: EAS Build or Bitrise, OTA update strategy declared

`engineering/performance-budgets.md`:
- App launch: cold start < 3s, warm start < 1s
- Binary size: declared per platform (iOS: < 50MB, Android: < 30MB AAB typical)
- Memory: no OOM in 30-minute session on minimum supported device

### Platform-specific security

`security/platform-controls.md`:
- App permissions: minimum required permissions declared in spec, no over-permission
- Keychain/Keystore: sensitive data stored in platform secure storage, never SharedPreferences/UserDefaults
- Certificate pinning: required for apps handling financial or health data
- Jailbreak/root detection: scope declared in threat model

`security/threat-model.md`:
- Reverse engineering: obfuscation strategy declared (ProGuard/R8 for Android)
- Deep link: validation required, no unauthenticated deep link actions
- Third-party SDKs: explicit allowlist, privacy policy covers all SDK data collection

### Spec template variant

P1 template sections: Supported OS Versions, Device Targets (phone/tablet), Offline Behavior, Push Notification Strategy, App Store Metadata

### Verification gates

- Device matrix: tested on minimum supported OS + latest OS
- App store compliance: guidelines checklist passed before submission
- Accessibility: VoiceOver (iOS) / TalkBack (Android) smoke test

---

## 5. Desktop

**Recipe signals:** `electron` in package.json, `tauri.conf.json`, `.NET` project targeting WPF/WinUI, `qt` dependency, Swift/AppKit Mac target

### Dev modules absorbed

| Module | Content |
|---|---|
| Electron | Main/renderer process separation, IPC patterns, context isolation (required), preload scripts |
| Tauri | Commands (Rust backend), events, updater, permissions (allowlist) |
| Native (macOS) | AppKit/SwiftUI, Sandbox entitlements, notarization |
| Native (Windows) | WPF/WinUI, MSIX packaging, Windows Store or sideload |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Electron: electron-builder or electron-forge, auto-updater declared
- Tauri: Cargo build + npm build, bundler config
- Code signing: required for distribution (Apple notarization, Windows Authenticode)

`engineering/performance-budgets.md`:
- Memory baseline: idle memory footprint declared
- App startup: cold start target declared per platform
- Installer size: declared (Electron apps are large — document and justify)

### Platform-specific security

`security/platform-controls.md`:
- Electron: context isolation ON (non-negotiable), nodeIntegration OFF, preload scripts only channel
- Tauri: allowlist minimal — only declared capabilities enabled
- Auto-update: signed updates only, TLS delivery
- Local data: encrypt sensitive local data (SQLCipher or equivalent)

### Spec template variant

P1 template sections: OS Targets (Win/Mac/Linux), Distribution Channel (store/sideload/enterprise), Update Strategy, Offline-First Requirements, Native Integration Needs

### Verification gates

- Code signing: verified before Delivery
- Auto-update: smoke tested (update from previous version works)
- OS-specific: tested on all declared OS targets

---

## 6. CLI

**Recipe signals:** `bin` field in package.json, `cli.py`/`__main__.py`, `cmd/` in Go project, `clap` in Cargo.toml, `cobra` import, shebang in entry file

### Dev modules absorbed

| Module | Content |
|---|---|
| CLI framework | Commander/Yargs (Node), Click/Typer (Python), Cobra (Go), Clap (Rust) |
| Output formatting | Color, tables, spinners, progress bars — terminal capability detection |
| Config | Config file conventions (XDG, ~/.apprc), env var override hierarchy |
| Distribution | npm global, PyPI, Homebrew, binary release (GitHub Releases) |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Single binary: preferred for Go/Rust CLIs (cross-compile targets declared)
- npm global: peer dependency warnings, postinstall scripts policy (avoid)
- Shell completions: generation for bash/zsh/fish declared in spec if required

`engineering/performance-budgets.md`:
- Startup time: < 100ms cold start for short-lived commands
- No unnecessary runtime dependencies loaded on startup

### Platform-specific security

`security/platform-controls.md`:
- Input: all CLI arguments validated, no shell injection from user input
- Credentials: never accept secrets as positional args (visible in ps, shell history) — use env vars or stdin
- File operations: validate all paths, no path traversal
- Network: explicit opt-in for any network calls, declare in help text

### Spec template variant

P1 template sections: Command Structure, Subcommand Hierarchy, Config File Schema, Output Modes (--json, --quiet), Stdin/Stdout/Stderr contract

### Verification gates

- Help text: all commands have --help output
- Exit codes: 0 success, non-zero failure — verified
- Shell completion: if declared, generated and tested

---

## 7. IoT/Embedded

**Recipe signals:** `CMakeLists.txt`, `platformio.ini`, `Makefile` with arm-none-eabi target, `micropython` import, `embassy` or `rtic` in Cargo.toml, firmware-specific config files

### New dev modules (no v5.3 equivalent)

| Module | Content |
|---|---|
| C/C++ | CMake patterns, header organization, embedded C idioms, MISRA guidance |
| MicroPython | MicroPython stdlib subset, asyncio patterns, flash-aware design |
| Embedded Rust | no_std patterns, embassy/RTIC async, PAC/HAL abstraction |
| Firmware build | Flash/RAM budget, linker script, objcopy, upload toolchain (JLink, openocd) |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Cross-compilation: target triple declared (arm-none-eabi, thumbv7em-none-eabihf, etc.)
- Dependency: vendor dependencies — no network access during build (embedded build offline)
- Flash map: memory layout declared and documented

`engineering/performance-budgets.md`:
- Flash budget: binary size vs. available flash declared per target MCU
- RAM budget: stack + heap declared, stack overflow detection enabled in debug
- CPU budget: interrupt latency target declared for real-time tasks

### Platform-specific security

`security/threat-model.md`:
- Firmware update: signed OTA required for network-connected devices
- Debug interfaces: JTAG/SWD disabled in production firmware
- Secrets: hardware security element (TPM/SE) for key storage where available
- Physical access: threat model declares physical attack scope

`security/platform-controls.md`:
- No dynamic memory allocation in critical paths (C/C++)
- Stack canaries enabled in debug builds
- Watchdog timer required for production firmware

### Spec template variant

P1 template sections: Target MCU/SoC, RTOS or bare-metal, Communication Protocol (UART/SPI/I2C/BLE/WiFi), Power Profile, OTA Update Strategy

### Verification gates

- Build: firmware builds for target hardware in CI
- Flash: runs on target hardware (or emulator if physical unavailable — declared)
- Memory: flash and RAM within declared budget

---

## 8. Library/Package

**Recipe signals:** `lib` or `index` as main entry, no `bin`, `package.json` with `files` field, `setup.py`/`pyproject.toml` with `[tool.poetry]` or `[project]`, `lib.rs` as crate root, `*.podspec`

### New dev modules (no v5.3 equivalent)

| Module | Content |
|---|---|
| API surface design | Minimal public API, backward compatibility, deprecation patterns |
| Semver | Semantic versioning enforcement, breaking change detection |
| Registry publishing | npm, PyPI, crates.io, Maven Central — publishing config, access tokens |
| Doc generation | TypeDoc, Sphinx, rustdoc, Javadoc — required for public API |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Dual output: ESM + CJS for JS libraries (until ESM-only is viable), declared
- Type declarations: .d.ts shipped, not generated at install time
- Peer dependencies: declared as peerDependencies, not dependencies (JS)
- Source maps: shipped for debugging downstream

`engineering/performance-budgets.md`:
- Bundle impact: library size impact on consumer bundle declared
- Tree-shakeable: ESM + named exports, no side effects in module roots

### Platform-specific security

`security/platform-controls.md`:
- Supply chain: no typosquatting risk in package name (verify before publish)
- No postinstall scripts that execute arbitrary code
- Dependency count: minimal transitive dependencies — each dep justified
- Publish auth: 2FA required on registry account

### Spec template variant

P1 template sections: Public API Surface, Versioning Strategy, Minimum Runtime Support, Peer Dependency Requirements, Documentation Coverage Target

### Verification gates

- API surface: public API reviewed before minor/major bump
- Type safety: no `any` in public types
- Doc coverage: all public exports documented

---

## 9. Extension/Plugin

**Recipe signals:** `manifest.json` with `manifest_version`, `.vscodeignore`, `vscode:package` script, `thunderbird-addon`, host application-specific config

### Dev modules absorbed/new

| Module | Content |
|---|---|
| Browser extension | Chrome MV3 manifest, service worker background, content script isolation, permissions model |
| VS Code extension | Extension API patterns, activation events, contributes schema, webview sandbox |
| Host sandbox patterns | Message passing between extension and host, no direct DOM in background context |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Browser: webpack/rollup bundle to dist/, manifest.json as source of truth
- VS Code: vsce package, esbuild bundling
- Review process: Chrome Web Store / VS Code Marketplace review requirements

`engineering/performance-budgets.md`:
- Background script: minimal memory footprint, no long-polling loops
- Content script: non-blocking injection, no DOM layout thrashing

### Platform-specific security

`security/platform-controls.md`:
- Permissions: minimum permission set — no broad host_permissions without justification
- Content Security Policy: manifest CSP declared (MV3 enforces strict CSP)
- Message validation: all messages validated, no eval() in message handlers
- External connections: declared in manifest, no undeclared network calls

`security/threat-model.md`:
- XSS via content script: sanitize all injected content
- Privilege escalation: background service worker is privileged — validate all messages from content scripts

### Spec template variant

P1 template sections: Host Application (browser/IDE/other), Permission Justification, Content Script Scope, Background Service Worker Lifecycle, Store Listing Requirements

### Verification gates

- Permission audit: each permission justified in spec
- CSP: no CSP violations in browser console during smoke test
- Store review: checklist for target marketplace before submission

---

## 10. Data/Pipeline

**Recipe signals:** `airflow_dag`, `*.pipeline.yaml`, `dbt_project.yml`, `spark` in dependencies, `kafka` import, `prefect`/`dagster` import, ETL-specific directory structure

### New dev modules (no v5.3 equivalent)

| Module | Content |
|---|---|
| ETL | Extract/transform/load patterns, idempotency, incremental vs. full load |
| Streaming | Kafka/Pulsar/Kinesis consumer patterns, consumer groups, offset management |
| Orchestration | Airflow/Prefect/Dagster DAG patterns, retry policies, backfill strategy |
| Schema evolution | Backward/forward compatibility, schema registry, migration without downtime |

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Pipeline containerization: Docker image per pipeline component
- Dependency isolation: no shared virtualenv across pipeline steps
- Data testing: Great Expectations or equivalent for data quality gates

`engineering/performance-budgets.md`:
- Throughput target: records/second declared per pipeline
- Latency SLA: end-to-end latency target declared (batch: hours, streaming: seconds/minutes)
- Backpressure: declared — no unbounded queue growth

### Platform-specific security

`security/platform-controls.md`:
- Data classification: PII/sensitive data declared in spec, handling policy per class
- Encryption: at rest + in transit for sensitive data
- Access: least-privilege per pipeline stage — no pipeline has full database access
- Audit log: all data access logged with source and destination

`security/threat-model.md`:
- Data exfiltration: egress controls for pipelines handling sensitive data
- Injection: parameterized queries for all database writes from pipeline output
- Schema poisoning: validate schema before write, reject malformed records

### Spec template variant

P1 template sections: Data Sources, Data Destinations, Transformation Logic, SLA (latency + freshness), Data Classification, Schema Registry

### Verification gates

- Data quality: quality gates pass on sample dataset before Delivery
- Idempotency: pipeline is idempotent (re-run produces same result)
- Schema compatibility: backward compatibility verified for schema changes

---

## 11. AI/Agent

**Recipe signals:** LLM SDK imports (openai, anthropic, langchain, llamaindex), `agent` in project name/description, `tools` array in prompt config, `.agent.yaml`, chain/graph definition files

### Dev modules

No separate dev module — AI/Agent platform is fed entirely by L4 AI gateway. Platform package SKILL.md routes to AI gateway for all implementation patterns.

### Platform-specific engineering

`engineering/build-toolchain.md`:
- Model pinning: model version pinned in config, not defaulted to "latest"
- Prompt versioning: prompts versioned alongside code, not hardcoded inline
- Eval harness: eval suite required before any prompt or model change ships

`engineering/performance-budgets.md`:
- Latency: p50 and p95 inference latency targets declared
- Cost: token budget per operation declared
- Fallback: declared behavior when model unavailable or over-quota

### Platform-specific security

`security/threat-model.md`:
- Prompt injection: all user input treated as untrusted, system prompt hardened
- Tool call scope: each tool has declared minimum permission, no over-broad tools
- Output validation: all LLM outputs validated before use in downstream systems
- PII in prompts: no PII sent to external models without explicit data processing agreement

`security/platform-controls.md`:
- API keys: env vars only, rotated on compromise
- Rate limiting: client-side rate limit to prevent runaway spend
- Human in the loop: irreversible actions require explicit Attestation gate

### Spec template variant

P1 template sections: Agent Capabilities, Tool Inventory, Context Window Budget, Evaluation Dimensions, Fallback Behavior, Human Oversight Points

### Verification gates

- Eval suite: declared eval dimensions pass before Delivery
- Tool scope: each tool's permission scope reviewed
- Cost ceiling: token spend in staging within declared budget

---

## Common Integration Points (all platforms)

| Module | Relationship |
|---|---|
| Recipe | Recipe identifies target, activates platform package via Recipe gate |
| Apply | Apply reads platform SKILL.md for gateway routing decisions |
| Executor | Executor loads platform spec templates and dev modules at wave start |
| Verifier | Verifier reads platform verification/gates.md for target-specific gate checks |
| Security gateway | Platform security modules feed cross-cutting Security gateway review |
| Engineering gateway | Platform engineering modules feed cross-cutting Engineering gateway review |
| _shared/dev/ | Platform packages load shared language, database, api-consumption modules on demand |

---

## Common Verification Mode

**Demonstration** — platform package activated correctly for detected target, platform-specific verification gates pass, platform spec template variant used, receipt written.

---

## Common Receipt Extension Fields

```json
{
  "platform_target": "web|api-service|game|mobile|desktop|cli|iot-embedded|library-package|extension-plugin|data-pipeline|ai-agent",
  "dev_modules_loaded": ["string"],
  "engineering_modules_loaded": ["string"],
  "security_modules_loaded": ["string"],
  "spec_template_variant": "string",
  "verification_gates_passed": ["string"],
  "verification_gates_failed": ["string"]
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Kotlin separate from Java in Mobile | Sub-section of Java module vs. own Mobile/Kotlin module | Per-platform build |
| Multi-platform targets (e.g. Web + Mobile) | Secondary target loaded alongside primary vs. separate run | P2 Recipe planning review |
| IoT sub-targets (MCU vs. SBC like RPi) | Same platform package vs. IoT/MCU + IoT/Linux split | Per-platform build |
| AI/Agent as both platform and gateway consumer | Route confirmed: platform package for target detection, AI gateway for implementation content | Locked |
