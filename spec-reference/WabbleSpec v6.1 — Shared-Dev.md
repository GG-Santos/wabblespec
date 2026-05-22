# WabbleSpec v6.1 — Shared Dev

**Layer:** L3 Shared (`_shared/dev/`)
**Tier:** 2 — FOUNDATION SHARED
**Document scope:** All _shared/dev/ modules — languages, databases, api-consumption

---

## Overview

`_shared/dev/` is a cross-platform reference library loaded on demand by platform packages and Recipe's tech-stack detection. It does not orchestrate — it injects context. All orchestration remains with Executor, Apply, and platform package SKILL.md files.

Three module groups:

| Group | Path | Modules |
|---|---|---|
| Languages | `_shared/dev/languages/` | node, python, go, rust, java |
| Databases | `_shared/dev/databases/` | sql, nosql, orm, migration |
| API Consumption | `_shared/dev/api-consumption/` | rest, graphql, grpc, realtime |

Each module group contains separate sub-modules, each with its own SKILL.md, skill-rules.json, and references/. Multiple modules from any group can be active simultaneously.

---

## How _shared/dev/ Loads

Loading follows four steps:

```
1. Recipe identifies build target and scans tech-stack signals
   (package.json, go.mod, Cargo.toml, requirements.txt, schema.prisma, etc.)

2. Matched module(s) activate via Activation gate:
   -> Language modules: matched by language indicator files
   -> Database modules: matched by ORM config, connection env vars, migration dirs
   -> API consumption modules: matched by client libraries (client-side only)

3. SKILL.md declares which references/ files load for this task shape

4. References injected into Executor context at wave start
```

No module loads without a matched signal. No duplication — shared modules are loaded once and referenced by all platform packages that need them.

---

## Languages

**Path:** `_shared/dev/languages/`

### Purpose

Idiomatic patterns, toolchain conventions, dependency management rules, and common pitfalls per language. Platform packages load the relevant language module on demand. Language modules do not contain application logic — they are reference context for Executor.

### Five Language Modules

| Module | Languages served | Build targets |
|---|---|---|
| `languages/node/` | JavaScript, TypeScript | Web, Extension/Plugin, CLI, API/Service, AI/Agent |
| `languages/python/` | Python | API/Service, Data/Pipeline, AI/Agent, CLI, IoT/Embedded |
| `languages/go/` | Go | API/Service, CLI, Desktop |
| `languages/rust/` | Rust | CLI, IoT/Embedded, Library/Package, Desktop |
| `languages/java/` | Java, Kotlin | API/Service, Mobile (Android), Desktop |

### Activation

| Module | Detection signals |
|---|---|
| node | `package.json`, `.nvmrc`, `.node-version` |
| python | `requirements.txt`, `pyproject.toml`, `setup.py`, `.python-version` |
| go | `go.mod`, `go.sum` |
| rust | `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml` |
| java | `pom.xml`, `build.gradle`, `build.gradle.kts` |

Explicit override: `/lang <language>`. Polyglot projects activate multiple language modules simultaneously.

### Module Content Structure

```
_shared/dev/languages/<lang>/
  SKILL.md
  skill-rules.json
  references/
    idioms.md               <- idiomatic patterns
    toolchain.md            <- build tools, package manager, version manager
    dependency-management.md <- lockfile policy, version constraints, scanning
    testing-conventions.md  <- test runner, structure, coverage tooling
    style.md                <- formatting, linting, code style
    pitfalls.md             <- common mistakes, anti-patterns, performance traps
  rules/
    version-floor.md        <- minimum supported language version
    lockfile-policy.md      <- lockfile required, pinning strategy
  schemas/
    receipt.schema.json
```

### Node

**Toolchain:** npm/yarn/pnpm — lockfile required for all. Node version managed via `.nvmrc` or `.node-version`, `engines` field in `package.json`. ESM preferred, CJS only with justification. TypeScript: `tsconfig.json` required, `strict: true`.

**Idioms:** async/await over raw Promise chains. Named exports preferred over default. No `require()` in ESM context.

