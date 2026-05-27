# Scope Declaration Rules — Clean

## Scope is required before Clean begins

Clean does not determine its own scope. A scope must be declared before any analysis begins. If no scope is declared, Clean does not activate.

## Valid scope forms

| Form | Example | Coverage |
|---|---|---|
| File path | `src/auth/token.ts` | Single file |
| Directory | `src/auth/` | All files in directory, non-recursive unless specified |
| Directory recursive | `src/auth/**` | All files in directory and subdirectories |
| Pattern | `**/*.test.ts` | All files matching glob pattern |
| Named scope | `deprecated-exports` | Explicit list from Specify flagged items |

## Scope boundaries

All scope targets must resolve within product space. Any target that resolves outside product space is rejected before analysis begins (I11 check).

Clean never self-expands scope. If Clean discovers that the cleanup in a declared scope logically connects to another file, it reports that connection — it does not include the connected file unless it is in the declared scope.

## Implicit scope is not permitted

The following are NOT valid scope declarations:
- "the codebase" — too broad
- "everything that needs cleanup" — undeclared
- "the usual files" — ambiguous

If the user's request implies unbounded scope, prompt for a specific scope declaration before proceeding.

## Scope from Specify deprecated items

When Specify flags deprecated patterns, it produces an explicit list. That list is a valid scope declaration. Clean processes only the items on that list — not adjacent code.
