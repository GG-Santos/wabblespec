# Vue Framework

Loaded by Apply when Vue is detected (vue in package.json or .vue files).

## Version baseline

Vue 3 + Composition API. If Options API patterns detected in existing code, note it and apply migration guidance.

## Composition API patterns

```typescript
// Preferred: <script setup> single-file component
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)

onMounted(() => {
  // side effects here, not in setup body
})
</script>
```

- `ref()` for primitives; `reactive()` for objects (but ref is often simpler)
- `computed()` for derived values — cached, auto-tracked
- `watch()` for side effects on data change; `watchEffect()` for immediate + auto-tracked
- Composables: extract reusable logic into `use*` functions

## State management

| Scope | Tool |
|---|---|
| Component-local | `ref`, `reactive` |
| Cross-component | Pinia (Vue 3 standard) |
| Server data | VueQuery (TanStack Query for Vue) or Pinia action with loading state |
| Route state | Vue Router `useRoute`, `useRouter` |

Vuex is Vue 2 era — use Pinia for new code.

## Vite build system

Vue 3 projects default to Vite. Spec must declare:
- `vite.config.ts` configured for Vue plugin
- Environment variables: `VITE_*` prefix exposes to client — no secrets there
- Alias paths declared (`@` → `src/`)
- Build targets: `esbuild` targets for browser support

## Vue Router

Spec must declare full route structure including:
- Named routes
- Route guards (`beforeEach` for auth)
- Lazy-loaded routes (`() => import('./views/Page.vue')`)
- Nested routes

## Template security

- `v-html`: equivalent to React's `dangerouslySetInnerHTML` — sanitize before use; declare uses in spec
- Interpolation `{{ }}` is auto-escaped — safe by default
- `v-bind` / `:attr`: safe for attribute values — no injection vector for standard attributes

## Testing

- Vitest + `@vue/test-utils`
- Mount components with `mount()` or `shallowMount()`
- Test through the component's public interface (props, emits, slots), not implementation
- E2E: Playwright (Cypress also works)
