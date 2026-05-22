# Module Plan — _shared/dev/api-consumption/ (L3 Shared)

**Tier:** 2 — FOUNDATION SHARED
**Layer:** L3 Shared (loaded by platform packages)
**v5.3 origin:** Development gateway — API group (client-side patterns only; server-side absorbed into API/Service platform)

---

## Purpose

Cross-platform API client reference modules. Each module holds patterns for consuming external APIs of a given protocol type — not building them. Server-side API implementation patterns live in the API/Service L3 platform package. These modules cover how platform code talks to external services: HTTP REST, GraphQL queries, gRPC client stubs, and realtime connection management.

---

## Scope

Four api-consumption modules:

| Module | Path | Covers |
|---|---|---|
| REST | `_shared/dev/api-consumption/rest/` | HTTP client patterns, auth, retries, error handling |
| GraphQL | `_shared/dev/api-consumption/graphql/` | Query/mutation/subscription clients, code generation, caching |
| gRPC | `_shared/dev/api-consumption/grpc/` | Proto loading, stub generation, channel management, streaming |
| Realtime | `_shared/dev/api-consumption/realtime/` | WebSocket, SSE, long-poll client patterns |

---

## Activation

`skill-rules.json` per module triggers:
- Recipe or Explore detects API client dependency signals
- Platform package declares api-consumption dependency
- Explicit `/api-client <type>` override command

Detection signals per module:

| Module | Detection signals |
|---|---|
| REST | `fetch`, `axios`, `got`, `requests`, `net/http`, `reqwest`, `okhttp` — client usage context |
| GraphQL | `graphql-request`, `urql`, `apollo-client`, `strawberry` (client usage), `.graphql` query files |
| gRPC | `grpc`, `@grpc/grpc-js`, `grpcio`, `google.golang.org/grpc`, `.proto` files |
| Realtime | `ws`, `socket.io-client`, `websockets`, `EventSource`, long-poll patterns |

Signal context matters: REST server-side (express, fastapi) does NOT trigger REST client module — only client usage patterns trigger.

---

## Content Structure (per module)

```
_shared/dev/api-consumption/<type>/
  SKILL.md                        <- loader spec: activation, load scope, authority
  skill-rules.json                <- detection signals with client-vs-server disambiguation
  references/
    patterns.md                   <- core consumption patterns
    auth.md                       <- authentication methods (Bearer, API key, OAuth, mTLS)
    error-handling.md             <- error classification, retry logic, fallback
    retries.md                    <- exponential backoff, jitter, circuit breaker
    testing.md                    <- mocking external APIs in tests, contract testing
    performance.md                <- connection pooling, caching, rate limit handling
  rules/
    no-credentials-in-code.md     <- API keys and tokens in env vars only
    retry-policy.md               <- minimum retry behavior (idempotent vs. non-idempotent)
  schemas/
    receipt.schema.json
```

---

## Per-Module Content Detail

### REST

`references/patterns.md`:
- Use a single configured HTTP client instance per service (not per request)
- Base URL and auth configuration injected at construction, not per-call
- Typed response models — do not pass raw JSON through application code
- Content-Type and Accept headers explicit on all requests

`references/auth.md`:
- Bearer token: Authorization header, never query parameter
- API key: header preferred (X-Api-Key), query param only if vendor requires
- OAuth 2.0: client credentials flow for service-to-service, token refresh handled by client wrapper
- mTLS: certificate path from env var, loaded once at startup

`references/error-handling.md`:
- HTTP status classification: 2xx success, 3xx redirect (follow by default), 4xx client error (do not retry except 429), 5xx server error (retry with backoff)
- 429 handling: respect Retry-After header if present, otherwise exponential backoff
- Error response: parse error body when content-type is application/json, log raw body otherwise
- Timeout: connect timeout and read timeout both required — no infinite wait

`references/retries.md`:
- Idempotent methods (GET, PUT, DELETE): retry on transient failure (5xx, network error)
- Non-idempotent (POST, PATCH): retry only on network error before server received request
- Backoff: base 100ms, multiplier 2x, jitter 0-50%, max 30s
- Max attempts: 3 by default, configurable per client

`references/testing.md`:
- Mock at HTTP boundary: intercept HTTP calls, not at service layer
- No real external calls in unit/integration tests
- Contract testing: consumer-driven contracts (Pact or equivalent) for critical external dependencies
- VCR/cassette pattern for recorded API interactions in integration tests

### GraphQL

`references/patterns.md`:
- Queries and mutations in `.graphql` files, not inline strings
- Code generation from schema (graphql-codegen or equivalent): types generated, not handwritten
- Fragments for shared field sets — no repeated field selections
- Introspection disabled in production client config

`references/auth.md`:
- JWT Bearer in Authorization header via client middleware
- Per-operation auth: headers injected at operation level for multi-tenant scenarios
- Token refresh: handled transparently by client link/middleware, not per-call

`references/error-handling.md`:
- GraphQL errors array: always checked — HTTP 200 with errors array is a failed operation
- Partial success: data + errors both present — handle explicitly, not silently
- Network error vs. GraphQL error: distinguish in client wrapper
- Error codes: use extensions.code for machine-readable classification when server provides it

