# React Framework

Loaded by Apply when React is detected without a meta-framework (pure SPA).

## Version baseline

React 18+. Concurrent features (Suspense, transitions) are available.

## Component model

- Functional components with hooks — class components only in legacy codebases
- Hooks rules: only in function components or custom hooks; no conditional hook calls
- Custom hooks: extract stateful logic; prefix with `use`

## State decisions

| State type | Tool |
|---|---|
| Local UI state | `useState` |
| Derived state | Compute during render (no state) |
| Shared across tree | Context + `useReducer` for complex; Zustand/Jotai for large apps |
| Server data | TanStack Query (React Query) or SWR |
| URL/router state | React Router `useSearchParams` / `useParams` |
| Form state | React Hook Form (uncontrolled, performant) or controlled if simple |

Anti-patterns:
- Storing server responses in global state — use a query cache
- `useEffect` for derived state — compute during render
- `useEffect` for event handlers — use the event directly

## Rendering and performance

- `React.memo` — wrap expensive pure components; profile before adding
- `useMemo` — memoize expensive computations; not for simple expressions
- `useCallback` — memoize callbacks passed to memoized children; not everywhere
- Virtualization — `react-window` or `@tanstack/react-virtual` for long lists (> 100 items)
- Code splitting — `React.lazy` + `Suspense` for route-level components

Spec must declare: which components are expected to be render-heavy and why.

## Error handling

- `ErrorBoundary` — required for any async data subtree (catches render errors)
- async errors in event handlers: `try/catch`; not caught by ErrorBoundary
- Query errors: handle via query library error state, not ErrorBoundary

## Patterns spec must declare

- Authentication: how auth state is provided to the tree (Context? Route guard? Layout?)
- Data fetching: which library, where fetches live, loading/error states
- Routing: React Router version, route structure, protected routes
- Forms: form library chosen, validation approach (Zod/Yup), submission pattern

## Testing

- Unit: Vitest + Testing Library (`@testing-library/react`)
- Interaction: Testing Library — render, user-event, assert on accessible queries
- Do not test implementation details (state values, private methods) — test observable behavior
- E2E: Playwright or Cypress for critical user flows
