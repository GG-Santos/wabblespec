# Framework-Specific Architecture: Next.js

> **Applies when:** `next.config.*` detected, or `app/` or `pages/` directory present with Next.js in package.json.
> **Replaces:** Generic web systems-design.md rendering strategy section. The Next.js architectural model (RSC, App Router, server actions) is absent from the generic template.
> **Version authority:** Next.js 14+ (App Router). If using Pages Router (legacy), note it explicitly — patterns differ significantly.

---

## Router Architecture Decision [REQUIRED]

App Router and Pages Router are incompatible within a single Next.js app. Declare which is in use.

| Router | Directory | Default rendering | When to use |
|---|---|---|---|
| **App Router** (preferred) | `app/` | React Server Components | New projects; full-stack data fetching; streaming |
| **Pages Router** (legacy) | `pages/` | Client Components + `getServerSideProps` | Existing projects; stable ecosystem requirement |
| **Mixed** | Both directories | Varies per file | Migration path only — declare end state |

**Declared router:** ___

---

## React Server Components (App Router only)

RSC is the default in App Router. Every component is a Server Component unless explicitly marked `'use client'`.

**Server Components:**
- Run on the server only — zero JavaScript sent to browser
- Can `async/await` directly — no `useEffect` for data fetching
- Cannot use: hooks (`useState`, `useEffect`), browser APIs (`window`, `document`), event handlers
- Cannot use: Context providers (they must be Client Components)

**Client Components** (`'use client'` at top of file):
- Render on server (for initial HTML) AND hydrate on client
- Can use all hooks and browser APIs
- Should be pushed to the leaves of the component tree — keep as small as possible

**Boundary rule:** A Server Component can import a Client Component. A Client Component cannot import a Server Component (it becomes Client automatically).

```tsx
// Server Component (default — no directive needed)
async function ProductList() {
  const products = await db.query('SELECT * FROM products')  // direct DB call OK here
  return <ul>{products.map(p => <ProductCard key={p.id} product={p} />)}</ul>
}

// Client Component — needs interactivity
'use client'
function AddToCartButton({ productId }: { productId: string }) {
  const [loading, setLoading] = useState(false)
  return <button onClick={() => addToCart(productId, setLoading)}>Add to cart</button>
}
```

---

## Data Fetching Patterns (App Router)

**Server Component fetch (preferred for read operations):**
```tsx
// app/products/page.tsx
async function ProductsPage() {
  // Next.js extends fetch with caching options
  const data = await fetch('https://api.example.com/products', {
    next: { revalidate: 60 }  // ISR: revalidate every 60 seconds
  })
  const products = await data.json()
  return <ProductList products={products} />
}
```

**Cache control per fetch:**
| Option | Behavior |
|---|---|
| `{ cache: 'force-cache' }` | Static — cached indefinitely until revalidated |
| `{ next: { revalidate: N } }` | ISR — cached for N seconds |
| `{ cache: 'no-store' }` | Dynamic — never cached, always fresh |
| Default (no option) | Static in production, no-store in dev |

**Route-level rendering mode:**
```tsx
// Force dynamic rendering for entire route
export const dynamic = 'force-dynamic'

// Force static rendering with revalidation
export const revalidate = 60
```

---

## Server Actions (App Router)

Server Actions are async functions that run on the server, callable from Client Components. Use for form submissions and mutations — they replace dedicated API route handlers for simple cases.

```tsx
// actions.ts
'use server'
export async function createProduct(formData: FormData) {
  const name = formData.get('name') as string
  await db.insert({ name })
  revalidatePath('/products')  // invalidate cached page
}

// Client Component using the action
'use client'
import { createProduct } from './actions'

function CreateProductForm() {
  return (
    <form action={createProduct}>
      <input name="name" />
      <button type="submit">Create</button>
    </form>
  )
}
```

**Server Action rules:**
- Must be declared in a file with `'use server'` or inline with `'use server'` directive
- Always run on the server — never exposed as a public API endpoint
- Input is `FormData` for form actions, or arbitrary arguments for programmatic calls
- Always validate and sanitize input server-side — the client cannot be trusted

---

## Route Handlers (API Routes)

For cases requiring a true HTTP endpoint (webhooks, third-party callbacks, streaming responses). Not a replacement for Server Actions in standard data mutation flows.

```typescript
// app/api/products/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const products = await db.query('SELECT * FROM products')
  return NextResponse.json(products)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  // validate body before use
  const product = await db.insert(body)
  return NextResponse.json(product, { status: 201 })
}
```

**Use Route Handlers for:** webhooks, file uploads, streaming, third-party OAuth callbacks, endpoints called by non-browser clients.

**Use Server Actions for:** form submissions, mutations triggered by user interaction in the app.

---

## next.config.js Governance

`next.config.js` controls security-relevant behavior. Changes require review.

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Declare all external image domains — do not use '*'
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.example.com', pathname: '/images/**' }
    ]
  },

  // Security headers — applied via middleware or here
  headers: async () => [
    {
      source: '/(.*)',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' }
      ]
    }
  ],

  // Redirect all http to https (also handle at CDN level)
  // Do not commit secrets here — use process.env only
}
```

**Forbidden in next.config.js:** Secrets, API keys, database connection strings. These belong in `.env.local` (not committed) and CI secrets, not config.

---

## Layout and Metadata Architecture (App Router)

```
app/
  layout.tsx       ← Root layout — wraps every page; providers go here
  page.tsx         ← Home route (/)
  (auth)/          ← Route group — no URL segment, groups related pages
    login/page.tsx
    register/page.tsx
  dashboard/
    layout.tsx     ← Nested layout — wraps only dashboard routes
    page.tsx       ← /dashboard
    settings/page.tsx ← /dashboard/settings
```

**Metadata per route:**
```tsx
// app/products/page.tsx
export const metadata = {
  title: 'Products | My Store',
  description: 'Browse our product catalog',
  openGraph: { title: 'Products', images: ['/og-products.png'] }
}
```

---

## GWT Acceptance Scenarios

```
Given: a component fetches data from the database
When: that component is a Server Component
Then: no fetch is made from the browser
      AND the database query runs on the server
      AND zero JavaScript for the fetch is included in the client bundle

Given: a Server Action handles a form submission
When: the action receives FormData
Then: all fields are validated server-side before any DB write
      AND the action calls revalidatePath or revalidateTag after mutation
      AND the UI reflects the updated state without a full page reload

Given: an external image domain is used
When: next/image renders the image
Then: the domain is listed explicitly in next.config.js remotePatterns
      AND the image is served with Next.js image optimization (size, format, lazy load)

Given: a route should always serve fresh data
When: the route is configured
Then: export const dynamic = 'force-dynamic' is present
      AND the route does not appear in the .next/static build output as a cached page
```
