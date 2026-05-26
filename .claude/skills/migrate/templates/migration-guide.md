# Migration Guide — <breaking-change-id>

> Consumer-facing document. Written by Migrate, published by Document.

**Version affected:** <version where BREAKING change ships>
**Migration deadline:** <Phase 2 target wave or release — when deprecated interface is removed>

## What changed and why

<Plain description of the breaking change. Explain the before state and the after state. State why the change was necessary.>

## Who is affected

<Describe which consumers are affected. Be specific: "Any caller of `authenticate(token)` that passes a string token directly.">

## How to migrate

### Before

```
<code example showing the old interface or usage>
```

### After

```
<code example showing the new interface or usage>
```

### Step-by-step

1. <Concrete action — specific enough to follow without context>
2. <Concrete action>
3. Verify: <how to confirm migration is complete>

## Automated migration

<!-- If a migration script was generated -->
Run `scripts/migrate/<change-id>.sh` from the project root. Review the diff before committing.

<!-- If no script -->
No automated migration script available. Follow the step-by-step guide above.

## Timeline

| Milestone | Target |
|---|---|
| Phase 1 (deprecated interface available) | <wave or version> |
| Phase 2 (deprecated interface removed) | <wave or version> |

## Help

<Where consumers can ask questions or report issues with the migration>
