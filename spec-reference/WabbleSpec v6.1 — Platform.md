# WabbleSpec v6.1 — Platform

Platform is the first hard routing decision after intake. It determines whether the project is Web, API/Service, Game, Mobile, Desktop, CLI, IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, or AI/Agent — then shapes every downstream artifact, capability handoff, verification gate, and delivery artifact around that target.

Platform exists because WabbleSpec must not treat every project like a web app with decorations. A browser product, a playable game, a signed mobile release, a local desktop app, a terminal tool, a distributable library, a firmware system, a data pipeline, and an AI agent all need different proof. The framework shares one spine. Each target deserves its own lifecycle.

---

## 1. Position in the Framework

Platform (L3) is downstream of Recipe and ScopeFrame, upstream of capability gateways and execution waves. No capability module, delivery module, or evolution module may claim platform authority. Platform defines what completion means per target.

**Layer:** L3 — Platform

**Inputs:** Build target from Recipe, scope from ScopeFrame, spec from Specify

**Outputs:** Platform contract, spec template variant, verification gate list, capability handoff declarations, engineering and security baseline, delivery artifact type

**Rule:** Platform is not a folder taxonomy. It is the contract that tells the system what completion means. A Web project is not complete until browser proof exists. A Game is not complete until the loop is playable. An IoT device is not complete until hardware, firmware, protocol, and safety evidence are explicit.

---

## 2. Common Package Structure

Every platform package follows this layout:

```
.wabblespec/platforms/<target>/
  SKILL.md                      ← routing logic, module load order, platform rules
  skill-rules.json              ← Recipe activation signals for this target
  spec-template/
    design-document.md          ← P1 spec template variant for this target
    systems-design.md           ← P2 template variant
    technical-spec.md           ← P3 template variant
  dev/                          ← platform-specific dev modules
    <framework-or-lang>/
      references/
      rules/
  engineering/
    build-toolchain.md
    performance-budgets.md
    platform-verification.md
  security/
    threat-model.md
    platform-controls.md
  verification/
    gates.md                    ← checkable verification gate list for this target
  schemas/
    receipt.schema.json
```

Platform packages are self-contained. Each owns its activation signals, engineering constraints, security controls, spec templates, and verification gates. Platform packages do not orchestrate across each other.

---

## 3. Router Contract

Recipe emits a route object before planning begins. All modules downstream read this — none may infer the target independently.

```yaml
build_target:
  primary: web|api-service|game|mobile|desktop|cli|iot-embedded|library-package|extension-plugin|data-pipeline|ai-agent
  secondary: []
  confidence: high|medium|low
  evidence:
    - user language signals
    - detected file signals (package.json, go.mod, CMakeLists.txt, etc.)
    - repository structure signals
  platform_artifacts:
    - required spec document
    - required receipts
  capability_handoff:
    always_load: []
    conditional_load: []
  verification_gates: []
```

If confidence is low, Interview asks only target-identification questions before planning proceeds.

---

## 4. Gate Matrix

| Target | Planning artifact | Build evidence | User-facing proof | Release proof |
|---|---|---|---|---|
| Web | WEB-SPEC.md | build, browser smoke | responsive matrix, WCAG 2.1 AA | routes/API/security, deploy receipt |
| API/Service | API-SPEC.md | contract tests, health check | error coverage, auth enforcement | load test, structured logs |
| Game | GDD.md + PLAYTEST.md | playable loop, controls | performance budget, playtest evidence | build/export |
| Mobile | MOBILE-SPEC.md | simulator/device smoke | permissions, offline/sync | signing, store readiness |
| Desktop | DESKTOP-SPEC.md | launch smoke, OS integration | local file/sandbox | signing, installer |
| CLI | CLI-SPEC.md | command matrix, help text | stdout/stderr, exit codes | golden tests, packaging |
| IoT/Embedded | IOT-SPEC.md | firmware compile, hardware smoke | protocol contract | safety limits, OTA/rollback |
| Library/Package | LIBRARY-SPEC.md | build, type check | public API documented | semver policy, publish dry-run |
| Extension/Plugin | EXTENSION-SPEC.md | manifest valid, CSP clean | permission audit | store checklist |
| Data/Pipeline | PIPELINE-SPEC.md | quality gates on sample | idempotency verified | schema compatibility |
| AI/Agent | AI-SPEC.md | eval suite run | guardrails tested | cost ceiling, safety policy |

---

## 5. Capability Handoff Rules

Platform does not replace capability gateways. It gives them target-shaped work. The same gateway name means different things per target.

