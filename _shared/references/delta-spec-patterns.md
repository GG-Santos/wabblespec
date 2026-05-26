# Delta Spec Patterns

ADDED/MODIFIED/REMOVED delta spec patterns for spec change documentation. Consumers: shift, specify, archive.

## Purpose

Delta specs document what changed between two versions of a spec artifact. They are written by Shift or by Specify when updating a task card. They allow downstream consumers to understand the change without diffing full documents.

## Three delta types

### ADDED
New requirement, field, constraint, or module added. Nothing removed. Additive only.

```
ADDED: <what was added>
  where: <section or schema field>
  class: ADDITIVE
  consumers_affected: <list of module IDs that may need to know>
```

Example:
```
ADDED: AC-7 — API endpoint must return ETag header on all GET responses
  where: task-card.md §Acceptance Criteria
  class: ADDITIVE
  consumers_affected: [executor, verifier]
```

### MODIFIED
Existing requirement, field, or constraint changed in meaning, value, or structure. May be BREAKING or ADDITIVE depending on the nature of the change.

```
MODIFIED: <what changed>
  where: <section or schema field>
  before: <previous value or statement>
  after: <new value or statement>
  class: BREAKING | ADDITIVE | COSMETIC
  consumers_affected: <list>
```

Example:
```
MODIFIED: P95 latency target
  where: constraints.md §Performance
  before: P95 < 300ms
  after: P95 < 200ms
  class: BREAKING
  consumers_affected: [executor, perf, monitor]
```

### REMOVED
Existing requirement, field, or behavior removed entirely. Always BREAKING unless the item was marked deprecated first.

```
REMOVED: <what was removed>
  where: <section or schema field>
  reason: <why removed>
  class: BREAKING | DEPRECATION (if sunset reached)
  consumers_affected: <list>
  migration: <what consumers should use instead, or null if no replacement>
```

Example:
```
REMOVED: Basic authentication support
  where: api-contract.json §Authentication
  reason: Security policy requires OAuth2 only
  class: BREAKING
  consumers_affected: [executor, apply, platform-api-service]
  migration: Use OAuth2 bearer token (see auth-guide.md)
```

## Marker conventions

`### ADDED`, `### MODIFIED`, and `### REMOVED` are structural markers, not organizational headings. Rules:

1. **Machine-readable contract.** Parsers may scan for these exact strings to extract change sets without parsing prose. Do not rename them or use synonyms.
2. **Omit empty sections.** If a delta has no removals, omit `### REMOVED` entirely. Do not include an empty stub.
3. **Fixed order.** When multiple sections are present: ADDED first, MODIFIED second, REMOVED third.

## Delta spec file format

Written by Shift to `.wabblespec/shift/diff-<timestamp>.md`:

```markdown
# Delta Spec — <artifact-name>

**Version before:** <version or timestamp>
**Version after:** <version or timestamp>
**Overall class:** BREAKING | DEPRECATION | ADDITIVE | COSMETIC

## Changes

### ADDED
<one ADDED block per addition>

### MODIFIED
<one MODIFIED block per modification>

### REMOVED
<one REMOVED block per removal>

## Consumer impact

| Module | Affected | Action required |
|---|---|---|
| executor | Yes | Review AC-7 before next wave |
| verifier | Yes | Add ETag check to verification |
| perf | Yes | Update latency budget |
```

## When to write a delta spec

- Any BREAKING or ADDITIVE change to a task card, schema, or SKILL.md
- When Archive post-hook triggers Shift
- When Specify --patch updates an existing task card
- Not for COSMETIC changes — delta spec is overhead for typo fixes
