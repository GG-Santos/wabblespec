# Version Policy Reference

**Consumed by:** l7/archive (delta_class → Shift trigger), l7/changelog (BREAKING CHANGE promotion), l7/commit (conventional commits), l7/release (version tag), l4/engineering (CHANGELOG convention gate)  
**Purpose:** Authoritative classification of change severity and the resulting version bump. Ensures consistent application of the BREAKING/ADDITIVE/NON_BREAKING taxonomy used throughout the framework.

---

## Semantic versioning summary

WabbleSpec projects follow [Semantic Versioning 2.0.0](https://semver.org/). Version format: `MAJOR.MINOR.PATCH`.

| Version component | Bumped when | Example |
|---|---|---|
| MAJOR | API or behavior contract broken — consumers must update their code to use the new version | `1.5.3` → `2.0.0` |
| MINOR | New capability added; all existing callers continue to work unchanged | `1.5.3` → `1.6.0` |
| PATCH | Bug fix, security patch, or internal refactor with no interface change | `1.5.3` → `1.5.4` |

**Pre-1.0 rule:** While `MAJOR == 0`, any version may include breaking changes. Stabilize at `1.0.0` when the public API is ready to commit to.

---

## WabbleSpec delta_class taxonomy

The Archive module classifies each task delivery by `delta_class`. This determines whether Shift triggers and which version component bumps.

| delta_class | SemVer component | Archive Shift trigger | Description |
|---|---|---|---|
| `BREAKING` | MAJOR | Yes | Contract change — existing callers or consumers must update |
| `ADDITIVE` | MINOR | Yes | New capability, new file, new field — backwards compatible |
| `NON_BREAKING` | PATCH | No | Fix, refactor, internal change — no interface change |

**Shift trigger:** When Archive records a BREAKING or ADDITIVE delivery, it signals downstream dependencies (via Nexus) to re-evaluate whether their cached project-map and reference slices are still valid. NON_BREAKING deliveries do not trigger Shift — downstream caches remain valid.

---

## What counts as BREAKING

A change is BREAKING if any existing caller, consumer, or integration must change their code or configuration to continue working correctly.

**Always BREAKING:**
- Removing a public function, method, class, or type
- Renaming a public function, method, class, or type without an alias
- Changing a function signature (removing or reordering parameters)
- Changing the type of a parameter or return value in a way that breaks type checks
- Removing a field from a stable JSON/API response schema
- Renaming a field in a stable JSON/API response schema
- Changing the meaning or unit of an existing field (e.g. seconds → milliseconds without rename)
- Removing a CLI flag or command
- Removing an environment variable the runtime depended on
- Changing an HTTP endpoint path or method
- Changing an event name in a pub/sub system
- Removing a database column used by external consumers
- Reducing a permission that existing users relied on

**Breaking in context (check usage before deciding):**
- Adding a required parameter to an existing function (breaking if callers don't update)
- Tightening validation (previously-valid input now rejected)
- Changing default behavior that callers relied on implicitly
- Changing an error code or error message format that callers parsed

---

## What counts as ADDITIVE

A change is ADDITIVE if it adds new capability without breaking existing usage.

**Always ADDITIVE:**
- Adding a new public function, method, or type
- Adding a new optional parameter to an existing function
- Adding a new field to an existing JSON/API response (unless consumers use strict deserialization)
- Adding a new CLI flag or command
- Adding a new environment variable (optional, with default)
- Adding a new API endpoint
- Deprecating (not removing) a public symbol
- Expanding an enum with new allowed values (unless consumers use exhaustive matching)
- New file in `.wabblespec/engine/shared/templates/` or `.wabblespec/engine/shared/references/`
- New module registered in framework.yaml

---

## What counts as NON_BREAKING

A change is NON_BREAKING if it does not change any public interface or observable behavior.

**Always NON_BREAKING:**
- Bug fix that makes behavior match the documented contract (the contract itself doesn't change)
- Performance improvement with no observable behavior change
- Internal refactor (rename of private function, extract helper, reorganize file structure)
- Adding or improving test coverage
- Updating documentation without changing the described behavior
- Adding or updating a comment
- Dependency version bump (patch or minor, no behavior change)
- Fixing a typo in a non-user-facing string
- Updating CI configuration

---

## Conventional commit type → delta_class mapping

| Conventional commit type | Default delta_class | Notes |
|---|---|---|
| `feat` | ADDITIVE | New feature |
| `fix` | NON_BREAKING | Bug fix |
| `refactor` | NON_BREAKING | Internal change |
| `perf` | NON_BREAKING | Performance improvement |
| `docs` | NON_BREAKING | Documentation only |
| `test` | NON_BREAKING | Tests only |
| `chore` | NON_BREAKING | Maintenance |
| `ci` | NON_BREAKING | CI config only |
| `build` | NON_BREAKING | Build system |
| `security` | NON_BREAKING (or BREAKING if patching breaks API) | Security fix |
| Any type with `!` suffix | BREAKING | Overrides default classification |
| Any commit with `BREAKING CHANGE:` footer | BREAKING | Overrides default classification |

**Changelog promotion rule (l7/changelog):** BREAKING CHANGE always appears in the "Changed" section with a "Breaking:" prefix, regardless of type. It is never silently omitted.

---

## Version bump decision tree

```
Is any change in this delivery BREAKING?
  YES → Bump MAJOR. Reset MINOR and PATCH to 0.
        Add BREAKING CHANGE entry to CHANGELOG.
        Archive Shift triggers.
  NO →
    Is any change ADDITIVE (new capability, new file, new API)?
      YES → Bump MINOR. Reset PATCH to 0.
            Archive Shift triggers.
      NO →
        All changes are NON_BREAKING.
        Bump PATCH only.
        No Shift trigger.
```

**Simultaneous BREAKING and ADDITIVE:** If a delivery includes both breaking and additive changes, classify as BREAKING. The MAJOR bump subsumes the MINOR.

**Mixed wave with independent changes:** If a wave includes changes that would individually be BREAKING and others that are NON_BREAKING, the BREAKING classification wins for the whole delivery. Consider splitting into two deliveries if the changes are logically independent.

---

## Version bump in the WabbleSpec seed pipeline

WabbleSpec's own version follows the same rules with a modified MAJOR.MINOR.PATCH interpretation during the `0.x.y` pre-stabilization period:

| Seed pipeline delta_class | WabbleSpec version component bumped |
|---|---|
| BREAKING (structure or schema change) | MINOR (`0.x`) — because MAJOR is reserved for post-stabilization |
| ADDITIVE (new content, new module, new template) | PATCH (`0.x.y`) within the same minor, or MINOR for significant expansions |
| NON_BREAKING (fixes, corrections) | PATCH |

Post `1.0.0` (when the L8 gate is cleared and Instinct activates): standard SemVer rules apply.

---

## Pre-release version conventions

| Pre-release suffix | Meaning | Example |
|---|---|---|
| `-alpha.N` | Early development; API may change drastically | `2.0.0-alpha.1` |
| `-beta.N` | Feature complete; API stabilizing; known issues | `2.0.0-beta.3` |
| `-rc.N` | Release candidate; production-ready pending final review | `2.0.0-rc.1` |

**Rule:** Pre-release versions must not be deployed to production. The Deploy gateway blocks pre-release tags from receiving Attestation.

**Promotion:** `rc.1` → `2.0.0` (no code changes — tag only). If a bug is found during RC, bump to `rc.2` and re-test.

---

## Version tag format (l7/release)

- Format: `v{MAJOR}.{MINOR}.{PATCH}` (e.g. `v1.2.3`)
- Must be an annotated signed tag: `git tag -a -s v1.2.3 -m "Release v1.2.3"`
- Tag message must match the CHANGELOG entry for that version
- No force-push to tags — tags are immutable once pushed
- Pre-release: `v2.0.0-rc.1`

---

## Cross-references

- `modules/l7/archive/SKILL.md` — delta_class field in delivery receipt; Shift trigger logic
- `modules/l7/changelog/SKILL.md` — BREAKING CHANGE promotion; conventional commit parsing
- `modules/l7/commit/SKILL.md` — conventional commit format; mixed-concern split rule
- `modules/l7/release/SKILL.md` — annotated signed tag requirement; production deploy receipt gate
- `.wabblespec/engine/shared/references/dependency-policy.md` — dep version bumps and upgrade workflow