| Capability | Web | API/Service | Game | Mobile | Desktop | CLI | IoT/Embedded |
|---|---|---|---|---|---|---|---|
| Development | app routes, components | endpoints, services | game loop, engine scripts | screens, device APIs | shell, windows, IPC | commands, flags, streams | firmware, services |
| Engineering | build, deploy pipeline | containerization, SLOs | build/export pipeline | native bridges, CI | packaging, updater | distribution, startup | reliability, power |
| Security | auth, CORS, secrets | RBAC, input validation | multiplayer, saves | permissions, storage | IPC, local trust | destructive cmds | device identity, OTA |
| Design | IA, responsive flows | API contract clarity | HUD, menus | navigation, platform controls | menus, windows | command grammar | field tool UI |
| Experience | browser workflow | — | play feel | touch, lifecycle | local app ergonomics | terminal ergonomics | installation, field ops |
| Aesthetic | brand, visual consistency | — | art direction, animation | native visual fit | app chrome | terminal clarity | industrial UI |
| AI | chat, generation, agents | model API integration | NPCs, procedural | on-device AI | local AI, privacy | agentic commands | edge inference |

---

## 6. Secondary Target Rules

1. Primary target owns completion gates.
2. Secondary targets are recorded explicitly — not ignored.
3. Secondary targets add capability requirements but cannot weaken primary gates.
4. If a secondary target becomes user-critical, ScopeFrame must decide whether it enters the current release or becomes a later phase.
5. Verifier must reject completion claims for secondary targets without specific evidence.
6. Package and Deploy record whether secondary targets are shipped, deferred, or not applicable.

---

## 7. Platform Definitions

### 7.1 Web

**Recipe signals:** `package.json` with react/next/vue/svelte/angular/astro/vite, `*.tsx`/`*.jsx`, `next.config.*`, `vite.config.*`, `index.html` at root

**Primary spec:** `WEB-SPEC.md`

**P1 spec template sections:** Target Users, Key Journeys, Visual Direction, Accessibility Requirements, Browser Support Matrix, Performance Budget

**Default capabilities:** Development (_shared/dev/ + web dev modules), Design, Experience, Security, Engineering

**Conditional capabilities:** Aesthetic, AI

**Common secondary targets:** CLI, Mobile, AI/Agent

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| React | Component patterns, hooks, state management (Zustand/Jotai/Redux), prop drilling avoidance |
| NextJS | App router vs. pages router, SSR/SSG/ISR, route handlers, middleware |
| Vue | Composition API, Pinia, SFC structure, Vue Router |
| Svelte | Stores, reactive declarations, SvelteKit routing |
| Angular | Standalone components, signals, RxJS patterns |
| HTML/CSS | Semantic HTML, ARIA roles, CSS custom properties |
| Styling | CSS Modules, Tailwind, CSS-in-JS — module declares active system |
| PWA | Service worker, manifest.json, offline strategy, install prompt |

---

#### Engineering

**Build toolchain:**
- Vite (default), Webpack (legacy only with written justification), Turbopack (Next 13+)
- Bundle analysis: bundle size tracked per build, budget declared in config
- Tree shaking: verified via bundle analyzer output

**Performance budgets:**
- Core Web Vitals: LCP < 2.5s, CLS < 0.1, INP < 200ms
- JS bundle: initial load < 200KB gzipped (configurable per project, documented if exceeded)
- Images: lazy loading via next/image or equivalent required

---

#### Security

**Platform controls:**
- CSP header required for all production deployments
- XSS: no `dangerouslySetInnerHTML` without sanitization, no `eval()`
- CORS: explicit allowlist, no wildcard in production
- Subresource integrity: SRI on all externally hosted scripts
- Secrets: environment variables only, never committed

---

#### Verification Gates

- Lighthouse CI: Core Web Vitals pass before Delivery
- Accessibility: axe-core or equivalent, zero critical violations (WCAG 2.1 AA)
- Bundle budget: enforced in CI
- Browser smoke: all declared browser targets
- Route coverage: all routes return expected status codes

---

#### Failure Modes

- Hydration or routing mismatch between SSR and client
- Auth/session and CORS misconfiguration
- Secret exposure in client bundle
- Responsive layout overlap on untested viewports
- Accessibility regressions after visual changes
- Unverified deployment (no receipt)

---

### 7.2 API/Service

**Recipe signals:** `server.ts`/`server.py`/`main.go`, `Dockerfile` with EXPOSE, `openapi.yaml`/`swagger.json`, framework-specific entry (fastapi, express, gin, nestjs, actix, spring-boot)

**Primary spec:** `API-SPEC.md`

**P1 spec template sections:** API Contract (OpenAPI/proto), Auth Model, Rate Limits, SLA, Error Response Format, Versioning Strategy

**Default capabilities:** Development (_shared/dev/ + API server modules), Engineering, Security

**Conditional capabilities:** AI (if model-backed)

**Common secondary targets:** Web (admin UI), Mobile (companion app)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| REST server | Express/Fastify/Gin/FastAPI/Actix route patterns, middleware, request validation |
| GraphQL server | Apollo Server, Strawberry, gqlgen — schema-first patterns, resolver design |
| gRPC server | Proto service definitions, interceptor patterns, server reflection |
| Realtime server | Socket.io, ws, SSE endpoint patterns |

Language module also loaded from `_shared/dev/languages/` based on detected stack.

---

#### Engineering

**Build toolchain:**
- Containerization: Dockerfile multi-stage build (builder + runtime image)
- Health check: `/health` and `/ready` endpoints required
- Graceful shutdown: SIGTERM handler, drain in-flight requests before exit

