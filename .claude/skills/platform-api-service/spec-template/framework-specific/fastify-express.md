# Framework-Specific Architecture: Fastify / Express (Node.js)

> **Applies when:** `fastify` or `express` in package.json + TypeScript + Node.js runtime detected.
> Covers Fastify 4.x (preferred for new projects) and Express 4.x (legacy). Declare which in technical-spec.md.
> **Version authority:** Fastify 4.26+. Express 4.x. Node.js 20+ LTS.

---

## Framework Declaration [REQUIRED]

| Framework | When to use |
|---|---|
| **Fastify** | New projects; performance-critical; schema-first validation; TypeScript first-class |
| **Express** | Existing codebase; ecosystem compatibility requirement; team familiarity |

**Declared framework:** ___

---

## Fastify — Plugin Architecture

Fastify's core design principle: everything is a plugin. Routes, middleware, decorators, and lifecycle hooks are all registered as plugins. This enables encapsulation and scope isolation.

```typescript
// src/app.ts — application factory
import Fastify, { FastifyInstance } from 'fastify'
import cors from '@fastify/cors'
import helmet from '@fastify/helmet'
import jwt from '@fastify/jwt'
import { productsPlugin } from './routes/products'

export async function buildApp(): Promise<FastifyInstance> {
  const app = Fastify({
    logger: { level: process.env.LOG_LEVEL ?? 'info' },  // built-in pino logger
    ajv: { customOptions: { removeAdditional: 'all' } }  // strip unknown fields
  })

  // Security plugins registered first
  await app.register(helmet)
  await app.register(cors, { origin: process.env.ALLOWED_ORIGINS?.split(',') })
  await app.register(jwt, { secret: process.env.JWT_SECRET! })

  // Route plugins — each runs in its own scope (encapsulated)
  await app.register(productsPlugin, { prefix: '/products' })

  return app
}

// src/server.ts — entrypoint
import { buildApp } from './app'
const app = await buildApp()
await app.listen({ port: 3000, host: '0.0.0.0' })
```

---

## Fastify Schema Validation

Fastify validates request and response against JSON Schema **before** the handler runs. Invalid requests are rejected automatically — no validation code in handlers.

```typescript
// routes/products.ts
import { FastifyPluginAsync } from 'fastify'
import { Type, Static } from '@sinclair/typebox'  // TypeBox: TypeScript → JSON Schema

const ProductSchema = Type.Object({
  id: Type.String({ format: 'uuid' }),
  name: Type.String({ minLength: 1, maxLength: 200 }),
  price: Type.Number({ minimum: 0.01 }),
})

const CreateProductBody = Type.Object({
  name: Type.String({ minLength: 1, maxLength: 200 }),
  price: Type.Number({ minimum: 0.01 }),
  categoryId: Type.String({ format: 'uuid' }),
})

type CreateProductBody = Static<typeof CreateProductBody>

export const productsPlugin: FastifyPluginAsync = async (app) => {
  // Authentication hook — applies to all routes in this plugin scope
  app.addHook('onRequest', async (request, reply) => {
    try {
      await request.jwtVerify()
    } catch (err) {
      reply.status(401).send({ error: 'Unauthorized' })
    }
  })

  app.post<{ Body: CreateProductBody }>('/', {
    schema: {
      body: CreateProductBody,          // validated before handler runs
      response: { 201: ProductSchema }  // response validated in dev; stripped in prod
    },
    handler: async (request, reply) => {
      const product = await productService.create(request.body)
      return reply.status(201).send(product)
    }
  })
}
```

**TypeBox integration:** Use `@sinclair/typebox` to define schemas as TypeScript types and JSON Schemas simultaneously. This eliminates the schema/type divergence that occurs with manual JSON Schema objects.

---

## Express — Middleware Pattern

```typescript
// src/app.ts
import express, { Application, Request, Response, NextFunction } from 'express'
import helmet from 'helmet'
import cors from 'cors'
import { productsRouter } from './routes/products'
import { errorHandler } from './middleware/errorHandler'

export function createApp(): Application {
  const app = express()

  // Security middleware — always first
  app.use(helmet())
  app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }))
  app.use(express.json({ limit: '1mb' }))  // explicit size limit

  // Routes
  app.use('/products', productsRouter)

  // 404 handler
  app.use((_req: Request, res: Response) => {
    res.status(404).json({ error: 'Not found' })
  })

  // Error handler — must be last, must have 4 params
  app.use(errorHandler)

  return app
}
```

```typescript
// middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express'

export function errorHandler(err: Error, _req: Request, res: Response, _next: NextFunction) {
  if (err.name === 'ValidationError') {
    return res.status(400).json({ error: err.message })
  }
  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({ error: 'Unauthorized' })
  }
  // Do not expose internal errors to clients
  console.error(err)
  res.status(500).json({ error: 'Internal server error' })
}
```

**Express validation:** Express does not validate by default. Use `zod` + `express-zod-api` or `joi` + manual checks. Never skip validation in Express routes — no framework safety net.

---

## Request Lifecycle and Error Handling

**Fastify lifecycle hooks:**
```typescript
// Hook order: onRequest → preParsing → preValidation → preHandler → handler → preSerialization → onSend → onResponse
// Error in any hook: → onError → onSend → onResponse

app.addHook('onRequest', async (request, reply) => { /* auth */ })
app.addHook('preHandler', async (request, reply) => { /* rate limit, logging */ })

// Fastify error handler
app.setErrorHandler(async (error, request, reply) => {
  if (error.validation) {
    return reply.status(400).send({ errors: error.validation })
  }
  request.log.error(error)
  reply.status(error.statusCode ?? 500).send({ error: error.message })
})
```

---

## TypeScript Configuration

```json
// tsconfig.json — strict settings required
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,   // arr[i] is T | undefined — forces null checks
    "exactOptionalPropertyTypes": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

---

## GWT Acceptance Scenarios

```
Given: a POST request body is missing a required field
When: Fastify receives the request (schema validation enabled)
Then: the handler never runs
      AND the response is HTTP 400 with a body listing the missing field
      AND no partial state is written to the database

Given: an unhandled exception is thrown inside a route handler
When: the error propagates to the error handler
Then: the client receives HTTP 500 with a generic error message (no stack trace)
      AND the full error (with stack) is logged server-side
      AND the server remains running (no process crash)

Given: a route requires authentication
When: the JWT hook runs before the handler
Then: an invalid or missing token returns HTTP 401 before the handler executes
      AND a valid token proceeds to the handler
      AND the decoded token payload is available on request.user (Fastify) or req.user (Express)
```
