# Next.js Framework

Loaded by Apply when `next.config.*` or App Router/Pages Router structure is detected.

## Version baseline

Next.js 14+ (App Router). If Pages Router detected, note it and apply Pages Router-specific rules.

## App Router vs Pages Router

| Concern | App Router (app/) | Pages Router (pages/) |
|---|---|---|
| Default component type | Server Component | Client Component |
| Data fetching | async/await in Server Components; use() in Client | getServerSideProps / getStaticProps |
| Layout | layout.tsx (nested, shared) | _app.tsx / _document.tsx |
| Caching | fetch() cache options; `cache: 'force-cache'` vs `revalidate` | ISR via `revalidate` in getStaticProps |
| Streaming | React Suspense + loading.tsx | Not supported |
| Server Actions | Yes — form mutations without API routes | No |
| Route Handlers | app/api/route.ts | pages/api/*.ts |

## Server Component rules

Server Components run on the server only. They cannot:
- Use browser APIs (window, document, localStorage)
- Use React hooks (useState, useEffect, useContext)
- Add event listeners

When a component needs any of the above, mark it `'use client'`. Prefer keeping the Client Component boundary as low in the tree as possible.

## Data fetching patterns

```typescript
// Server Component — preferred for initial data
async function Page() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'no-store',         // always fresh
    // OR
    next: { revalidate: 60 }, // ISR: revalidate every 60s
  })
  return <div>{data.name}</div>
}

// Client Component — for user-interaction-driven data
'use client'
import { useState, useEffect } from 'react'
```

Spec must declare: which data is fetched server-side vs client-side, and the cache/revalidate strategy for each.

## Route structure

Spec must include full route inventory:
```
app/
  layout.tsx          — root layout (shared)
  page.tsx            — / (home)
  (auth)/             — route group (no URL segment)
    login/page.tsx    — /login
  dashboard/
    layout.tsx        — dashboard layout
    page.tsx          — /dashboard
    [id]/page.tsx     — /dashboard/:id
  api/
    route.ts          — API route (GET, POST, etc.)
```

## Middleware

`middleware.ts` runs on the Edge before every request. Use for:
- Auth token validation (redirect to login if no session)
- Locale detection
- A/B testing assignments

Do not use middleware for: heavy computation, database queries (Edge limitations), or anything requiring Node.js APIs.

## Performance — Next.js specific

- `next/image`: use for all images — automatic WebP, lazy loading, size optimization
- `next/font`: use for all fonts — eliminates CLS from font loading
- `next/link`: prefetches linked pages on hover
- Code splitting: automatic per route; no manual dynamic import needed for route boundaries
- Bundle analyzer: `@next/bundle-analyzer` — run when bundle size exceeds budget

## Security — Next.js specific

- Headers: configure in `next.config.js` `headers()` — add CSP, HSTS, X-Frame-Options
- Server Actions: validate all inputs; Server Actions are POST endpoints exposed to the browser
- Environment variables: `NEXT_PUBLIC_*` prefix exposes vars to client bundle — never put secrets there
- Route Handlers: validate auth on every route handler — Next.js does not add auth by default
