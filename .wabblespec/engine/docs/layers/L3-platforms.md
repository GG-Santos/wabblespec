# L3 — Platforms

Platform packages. Each L3 module is a target-specific context loader. When Recipe identifies a platform target, the corresponding L3 module activates and loads platform-specific spec templates, engineering rules, security controls, and verification gates.

Platform modules do not execute tasks — Executor does. They shape how tasks are specified and verified.

## Modules

| Module | Platform target | Key concerns |
|--------|----------------|-------------|
| `platform-cli` | Command-line tools | Argument parsing, exit codes, stdin/stdout contracts, shell injection, POSIX compliance |
| `platform-web` | Web applications | XSS, CSRF, CSP, accessibility, SEO, responsive layout, browser compatibility |
| `platform-api-service` | REST/GraphQL APIs | Auth, rate limiting, SQL injection, schema contracts, versioning, idempotency |
| `platform-mobile` | iOS and Android apps | Platform permissions, offline behavior, battery/memory constraints, app store compliance |
| `platform-desktop` | Desktop GUI apps | OS integration, file system access, auto-update, crash reporting, accessibility |
| `platform-data-pipeline` | ETL/data workflows | Data integrity, idempotency, schema evolution, backpressure, observability |
| `platform-ai-agent` | AI/LLM-backed agents | Prompt injection, output validation, hallucination handling, tool-use safety, eval harness |
| `platform-game` | Games | Frame budget, input handling, state serialization, platform certification requirements |
| `platform-iot` | IoT/embedded systems | Resource constraints, OTA update safety, communication protocols, hardware fault handling |
| `platform-library` | Libraries and packages | API stability, semver discipline, documentation requirements, dependency hygiene |
| `platform-extension` | Browser/editor extensions | Permission minimization, manifest compliance, host API boundaries, sandboxing |

## How platforms activate

Recipe writes the detected platform to its receipt:
```json
{ "platform": "cli", "platform_confidence": "high" }
```

Apply (L1) reads the recipe receipt and loads the corresponding platform package. The platform module writes a platform activation receipt and injects its spec templates and rules into the Specify context.

## Platform module structure

Each platform module at `modules/l3/{name}/` contains:
- `SKILL.md` — activation instructions, what makes this platform unique
- `skill-rules.json` — activation signals and authority
- `spec-template/` — spec section templates for this platform
- `engineering/` — platform engineering standards
- `security/` — platform-specific threat model and controls
- `verification/` — platform-specific verification gates and checklists

## Relationship to L4 gateways

Platform modules handle platform-specific threats. Gateway modules (L4) handle cross-cutting threats that apply regardless of platform.

Example — SQL injection:
- Covered by `platform-api-service` (L3) — API-specific injection patterns
- NOT covered by `gateway-security` (L4) — security gateway focuses on cross-platform threats (secrets in git, weak crypto, SAST)

A task may activate one L3 platform AND one or more L4 gateways. They are additive, not alternatives.