**Pitfalls:** Prototype pollution in object merge utilities. Event loop blocking on sync I/O in server context. Unhandled promise rejections. Package lock drift between environments.

### Python

**Toolchain:** `uv` preferred for dependency management, `pip+venv` acceptable, `pipenv` deprecated. Python version declared in `.python-version` (pyenv), minimum 3.11. Type hints required for library code, recommended for application code. `ruff` for lint and format (replaces flake8/black/isort).

**Idioms:** Dataclasses or attrs for structured data — not raw dicts. Context managers for resource management. Generator expressions for lazy evaluation. f-strings over `.format()` or `%`.

**Pitfalls:** Mutable default arguments. Late binding in closures. GIL impact on CPU-bound parallelism (use multiprocessing). Circular imports in large packages.

### Go

**Toolchain:** `go.mod` required, `go.sum` committed. Go version declared in `go.mod`, minimum 1.21. `gofmt`/`goimports` enforced in CI (non-negotiable).

**Idioms:** Errors as values — always check returned errors. Interfaces defined at consumption site, not declaration site. Table-driven tests. Goroutine lifecycle: always define exit condition.

**Pitfalls:** Goroutine leaks from missing context cancellation. Copying `sync.Mutex` (pass by pointer). Slice header aliasing. nil pointer dereference on interface embedding.

### Rust

**Toolchain:** `Cargo.toml` + `Cargo.lock` (lock committed for binaries, gitignored for libraries). Rust edition declared in `Cargo.toml`, minimum 2021. `rust-toolchain.toml` for version pinning. `rustfmt` enforced, `clippy` warnings as errors in CI.

**Idioms:** Prefer owned types at API boundaries, borrow internally. `thiserror` for library errors, `anyhow` for application errors. Avoid `unwrap()` in non-test code — use `?` or explicit error handling. Newtypes for semantic distinction.

**Pitfalls:** Excessive `Arc<Mutex<>>` — reconsider data design. Stack overflow from deep recursion (use iteration or explicit stack). Overly generic types increasing compile time. `unsafe` blocks without explicit safety justification comments.

### Java

**Toolchain:** Gradle (Kotlin DSL) preferred, Maven acceptable. Java version minimum 21 LTS. Dependency management via BOM for version alignment — no range versions. `google-java-format` or `spotless` for formatting.

**Idioms:** Records for immutable data carriers (Java 16+). Sealed classes for closed hierarchies. `Optional` for nullable return — never null return in public API. Stream API for collection transformation.

**Pitfalls:** NullPointerException from unchecked optionals. Thread safety violations on shared mutable state. Resource leaks without try-with-resources. Reflection at runtime breaking GraalVM native image.

### Language Receipt Extension Fields

```json
{
  "language": "node|python|go|rust|java",
  "detected_version": "string",
  "version_floor_met": true,
  "references_loaded": ["string"],
  "rules_applied": ["string"]
}
```

---

## Databases

**Path:** `_shared/dev/databases/`

### Purpose

Connection patterns, query conventions, schema management rules, and platform-specific integration guidance per database type. Platform packages load relevant database module(s) on demand. Multiple database modules can activate simultaneously — SQL + ORM + Migration is the typical combination.

### Four Database Modules

| Module | Path | Covers |
|---|---|---|
| SQL | `databases/sql/` | PostgreSQL, MySQL/MariaDB, SQLite |
| NoSQL | `databases/nosql/` | MongoDB, Redis, DynamoDB, Firestore |
| ORM | `databases/orm/` | Prisma, SQLAlchemy, GORM, Hibernate, Drizzle |
| Migration | `databases/migration/` | Schema versioning, migration tooling, rollback |

### Activation Detection Signals

| Module | Detection signals |
|---|---|
| SQL | `DATABASE_URL` with postgres/mysql/sqlite scheme; `psycopg`, `mysql-connector`, `better-sqlite3`, `pg` packages |
| NoSQL | `MONGO_URI`, `REDIS_URL`; `mongoose`, `redis`, `dynamoose`, `firebase-admin` packages |
| ORM | `schema.prisma`, `sqlalchemy` import, `gorm` import, `hibernate.cfg.xml`, `drizzle.config.*` |
| Migration | `migrations/` directory, `alembic.ini`, `flyway.conf`, `liquibase.properties`, `db/migrate/` |

