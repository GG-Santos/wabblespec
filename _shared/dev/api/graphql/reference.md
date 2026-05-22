# GraphQL API Consumption Reference

> **Type:** API reference | Loaded by platform packages on demand.

---

## Non-Negotiable Rules

1. **Queries in `.graphql` files.** No inline query strings in application code.
2. **Code generation from schema.** Types derived from schema — not hand-written.
3. **Partial success handled explicitly.** GraphQL returns 200 with `errors` array — check it.
4. **Query complexity awareness.** Deep nested queries can be expensive — understand cost.

---

## Query Files

```graphql
# queries/GetUser.graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    email
    profile {
      displayName
      avatarUrl
    }
  }
}

# mutations/UpdateProfile.graphql
mutation UpdateProfile($input: UpdateProfileInput!) {
  updateProfile(input: $input) {
    id
    displayName
  }
}
```

**Why `.graphql` files:**
- Static analysis catches typos at build time
- Code generation produces typed client code
- Queries are auditable — no inline strings buried in components

---

## Code Generation

```bash
# GraphQL Code Generator (TypeScript)
npx graphql-codegen --config codegen.yml

# codegen.yml
schema: https://api.example.com/graphql
documents: src/**/*.graphql
generates:
  src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-urql   # or typescript-react-apollo
```

Generated types update when schema changes — run codegen in CI to catch schema drift.

---

## Partial Success Handling

GraphQL responses can have both `data` AND `errors` simultaneously:

```typescript
// WRONG: assuming 200 = success
const response = await client.query({ query: GET_USER, variables: { id } });
const user = response.data.user;  // may be null if errors occurred

// CORRECT: check errors explicitly
const { data, errors } = await client.query({
  query: GET_USER,
  variables: { id },
  errorPolicy: 'all',  // urql: receive both data and errors
});

if (errors && errors.length > 0) {
  // Handle errors — data may be partial, null, or valid
  errors.forEach(err => log.error('GraphQL error', err.message, err.extensions));
}

if (!data?.user) {
  throw new NotFoundError(`User ${id} not found`);
}
```

**`errorPolicy: 'none'` (default in Apollo):** Throws on any error, discards partial data. May be too strict for partially-failing queries.
**`errorPolicy: 'all'`:** Returns both data and errors. Handle explicitly.

---

## Client Setup

```typescript
// urql — single client per endpoint
import { createClient, cacheExchange, fetchExchange, retryExchange } from 'urql';

const client = createClient({
  url: process.env.GRAPHQL_ENDPOINT!,
  exchanges: [
    retryExchange({
      maxNumberAttempts: 3,
      retryIf: (error) => error.networkError !== null,  // retry network errors, not GraphQL errors
    }),
    cacheExchange,
    fetchExchange,
  ],
  fetchOptions: () => ({
    headers: { Authorization: `Bearer ${getToken()}` },
  }),
});
```

---

## Fragments for Reuse

```graphql
# fragments/UserFields.graphql
fragment UserFields on User {
  id
  email
  profile { displayName }
}

# queries/GetPost.graphql
query GetPost($id: ID!) {
  post(id: $id) {
    title
    author {
      ...UserFields
    }
  }
}
```

Fragments prevent copy-paste of field sets and keep codegen output DRY.

---

## Subscriptions

```typescript
// WebSocket for subscriptions — not polling
const subscription = client.subscription(ON_NEW_MESSAGE, { roomId }).subscribe({
  next: ({ data }) => handleMessage(data?.newMessage),
  error: (err) => log.error('Subscription error', err),
});

// Cleanup — always unsubscribe
return () => subscription.unsubscribe();
```

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Runtime type error | Hand-written types drift from schema | Run codegen; never hand-write query types |
| Silent partial failure | Not checking `errors` in response | Always check `response.errors`; set `errorPolicy: 'all'` |
| N+1 on server | Deep nested query without DataLoader | Add query complexity limit; discuss with API team |
| Inline query string | Query string in component | Move to `.graphql` file; codegen validates |
| Token not refreshed | Auth error not intercepted | Handle 401 UNAUTHENTICATED extension code specifically |
