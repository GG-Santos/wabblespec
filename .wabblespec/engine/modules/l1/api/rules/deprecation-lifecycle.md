# Deprecation Lifecycle

Deprecation is a structured process, not an annotation. Deprecating without a plan is the same as a BREAKING change without warning.

## Lifecycle stages

### Stage 1 — Notice

Deprecation is announced. The deprecated endpoint/field/version continues to function without change.

**Requirements:**
- Deprecation notice added to API documentation
- Response header added: `Deprecation: true` and `Sunset: <date>`
- Migration path documented (what to use instead)
- Record `deprecations_added: N` in receipt

**Duration:** Minimum 1 major version cycle or 90 days, whichever is longer. For widely-used public APIs: minimum 180 days.

---

### Stage 2 — Warning

The deprecated item still functions but active warnings are surfaced to consumers.

**Requirements:**
- Log warning on each use of deprecated endpoint/field
- Deprecation warning in API response body (optional field, not breaking)
- Migration guide actively linked from documentation

---

### Stage 3 — Sunset

The deprecated item is removed. This is a BREAKING change and requires a major version bump.

**Requirements:**
- Sunset date was declared in Stage 1 and that date has passed (or explicit user override)
- Migration path has been live for the full notice period
- `deprecations_sunset: N` recorded in receipt
- Changelog entry with BREAKING label

---

## Deprecation without replacement

If a feature is removed without replacement (not moved — just removed): this is BREAKING from Stage 1. No deprecation period shortens this obligation. Document explicitly why no replacement exists.

## Receipt tracking

- `deprecations_added`: count of items entering Stage 1 this session
- `deprecations_sunset`: count of items reaching Stage 3 (removed) this session
- `breaking_changes`: count of changes requiring a major version bump
