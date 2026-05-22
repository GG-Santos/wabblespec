# ORM Reference

> **Type:** Database reference | Loaded by platform packages on demand.
> **Applies to:** Prisma, SQLAlchemy, GORM, Hibernate, Drizzle

---

## Non-Negotiable Rules

1. **Generated client — never edit.** ORM-generated files are artifacts, not source. Regenerate when schema changes.
2. **Raw queries for complex operations.** ORMs abstract simple CRUD — complex joins, window functions, and bulk ops belong in raw SQL.
3. **Eager load to prevent N+1.** Default lazy loading causes N+1 queries. Identify and explicitly include relations.
4. **Column selection explicit.** Never `findAll()` / `SELECT *` when only a few columns needed.

---

## Prisma (TypeScript)

```typescript
// Generated client — never edit node_modules/.prisma/ or @prisma/client
// Regenerate: npx prisma generate

// Explicit select — avoid over-fetching
const user = await prisma.user.findUnique({
  where: { id: userId },
  select: { id: true, email: true, createdAt: true },  // NOT: omit select
});

// Eager load relations — no N+1
const posts = await prisma.post.findMany({
  where: { published: true },
  include: { author: { select: { name: true } } },  // one query, not N+1
});

// Transactions for multi-step writes
const [order, _] = await prisma.$transaction([
  prisma.order.create({ data: orderData }),
  prisma.inventory.update({ where: { sku }, data: { qty: { decrement: 1 } } }),
]);

// Raw query for complex operations
const result = await prisma.$queryRaw<Row[]>`
  SELECT user_id, COUNT(*) as order_count
  FROM orders
  WHERE created_at > ${cutoff}
  GROUP BY user_id
  HAVING COUNT(*) > 5
`;
// $queryRaw uses tagged template — parameterized automatically
```

---

## SQLAlchemy (Python)

```python
# Use ORM session context manager — auto-closes
from sqlalchemy.orm import Session

with Session(engine) as session:
    # Explicit column selection
    user = session.execute(
        select(User.id, User.email).where(User.id == user_id)
    ).one()

    # Eager loading
    posts = session.execute(
        select(Post).options(selectinload(Post.author)).where(Post.published == True)
    ).scalars().all()

    # Bulk insert — not ORM loop
    session.execute(insert(Event), [{"user_id": uid, "type": t} for uid, t in events])
    session.commit()

# Never use session outside context — detached object errors
```

---

## GORM (Go)

```go
// Explicit column selection
var user User
db.Select("id", "email", "created_at").First(&user, userID)

// Eager loading — Preload for relations
var posts []Post
db.Preload("Author").Where("published = ?", true).Find(&posts)

// Transaction
err := db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&order).Error; err != nil {
        return err  // auto-rollback on error return
    }
    return tx.Model(&inventory).Update("qty", gorm.Expr("qty - ?", 1)).Error
})

// Raw query — parameterized
var results []struct{ UserID uint; Count int }
db.Raw("SELECT user_id, COUNT(*) as count FROM orders WHERE created_at > ? GROUP BY user_id", cutoff).
   Scan(&results)
```

---

## Common ORM Pitfalls

### N+1 Query

```
// Problem: 1 query for posts + N queries for each author
posts := getAllPosts()
for _, post := range posts {
    author := getUser(post.AuthorID)  // N queries
}

// Fix: JOIN or eager load
posts := getAllPostsWithAuthors()  // 1 query with JOIN or 2 queries with IN
```

### Lazy Load Outside Session

```python
# SQLAlchemy: accessing relation after session closes = DetachedInstanceError
with Session(engine) as session:
    user = session.get(User, user_id)

user.posts  # ERROR — session closed, lazy load impossible

# Fix: eager load inside session OR use selectinload()
```

### Missing Transaction on Multi-Step Write

```
# Problem: order created, inventory update fails — data inconsistent
create_order()      # succeeds
update_inventory()  # fails — order exists but inventory not decremented

# Fix: wrap both in transaction — either both succeed or neither do
```

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| N+1 queries | Default lazy loading | Eager load with include/Preload/selectinload |
| Slow bulk insert | ORM loop (one INSERT per row) | Bulk insert / `createMany` / `executemany` |
| SQL injection via ORM raw | String interpolation in raw query | Use parameterized raw query APIs (`$queryRaw`, `Raw`) |
| Detached instance error | Accessing lazy relation outside session | Eager load inside session context |
| Generated client out of sync | Schema changed, forgot to regenerate | Add `prisma generate` / `sqlc generate` to dev startup |
