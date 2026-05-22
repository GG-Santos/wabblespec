# Module Plan — _shared/dev/languages/ (L3 Shared)

**Tier:** 2 — FOUNDATION SHARED
**Layer:** L3 Shared (loaded by platform packages)
**v5.3 origin:** Development gateway — Language group (Node, Python, Go, Rust, Java)

---

## Purpose

Cross-platform language reference modules. Each language module holds idiomatic patterns, toolchain conventions, dependency management rules, and common pitfalls for one language. Platform packages load the relevant language module(s) on demand — no duplication across targets. Not orchestration modules. Reference libraries with activation logic.

---

## Scope

Five language modules:

| Module | Path | Languages served |
|---|---|---|
| Node | `_shared/dev/languages/node/` | JavaScript, TypeScript — all JS-family targets |
| Python | `_shared/dev/languages/python/` | Python — API/Service, Data/Pipeline, AI/Agent, CLI, IoT |
| Go | `_shared/dev/languages/go/` | Go — API/Service, CLI, Desktop |
| Rust | `_shared/dev/languages/rust/` | Rust — CLI, IoT/Embedded, Library/Package, Desktop |
| Java | `_shared/dev/languages/java/` | Java/Kotlin — API/Service, Mobile (Android), Desktop |

---

## Activation

`skill-rules.json` per language module triggers:
- Recipe detects language in tech stack signals (package.json, requirements.txt, go.mod, Cargo.toml, pom.xml/build.gradle)
- Platform package explicitly loads language module (dependency declaration)
- Explicit `/lang <language>` override command

No language module loads without a matched signal. Multiple language modules can be active simultaneously (polyglot projects).

---

## Content Structure (per language module)

```
_shared/dev/languages/<lang>/
  SKILL.md                    <- loader spec: activation, what gets loaded, authority
  skill-rules.json            <- tech-stack detection signals
  references/
    idioms.md                 <- idiomatic patterns for this language
    toolchain.md              <- build, package manager, version manager
    dependency-management.md  <- lockfile policy, version constraints, security scanning
    testing-conventions.md    <- test runner, structure, coverage tooling
    style.md                  <- formatting, linting, code style conventions
    pitfalls.md               <- common mistakes, anti-patterns, performance traps
  rules/
    version-floor.md          <- minimum supported language version
    lockfile-policy.md        <- lockfile required, pinning strategy
  schemas/
    receipt.schema.json
```

---

## Per-Language Content Detail

### Node

`references/toolchain.md`:
- Package managers: npm, yarn, pnpm — lockfile required for all
- Node version: managed via .nvmrc or .node-version, engines field in package.json
- Module system: ESM preferred, CJS legacy only with justification
- TypeScript: tsconfig.json required for all TS projects, strict mode on

`references/idioms.md`:
- Async/await over raw Promise chains
- Error-first patterns where callbacks unavoidable
- Module boundaries: named exports preferred over default
- No require() in ESM context

`references/pitfalls.md`:
- Prototype pollution risks in object merge utilities
- Event loop blocking on sync I/O in server context
- Unhandled promise rejections
- Package lock drift between environments

### Python

`references/toolchain.md`:
- Dependency management: uv preferred, pip+venv acceptable, pipenv deprecated
- Python version: .python-version required (pyenv), minimum 3.11
- Type hints required for library code, recommended for application code
- Formatting: ruff (lint + format), replaces flake8/black/isort

`references/idioms.md`:
- Dataclasses or attrs for structured data, not raw dicts
- Context managers for resource management
- Generator expressions for lazy evaluation
- f-strings over .format() or %

`references/pitfalls.md`:
- Mutable default arguments
- Late binding in closures
- GIL impact on CPU-bound parallelism (use multiprocessing or C extensions)
- Circular imports in large packages

### Go

`references/toolchain.md`:
- Modules: go.mod required, go.sum committed
- Go version: declared in go.mod, minimum 1.21
- Build: standard go build, Makefile for multi-target
- Formatting: gofmt/goimports (non-negotiable, enforced in CI)