**Performance budgets:**
- p99 latency target declared per endpoint type (REST: 200ms, gRPC: 50ms defaults — override in spec)
- Throughput: RPS target declared in spec, not assumed
- Connection pool sizing: declared explicitly, not left at framework defaults

---

#### Security

**Threat model:**
- Authentication: every endpoint declares its auth requirement, or explicit `public`
- Authorization: RBAC or ABAC pattern declared in spec
- Input validation: all external inputs validated at boundary (Zod, Pydantic, etc.)
- Rate limiting: required for all public-facing endpoints

**Platform controls:**
- Secrets: env vars only, no config files with secrets in repo
- TLS: required in production, minimum TLS 1.2
- OWASP API Security Top 10: checklist in verification gates

---

#### Verification Gates

- Contract test: generated client against server passes (or OpenAPI contract test)
- Auth coverage: every endpoint has both authenticated and unauthorized test cases
- Load test: baseline RPS target met before Delivery
- Structured logging: log schema verified
- Health endpoint: returns 200 within 2s under load

---

#### Failure Modes

- Endpoints without auth declaration
- Input validation missing at boundary
- No graceful shutdown — dropped requests on deploy
- Rate limiting absent on public routes
- Error responses leaking internal stack traces

---

### 7.3 Game

**Recipe signals:** `unity/`, `godot.project`, `*.gd`, `bevy` in Cargo.toml, `phaser` in package.json, Unreal `.uproject`

**Primary spec:** `GDD.md` + `PLAYTEST.md`

**P1 spec template sections:** Game Loop, Core Mechanics, Platform Targets, Input Scheme, Monetization Model (if any), Target Framerate

**Default capabilities:** Development (game dev modules), Aesthetic, Experience, Engineering

**Conditional capabilities:** Security (if networked/multiplayer), AI (procedural/NPCs)

**Common secondary targets:** Desktop, Mobile, Web (browser export)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| Engine | Unity/Godot/Bevy/Unreal — project structure, scene management, asset pipeline |
| TwoD | Sprite, tilemap, 2D physics (Box2D/Rapier), camera patterns |
| ThreeD | Mesh, material, PBR lighting, 3D physics, LOD |
| GamePhysics | Collision layers, rigidbody patterns, trigger vs. collider |
| GameAudio | AudioSource pooling, spatial audio, music/sfx separation, audio bus management |

---

#### Engineering

**Build toolchain:**
- Build targets: platform-specific export (WebGL, PC, Console, Mobile) declared in spec
- Asset pipeline: atlas packing, compression settings, streaming strategy
- Engine version pinned in project config (no floating version)

**Performance budgets:**
- Frame budget: target framerate declared (30/60/120fps), frame time budget derived
- Draw calls: budget per scene type declared
- Memory: texture memory, audio memory, GC allocation budgets declared

---

#### Security

**Platform controls:**
- Anti-cheat scope: server-authoritative for multiplayer, client-side only for single-player (declared)
- Save data: local save encryption if sensitive progression
- Network: dedicated server vs. P2P — security model declared per choice

---

#### Verification Gates

- Frame rate: profiler baseline on target hardware before Delivery
- Input: tested on all declared input schemes (keyboard, gamepad, touch)
- Crash: no crash in 10-minute smoke test on each declared target platform
- Playtest: receipt from at least one human playtest session

---

#### Failure Modes

- Prototype without a verified playable loop
- Control feel ignored — input latency unmeasured
- Asset and audio budgets unmanaged
- Performance collapse discovered post-ship
- Export targets assumed — not verified

---

### 7.4 Mobile

**Recipe signals:** `ios/` directory, `android/` directory, `*.swift`, `*.kt`, `react-native.config.js`, `pubspec.yaml` (Flutter), `Podfile`

**Primary spec:** `MOBILE-SPEC.md`

**P1 spec template sections:** Supported OS Versions, Device Targets (phone/tablet), Offline Behavior, Push Notification Strategy, App Store Metadata

**Default capabilities:** Development (mobile dev modules), Experience, Security, Engineering

**Conditional capabilities:** Aesthetic, AI (on-device or server-backed)

**Common secondary targets:** Web (admin), API/Service (backend)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| iOS | Swift patterns, UIKit vs. SwiftUI, Xcode project structure, App Store review requirements |
| Android | Kotlin patterns, Jetpack Compose, Gradle module structure, Play Store requirements |
| ReactNative | Bridge vs. JSI, Metro bundler, EAS Build, `Platform.OS` patterns |
| Flutter | Widget tree, state management (Riverpod/Bloc), Dart null safety, platform channels |

---

#### Engineering

**Build toolchain:**
- iOS: Xcode + fastlane, code signing declared (automatic vs. manual)
- Android: Gradle wrapper committed, keystore in CI secrets
- RN/Flutter: EAS Build or equivalent, OTA update strategy declared

**Performance budgets:**
- App launch: cold start < 3s, warm start < 1s
- Binary size: declared per platform (iOS: < 50MB, Android: < 30MB AAB typical — documented if exceeded)
- Memory: no OOM in 30-minute session on minimum supported device