### Module Content Structure

```
_shared/dev/databases/<type>/
  SKILL.md
  skill-rules.json
  references/
    patterns.md              <- core access patterns, query conventions
    connection-management.md <- pooling, retries, health checks
    transactions.md          <- scope, isolation levels, rollback
    security.md              <- injection prevention, credentials, least-privilege
    performance.md           <- indexing, query analysis, N+1 prevention
    testing.md               <- test database setup, seeding, teardown
  rules/
    credentials-policy.md    <- no hardcoded credentials, env var required
    connection-pool-policy.md <- pool sizing, timeout, overflow
  schemas/
    receipt.schema.json
```

### SQL

**Patterns:** PostgreSQL: JSONB for semi-structured data, CTEs for complex queries, EXPLAIN ANALYZE before shipping slow queries. MySQL: explicit charset (`utf8mb4`), InnoDB engine, avoid `SELECT *`. SQLite: WAL mode for concurrent reads, single-writer model — appropriate for embedded/local targets only.

Parameterized queries mandatory — no string interpolation in queries (SQL injection prevention).

**Transactions:** Keep short — never span user interactions. `READ COMMITTED` default isolation, `SERIALIZABLE` only when conflict detection required. Rollback on any exception. Deadlock handling: retry with exponential backoff, max 3 attempts.

**Security:** Parameterized queries (enforced, not optional). Credentials in env vars only. Application user has no DDL permissions in production. Connection strings never logged.

**Performance:** Index on all foreign keys and frequently queried columns. Avoid `SELECT *`. N+1 detected with query count assertions in tests. `EXPLAIN ANALYZE` required for any query touching > 10k rows in production schema.

### NoSQL

**MongoDB:** Schema validation at collection level even without enforced schema. Avoid unbounded arrays as document fields. Replica set or Atlas connection in production, `retryWrites` enabled.

**Redis:** Key naming convention `service:entity:id`. TTL on all cache keys. Redis is not a primary store. AUTH required if network-exposed — never expose Redis port publicly.

**DynamoDB:** Access-pattern-first design. Single-table design for related entities. Avoid scan operations. Exponential backoff on `ProvisionedThroughputExceededException`. IAM role-based access — no long-lived keys in code.

**Firestore:** Subcollections over nested documents for large lists. Avoid deeply nested paths. Security Rules required — no open read/write. Offline persistence: declared explicitly (on/off).

### ORM

**Prisma:** Generated client typed from schema. Migrations via `prisma migrate`. Never edit generated files.

**SQLAlchemy:** Prefer Core for complex queries, ORM for simple CRUD. Avoid lazy loading in async contexts.

**GORM:** Use pointer receivers for models. Explicit preloading over N+1 lazy.

**Hibernate:** Second-level cache only with explicit justification. Avoid open-session-in-view.

**Drizzle:** Schema-as-code. Type-safe queries. Migrations via `drizzle-kit`.

**Performance (all ORMs):** Eager loading for known relationship traversals. Bulk insert/update over individual row operations. Raw queries acceptable for complex reporting — must be documented. Log all generated queries in development mode.

**Testing:** Separate schema or in-memory database for unit tests. Wrap each test in a transaction, rollback after. Factory patterns for seed data. Run ORM migrations against test database before CI test suite.

### Migration

**Patterns:** Sequential or timestamp-prefixed migration files. Never modify committed migrations. Every migration has a rollback path (down migration required). Migrations must be idempotent (`CREATE IF NOT EXISTS`, not `CREATE`). Additive changes (new columns with defaults) safe in production. Column removal requires two-phase deploy.

**Transactions:** Wrap each migration in explicit transaction where database supports it. PostgreSQL supports DDL transactions; MySQL does not — document non-transactional steps explicitly.

**Security:** Migration runner has separate credentials from application user — migration user has DDL, app user does not. Schema changes require Reviewer before production apply. Snapshot before destructive migrations (DROP, TRUNCATE, column removal).

