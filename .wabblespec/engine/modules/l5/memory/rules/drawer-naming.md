# Drawer Naming Convention

---

## Drawer ID Format

```
{topic-slug}-{YYYYMMDD}
```

Examples:
- `auth-design-20260521`
- `db-schema-decisions-20260521`
- `api-rate-limiting-20260603`

Rules:
- Lowercase only
- Hyphens between words, no underscores
- Topic slug: max 40 characters, derived from topic field
- Date: UTC date of first write
- Total ID length: max 60 characters

---

## Topic Slug Derivation

1. Take topic field value
2. Lowercase
3. Replace spaces and special chars with hyphens
4. Collapse consecutive hyphens to one
5. Strip leading/trailing hyphens
6. Truncate to 40 chars at word boundary

Example: "JWT Authentication Token Expiry Design" → `jwt-authentication-token-expiry-design`

---

## Wing and Room Assignment

Wing = top-level subject area. Room = subtopic within wing.

Suggested wings (not exhaustive — add as needed):
| Wing | Content |
|---|---|
| `architecture` | Structural decisions, patterns, module design |
| `requirements` | Goals, constraints, acceptance criteria |
| `implementation` | Code-level facts, API shapes, algorithms |
| `infrastructure` | Build, deploy, tooling facts |
| `research` | External references, dependency facts |
| `decisions` | ADR-level choices and rationale |

Rooms are free-form within each wing. Use lowercase-hyphen format matching the wing convention.

---

## File Path

```
.wabblespec/state/memory/wings/{wing}/rooms/{room}/drawers/{drawer-id}.json
```

Example:
```
.wabblespec/state/memory/wings/architecture/rooms/auth/drawers/jwt-token-expiry-20260521.json
```

---

## Collision Handling

If a drawer with the same ID already exists on a different date, append `-v2`, `-v3` etc.
This is rare — prefer updating the existing drawer over creating a versioned duplicate unless the evidence fundamentally contradicts the existing content.
