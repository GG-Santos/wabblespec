# Svelte / SvelteKit Framework

Loaded by Apply when Svelte is detected (svelte in package.json or .svelte files).

## Version baseline

Svelte 5 + SvelteKit 2. If Svelte 4 runes not detected, note it.

## Svelte 5 runes model

```svelte
<script>
  let count = $state(0)                    // reactive state
  let doubled = $derived(count * 2)        // derived (replaces $: reactive)
  
  $effect(() => {                          // side effects
    console.log('count changed:', count)
  })
</script>
```

- `$state()` — reactive primitive (replaces `let x`)
- `$derived()` — reactive computation (replaces `$: computed`)
- `$effect()` — side effect (replaces `afterUpdate`/`onMount` for effects)
- Runes work in `.svelte` and `.svelte.ts` files

## SvelteKit routing

SvelteKit uses file-based routing:
```
src/routes/
  +layout.svelte        — root layout
  +page.svelte          — / (home)
  login/
    +page.svelte        — /login
  api/
    data/+server.ts     — /api/data (REST endpoint)
  [id]/
    +page.svelte        — /[id] (dynamic)
    +page.ts            — load function for /[id]
```

Spec must declare full route structure including load functions and server routes.

## Load functions

```typescript
// +page.ts — runs on server + client
export async function load({ params, fetch }) {
  const data = await fetch(`/api/data/${params.id}`)
  return { item: await data.json() }
}

// +page.server.ts — runs on server only
export async function load({ locals }) {
  // access locals (auth session, db) here
}
```

Spec must declare: which routes use server vs universal load functions and why.

## Form actions

SvelteKit form actions handle mutations without client JS:
```typescript
// +page.server.ts
export const actions = {
  create: async ({ request, locals }) => {
    const data = await request.formData()
    // validate, mutate
  }
}
```

Spec must declare: which mutations use form actions vs API endpoints.

## State management

| Scope | Tool |
|---|---|
| Component-local | `$state()` |
| Cross-component | Svelte stores (`writable`, `readable`) or `$state` in module |
| URL state | SvelteKit `page` store, `goto()` |
| Server data | load functions + SvelteKit invalidation |

## Security

- CSRF: SvelteKit adds CSRF protection for form actions by default — do not disable
- `{@html ...}`: equivalent to innerHTML — sanitize before use; declare in spec
- Environment variables: `PUBLIC_*` prefix exposes to client — no secrets there