### Database Receipt Extension Fields

```json
{
  "db_modules_loaded": ["sql", "orm", "migration"],
  "detected_databases": ["postgresql"],
  "credentials_policy_checked": true,
  "references_loaded": ["string"],
  "security_rules_forwarded": true
}
```

---

## API Consumption

**Path:** `_shared/dev/api-consumption/`

### Purpose

Patterns for consuming external APIs — not building them. Server-side API implementation lives in the API/Service L3 platform package. These modules cover how platform code talks to external services: HTTP REST, GraphQL, gRPC, and realtime connections.

Client-vs-server disambiguation is critical: REST server frameworks (Express, FastAPI) do NOT trigger the REST client module. Only client-side usage patterns trigger these modules.

### Four API Consumption Modules

| Module | Path | Covers |
|---|---|---|
| REST | `api-consumption/rest/` | HTTP client patterns, auth, retries, error handling |
| GraphQL | `api-consumption/graphql/` | Query/mutation/subscription clients, codegen, caching |
| gRPC | `api-consumption/grpc/` | Proto loading, stub generation, channel management, streaming |
| Realtime | `api-consumption/realtime/` | WebSocket, SSE, long-poll client patterns |

### Activation Detection Signals

| Module | Detection signals (client-side only) |
|---|---|
| REST | `fetch`, `axios`, `got`, `requests`, `net/http`, `reqwest`, `okhttp` in client usage context |
| GraphQL | `graphql-request`, `urql`, `apollo-client`; `.graphql` query files |
| gRPC | `grpc`, `@grpc/grpc-js`, `grpcio`, `google.golang.org/grpc`; `.proto` files |
| Realtime | `ws`, `socket.io-client`, `websockets`, `EventSource`; long-poll patterns |

### Module Content Structure

```
_shared/dev/api-consumption/<type>/
  SKILL.md
  skill-rules.json
  references/
    patterns.md         <- core consumption patterns
    auth.md             <- Bearer, API key, OAuth, mTLS
    error-handling.md   <- error classification, retry logic, fallback
    retries.md          <- exponential backoff, jitter, circuit breaker
    testing.md          <- mocking external APIs, contract testing
    performance.md      <- connection pooling, caching, rate limit handling
  rules/
    no-credentials-in-code.md  <- API keys and tokens in env vars only
    retry-policy.md            <- minimum retry behavior
  schemas/
    receipt.schema.json
```

### REST

**Patterns:** Single configured HTTP client instance per service (not per request). Base URL and auth injected at construction. Typed response models — no raw JSON through application code. Content-Type and Accept headers explicit on all requests.

**Auth:** Bearer token in Authorization header — never query parameter. API key in header preferred (`X-Api-Key`). OAuth 2.0 client credentials for service-to-service with token refresh in client wrapper. mTLS certificate path from env var.

**Error handling:** 4xx client errors — do not retry except 429. 5xx server errors — retry with backoff. 429: respect `Retry-After` header if present. Timeout: connect timeout and read timeout both required — no infinite wait.

**Retries:** Idempotent methods (GET, PUT, DELETE) — retry on transient failure. Non-idempotent (POST, PATCH) — retry only on network error before server received request. Backoff: base 100ms, multiplier 2x, jitter 0–50%, max 30s. Max attempts: 3 default.

**Testing:** Mock at HTTP boundary — not at service layer. No real external calls in unit/integration tests. Consumer-driven contracts (Pact or equivalent) for critical external dependencies.

### GraphQL

**Patterns:** Queries and mutations in `.graphql` files — not inline strings. Code generation from schema (graphql-codegen or equivalent). Fragments for shared field sets. Introspection disabled in production client config.

**Error handling:** GraphQL errors array always checked — HTTP 200 with errors array is a failed operation. Partial success (data + errors both present) handled explicitly, not silently. Distinguish network error from GraphQL error in client wrapper.

