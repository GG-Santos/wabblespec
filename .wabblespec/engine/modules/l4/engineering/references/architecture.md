# Architecture Engineering Standards

Circular dependency prevention, API versioning, and backwards compatibility requirements.

## Circular dependency prevention

Circular dependencies produce: unpredictable initialization order, difficult testing, tight coupling, and module resolution errors.

### Layer rules

```
Allowed dependency direction: higher layer → lower layer only

L8 → L7 → L6 → L5 → L4 → L3 → L2 → L1 → L0
                               ↑
                     No upward dependencies allowed
```

Applied to application code:
```
UI components → business logic → data access → external integrations
                                             ↑
                              No circular imports allowed
```

### Detection

```bash
# JavaScript/TypeScript: madge
npx madge --circular src/

# Python: pydeps
pydeps --max-bacon 2 mypackage

# Go: go list (circular imports are compile errors — Go catches at build time)
```

Add circular dependency detection to CI. Fail on any new circular dependency.

### Remediation patterns

**Dependency inversion**: A depends on B, B depends on A → extract interface I, A implements I, B depends on I.

```typescript
// Before: circular
// user.ts imports from notification.ts
// notification.ts imports from user.ts

// After: inversion
// user.ts defines NotificationTarget interface
// notification.ts depends on NotificationTarget (not user.ts)
// user.ts implements NotificationTarget
```

**Event-based decoupling**: A calls B directly → A emits event, B subscribes.

**Shared module**: common code extracted to a shared module that neither A nor B imports.

## API versioning

### URL versioning (recommended for REST)

```
/api/v1/users    ← stable
/api/v2/users    ← new version with breaking changes
```

Versioning rules:
- Increment major version on any breaking change
- Old versions kept alive for deprecation period (declare in spec; minimum 6 months)
- Sunset header on deprecated versions: `Sunset: Sat, 31 Dec 2026 00:00:00 GMT`
- Version endpoint: `GET /api/version` returns current version and supported versions list

### Header versioning (alternative)

```
API-Version: 2026-05-24
```

Date-based header versioning used by Stripe, GitHub. Good for: APIs where URL must stay stable. Requires: explicit version in every request.

### Content negotiation (alternative)

```
Accept: application/vnd.myapi.v2+json
```

Rarely used for internal APIs. Used for: public APIs with complex content type requirements.

## Backwards compatibility

### Consumer-driven contract testing

When multiple services consume an API, use contract tests to verify backwards compatibility:

```
Provider (API) tests verify: can serve all contracts
Consumer (client) tests verify: can handle provider's responses
```

Pact or similar: each consumer defines what it expects from the provider. Provider CI runs all consumer contracts on every build.

### Tolerant reader pattern

Consumers must not break when providers add new fields:
- Ignore unknown fields (do not reject responses with extra fields)
- Use default values for missing optional fields
- Parse only what you need

```typescript
// Tolerant reader: ignores new fields
const { id, name, email } = response.user  // ignores any new fields from provider
```

### Graceful degradation

When a dependency changes its API:
- Detect the change (version header, schema validation)
- Fall back to compatible behavior if possible
- Fail informatively if fallback is not possible (not silently return wrong data)

## Module cohesion and coupling

### High cohesion rule

A module should have one reason to change. If a module changes for multiple unrelated reasons, split it.

Signs of low cohesion:
- Module name contains "and" or "utils"
- Module imports from more than 3 other modules
- More than one team changes the module regularly

### Low coupling rule

Modules should depend on interfaces, not implementations. The fewer the dependencies, the easier to test and change.

Coupling measurements:
- **Afferent coupling (Ca)**: how many modules depend on this module
- **Efferent coupling (Ce)**: how many modules this module depends on
- **Instability (I)**: Ce / (Ca + Ce) → 0 = stable (many dependents, few dependencies); 1 = unstable

Stable modules (shared utilities, interfaces) should have low instability. Business logic modules can have higher instability.

## Modular monolith vs microservices

Spec must declare deployment model and justify it:

| Model | When | Trade-offs |
|---|---|---|
| Monolith | Team < 10; early stage; simple domain | Simple to deploy, test, debug; hard to scale independently |
| Modular monolith | Medium complexity; single team | Strong module boundaries; shared deployment; no network overhead |
| Microservices | Large teams; independent scaling needs; complex domain | Independent deploy; network complexity; distributed system problems |

Do not distribute a system that is not already a well-structured monolith. Distribution amplifies complexity — it does not fix architectural problems.