`references/performance.md`:
- Fragment colocation: fragment defined next to component that uses it
- Caching: normalized cache (Apollo InMemoryCache or equivalent) for web clients
- Persisted queries: for production web clients over HTTP/1.1
- Subscription cleanup: unsubscribe on component unmount / scope exit

### gRPC

`references/patterns.md`:
- Proto files: source of truth, committed to repo, generated code excluded from VCS
- Stub generation: part of build process, not manual
- Channel: one channel per service, not per call — channel is expensive to create
- Deadline: every RPC call has explicit deadline, no calls without timeout

`references/auth.md`:
- Token-based: PerRPCCredentials interface, token injected per call via interceptor
- mTLS: channel credentials at channel construction
- Metadata: auth in metadata, not in proto message fields

`references/error-handling.md`:
- Status codes: use gRPC status codes (NOT HTTP codes) — NOT_FOUND, UNAVAILABLE, DEADLINE_EXCEEDED, etc.
- UNAVAILABLE: retry with backoff (server temporarily unavailable)
- DEADLINE_EXCEEDED: do not retry — deadline has passed
- Client interceptors: error classification in interceptor, not scattered per-call

`references/retries.md`:
- Server-side retry policy: declare in service config JSON where supported
- Client-side: interceptor-based, same backoff policy as REST
- Streaming RPCs: reconnect on stream error, handle stream half-close correctly
- Hedging: evaluate only for read-heavy low-latency calls — not default

`references/testing.md`:
- In-process server: spin up gRPC server in test process, no network required
- Proto mocking: mock at stub level, not at channel level
- Deadline testing: test timeout behavior explicitly with controlled server delay

### Realtime

`references/patterns.md`:
- WebSocket: single connection per logical session, multiplex messages over it
- SSE (Server-Sent Events): use for server-push only scenarios (uni-directional)
- Long-poll: legacy fallback only — prefer WebSocket or SSE for new code
- Message framing: explicit message type field in all payloads, no raw string matching

`references/error-handling.md`:
- Connection loss: detect via heartbeat/ping, not only on close event
- Reconnect: exponential backoff with jitter, max reconnect attempts configurable
- Message ordering: do not assume ordered delivery — include sequence numbers for ordered protocols
- Duplicate delivery: design handlers to be idempotent

`references/auth.md`:
- WebSocket: send auth token in first message after connect (not in URL — URLs are logged)
- SSE: Bearer token in EventSource polyfill headers, or cookie-based for browser-native EventSource
- Connection-level auth: validate at connection establishment, not per-message (performance)
- Token refresh: reconnect with new token when auth expires during active connection

`references/performance.md`:
- Message size: enforce max message size at both ends
- Backpressure: do not enqueue unbounded messages client-side
- Connection reuse: no new WebSocket per operation
- Heartbeat interval: 30s ping from client, 60s timeout — configurable per environment

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Loaded references | In-context during active wave | API client patterns available to Executor |
| API client receipt | `.wabblespec/receipts/api-client-<type>-receipt.md` | I10 compliance |

---

## Workflow

```
1. Recipe identifies build target
2. API client dependency signals scanned (client-side only)
3. Matched api-consumption module(s) activated via Activation gate
4. SKILL.md declares load scope based on detected protocols
5. References injected into Executor context at wave start
6. Credentials policy rule applied during Apply
7. Security gateway receives auth pattern check (cross-cutting)
8. Write api-client receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` per module | Required | Load scope and client-vs-server disambiguation |
| `skill-rules.json` per module | Required | Detection signals |
| `references/` per module | Required | All reference content |
| `rules/no-credentials-in-code.md` | Rules | Env var enforcement for all credentials |
| `rules/retry-policy.md` | Rules | Minimum retry behavior per method idempotency |
| `schemas/receipt.schema.json` | Schema | Receipt per activation |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Tech-stack signals trigger api-consumption module activation |
| Explore | Explore detects API client patterns to populate project-map.md |
| Platform packages (L3) | Platform SKILL.md declares which api-consumption modules it may load |
| Apply | Apply reads loaded auth and retry rules during gateway routing |
| Security gateway | Auth patterns and credential policy forwarded for cross-cutting review |
| API/Service platform (L3) | Shares proto files and schema context but covers server-side separately |

---

## Verification Mode

**Observation** — correct protocol module(s) activated, credentials policy honored, no server-side patterns misloaded into client context, receipt written.

---

## Receipt Extension Fields

```json
{
  "protocols_loaded": ["rest|graphql|grpc|realtime"],
  "auth_methods_detected": ["string"],
  "credentials_policy_checked": "boolean",
  "references_loaded": ["string"],
  "security_forwarded": "boolean"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| tRPC coverage | Sub-section in REST vs. own module vs. TypeScript-specific in Node language module | P10 Web platform planning |
| GraphQL subscriptions | Covered under GraphQL vs. split to Realtime module | Per-module planning |
| OpenAPI client codegen | Reference in REST vs. separate codegen module | P10 API/Service platform planning |