---

#### Security

**Platform controls:**
- App permissions: minimum required permissions declared in spec
- Keychain/Keystore: sensitive data in platform secure storage — never SharedPreferences/UserDefaults
- Certificate pinning: required for apps handling financial or health data
- Jailbreak/root detection: scope declared in threat model

**Threat model:**
- Reverse engineering: obfuscation strategy declared (ProGuard/R8 for Android)
- Deep links: validation required, no unauthenticated deep link actions
- Third-party SDKs: explicit allowlist, privacy policy covers all SDK data collection

---

#### Verification Gates

- Device matrix: tested on minimum supported OS + latest OS
- App Store compliance: guidelines checklist passed before submission
- Accessibility: VoiceOver (iOS) / TalkBack (Android) smoke test
- Permissions: all declared permissions verified with user-facing rationale

---

#### Failure Modes

- Desktop layout assumptions leaking into mobile
- Permissions added without documented user value
- Offline paths untested — sync conflicts on resume
- Store privacy policy mismatch (SDK data collection undisclosed)
- Signing delay blocking release

---

### 7.5 Desktop

**Recipe signals:** `electron` in package.json, `tauri.conf.json`, `.NET` targeting WPF/WinUI, `qt` dependency, Swift/AppKit Mac target

**Primary spec:** `DESKTOP-SPEC.md`

**P1 spec template sections:** OS Targets (Win/Mac/Linux), Distribution Channel (store/sideload/enterprise), Update Strategy, Offline-First Requirements, Native Integration Needs

**Default capabilities:** Development (desktop dev modules), Experience, Security, Engineering

**Conditional capabilities:** Aesthetic, AI (local assistant)

**Common secondary targets:** CLI, Web, AI/Agent

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| Electron | Main/renderer process separation, IPC patterns, context isolation (required), preload scripts |
| Tauri | Commands (Rust backend), events, updater, permissions (allowlist) |
| Native macOS | AppKit/SwiftUI, Sandbox entitlements, notarization |
| Native Windows | WPF/WinUI, MSIX packaging, Windows Store or sideload |

---

#### Engineering

**Build toolchain:**
- Electron: electron-builder or electron-forge, auto-updater declared
- Tauri: Cargo build + npm build, bundler config
- Code signing: required for distribution (Apple notarization, Windows Authenticode)

**Performance budgets:**
- Memory baseline: idle memory footprint declared
- App startup: cold start target declared per platform
- Installer size: declared (Electron apps are large — document and justify in spec)

---

#### Security

**Platform controls:**
- Electron: `contextIsolation: true` (non-negotiable), `nodeIntegration: false`, preload scripts only channel
- Tauri: allowlist minimal — only declared capabilities enabled
- Auto-update: signed updates only, TLS delivery enforced
- Local data: encrypt sensitive local data (SQLCipher or equivalent)

---

#### Verification Gates

- Code signing: verified before Delivery
- Auto-update: smoke tested (update from previous version succeeds)
- OS-specific: tested on all declared OS targets
- Context isolation: verified in Electron renderer process

---

#### Failure Modes

- Local trust model treated like web trust (no sandbox boundaries)
- IPC surface exposed too broadly from renderer
- Auto-update not planned — manual reinstall required for fixes
- Installer not verified on actual target OS
- Cross-OS behavior assumed, not tested

---

### 7.6 CLI

**Recipe signals:** `bin` field in package.json, `cli.py`/`__main__.py`, `cmd/` in Go project, `clap` in Cargo.toml, `cobra` import, shebang in entry file

**Primary spec:** `CLI-SPEC.md`

**P1 spec template sections:** Command Structure, Subcommand Hierarchy, Config File Schema, Output Modes (--json, --quiet), Stdin/Stdout/Stderr Contract

**Default capabilities:** Development (_shared/dev/ + CLI framework modules), Engineering, Experience (terminal UX)

**Conditional capabilities:** Security (if filesystem or network risk exists)

**Common secondary targets:** Desktop (wrapper), Web (configuration UI)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| CLI framework | Commander/Yargs (Node), Click/Typer (Python), Cobra (Go), Clap (Rust) |
| Output formatting | Color, tables, spinners, progress bars — terminal capability detection |
| Config | Config file conventions (XDG, `~/.apprc`), env var override hierarchy |
| Distribution | npm global, PyPI, Homebrew, binary release (GitHub Releases) |

---

#### Engineering

**Build toolchain:**
- Single binary: preferred for Go/Rust CLIs, cross-compile targets declared
- npm global: peer dependency warnings addressed, postinstall scripts avoided
- Shell completions: generation for bash/zsh/fish declared in spec if required

**Performance budgets:**
- Startup time: < 100ms cold start for short-lived commands
- No unnecessary runtime dependencies loaded on startup (no full framework for a utility)

---

#### Security

**Platform controls:**
- Input: all CLI arguments validated, no shell injection from user input
- Credentials: never accepted as positional args (visible in `ps`, shell history) — use env vars or stdin
- File operations: validate all paths, no path traversal
- Network: explicit opt-in for any network calls, documented in help text

