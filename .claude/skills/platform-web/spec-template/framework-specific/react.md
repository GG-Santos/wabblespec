# Framework-Specific Architecture: React (SPA)

> **Applies when:** `react` in package.json + no Next.js/Remix/other framework detected. Pure client-side SPA.
> **Replaces:** Generic rendering strategy section. React SPA has no SSR, no server components, no build-time generation — all concerns are client-side.

---

## SPA Architecture Model

React SPA renders entirely in the browser. The server delivers a minimal HTML shell; React hydrates and manages everything from there.

```
index.html (shell — delivered from CDN or server)
  └── <div id="root" />
        └── React tree (mounted by main.tsx)
              ├── Providers (query client, theme, auth context)
              ├── Router (react-router)
              │     ├── Route /        → HomePage
              │     ├── Route /dashboard → DashboardPage
              │     └── Route /profile  → ProfilePage
              └── ErrorBoundary (catches render errors)
```

**Implications:** Every page requires a JS download before rendering. LCP is gated on JS parse + execute. Code splitting is mandatory — not optional.

---

## State Management Declaration [REQUIRED]

Declare one primary state management pattern before implementation begins. Mixed patterns create unpredictable update behavior.

| Pattern | Best for | Avoid when |
|---|---|---|
| **Zustand** | Simple global state, low boilerplate | Complex state machines |
| **Redux Toolkit** | Complex state with many slices, devtools needed | Small apps (overhead not justified) |
| **React Query / TanStack Query** | Server state (API data, caching, invalidation) | Local-only UI state |
| **Context API** | Theming, auth state — rarely re-renders | Frequently updating state (causes full tree re-render) |
| **Local `useState`** | Component-local state — always preferred first | When state must be shared with non-parent components |

**Declared pattern:** ___

**Rule:** Server state (API data) and client state (UI interactions) are different. Declare them separately. React Query for server state + Zustand for client state is a common valid pairing — but declare it explicitly.

---

## Client-Side Routing (react-router v6+)

```tsx
// main.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,   // catches route errors
    children: [
      { index: true, element: <HomePage /> },
      {
        path: 'dashboard',
        element: <ProtectedRoute><DashboardPage /></ProtectedRoute>,
        loader: dashboardLoader,   // data loading before render
      },
      { path: '*', element: <NotFoundPage /> }
    ]
  }
])
```

**Route-level code splitting:**
```tsx
const DashboardPage = lazy(() => import('./pages/DashboardPage'))

// In route definition:
{ path: 'dashboard', element: <Suspense fallback={<Skeleton />}><DashboardPage /></Suspense> }
```

Every route that is not part of the critical path (home, login) must be lazy-loaded. No exceptions — a monolithic bundle is a Gate 4 (bundle budget) failure.

---

## Data Fetching with TanStack Query

```tsx
// Declare query keys as constants — prevents typos and enables cache invalidation
const QUERY_KEYS = {
  products: ['products'] as const,
  product: (id: string) => ['products', id] as const,
  userProfile: ['user', 'profile'] as const,
}

// Query hook
function useProducts() {
  return useQuery({
    queryKey: QUERY_KEYS.products,
    queryFn: () => apiClient.get('/products').then(r => r.data),
    staleTime: 5 * 60 * 1000,   // consider fresh for 5 minutes
  })
}

// Mutation hook
function useCreateProduct() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateProductDto) => apiClient.post('/products', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.products })
    }
  })
}
```

**Never `useEffect` for data fetching.** `useEffect` for fetching creates race conditions, no deduplication, no caching, and no loading/error state management. React Query replaces all of these patterns.

---

## Component Patterns

**Compound components** (for complex UI that shares state):
```tsx
// Instead of <Table data={data} columns={columns} onSort={...} onFilter={...} />
// Use compound pattern when the consumer needs layout control:
<Table>
  <Table.Header>
    <Table.Column key="name" sortable>Name</Table.Column>
  </Table.Header>
  <Table.Body data={data} />
  <Table.Pagination />
</Table>
```

**Render prop / children-as-function** — avoid unless necessary. Prefer composition or custom hooks.

**Custom hooks for reusable logic:**
```tsx
// Logic extracted from component — testable independently
function useProductSearch(initialQuery = '') {
  const [query, setQuery] = useState(initialQuery)
  const debouncedQuery = useDebounce(query, 300)
  const results = useProducts({ search: debouncedQuery })
  return { query, setQuery, results }
}
```

---

## Error Boundaries

Every async boundary (lazy-loaded routes, data-fetching regions) needs an Error Boundary. Unhandled render errors without a boundary crash the entire app.

```tsx
// Use react-error-boundary library or write:
class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    reportError(error, info)  // send to error tracking service
  }

  render() {
    if (this.state.hasError) return <this.props.fallback error={this.state.error} />
    return this.props.children
  }
}

// Placement:
// - Route level: catches route component failures
// - Section level: allows rest of page to render on partial failure
// - Never: wrapping every individual component (too granular, noisy)
```

---

## Performance Patterns

**Memoization — when to use, when not to:**
```tsx
// useMemo: only for expensive calculations (not for objects that aren't passed as props)
const sortedData = useMemo(() => data.sort(compareFn), [data])

// useCallback: only when the function is a dep of another hook or child component prop
const handleSubmit = useCallback((e: FormEvent) => { ... }, [dependency])

// memo(): only when component re-renders measurably impact performance
const ProductCard = memo(function ProductCard({ product }: Props) { ... })
```

**Premature memoization is a maintenance cost, not a performance gain.** Profile first. Only add `memo`/`useMemo`/`useCallback` when you have measured a performance problem.

---

## GWT Acceptance Scenarios

```
Given: a route beyond the critical path is visited for the first time
When: the browser network tab is observed during navigation
Then: only the JS chunk for that route is fetched (not the full bundle)
      AND a loading state (Suspense fallback) is shown while the chunk downloads

Given: an API request fails inside a useQuery call
When: the component using that query renders
Then: the error state is displayed (not a blank component or console error)
      AND React Query retries the request up to the configured retry count
      AND the error is not swallowed silently

Given: a form is submitted
When: the mutation is in-flight
Then: the submit button is disabled (no double-submit)
      AND a loading indicator is visible
      AND on success: the relevant query cache is invalidated and UI updates
      AND on failure: the error is displayed inline, not as an alert()
```
