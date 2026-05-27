# Platform API/Service — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified API/Service as the primary target,
When platform-api-service is invoked,
Then it surfaces: "platform-api-service requires Recipe to have identified API/Service as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified API/Service as the primary target,
When platform-api-service activates,
Then the activation sequence completes in order: spec-template load → language/framework detection → language module load → engineering load → security load → Verifier gate registration → receipt write.

## Framework routing: Node.js HTTP

Given `fastify`, `express`, `hono`, or `@nestjs/core` is in package.json,
When platform-api-service detects the framework,
Then `.wabblespec/engine/shared/dev/languages/node/` is loaded.

## Framework routing: Python ASGI/WSGI

Given `fastapi`, `flask`, `django`, or `starlette` is in requirements,
When platform-api-service detects the framework,
Then `.wabblespec/engine/shared/dev/languages/python/` is loaded.

## Framework routing: gRPC

Given `.proto` files exist or `grpc` is in any dependency,
When platform-api-service detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/api/grpc.md` is loaded.
Then protobuf conventions are applied.

## Framework routing: serverless

Given `serverless.yml`, `template.yaml` (SAM), or a `functions/` directory is present,
When platform-api-service detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/api/serverless.md` is loaded.

## API/Service-specific concerns injected into spec

Given platform-api-service is active,
When spec context is assembled,
Then API versioning strategy is declared.
Then OpenAPI contract requirement is present.
Then auth scheme is declared (Bearer token, API key in header, or mTLS).
Then rate limiting design is declared.
Then health and readiness endpoints are declared.
Then structured logging format is specified.
Then p99 latency < 200ms performance budget is declared.
Then error response schema (RFC 7807 Problem Details) is declared.
Then idempotency requirements for mutating endpoints are addressed.

## Database connection pool declared

Given the spec includes database access,
When spec context is assembled,
Then connection pool sizing is declared in the systems-design spec.

## Capability handoff

Given platform-api-service has activated,
When the capability handoff is declared in the receipt,
Then `.wabblespec/engine/shared/dev/frameworks/api/core.md` and `.wabblespec/engine/shared/dev/frameworks/api/security.md` are always loaded.
Then gateway references include gateway-security/references/ and gateway-engineering/references/.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-api-service attempts to register gates with Verifier,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then the activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-api-service run,
Then platform-api-service does not use CLI or Web spec templates for an API target.
Then platform-api-service does not activate gateway-aesthetic references (API has no visual surface).
Then platform-api-service does not omit auth scheme declaration for any HTTP endpoint.

## Receipt fields

Given any successful platform-api-service activation,
Then a receipt is written to `.wabblespec/receipts/platform-api-service-<timestamp>.json`.
Then the receipt contains: platform, language_module_loaded, framework_detected, templates_activated, engineering_files_loaded, security_files_loaded, gates_registered, capability_handoff.
