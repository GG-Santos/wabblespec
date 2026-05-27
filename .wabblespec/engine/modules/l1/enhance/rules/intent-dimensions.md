# Intent Dimensions

Nine dimensions of user intent. Enhance scores each as Present, Absent, or Derived.

## Dimension 1 — Task (CRITICAL)

What action is the user requesting? Distinguish action verbs: build, fix, refactor, document, analyze, test, deploy, review, migrate, add, remove, optimize.

**Present:** "add authentication" — action (add) and subject (authentication) stated.
**Absent:** "make it better" — no specific action.
**Derived:** "the login is broken" → derived task is "fix the login flow."

## Dimension 2 — Target (CRITICAL)

What specific artifact is the task applied to? Must be nameable: a file path, module name, component, service, endpoint, feature, class, or function.

**Present:** "update `src/auth/login.ts`" or "the authentication module."
**Absent:** "make the code cleaner" — no named artifact.
**Derived:** "the login button doesn't work" → derived target is "the login button component."

## Dimension 3 — Format (CRITICAL)

What form should the output take? Code change? Documentation? Analysis? Test cases? Plan? Explanation?

**Present:** "write tests for..." or "add documentation to..."
**Absent:** "help with authentication" — no output format.
**Derived:** "why is X broken?" → derived format is "analysis / explanation."

## Dimension 4 — Constraints

Limits on the solution. Must-not conditions, deadlines, resource limits, compatibility requirements, or performance targets.

**Present:** "without breaking the existing API" or "in under 200 tokens."
**Absent:** no mention of what the solution must not do or must stay within.
**Derived:** complexity declared High in recipe.json → derives constraint "must preserve existing interface."

## Dimension 5 — Input

What is the user providing as material? Code to refactor? A document to improve? A dataset to analyze?

**Present:** "here is the current implementation..." or "analyze this log file."
**Absent:** no input material mentioned.
**Derived:** recipe.json target = Web + task = "add feature" → derives input is "existing codebase."

## Dimension 6 — Context

Background that explains why this is being done. Useful for prioritization and interpretation but not required for scoping.

**Present:** "we're migrating from v1 to v2 and need to..."
**Absent:** no background context.
**Not derivable:** context is user-specific knowledge; do not fabricate.

## Dimension 7 — Audience

Who will consume the output? Developer, end user, stakeholder, automated system?

**Present:** "write this so a junior dev can understand it."
**Absent:** no mention of audience.
**Derived:** "add user documentation" → derived audience is "end user."

## Dimension 8 — Success criteria

How will the user know the output is good? A test that passes? A metric achieved? Approval from a stakeholder?

**Present:** "it should pass all existing tests without adding new ones."
**Absent:** no success signal given.
**Derived:** task card from Specify (if present) provides criteria.

## Dimension 9 — Examples

Examples of what good output looks like. Highly useful when format is ambiguous.

**Present:** "like the pattern we used in `src/users/`."
**Absent:** no examples.
**Not derivable:** examples are user-specific; do not fabricate.
