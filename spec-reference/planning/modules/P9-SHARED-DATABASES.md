# Module Plan — _shared/dev/databases/ (L3 Shared)

**Tier:** 2 — FOUNDATION SHARED
**Layer:** L3 Shared (loaded by platform packages)
**v5.3 origin:** Development gateway — Database group (SQL, NoSQL, ORM, Migration)

---

## Purpose

Cross-platform database reference modules. Each database module holds connection patterns, query conventions, schema management rules, and platform-specific integration guidance. Platform packages load the relevant database module(s) on demand. Not orchestration modules. Reference libraries with activation logic.

---

## Scope

Four database modules:

| Module | Path | Covers |
|---|---|---|
| SQL | `_shared/dev/databases/sql/` | PostgreSQL, MySQL/MariaDB, SQLite |
| NoSQL | `_shared/dev/databases/nosql/` | MongoDB, Redis, DynamoDB, Firestore |
| ORM | `_shared/dev/databases/orm/` | Prisma, SQLAlchemy, GORM, Hibernate, Drizzle |
| Migration | `_shared/dev/databases/migration/` | Schema versioning, migration tooling, rollback |

---

## Activation

`skill-rules.json` per database module triggers:
- Recipe detects database dependency signals (connection string env vars, ORM config files, migration directories, database-specific packages)
- Platform package declares database dependency
- Explicit `/db <type>` override command

Detection signals per module:

| Module | Detection signals |
|---|---|
| SQL | `DATABASE_URL` with postgres/mysql/sqlite scheme, `psycopg`, `mysql-connector`, `better-sqlite3`, `pg` packages |
| NoSQL | `MONGO_URI`, `REDIS_URL`, `mongoose`, `redis`, `dynamoose`, `firebase-admin` packages |
| ORM | `schema.prisma`, `sqlalchemy` import, `gorm` import, `hibernate.cfg.xml`, `drizzle.config.*` |
| Migration | `migrations/` directory, `alembic.ini`, `flyway.conf`, `liquibase.properties`, `db/migrate/` |

Multiple database modules can activate simultaneously (SQL + ORM + Migration is typical).

---

## Content Structure (per database module)

```
_shared/dev/databases/<type>/
  SKILL.md                      <- loader spec: activation, load scope, authority
  skill-rules.json              <- detection signals
  references/
    patterns.md                 <- core access patterns, query conventions
    connection-management.md    <- pooling, retries, health checks
    transactions.md             <- transaction scope, isolation levels, rollback
    security.md                 <- injection prevention, credentials, least-privilege
    performance.md              <- indexing, query analysis, N+1 prevention
    testing.md                  <- test database setup, seeding, teardown patterns
  rules/
    credentials-policy.md       <- no hardcoded credentials, env var required
    connection-pool-policy.md   <- pool sizing, timeout, overflow behavior
  schemas/
    receipt.schema.json
```

---

## Per-Module Content Detail

### SQL

`references/patterns.md`:
- PostgreSQL: JSONB for semi-structured data, CTEs for complex queries, EXPLAIN ANALYZE before shipping slow queries
- MySQL: explicit charset (utf8mb4), engine InnoDB, avoid SELECT *
- SQLite: WAL mode for concurrent reads, single-writer model, appropriate for embedded/local targets only
- Parameterized queries mandatory — no string interpolation in queries

`references/transactions.md`:
- Transaction scope: keep short, never span user interactions
- Isolation level: READ COMMITTED default, SERIALIZABLE only when conflict detection required
- Rollback on any exception — no partial commits
- Deadlock handling: retry with exponential backoff, max 3 attempts

`references/security.md`:
- SQL injection: parameterized queries (never format strings)
- Credentials: env vars only, never in code or config files committed to repo
- Least-privilege: application user has no DDL permissions in production
- Connection string: never logged

`references/performance.md`:
- Index on all foreign keys and frequently queried columns
- Avoid SELECT * in application code
- N+1: detect with query count assertions in tests
- EXPLAIN ANALYZE: required for any query touching > 10k rows in production schema

### NoSQL

`references/patterns.md`:
- MongoDB: schema validation at collection level even without enforced schema, avoid unbounded arrays as document fields
- Redis: key naming convention (service:entity:id), TTL on all cache keys, no Redis as primary store
- DynamoDB: access-pattern-first design, single-table design for related entities, avoid scan operations
- Firestore: subcollections over nested documents for large lists, avoid deeply nested paths