---

#### Verification Gates

- Help text: all commands and subcommands have `--help` output
- Exit codes: 0 = success, non-zero = failure — every error path verified
- Stdout/stderr: machine-readable output (--json) tested for parsability
- Golden tests: known-input → known-output verified
- Shell completion: if declared in spec, generated and tested

---

#### Failure Modes

- Human-readable text mixed into machine-parseable stdout
- Exit codes undocumented or inconsistent
- Config precedence unclear (env var vs. config file vs. flag)
- Destructive commands with no `--dry-run` or confirmation prompt
- Help text stale — flags added but not documented

---

### 7.7 IoT/Embedded

**Recipe signals:** `CMakeLists.txt`, `platformio.ini`, `Makefile` with arm-none-eabi target, `micropython` import, `embassy` or `rtic` in Cargo.toml, firmware-specific config files

**Primary spec:** `IOT-SPEC.md`

**P1 spec template sections:** Target MCU/SoC, RTOS or bare-metal, Communication Protocol (UART/SPI/I2C/BLE/WiFi), Power Profile, OTA Update Strategy

**Default capabilities:** Development (embedded dev modules), Engineering, Security

**Conditional capabilities:** Experience (companion UI), Web or Mobile (companion app as secondary target)

**Common secondary targets:** Web (dashboard), Mobile (companion app), API/Service (cloud backend)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| C/C++ | CMake patterns, header organization, embedded C idioms, MISRA guidance |
| MicroPython | MicroPython stdlib subset, asyncio patterns, flash-aware design |
| Embedded Rust | no_std patterns, embassy/RTIC async, PAC/HAL abstraction |
| Firmware build | Flash/RAM budget, linker script, objcopy, upload toolchain (JLink, openocd) |

---

#### Engineering

**Build toolchain:**
- Cross-compilation: target triple declared (arm-none-eabi, thumbv7em-none-eabihf, etc.)
- Dependencies: vendored — no network access during build (embedded builds are offline)
- Flash map: memory layout declared and documented

**Performance budgets:**
- Flash budget: binary size vs. available flash declared per target MCU
- RAM budget: stack + heap declared, stack overflow detection enabled in debug builds
- CPU budget: interrupt latency target declared for real-time tasks

---

#### Security

**Threat model:**
- Firmware update: signed OTA required for all network-connected devices
- Debug interfaces: JTAG/SWD disabled in production firmware
- Secrets: hardware security element (TPM/SE) for key storage where available
- Physical access: threat model explicitly declares physical attack scope

**Platform controls:**
- No dynamic memory allocation in critical paths (C/C++)
- Stack canaries enabled in debug builds
- Watchdog timer required in all production firmware

---

#### Verification Gates

- Build: firmware builds for target hardware in CI
- Flash: runs on target hardware (or declared emulator with explicit Not-tested)
- Memory: flash and RAM within declared budget
- Safety: all safety constraints from spec verified
- OTA: rollback procedure documented and smoke-tested

---

#### Failure Modes

- Software-only test presented as hardware proof
- Unsafe actuator defaults (fails open, not closed)
- Protocol retries missing — silent failure on packet loss
- OTA rollback absent — bricked device on bad update
- Physical access threat not modeled

---

### 7.8 Library/Package

**Recipe signals:** `lib` or `index` as main entry, no `bin` field, `package.json` with `files` field, `setup.py`/`pyproject.toml` with `[project]`, `lib.rs` as crate root, `*.podspec`

**Primary spec:** `LIBRARY-SPEC.md`

**P1 spec template sections:** Public API Surface, Versioning Strategy, Minimum Runtime Support, Peer Dependency Requirements, Documentation Coverage Target

**Default capabilities:** Development (_shared/dev/ + library modules), Engineering

**Conditional capabilities:** Security (if library handles auth, crypto, or sensitive data)

**Common secondary targets:** CLI (development tool companion), Web (demo site)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| API surface design | Minimal public API, backward compatibility, deprecation patterns |
| Semver | Semantic versioning enforcement, breaking change detection |
| Registry publishing | npm, PyPI, crates.io, Maven Central — publishing config, access tokens |
| Doc generation | TypeDoc, Sphinx, rustdoc, Javadoc — required for all public exports |

---

#### Engineering

**Build toolchain:**
- Dual output: ESM + CJS for JS libraries (documented if ESM-only with compatibility justification)
- Type declarations: `.d.ts` shipped, not generated at install time
- Peer dependencies: declared as `peerDependencies`, not `dependencies` (JS)
- Source maps: shipped for debugging by downstream consumers

**Performance budgets:**
- Bundle impact: library size impact on consumer bundle declared
- Tree-shakeable: ESM + named exports, no side effects in module root files

---

#### Security

**Platform controls:**
- Supply chain: no typosquatting risk in package name — verify before publish
- No postinstall scripts that execute arbitrary code
- Dependency count: minimal transitive dependencies — each dependency justified
- Publish auth: 2FA required on registry account

---

#### Verification Gates

