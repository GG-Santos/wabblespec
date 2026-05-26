# Audit Dimensions

Organize audits the file structure against five dimensions. Each dimension produces a count that appears in the receipt.

## Dimension 1 — Orphans

A file is an orphan when:
- No other file references it (no imports, no `$ref`, no wikilinks, no SKILL.md pointer)
- It is not a declared output artifact of any module in framework.yaml
- It is not a well-known root file (CLAUDE.md, README.md, CHANGELOG.md, VERSION, framework.yaml)

**Action:** List orphan paths. Do not auto-delete. Require human confirmation before removal.

---

## Dimension 2 — Naming violations

A file has a naming violation when it does not follow the established naming convention for its location:

| Location | Convention |
|---|---|
| Module `schemas/` | `<module>-receipt.schema.json`, `<artifact>.schema.json` |
| Module `rules/` | `<rule-topic>.md` (kebab-case, descriptive) |
| Module `agents/` | `<agent-role>.md` (kebab-case) |
| Module `scripts/` | `<verb>-<noun>.py` or `<verb>-<noun>.sh` |
| `_shared/schemas/` | `<artifact>.schema.json` or `<artifact>.base.schema.json` |
| `_shared/references/` | `<topic>.md` |
| `_shared/infrastructure/` | `<topic>.md` |

Flag PascalCase, snake_case, or arbitrary names in these locations.

---

## Dimension 3 — Depth violations

A file is at excessive depth when it is more than 4 directory levels below the project root (not counting the project root itself).

Modules should not create subdirectories within their established structure (`rules/`, `schemas/`, `agents/`, `scripts/`) without declaration in framework.yaml.

---

## Dimension 4 — Duplicates

A file is a duplicate when:
- Its content hash matches another file in the same or nearby location
- Two schema files declare the same `title` field

Duplicates in schemas are a validation hazard. Duplicates in rules create competing authority.

---

## Dimension 5 — Declared vs actual structure

Compare the module directory structure to what framework.yaml declares. Files that exist but are not declared as outputs in framework.yaml are structural orphans (different from content orphans — they may be referenced but not declared).

Record count of undeclared files per module.
