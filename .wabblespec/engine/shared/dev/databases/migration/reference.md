# Database Migration Reference

> **Type:** Database reference | Loaded by platform packages on demand.

---

## Non-Negotiable Rules

1. **Every schema change through a migration.** No manual `ALTER` in production.
2. **Sequential or timestamp-prefixed filenames.** Order is enforced by filename.
3. **Up and down required.** Every migration reversible — or explicitly documented as irreversible.
4. **Two-phase for destructive changes.** Removing a column or table requires a deploy gap.
5. **Migrations run in CI before tests.** Never test against stale schema.

---

## Naming Convention

```
Sequential:   001_create_users.sql        002_add_email_index.sql
Timestamp:    20260522103000_create_users.sql

Pick one — be consistent. Timestamp preferred for multi-branch development (avoids conflicts).
```

---

## Migration File Structure

```sql
-- migrations/20260522103000_add_users_role.sql

-- Up
ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'viewer';
CREATE INDEX idx_users_role ON users(role);

-- Down
DROP INDEX idx_users_role;
ALTER TABLE users DROP COLUMN role;
```

**Tooling:** Flyway, Liquibase, Alembic, golang-migrate, Prisma Migrate, Rails migrations. All enforce sequential application and track applied migrations in a schema history table.

---

## Two-Phase Destructive Changes

Never drop a column or table in the same deploy that removes application code using it. Old instances still running will fail if the column vanishes.

### Remove a Column (safe sequence)

```
Phase 1 — Deploy A: Stop writing to column in application code.
          Leave column in place. Old + new app instances work.

Phase 2 — After all instances run Deploy A:
          Run migration to DROP COLUMN.
          Column is now gone — no code references it.
```

### Rename a Column (safe sequence)

```
Phase 1: Add new column. Dual-write to old + new. Read from old.
Phase 2: Migrate existing data (backfill). Read from new. Write to new only.
Phase 3: Drop old column.
```

### Add NOT NULL Column (safe sequence)

```
Phase 1: Add column as nullable. Backfill existing rows. Add NOT NULL constraint.
         (Or: add with DEFAULT, then remove DEFAULT after backfill if needed.)
```

---

## Tooling Examples

### Prisma

```bash
# Create migration from schema change
npx prisma migrate dev --name add_users_role

# Apply in production (CI/CD)
npx prisma migrate deploy

# Check status
npx prisma migrate status
```

### Alembic (Python)

```bash
# Generate migration
alembic revision --autogenerate -m "add users role"

# Apply
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

### golang-migrate

```bash
# Apply
migrate -path ./migrations -database "$DATABASE_URL" up

# Rollback one
migrate -path ./migrations -database "$DATABASE_URL" down 1
```

---

## CI Integration

```yaml
# Run migrations before tests — always
- name: Run migrations
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ env.TEST_DATABASE_URL }}

- name: Run tests
  run: npm test
```

**Never run tests against the previous schema.** Migration failures surface in CI, not production.

---

## Irreversible Migrations

Some operations cannot be undone (data destruction). Document explicitly:

```sql
-- Down: IRREVERSIBLE — data permanently deleted
-- Backup required before running up migration.
-- Rollback: restore from backup.
```

Do not write a fake `DROP TABLE` in the Down section for a migration that lost data. Document the real rollback procedure.

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Schema drift | Manual ALTER in production | All changes through migrations; audit with `prisma db pull` |
| Migration conflict (sequential) | Two branches both create migration N | Use timestamp prefix instead of sequential |
| Dropped column breaks old instance | Same-deploy remove | Two-phase: stop writing first, drop in next deploy |
| NOT NULL failure on existing rows | Added NOT NULL without backfill | Add nullable, backfill, then add constraint |
| Migration runs in wrong order | Filename not sortable | Enforce zero-padded sequential or ISO timestamp prefix |
| Prod migration never tested | Only applied to dev | Run `migrate deploy` in CI against test DB before merge |