**Performance:** Fragment colocation — fragment defined next to component that uses it. Normalized cache (Apollo InMemoryCache or equivalent) for web clients. Persisted queries for production web clients over HTTP/1.1. Subscriptions cleaned up on component unmount or scope exit.

### gRPC

**Patterns:** Proto files committed to repo, generated code excluded from VCS. Stub generation part of build process — not manual. One channel per service — channel is expensive to create. Every RPC call has explicit deadline — no calls without timeout.

**Auth:** `PerRPCCredentials` interface, token injected per call via interceptor. mTLS at channel construction. Auth in metadata — not in proto message fields.

**Error handling:** gRPC status codes (NOT HTTP codes) — `NOT_FOUND`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`. `UNAVAILABLE`: retry with backoff. `DEADLINE_EXCEEDED`: do not retry — deadline has passed. Error classification in interceptor — not scattered per-call.

**Testing:** In-process gRPC server for tests — no network required. Mock at stub level. Test timeout behavior explicitly with controlled server delay.

### Realtime

**Patterns:** WebSocket: single connection per logical session, multiplex messages over it. SSE for server-push-only scenarios (uni-directional). Long-poll is legacy fallback only — prefer WebSocket or SSE for new code. Explicit message type field in all payloads.

**Auth:** WebSocket auth token sent in first message after connect — not in URL (URLs are logged). SSE: Bearer token in headers via polyfill, or cookie-based for browser-native EventSource. Token refresh: reconnect with new token when auth expires.

**Error handling:** Connection loss detected via heartbeat/ping — not only on close event. Reconnect: exponential backoff with jitter. Message ordering: include sequence numbers — do not assume ordered delivery. Handlers must be idempotent (duplicate delivery).

**Performance:** Enforce max message size at both ends. No unbounded message queue client-side. No new WebSocket per operation. Heartbeat: 30s ping, 60s timeout (configurable).

### API Consumption Receipt Extension Fields

```json
{
  "protocols_loaded": ["rest", "graphql"],
  "auth_methods_detected": ["Bearer"],
  "credentials_policy_checked": true,
  "references_loaded": ["string"],
  "security_forwarded": true
}
```

---

## Common Patterns Across All _shared/dev/ Modules

### Load Model

All _shared/dev/ modules follow the same load model:
1. Tech-stack signal detected (Recipe or Explore)
2. Activation gate matched
3. SKILL.md declares which references/ files load for this task shape
4. References injected into Executor context at wave start
5. Rules applied during Apply (gateway routing)
6. Receipt written

### Credentials Rule (universal)

Applies to all three module groups:
- No credentials in code
- No credentials in committed config files
- Credentials from environment variables only
- Connection strings, API keys, tokens — all env vars

This rule is enforced by both the relevant _shared/dev/ module (rules/credentials-policy.md or rules/no-credentials-in-code.md) and the Security gateway (cross-cutting).

### Security Gateway Forwarding

Database security rules and API consumption auth patterns are forwarded to the Security gateway for cross-cutting review. The _shared/dev/ modules declare what the security requirements are; the Security gateway ensures they are applied consistently across all targets.

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Tech-stack signals trigger module activation |
| Explore | Explore detects tech stack to populate project-map.md and notifies Recipe |
| Platform packages (L3) | Platform SKILL.md declares which _shared/dev/ modules it may load |
| Apply | Apply reads loaded rules during gateway routing |
| Executor | Executor receives references injected at wave start |
| Security gateway | Database and API auth rules forwarded for cross-cutting security review |
| Engineering gateway | Engineering cross-cutting standards override language-specific when in conflict |

---

## Verification Mode

**Observation** — correct modules activated for detected tech stack, version floors honored, credentials policy applied, receipts written.

---

## Cross-References

- L3 Platform packages (consumers of _shared/dev/): `WabbleSpec v6.1 — Platform.md`
- Security gateway (credentials cross-cutting): `WabbleSpec v6.1 — Security.md`
- Engineering gateway (standards override): `WabbleSpec v6.1 — Engineering.md`
- AI gateway (vector database routing): `WabbleSpec v6.1 — AI.md`
- Invariants: `WabbleSpec v6.1 — Core.md` § Invariants
