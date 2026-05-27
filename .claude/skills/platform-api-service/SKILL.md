---
name: platform-api-service
description: API/Service platform package. Activates when Recipe detects an HTTP API, gRPC service, or background service target. Loads API spec templates, latency/throughput budgets, auth and injection security controls, and observability gates. Produces a materially different spec from CLI or Web targets for the same task.
---

# Platform: API/Service

You are the API/Service platform layer. You activate when Recipe identifies an HTTP API, gRPC service, or long-running backend service and you load the constraints, templates, and verification gates specific to that target. You do not execute tasks — Executor does. You provide the platform-specific frame that shapes how those tasks are specified and verified.

## What this skill does

Loads API/Service-specific spec templates, engineering standards, security controls, and verification gates into the active WabbleSpec context. Routes to language modules based on detected tech stack. Writes a platform activation receipt.

## When to use

Recipe must have already run and identified API/Service as the primary target. Activation signals in `skill-rules.json`.

## What makes API/Service different from other targets

| Concern | API/Service | CLI | Web |
|---|---|---|---|
| Primary user interface | HTTP endpoints / gRPC methods | Terminal args, stdin, stdout | Browser DOM |
| Success signal | HTTP 2xx / gRPC OK status | Exit code 0 | Visual render + CWV |
| Auth mechanism | Bearer token, API key in header, mTLS | Env vars or stdin | Session cookies / JWTs in memory |
| Performance measure | p99 latency < 200ms, throughput RPS | Cold start < 100ms | LCP < 2.5s, CLS < 0.1 |
| Security primary concern | Auth bypass, injection, SSRF, IDOR | Shell injection, credential exposure | XSS, CSRF, CSP |
| Accessibility | API docs (OpenAPI), versioning | --help text quality | WCAG 2.1 AA |
| Distribution | Container registry (Docker), serverless | Binary / npm global | CDN / hosting |
| Output contract | JSON/Protobuf response body, status codes | stdout (data) + stderr (errors) | HTML/CSS/JS rendered in browser |
| Config | Env vars, secrets manager, mounted secrets | XDG config file, env vars | localStorage, build-time env vars |
| Observability | Structured logs, distributed traces, health endpoint | stderr log output | Browser error tracking |

A spec written without this platform context misses: API versioning strategy, OpenAPI contract requirement, auth scheme declaration, rate limiting design, health and readiness endpoints, structured logging format, p99 latency budget, database connection pool sizing, idempotency requirements for mutating endpoints, and error response schema (RFC 7807).

## Activation sequence

```
1. Recipe identifies API/Service target and signals platform-api-service activation
2. Load spec-template variant (design-document.md, systems-design.md, technical-spec.md)
3. Detect language stack and framework via skill-rules.json signals
4. Load matched language module(s) from .wabblespec/engine/shared/dev/languages/
5. Load engineering/build-toolchain.md and engineering/performance-budgets.md
6. Load security/threat-model.md and security/platform-controls.md
7. Register verification/gates.md with Verifier
8. Write platform activation receipt
```

## Design phase sequence

```
P0: service-contract.md          ← Pillars, consumer registry, SLO targets, API style (REQUIRED before P1)
P1: design-document.md           ← Endpoint inventory, auth scheme, versioning, error schema
P2: systems-design.md            ← Request pipeline, middleware stack, data layer, observability
    framework-specific/          ← Load matched framework doc (conditional on detection)
      fastapi.md                 ← If fastapi in requirements.txt
      fastify-express.md         ← If fastify or express in package.json
      grpc.md                    ← If .proto files detected
      serverless.md              ← If serverless.yml or SAM template detected
P3: technical-spec.md            ← Implementation spec, GWT acceptance scenarios
```

**Invariant:** service-contract.md must be declared before Specify receipt. Consumer registry (every consumer declared) and SLO targets are blocking — implementation without declared consumers produces an API with no contract owner.

## Framework routing

| Detected signal | Framework context |
|---|---|
| `fastify`, `express`, `hono`, `@nestjs/core` in package.json | Node.js HTTP framework |
| `fastapi`, `flask`, `django`, `starlette` in requirements | Python ASGI/WSGI |
| `gin`, `echo`, `chi`, `net/http` in go.mod | Go HTTP framework |
| `axum`, `actix-web`, `warp` in Cargo.toml | Rust HTTP framework |
| `.proto` files, `grpc` in any dependency | gRPC service (load protobuf conventions) |
| `serverless.yml`, `template.yaml` (SAM), `functions/` directory | Serverless functions |

## Spec template variant

- `spec-template/design-document.md` — P1: API contract, auth scheme, versioning, endpoint inventory
- `spec-template/systems-design.md` — P2: Request pipeline, middleware stack, data layer, observability
- `spec-template/technical-spec.md` — P3: Implementation spec with GWT acceptance scenarios

Use these templates instead of generic WabbleSpec templates when API/Service is the active platform.

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `.wabblespec/engine/shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - .wabblespec/engine/shared/dev/frameworks/api/core.md
    - .wabblespec/engine/shared/dev/frameworks/api/security.md
    - modules/l3/api-service/spec-template/service-contract.md
  conditional_load:
    - signal: "fastapi in requirements.txt or pyproject.toml"
      load: modules/l3/api-service/spec-template/framework-specific/fastapi.md
    - signal: "fastify or express in package.json"
      load: modules/l3/api-service/spec-template/framework-specific/fastify-express.md
    - signal: ".proto files or grpc in dependencies"
      load: modules/l3/api-service/spec-template/framework-specific/grpc.md
    - signal: "graphql in dependencies"
      load: .wabblespec/engine/shared/dev/frameworks/api/graphql.md
    - signal: "serverless.yml or sam.yaml or template.yaml"
      load: modules/l3/api-service/spec-template/framework-specific/serverless.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
```

## Output contract

**Platform activation receipt** (`.wabblespec/state/receipts/platform-api-service-{timestamp}.json`):

Base receipt schema with API/Service extension fields (see `schemas/receipt.schema.json`).

## Files loaded by this module

**Always loaded:**
```
modules/l3/api-service/
  spec-template/service-contract.md       ← P0 (always)
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  engineering/qa-pipeline.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```

**Conditionally loaded (framework-specific):**
```
modules/l3/api-service/spec-template/framework-specific/
  fastapi.md           ← if fastapi in requirements.txt or pyproject.toml
  fastify-express.md   ← if fastify or express in package.json
  grpc.md              ← if .proto files detected
  serverless.md        ← if serverless.yml, sam.yaml, or template.yaml detected
```
