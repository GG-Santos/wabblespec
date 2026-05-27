# Conventional Commits

Type selection rules, format enforcement, and edge cases.

## Type definitions

| Type | Use when | User-facing? |
|---|---|---|
| `feat` | New capability or behavior visible to a user or API consumer | Yes |
| `fix` | Corrects incorrect behavior; resolves a bug | Yes |
| `perf` | Performance improvement (speed, memory, efficiency) | Yes |
| `refactor` | Internal restructuring; no behavior change from consumer perspective | No |
| `docs` | Documentation only changes | Conditional |
| `test` | Adding or correcting tests only | No |
| `chore` | Maintenance, dependency updates, config changes | No |
| `style` | Formatting, whitespace, punctuation — no logic changes | No |
| `ci` | CI/CD configuration changes | No |
| `build` | Build system changes | No |
| `security` | Security-specific fixes or improvements | Yes |

## Format

```
type(scope)!: subject

body

footer
```

**Type:** lowercase. One of the approved types above.

**Scope:** optional; lowercase; identifies the area of change. Use module name, feature area, or component. Examples: `auth`, `api`, `dashboard`, `memory`, `schemas`.

**!:** breaking change indicator. Append to type when the change breaks a previously stable API or behavior for a consumer.

**Subject:** 
- Imperative mood ("add", "fix", "remove" — not "added", "fixes", "removes")
- Lowercase first letter
- No period at end
- Total line (type + scope + subject) ≤ 72 characters

**Body:** optional; explains WHY, not what. Wrap at 72 chars. Separate from subject with blank line.

**Footer:** optional; `BREAKING CHANGE: {description}` and issue references.

## Type selection disambiguation

**feat vs refactor:** If a user or API consumer can observe the change → `feat` or `fix`. If only the internal structure changed with identical external behavior → `refactor`.

**fix vs refactor:** A bug was causing incorrect behavior → `fix`. The code was correct but messy → `refactor`.

**feat vs perf:** New capability → `feat`. Same capability, measurably faster → `perf`.

**chore vs build:** Dependency version bump, lock file update → `chore`. Build tool configuration, Makefile, webpack config → `build`.

**docs (include vs exclude):** User-facing documentation (README, API docs, guides) → `docs`. Internal architecture docs, comments, decision records → `chore` or omit.

## Breaking change rules

A change is breaking when an existing consumer (user, API caller, another module) must change their behavior or code to continue working after this commit.

Examples:
- Removing a public API endpoint → breaking
- Renaming a required parameter → breaking
- Changing the output format of a schema field → breaking
- Adding an optional parameter → not breaking (additive)
- Fixing a bug that consumers were depending on (bug-as-feature) → breaking

Breaking changes require `!` in the type AND a `BREAKING CHANGE:` footer describing what breaks and what consumers must do.

## Subject line checklist

Before finalizing:
- [ ] Imperative mood
- [ ] Lowercase after type prefix
- [ ] No period
- [ ] Total line ≤ 72 characters
- [ ] Describes the effect (what it does), not the mechanism (how it does it)
