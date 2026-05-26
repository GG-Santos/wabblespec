# Framework-Specific Architecture: Vue 3

> **Applies when:** `vue` in package.json + `*.vue` files detected. Covers Vue 3 Composition API. If Nuxt.js is detected (`nuxt.config.*`), also load SSR concerns from nextjs.md (same RSC/hydration concepts apply with Nuxt-specific syntax).
> **Version authority:** Vue 3.x Composition API. Options API is legacy — do not introduce it in new components.

---

## Composition API — Core Pattern

Vue 3's Composition API uses `<script setup>` syntax. Options API (`data()`, `methods:`, `computed:`) is not used in new code.

```vue
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useProductStore } from '@/stores/products'

// Props — typed
const props = defineProps<{
  productId: string
  editable?: boolean
}>()

// Emits — typed
const emit = defineEmits<{
  updated: [product: Product]
  deleted: [id: string]
}>()

// Reactive state
const loading = ref(false)
const error = ref<string | null>(null)

// Store access
const productStore = useProductStore()

// Computed
const product = computed(() => productStore.getById(props.productId))

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    await productStore.fetchProduct(props.productId)
  } catch (e) {
    error.value = 'Failed to load product'
  } finally {
    loading.value = false
  }
})

// Watch
watch(() => props.productId, (newId) => {
  productStore.fetchProduct(newId)
})
</script>
```

**`ref` vs `reactive`:** Use `ref` for primitives and single values. Use `reactive` for objects that are always accessed as a whole — but be aware that destructuring a `reactive` loses reactivity. When in doubt, use `ref`.

---

## State Management — Pinia [REQUIRED]

Vuex is deprecated for Vue 3. All new stores use Pinia.

```typescript
// stores/products.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProductStore = defineStore('products', () => {
  // State
  const products = ref<Product[]>([])
  const loading = ref(false)

  // Getters (computed)
  const getById = computed(() => (id: string) => products.value.find(p => p.id === id))
  const count = computed(() => products.value.length)

  // Actions
  async function fetchProducts() {
    loading.value = true
    try {
      products.value = await api.get('/products')
    } finally {
      loading.value = false
    }
  }

  async function createProduct(data: CreateProductDto) {
    const product = await api.post('/products', data)
    products.value.push(product)
    return product
  }

  return { products, loading, getById, count, fetchProducts, createProduct }
})
```

**Store organization:** One store per domain entity or feature area. Never one global store for all state. Stores access other stores via `useOtherStore()` inside actions — not via import at module level.

---

## Composables — Reusable Logic

Composables replace mixins. A composable is a function prefixed with `use` that returns reactive state and methods.

```typescript
// composables/useProductSearch.ts
export function useProductSearch() {
  const query = ref('')
  const debouncedQuery = useDebounce(query, 300)

  const { data: results, loading, error } = useQuery(
    computed(() => `/products?search=${debouncedQuery.value}`)
  )

  return { query, results, loading, error }
}

// Usage in component:
const { query, results, loading } = useProductSearch()
```

**Composable rules:**
- Always call composables at the top level of `<script setup>` — not inside conditionals or loops
- A composable that uses lifecycle hooks must be called during component setup
- Return only what the consumer needs — not the entire internal state

---

## Template Patterns

```vue
<template>
  <!-- v-if vs v-show: v-if removes from DOM; v-show hides with CSS -->
  <!-- Use v-if for: content that rarely toggles, expensive subtrees -->
  <!-- Use v-show for: content that toggles frequently (menus, tabs) -->

  <!-- Always key v-for items — never use index as key when list reorders -->
  <li v-for="product in products" :key="product.id">
    {{ product.name }}
  </li>

  <!-- Avoid v-if + v-for on the same element -->
  <!-- BAD:  <li v-for="item in items" v-if="item.active"> -->
  <!-- GOOD: filter the array in a computed property first -->

  <!-- Event modifiers -->
  <form @submit.prevent="handleSubmit">  <!-- prevents page reload -->
  <a @click.stop="handleClick">          <!-- stops propagation -->
</template>
```

---

## Nuxt 3 Extensions (if Nuxt detected)

```typescript
// pages/products/[id].vue — file-based routing
// server/api/products/[id].get.ts — server routes (auto-imported)
// composables/useProducts.ts — auto-imported composables (no import needed)

// Server route
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  return await db.products.findById(id)
})

// Nuxt data fetching (SSR-aware)
const { data: product, error } = await useFetch(`/api/products/${id}`)
// useFetch runs on server during SSR; data is sent to client — no second fetch
```

**Nuxt-specific concerns:** `useFetch` and `useAsyncData` prevent duplicate fetches (server + client). Raw `fetch` in a component does not — always use Nuxt's composables for data that is available at render time.

---

## GWT Acceptance Scenarios

```
Given: a Pinia store action modifies state
When: any component using that state re-renders
Then: the component receives the updated state reactively
      AND no component calls the action directly on the store instance — it calls the action function

Given: a composable uses onMounted
When: it is called inside <script setup>
Then: the lifecycle hook is registered correctly for the host component
      AND the composable is not called conditionally or inside a loop

Given: a v-for renders a list that can reorder
When: the list is observed in Vue DevTools
Then: each item has a stable, unique :key (not array index)
      AND items animate correctly when the list reorders (no flicker)
```