- API surface: public API reviewed before every minor or major version bump
- Type safety: no `any` in public type signatures (TypeScript/typed languages)
- Doc coverage: all public exports documented
- Consumer test: downstream consumer integration test passes
- Publish dry-run: `npm pack` or equivalent dry-run passes

---

#### Failure Modes

- Breaking changes shipped in patch or minor versions
- Type declarations missing or incorrect
- `any` types in public API (downstream consumers lose type safety)
- Undeclared peer dependencies (runtime errors in consumer)
- No documentation for public exports

---

### 7.9 Extension/Plugin

**Recipe signals:** `manifest.json` with `manifest_version`, `.vscodeignore`, `vscode:package` script, host-application-specific config files

**Primary spec:** `EXTENSION-SPEC.md`

**P1 spec template sections:** Host Application (browser/IDE/other), Permission Justification, Content Script Scope, Background Service Worker Lifecycle, Store Listing Requirements

**Default capabilities:** Development (extension dev modules), Security, Engineering

**Conditional capabilities:** Experience (popup/sidebar UI), Aesthetic

**Common secondary targets:** Web (extension options page)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| Browser extension | Chrome MV3 manifest, service worker background, content script isolation, permissions model |
| VS Code extension | Extension API patterns, activation events, contributes schema, webview sandbox |
| Host sandbox patterns | Message passing between extension and host, no direct DOM in background context |

---

#### Engineering

**Build toolchain:**
- Browser: webpack/rollup bundle to `dist/`, manifest.json as source of truth
- VS Code: vsce package, esbuild bundling
- Review process: Chrome Web Store / VS Code Marketplace review requirements documented before submission

**Performance budgets:**
- Background script: minimal memory footprint, no long-polling loops
- Content script: non-blocking injection, no DOM layout thrashing

---

#### Security

**Platform controls:**
- Permissions: minimum permission set — no broad `host_permissions` without written justification
- Content Security Policy: manifest CSP declared (MV3 enforces strict CSP — no relaxation)
- Message validation: all messages validated before processing, no `eval()` in message handlers
- External connections: all declared in manifest, no undeclared network calls

**Threat model:**
- XSS via content script: all injected content sanitized
- Privilege escalation: background service worker is privileged — validate all messages from content scripts before acting

---

#### Verification Gates

- Permission audit: each permission justified in spec and receipt
- CSP: no CSP violations in browser console during smoke test
- Isolation: content script cannot escalate to background privileges
- Store review: marketplace checklist completed before submission

---

#### Failure Modes

- Over-permissioned manifest (permissions added for potential future use)
- Content script injected into pages outside declared scope
- Background service worker with privileged access not validating content script messages
- CSP relaxed to accommodate inline scripts

---

### 7.10 Data/Pipeline

**Recipe signals:** `airflow_dag`, `*.pipeline.yaml`, `dbt_project.yml`, `spark` in dependencies, `kafka` import, `prefect`/`dagster` import, ETL-specific directory structure

**Primary spec:** `PIPELINE-SPEC.md`

**P1 spec template sections:** Data Sources, Data Destinations, Transformation Logic, SLA (latency + freshness), Data Classification, Schema Registry

**Default capabilities:** Development (pipeline dev modules), Engineering, Security

**Conditional capabilities:** AI (if ML pipeline)

**Common secondary targets:** Web (monitoring dashboard), API/Service (output sink)

---

#### Dev Modules Loaded

| Module | Content |
|---|---|
| ETL | Extract/transform/load patterns, idempotency, incremental vs. full load |
| Streaming | Kafka/Pulsar/Kinesis consumer patterns, consumer groups, offset management |
| Orchestration | Airflow/Prefect/Dagster DAG patterns, retry policies, backfill strategy |
| Schema evolution | Backward/forward compatibility, schema registry, migration without downtime |

---

#### Engineering

**Build toolchain:**
- Pipeline containerization: Docker image per pipeline component
- Dependency isolation: no shared virtualenv across pipeline steps
- Data testing: Great Expectations or equivalent for data quality gates

**Performance budgets:**
- Throughput target: records/second declared per pipeline
- Latency SLA: end-to-end latency declared (batch: hours, streaming: seconds/minutes)
- Backpressure: declared — no unbounded queue growth

---

#### Security

**Platform controls:**
- Data classification: PII/sensitive data declared in spec, handling policy per classification
- Encryption: at rest + in transit for all sensitive data
- Access: least-privilege per pipeline stage — no pipeline has full database access
- Audit log: all data access logged with source, destination, and timestamp

**Threat model:**
- Data exfiltration: egress controls for pipelines handling sensitive data
- Injection: parameterized queries for all database writes from pipeline output
- Schema poisoning: validate schema before write, reject malformed records

---

#### Verification Gates

- Data quality: quality gates pass on sample dataset before Delivery
- Idempotency: pipeline re-run produces identical output
- Schema compatibility: backward compatibility verified for schema changes
- Lineage: data lineage documented for all transformations

---

#### Failure Modes

- Pipeline not idempotent — re-runs produce duplicates or corruption
- Schema changes break downstream consumers silently
- PII handled without declared classification
- No backpressure — queue grows unbounded under load
- Retry logic absent — transient failures cause pipeline stall

