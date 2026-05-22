# SQL Reference

> **Type:** Database reference | Loaded by platform packages on demand.
> **Applies to:** PostgreSQL, MySQL, SQLite

---

## Non-Negotiable Rules

1. **Parameterized queries always.** No string concatenation into SQL. Ever.
2. **Transaction scope: short.** Open, write, commit. No user interaction inside a transaction.
3. **Migrations: versioned, up+down.** Never modify production schema outside a migration.
4. **Indexes declared at design time.** Every foreign key indexed. Every `WHERE` column on hot queries analyzed.

---

## Parameterized Queries

```sql
-- NEVER: string concatenation (SQL injection)
query = "SELECT * FROM users WHERE email = '" + email + "'"

-- ALWAYS: parameterized
-- PostgreSQL (node-postgres):
const result = await client.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);

-- Python (psycopg3):
cur.execute("SELECT * FROM users WHERE email = %s", (email,))

-- Go (database/sql):
row := db.QueryRowContext(ctx,
  "SELECT id FROM users WHERE email = $1", email)
```

**ORMs parameterize by default — only unsafe when using raw query methods with interpolation.**

---

## Transaction Scope

```sql
-- Short transaction: write, commit, done
BEGIN;
  INSERT INTO orders (user_id, total) VALUES ($1, $2);
  UPDATE inventory SET qty = qty - $3 WHERE sku = $4;
COMMIT;

-- NEVER: long-running transaction
BEGIN;
  SELECT * FROM products;  -- read
  -- ... wait for user input ...  -- NEVER
  UPDATE cart SET ...;
COMMIT;
```

Long transactions:
- Hold row locks — block concurrent writes
- Inflate WAL (PostgreSQL autovacuum debt)
- Increase deadlock probability

**Rule:** No transaction spans a network call, user input, or external API call.

---

## Index Strategy

```sql
-- Always index foreign keys
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Compound index: column order matters — most selective first, or match WHERE + ORDER BY
CREATE INDEX idx_events_user_created ON events(user_id, created_at DESC);

-- Partial index for common filtered queries
CREATE INDEX idx_active_users ON users(email) WHERE deleted_at IS NULL;

-- Analyze query plans before shipping hot queries
EXPLAIN (ANALYZE, BUFFERS)
  SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC LIMIT 20;
-- Look for: Seq Scan on large table = missing index
```

---

## Connection Pooling

```
Application → Connection Pool → PostgreSQL

Pool size: (num_cores × 2) + effective_spindle_count
Typical: 10–20 connections per application instance

PgBouncer: transaction mode for most workloads
Prisma/SQLAlchemy/GORM: built-in pool config — always set max explicitly
```

**Never open a new connection per request.** Always use a pool.

---

## PostgreSQL-Specific

```sql
-- Use RETURNING to avoid round-trip
INSERT INTO users (email) VALUES ($1) RETURNING id, created_at;

-- JSONB for semi-structured data (indexed, queryable)
ALTER TABLE events ADD COLUMN metadata JSONB;
CREATE INDEX idx_events_metadata ON events USING GIN(metadata);

-- Avoid SELECT * in production — list columns explicitly
-- SELECT * breaks when columns added/reordered in ORM mapping

-- UPSERT
INSERT INTO settings (user_id, key, value)
VALUES ($1, $2, $3)
ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value;
```

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| SQL injection | String concatenation | Parameterized queries always |
| Deadlock | Lock acquisition order differs across transactions | Consistent lock order; short transactions |
| Slow query in production | No index on WHERE/JOIN column | `EXPLAIN ANALYZE` before shipping; add index |
| Connection exhaustion | No pool, or pool too small | Configure pool; `max_connections` in pg config |
| Schema drift | Manual ALTER in production | Every schema change through migration |
| N+1 query | ORM lazy-loading in loop | Eager load with JOIN or `include`; batch queries |
