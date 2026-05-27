# Framework-Specific Architecture: Svelte / SvelteKit

> **Applies when:** `svelte` in package.json + `*.svelte` files detected.
> Covers SvelteKit (full-stack) and Svelte (SPA via Vite). Declare which in technical-spec.md.
> **Version authority:** Svelte 4/5 + SvelteKit 2.x. Svelte 5 introduces Runes — declare which reactivity model is in use.

---

## Reactivity Model Declaration [REQUIRED]

Svelte 4 and Svelte 5 have different reactivity syntax. Mixing them in one project is supported but confusing — declare which is primary.

**Svelte 4 (reactive declarations):**
```svelte
<script lang="ts">
  let count = 0                          // reactive by default in component scope
  $: doubled = count * 2                 // reactive statement — runs when count changes
  $: if (count > 10) { console.log() }  // reactive block

  function increment() { count++ }
</script>
```

**Svelte 5 (Runes — explicit reactivity):**
```svelte
<script lang="ts">
  let count = $state(0)              // $state rune — explicit reactive state
  let doubled = $derived(count * 2)  // $derived rune — replaces $:
  let { name, optional = 'default' } = $props()  // $props rune — replaces export let

  $effect(() => {                    // $effect rune — replaces reactive blocks + onMount/onDestroy
    console.log(`count is ${count}`)
    return () => { /* cleanup */ }   // cleanup on unmount or re-run
  })
</script>
```

**Declared reactivity model:** ___

---

## SvelteKit File System Routing

```
src/routes/
  +layout.svelte          ← Root layout — wraps all routes
  +layout.ts              ← Root layout load function
  +page.svelte            ← / route
  +page.ts                ← / load function (runs on server + client)
  +error.svelte           ← Error page
  products/
    +page.svelte          ← /products route
    +page.server.ts       ← Server-only load (never sent to client) — use for DB calls, secrets
    [id]/
      +page.svelte        ← /products/[id] dynamic route
      +page.server.ts
  api/
    products/
      +server.ts          ← API endpoint — GET/POST handlers
```

**`+page.ts` vs `+page.server.ts`:**
- `+page.ts` — load function runs on server during SSR, re-runs on client during navigation. No secrets. No direct DB calls.
- `+page.server.ts` — load function runs server-only. Can access secrets, DB, env vars. Data is serialized to JSON and sent to client.

---

## Load Functions and Form Actions

**Load function:**
```typescript
// +page.server.ts
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ params, locals, depends }) => {
  depends('app:products')  // declare dependency for invalidation
  const product = await db.products.findById(params.id)
  if (!product) throw error(404, 'Product not found')
  return { product }  // typed — available as `data.product` in +page.svelte
}
```

**Form actions (no API route needed for mutations):**
```typescript
// +page.server.ts
import type { Actions } from './$types'

export const actions: Actions = {
  create: async ({ request, locals }) => {
    const data = await request.formData()
    const name = data.get('name')?.toString()
    if (!name) return fail(400, { name, missing: true })
    await db.products.create({ name })
    throw redirect(303, '/products')
  },

  delete: async ({ params }) => {
    await db.products.delete(params.id)
    return { success: true }
  }
}
```

```svelte
<!-- +page.svelte — use enhance for progressive enhancement -->
<script lang="ts">
  import { enhance } from '$app/forms'
  export let data  // typed from load function
  export let form  // typed from action return
</script>

<form method="POST" action="?/create" use:enhance>
  <input name="name" value={form?.name ?? ''} />
  {#if form?.missing}<span>Name is required</span>{/if}
  <button>Create</button>
</form>
```

---

## Stores (Svelte 4) / $state (Svelte 5)

**Svelte 4 stores — for cross-component state:**
```typescript
// stores/cart.ts
import { writable, derived } from 'svelte/store'

export const cartItems = writable<CartItem[]>([])
export const cartTotal = derived(cartItems, $items =>
  $items.reduce((sum, item) => sum + item.price * item.quantity, 0)
)
export function addToCart(item: CartItem) {
  cartItems.update(items => [...items, item])
}
```

```svelte
<script lang="ts">
  import { cartItems, cartTotal, addToCart } from '$lib/stores/cart'
  // $cartItems — auto-subscribe/unsubscribe syntax
</script>

<p>Items: {$cartItems.length} | Total: ${$cartTotal.toFixed(2)}</p>
```

**Svelte 5 — context + $state for shared state:**
```svelte
<!-- Parent.svelte -->
<script lang="ts">
  import { setContext } from 'svelte'
  const cart = $state({ items: [], total: 0 })
  setContext('cart', cart)
</script>

<!-- Child.svelte -->
<script lang="ts">
  import { getContext } from 'svelte'
  const cart = getContext('cart')
</script>
<p>{cart.items.length} items</p>
```

---

## GWT Acceptance Scenarios

```
Given: a +page.server.ts load function accesses a database
When: the page is navigated to
Then: the DB call runs on the server only
      AND no DB connection string or query appears in client-side JavaScript
      AND the data is available as data.property in the page component

Given: a form is submitted via use:enhance
When: JavaScript is disabled in the browser
Then: the form submits via standard HTML POST
      AND the server action processes it correctly
      AND the response is the redirect or the form with errors (no JavaScript required)

Given: a Svelte 4 store is subscribed to in a component
When: the component is destroyed
Then: the store subscription is automatically cleaned up ($ prefix syntax handles this)
      AND no memory leak occurs from orphaned subscriptions
```