---

### 7.11 AI/Agent

**Recipe signals:** LLM SDK imports (openai, anthropic, langchain, llamaindex), `agent` in project name or description, `tools` array in prompt config, `.agent.yaml`, chain/graph definition files

**Primary spec:** `AI-SPEC.md`

**P1 spec template sections:** Agent Capabilities, Tool Inventory, Context Window Budget, Evaluation Dimensions, Fallback Behavior, Human Oversight Points

**Default capabilities:** Development (routes entirely to AI gateway), Engineering, Security, AI gateway

**Conditional capabilities:** Experience (if user-facing), Design (if chat UI or agent UI)

**Common secondary targets:** Web (chat UI), API/Service (agent API)

---

#### Dev Modules

AI/Agent platform routes all implementation patterns to the L4 AI gateway. The platform package SKILL.md does not contain implementation patterns — it declares routing, spec template, engineering constraints, security baseline, and verification gates. L4 AI gateway owns the implementation content.

---

#### Engineering

**Build toolchain:**
- Model pinning: model version pinned in config — never `"latest"` in production
- Prompt versioning: prompts versioned alongside code, not hardcoded inline
- Eval harness: eval suite required before any prompt or model change ships

**Performance budgets:**
- Latency: p50 and p95 inference latency targets declared
- Cost: token budget per operation declared in spec
- Fallback: declared behavior when model unavailable or over-quota

---

#### Security

**Threat model:**
- Prompt injection: all user input treated as untrusted, system prompt hardened against injection
- Tool call scope: each tool has minimum declared permission — no over-broad tool access
- Output validation: all LLM outputs validated before use in downstream systems
- PII in prompts: no PII sent to external models without explicit data processing agreement

**Platform controls:**
- API keys: env vars only, rotated on compromise detection
- Rate limiting: client-side rate limit to prevent runaway spend
- Human-in-the-loop: irreversible agent actions require Attestation gate

---

#### Verification Gates

- Eval suite: all declared eval dimensions pass before Delivery
- Tool scope: each tool's permission scope reviewed and documented
- Cost ceiling: token spend in staging within declared budget
- Guardrails: prompt injection tests pass
- Fallback: degraded behavior verified (model unavailable scenario)

---

#### Failure Modes

- Prompt injection via user input reaching system context
- Tool with over-broad permissions (reads entire filesystem when only one directory needed)
- No eval suite — model behavior changes undetected
- Cost runway not declared — runaway spend in production
- No fallback behavior — total failure when model API is unavailable

---

## 8. Platform Completion Definitions

A platform target is complete only when:

1. The required planning artifact exists (WEB-SPEC.md, GDD.md, etc.)
2. All core artifacts are present and linked in receipts
3. Platform verification gates have either PASS or explicit NOT-TESTED status
4. NOT-TESTED items name the specific missing tool, device, or environment
5. Package and Deploy state is recorded when the target requires distribution
6. No undocumented gaps between the spec and the verification evidence

Anything less is in-progress, not complete. Verifier enforces this — no prose-only success claim passes.

---

## 9. Target Walkthroughs

### 9.1 Web Walkthrough

```
1. Recipe sees signals: package.json with React/Next/Vue, *.tsx, next.config.*
2. Recipe emits primary target 'web' with confidence and evidence
3. ScopeFrame bounds the release (MVP, prototype, production)
4. ReferenceLoad selects web-relevant packs
5. Specify writes WEB-SPEC.md with EARS requirements, browser matrix, performance budget
6. Web platform package loads dev modules (React/Next/Vue/etc.), engineering, security
7. Decompose creates waves; verification gate list loaded from verification/gates.md
8. Executor applies changes under project/repo/
9. Verifier: build, browser smoke, responsive matrix, WCAG 2.1 AA, routes/API/security
10. Package → Deploy → Release → Archive
```

### 9.2 API/Service Walkthrough

```
1. Recipe sees signals: server.ts, Dockerfile with EXPOSE, openapi.yaml
2. Recipe emits primary target 'api-service'
3. Specify writes API-SPEC.md with contract, auth model, SLA, error format
4. API/Service platform loads REST/GraphQL/gRPC server modules, engineering, security
5. Decompose creates endpoint-group waves
6. Verifier: contract tests, auth coverage, load test baseline, health endpoint
7. Monitor: SLO definitions, alert rules, structured log schema
8. Package → Deploy → Release → Archive
```

### 9.3 Game Walkthrough

```
1. Recipe sees signals: godot.project, *.gd, unity/ directory
2. Recipe emits primary target 'game'
3. Specify writes GDD.md + PLAYTEST.md
4. Game platform loads engine/2D/3D/physics/audio modules, engineering, security (if networked)
5. Decompose: core loop first, then systems, then assets
6. Verifier: playable loop, controls on all input schemes, frame rate budget, playtest receipt, build/export
7. Package → Release → Archive
```

### 9.4 Mobile Walkthrough