`references/connection-management.md`:
- MongoDB: replica set or Atlas connection only in production, retryWrites enabled
- Redis: connection pooling, reconnect-on-failure, circuit breaker pattern for cache unavailability
- DynamoDB: exponential backoff on ProvisionedThroughputExceededException
- Firestore: offline persistence — declare intent explicitly (on/off)

`references/security.md`:
- MongoDB: authentication required, authSource specified, TLS in production
- Redis: AUTH required if network-exposed, never expose Redis port publicly
- DynamoDB: IAM role-based access, no long-lived keys in code
- Firestore: Security Rules required — no open read/write

### ORM

`references/patterns.md`:
- Prisma: generated client typed from schema, migrations via `prisma migrate`, never edit generated files
- SQLAlchemy: prefer Core for complex queries, ORM for simple CRUD, avoid lazy loading in async contexts
- GORM: use pointer receivers for models, explicit preloading over N+1 lazy
- Hibernate: second-level cache only with explicit justification, avoid open-session-in-view
- Drizzle: schema-as-code, type-safe queries, migrations via drizzle-kit

`references/performance.md`:
- Eager loading: declare joins explicitly for known relationship traversals
- Batch operations: bulk insert/update over individual row operations
- Raw queries: acceptable for complex reporting queries that ORM generates inefficiently — must be documented
- ORM instrumentation: log all generated queries in development mode

`references/testing.md`:
- Test database: separate schema or in-memory database for unit tests
- Transactions: wrap each test in a transaction, rollback after (no teardown scripts)
- Factories: use factory patterns for seed data — no hardcoded fixture files
- ORM migrations: run against test database before CI test suite

### Migration

`references/patterns.md`:
- Migration files: sequential or timestamp-prefixed, never modify committed migrations
- Up + down: every migration has rollback path (down migration required)
- Idempotency: migrations must be safe to re-run (CREATE IF NOT EXISTS, not CREATE)
- Schema changes: additive changes (new columns with defaults) safe in production; column removal requires two-phase deploy

`references/transactions.md`:
- Wrap each migration in explicit transaction where database supports it
- DDL transactions: PostgreSQL supports, MySQL does not — document non-transactional steps explicitly
- Long-running migrations: run with explicit timeout, monitor lock acquisition

`references/security.md`:
- Migration runner: separate credentials from application user — migration user has DDL, app user does not
- Review: schema changes require Reviewer before production apply
- Backup: snapshot before destructive migrations (DROP, TRUNCATE, column removal)

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Loaded references | In-context during active wave | Database patterns available to Executor |
| Database receipt | `.wabblespec/receipts/db-<type>-receipt.md` | I10 compliance, tracks which modules loaded |

---

## Workflow

```
1. Recipe identifies build target
2. Database dependency signals scanned
3. Matched database module(s) activated via Activation gate
4. SKILL.md declares which references/ files load for this task shape
5. References injected into Executor context at wave start
6. Database-specific rules applied during Apply
7. Security rules passed to Security gateway (cross-cutting check)
8. Write database receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` per module | Required | Load scope and activation signals |
| `skill-rules.json` per module | Required | Detection signal patterns |
| `references/` per module | Required | All reference content |
| `rules/credentials-policy.md` | Rules | No hardcoded credentials enforcement |
| `rules/connection-pool-policy.md` | Rules | Pool sizing and timeout policy |
| `schemas/receipt.schema.json` | Schema | Receipt per activation |

---

## Integration Points

| Module | Relationship |
|---|---|
| Recipe | Tech-stack signals trigger database module activation |
| Platform packages (L3) | Platform SKILL.md declares which database modules it may load |
| Apply | Apply reads database rules during gateway routing |
| Executor | Executor receives database references injected at wave start |
| Security gateway | Database security rules forwarded to Security for cross-cutting review |
| Migration | Migration module integrates with Engineering gateway for schema review gate |

---

## Verification Mode

**Observation** — correct database module(s) activated for detected stack, credentials policy honored, receipt written.

---

## Receipt Extension Fields

```json
{
  "db_modules_loaded": ["sql|nosql|orm|migration"],
  "detected_databases": ["string"],
  "credentials_policy_checked": "boolean",
  "references_loaded": ["string"],
  "security_rules_forwarded": "boolean"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| GraphQL as database layer | Separate module vs. api-consumption concern | P9 api-consumption planning |
| Time-series databases (InfluxDB, TimescaleDB) | Sub-section in SQL vs. own module | P10 Data/Pipeline platform planning |
| Vector databases (pgvector, Pinecone, Weaviate) | Sub-section in NoSQL vs. fed from L4 AI gateway | P11 AI gateway planning |
