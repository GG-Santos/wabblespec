# NoSQL Reference

> **Type:** Database reference | Loaded by platform packages on demand.
> **Applies to:** MongoDB, Redis, DynamoDB, Firestore

---

## Non-Negotiable Rules

1. **TTL on all cache keys.** No cache key without an expiry. Unbounded cache = eventual OOM.
2. **Collection/table-level validation.** Schema validation at the database layer — not application-only.
3. **Access pattern drives data model.** NoSQL schema design starts with query requirements, not normalization.
4. **Idempotent writes.** NoSQL operations often retry — design writes to be safe if replayed.

---

## Redis

```typescript
// ALWAYS set TTL — never persist indefinitely to cache
await redis.set(`session:${userId}`, JSON.stringify(session), {
  EX: 3600,  // 1 hour — always explicit
});

// NEVER: await redis.set(key, value)  ← no TTL = memory leak

// Atomic operations for counters (avoid race conditions)
await redis.incr(`rate:${userId}:${minuteBucket}`);
await redis.expire(`rate:${userId}:${minuteBucket}`, 60);

// Lua script for atomic get+set
const script = `
  local current = redis.call('GET', KEYS[1])
  if current == false then
    redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
    return ARGV[1]
  end
  return current
`;
```

**Redis is not a database.** Use it for: sessions, rate limiting, pub/sub, leaderboards, short-lived state. Not for: primary data, critical business records, anything that can't be lost.

**Redis persistence:** If data must survive restart, enable RDB or AOF. Default is none.

---

## MongoDB

```javascript
// Collection-level schema validation (MongoDB 3.6+)
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "createdAt"],
      properties: {
        email: { bsonType: "string", pattern: "^.+@.+\\..+$" },
        createdAt: { bsonType: "date" },
      }
    }
  },
  validationAction: "error"  // reject invalid docs — not "warn"
});

// Always use parameterized queries — no string interpolation in operators
// NEVER:
db.users.find({ email: userInput });  // injection if userInput = { $gt: "" }

// Safe: validate and type-check input before passing to query
const email = z.string().email().parse(userInput);
db.users.find({ email });

// TTL index for auto-expiring documents
db.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
```

**Projection always:** `db.collection.find({}, { field1: 1, field2: 1 })` — never return full documents when only a few fields needed.

---

## DynamoDB

```python
# Single-table design: partition key + sort key carry semantics
# PK: "USER#userId", SK: "PROFILE" or "ORDER#orderId"

# Conditional writes for idempotency
table.put_item(
    Item={"PK": f"USER#{user_id}", "SK": "PROFILE", "email": email},
    ConditionExpression="attribute_not_exists(PK)"  # fail if exists
)

# TTL attribute (epoch seconds)
table.put_item(Item={
    "PK": f"SESSION#{session_id}",
    "SK": "SESSION",
    "ttl": int(time.time()) + 3600,  # DynamoDB auto-deletes expired items
    "data": session_data
})
```

**DynamoDB query patterns:** Design GSIs (Global Secondary Indexes) for every non-PK access pattern before writing data. Retroactively adding GSIs is costly.

---

## Firestore

```typescript
// Batch writes for atomicity (up to 500 ops per batch)
const batch = db.batch();
batch.set(userRef, userData);
batch.update(statsRef, { count: FieldValue.increment(1) });
await batch.commit();

// TTL: use scheduled Cloud Functions or TTL policy on collection
// Firestore TTL (GA): set a timestamp field, configure TTL policy in console

// Security rules are the access control layer — not application code alone
// rules_version = '2';
// service cloud.firestore { match /databases/{database}/documents {
//   match /users/{userId} { allow read, write: if request.auth.uid == userId; }
// }}
```

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Redis OOM | Keys without TTL accumulate | Enforce TTL on every SET; set `maxmemory-policy allkeys-lru` |
| MongoDB injection | User input passed as operator | Validate/type-check all query inputs |
| DynamoDB hot partition | All traffic to one PK | Distribute writes; add random suffix to PK if needed |
| Firestore read amplification | Reading full documents for one field | Use field masks in queries |
| Lost cache invalidation | Cache updated before DB write completes | Write DB first, then invalidate cache (cache-aside) |