```
1. Recipe sees signals: ios/ directory, pubspec.yaml, react-native.config.js
2. Recipe emits primary target 'mobile'
3. Specify writes MOBILE-SPEC.md with OS matrix, permissions, offline behavior
4. Mobile platform loads iOS/Android/RN/Flutter modules, engineering, security
5. Decompose: navigation first, then features, then device-specific
6. Verifier: simulator/device smoke, permissions, offline/sync, store readiness
7. Package → Deploy (TestFlight/Play internal) → Release → Archive
```

### 9.5 Desktop Walkthrough

```
1. Recipe sees signals: electron in package.json, tauri.conf.json
2. Recipe emits primary target 'desktop'
3. Specify writes DESKTOP-SPEC.md with OS targets, distribution channel, update strategy
4. Desktop platform loads Electron/Tauri/native modules, engineering, security
5. Decompose: core shell first, then features, then packaging
6. Verifier: launch smoke, context isolation, auto-update smoke, OS-specific tests
7. Package (signed) → Deploy → Release → Archive
```

### 9.6 CLI Walkthrough

```
1. Recipe sees signals: bin field in package.json, cmd/ in Go project, clap in Cargo.toml
2. Recipe emits primary target 'cli'
3. Specify writes CLI-SPEC.md with command contract, output modes, exit codes
4. CLI platform loads framework/output/config/distribution modules, engineering
5. Decompose: commands as waves
6. Verifier: help text, stdout/stderr contract, exit codes, golden tests, packaging
7. Package → Release → Archive
```

### 9.7 IoT/Embedded Walkthrough

```
1. Recipe sees signals: CMakeLists.txt, platformio.ini, embedded Rust in Cargo.toml
2. Recipe emits primary target 'iot-embedded'
3. Specify writes IOT-SPEC.md with MCU target, safety constraints, OTA strategy
4. IoT platform loads C/C++/MicroPython/Embedded Rust modules, engineering, security
5. Decompose: firmware core → protocol → telemetry → OTA
6. Verifier: build, flash on hardware (or marked emulator), memory budget, safety gates
7. Package → Deploy (fleet) → Release → Archive
```

### 9.8 Library/Package Walkthrough

```
1. Recipe sees signals: no bin, files field, lib.rs as crate root
2. Recipe emits primary target 'library-package'
3. Specify writes LIBRARY-SPEC.md with public API surface, semver policy
4. Library platform loads API surface/semver/registry/doc modules, engineering
5. Decompose: API design first, then implementation, then consumer tests
6. Verifier: type safety, doc coverage, consumer test, publish dry-run
7. Package → Release (registry publish) → Archive
```

### 9.9 Extension/Plugin Walkthrough

```
1. Recipe sees signals: manifest.json with manifest_version, .vscodeignore
2. Recipe emits primary target 'extension-plugin'
3. Specify writes EXTENSION-SPEC.md with permissions, content script scope
4. Extension platform loads browser extension/VS Code/sandbox modules, security
5. Decompose: manifest + permissions first, then features
6. Verifier: permission audit, CSP clean, store checklist
7. Package → Release (store submission) → Archive
```

### 9.10 Data/Pipeline Walkthrough

```
1. Recipe sees signals: dbt_project.yml, airflow_dag, kafka import
2. Recipe emits primary target 'data-pipeline'
3. Specify writes PIPELINE-SPEC.md with sources, schema, SLA, data classification
4. Pipeline platform loads ETL/streaming/orchestration/schema modules, engineering, security
5. Decompose: ingestion → transform → load → quality gates
6. Verifier: quality gates on sample, idempotency, schema compatibility, lineage
7. Monitor: SLO alert rules, data quality metrics
8. Package → Deploy → Release → Archive
```

### 9.11 AI/Agent Walkthrough

```
1. Recipe sees signals: LLM SDK imports, agent in project name, tools array
2. Recipe emits primary target 'ai-agent'
3. Specify writes AI-SPEC.md with capabilities, tool inventory, eval dimensions
4. AI/Agent platform routes to AI gateway for all implementation patterns
5. Decompose: model access → logging → features → eval → guardrails
6. Verifier: eval suite pass, tool scope review, cost ceiling, guardrails, fallback
7. Monitor: LLM-specific metrics (latency, cost, eval score drift, error rate)
8. Package → Deploy → Release → Archive
```

---

## 10. Platform Receipt Extension Fields

```json
{
  "platform_target": "web|api-service|game|mobile|desktop|cli|iot-embedded|library-package|extension-plugin|data-pipeline|ai-agent",
  "primary_target_confidence": "high|medium|low",
  "secondary_targets": ["string"],
  "dev_modules_loaded": ["string"],
  "engineering_modules_loaded": ["string"],
  "security_modules_loaded": ["string"],
  "spec_template_variant": "string",
  "spec_artifact_path": "string",
  "verification_gates_passed": ["string"],
  "verification_gates_failed": ["string"],
  "verification_gates_not_tested": [
    {
      "gate": "string",
      "missing": "string"
    }
  ],
  "capability_handoff": {
    "always_loaded": ["string"],
    "conditional_loaded": ["string"]
  }
}
```
