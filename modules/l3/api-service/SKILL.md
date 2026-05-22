---
name: platform-api-service
description: API/Service platform package. Activates when Recipe detects an HTTP API, gRPC service, or background service target. Loads API spec templates, latency/throughput budgets, auth and injection security controls, and observability gates. Produces a materially different spec from CLI or Web targets for the same task.
---

# Platform: API/Service

You are the API/Service platform layer. You activate when Recipe identifies an HTTP API, gRPC service, or long-running backend service and you load the constraints, templates, and verification gates specific to that target. You do not execute tasks — Executor does. You provide the platform-specific frame that shapes how those tasks are specified and verified.

## What this skill does

Loads API/Service-specific spec templates, engineering standards, security controls, and verification gates into the active WabbleSpec context. Routes to language modules based on detected tech stack. Writes a platform activation receipt.

## When to activate

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
4. Load matched language module(s) from _shared/dev/languages/
5. Load engineering/build-toolchain.md and engineering/performance-budgets.md
6. Load security/threat-model.md and security/platform-controls.md
7. Register verification/gates.md with Verifier
8. Write platform activation receipt
```

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

## Output contract

**Platform activation receipt** (`.wabblespec/receipts/platform-api-service-{timestamp}.json`):

Base receipt schema with API/Service extension fields (see `schemas/receipt.schema.json`).

## Files loaded by this module

```
modules/l3/api-service/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