`references/idioms.md`:
- Errors as values: always check returned errors
- Interfaces defined at consumption site, not declaration site
- Table-driven tests
- Goroutine lifecycle: always define exit condition

`references/pitfalls.md`:
- Goroutine leaks from missing context cancellation
- Copying sync.Mutex (pass by pointer)
- Slice header aliasing
- nil pointer dereference on interface embedding

### Rust

`references/toolchain.md`:
- Cargo.toml + Cargo.lock (lock committed for binaries, gitignored for libraries)
- Rust edition: declared in Cargo.toml, minimum 2021
- Toolchain: rust-toolchain.toml for version pinning
- Formatting: rustfmt (enforced), clippy (warnings as errors in CI)

`references/idioms.md`:
- Ownership model: prefer owned types at API boundaries, borrow internally
- Error handling: thiserror for library errors, anyhow for application errors
- Avoid unwrap() in non-test code — use ? or explicit error handling
- Newtypes for semantic distinction

`references/pitfalls.md`:
- Fighting the borrow checker with excessive Arc<Mutex<>> — reconsider data design
- Stack overflow from deep recursion (use iteration or explicit stack)
- Overly generic types increasing compile time
- Unsafe blocks without explicit safety justification comments

### Java

`references/toolchain.md`:
- Build: Gradle (Kotlin DSL) preferred, Maven acceptable
- Java version: specified in build config, minimum 21 LTS
- Dependency management: BOM for version alignment, no range versions
- Formatting: google-java-format or spotless

`references/idioms.md`:
- Records for immutable data carriers (Java 16+)
- Sealed classes for closed hierarchies
- Optional for nullable return — never null return in public API
- Stream API for collection transformation

`references/pitfalls.md`:
- NullPointerException from unchecked optionals
- Thread safety violations on shared mutable state
- Resource leaks without try-with-resources
- Reflection at runtime breaking GraalVM native image

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Loaded references | In-context during active wave | Language patterns available to Executor |
| Language receipt | `.wabblespec/receipts/lang-<lang>-receipt.md` | I10 compliance, tracks which version loaded |

---

## Workflow

```
1. Recipe identifies build target
2. tech-stack signals scanned for language indicators
3. Matched language module(s) activated via Activation gate
4. SKILL.md declares which references/ files load for this task shape
5. References injected into Executor context at wave start
6. Language-specific rules applied during Apply (gateway routing)
7. Write language receipt
```

Language modules do not orchestrate. They inject context. All orchestration remains with Executor, Apply, and platform package SKILL.md.

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` per language | Required | Declares load scope and activation signals |
| `skill-rules.json` per language | Required | Tech-stack signal patterns |
| `references/` per language | Required | All reference content |
| `rules/version-floor.md` | Rules | Minimum version enforcement |
| `rules/lockfile-policy.md` | Rules | Lock file requirements |
| `schemas/receipt.schema.json` | Schema | Receipt per activation |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Recipe signals activate language module(s) via tech-stack detection |
| Platform packages (L3) | Platform SKILL.md declares which language modules it may load |
| Apply | Apply reads loaded language rules during gateway routing |
| Executor | Executor receives language references injected at wave start |
| Explore | Explore reads language module signals to detect project tech stack |
| Engineering gateway | Engineering cross-cutting standards override language-specific when in conflict |

---

## Verification Mode

**Observation** — correct language module(s) activated for detected tech stack, version floor honored, lockfile present, receipt written.

---

## Receipt Extension Fields

```json
{
  "language": "node|python|go|rust|java",
  "detected_version": "string",
  "version_floor_met": "boolean",
  "references_loaded": ["string"],
  "rules_applied": ["string"]
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Kotlin separate from Java | Kotlin gets own module vs. sub-section in java/ | Per-module planning for Mobile/Android |
| Ruby, PHP, C# coverage | Add modules vs. declare out of scope for v6.1 | P10 platform planning |
| Polyglot load order | Load all matched vs. primary + secondary like Recipe | Per-module planning |
