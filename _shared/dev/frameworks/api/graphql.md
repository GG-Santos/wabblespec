# GraphQL Framework

Loaded by Apply when graphql is detected in dependencies.

## Version baseline

GraphQL spec 2021. Declare: library (Apollo Server, graphql-yoga, Strawberry, Hasura, etc.).

## Schema-first vs code-first

| Approach | Definition |
|---|---|
| Schema-first | Write `.graphql` SDL; generate resolvers from schema |
| Code-first | Write resolvers in code; generate schema from code (Pothos, Strawberry) |

Spec must declare which approach is used and why.

## Schema design

```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilter, page: PageInput): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}

type Subscription {
  userUpdated(userId: ID!): User!
}

type User {
  id: ID!
  email: String!
  name: String!
  createdAt: DateTime!
  orders: [Order!]!         # nested relationship
}

# Pagination — Relay-style cursor pagination
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  cursor: String!
  node: User!
}
```

## Pagination — cursor vs offset

Prefer cursor-based (Relay spec) for:
- Large datasets that change frequently
- Infinite scroll patterns

Use offset only for: fixed, small datasets with page UI.

## N+1 problem and DataLoader

GraphQL resolvers run independently per field, causing N+1 database queries for lists:

```javascript
// N+1: runs N queries for orders on N users
const resolvers = {
  User: {
    orders: (user) => db.orders.findByUserId(user.id)  // called N times
  }
}

// Fix: DataLoader batches and caches per request
const ordersByUserLoader = new DataLoader(async (userIds) => {
  const orders = await db.orders.findByUserIds(userIds)
  return userIds.map(id => orders.filter(o => o.userId === id))
})

const resolvers = {
  User: {
    orders: (user) => ordersByUserLoader.load(user.id)  // batched to 1 query
  }
}
```

DataLoader is required for any list relationship resolver. Spec must identify all N+1 risks.

## Authorization in GraphQL

GraphQL's single endpoint means authorization cannot be handled at the route level — it must be per-field or per-resolver.

```javascript
const resolvers = {
  Query: {
    adminDashboard: (_, __, ctx) => {
      if (!ctx.user?.roles.includes('admin')) {
        throw new GraphQLError('Forbidden', { extensions: { code: 'FORBIDDEN' } })
      }
      return getAdminData()
    }
  }
}
```

Spec must declare: authorization model (field-level? resolver-level? directive-based?) and which fields require which permissions.

## Error handling

GraphQL returns HTTP 200 with errors in the response body:

```json
{
  "data": { "user": null },
  "errors": [{
    "message": "User not found",
    "extensions": { "code": "NOT_FOUND" },
    "path": ["user"]
  }]
}
```

Use `extensions.code` for machine-readable error codes. Never expose stack traces in production.

## Query depth and complexity limits

Without limits, clients can construct deeply nested queries that exhaust resources:

```javascript
// Server config
const server = new ApolloServer({
  schema,
  plugins: [
    ApolloServerPluginQueryDepthLimit({ maxDepth: 10 }),
    ApolloServerPluginQueryComplexityLimit({ maxComplexity: 1000 }),
  ]
})
```

Spec must declare: maximum query depth, complexity scoring strategy, and cost per field type.

## Persisted queries

For production: use persisted queries (client sends hash; server looks up query). Benefits:
- Prevents arbitrary queries from public clients
- Enables query-level caching and analytics
- Reduces request payload size

Declare: APQ (Automatic Persisted Queries) or registered queries.
