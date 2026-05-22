---
name: specify
description: Produces a one-page task card with goal, non-goals, assumptions, and GWT acceptance criteria. The spec every downstream module executes against.
---

# Specify

You write the single source of truth. Everything downstream — Decompose, Executor, Verifier — runs against what you produce here. If the task card is vague, the execution will be vague. Specificity is not a style choice; it is an engineering requirement (I1, I12).

## What this skill does

Reads the locked scope and user intent. Produces a one-page task card with: goal (one sentence), non-goals (from scope.md), assumptions (from scope.md), and acceptance criteria in GWT format. Validates criteria quality. Writes a receipt.

## When to use / when not to use

**Use when:**
- ScopeFrame has locked scope.md (receipt exists)
- Explicit `/specify` command
- Scope change triggers a re-specify

**Do not use when:**
- scope.md is not locked (ScopeFrame must run first — I10 chain)
- Task card already exists and scope has not changed

## Inputs

- `.wabblespec/scope.md` (locked scope)
- `.wabblespec/recipe.json` (target, complexity)
- User task description

## How to do it

### Step 1 — Write the goal statement

One sentence. States what will be true when this task is complete. Must be falsifiable — you can test whether it is true or false.

Bad: "Improve the authentication system."
Good: "Users can authenticate via OAuth 2.0 with Google, replacing the current username/password form."

### Step 2 — Transfer non-goals and assumptions

Copy directly from scope.md. Do not add new ones here — changes go through ScopeFrame. If you notice a gap, surface it and loop back.

### Step 3 — Write acceptance criteria in GWT format

GWT = Given / When / Then. Each criterion is one testable scenario.

```
Given <precondition>
When <action>
Then <expected outcome>
```

Rules for GWT criteria:
- Each criterion is independent — tests exactly one thing
- "Then" is observable: can be confirmed by reading output, running a test, or checking a state change
- Cover the happy path first, then critical failure paths
- Low complexity: 2–4 criteria. Medium: 4–8. High: 8–12.
- No criterion that cannot be verified (I4 — every output must pass a gate)

**GWT vs EARS:** GWT is the default for Phase 2 task cards. EARS (Easy Approach to Requirements Syntax) is appropriate for standing system rules rather than scenarios, e.g. "The CLI shall always exit with code 0 on success." Use EARS when GWT produces an awkward scenario framing. When in doubt, use GWT.

### Step 3.5 — Classify the change delta

Before writing the task card or receipt, declare the change class. This field is required on the receipt and must match the `change_class` field in the task card.

| Class | When to use |
|---|---|
| `BREAKING` | Removes or incompatibly changes existing behavior. Activates Migrate. |
| `ADDITIVE` | New capability alongside existing behavior. No migration required. |
| `COSMETIC` | Refactor, rename, or documentation only. No behavior change. |

When delta_class is `BREAKING`, also write:
- `change_summary`: one line per changed item, prefixed `BREAKING: ...`
- `affected_specs`: paths to spec artifacts or capability areas being changed (used by Migrate and Provenance cascade)

When in doubt between ADDITIVE and BREAKING: if any consumer calling the existing interface must change their code, it is BREAKING.

### Step 4 — Validate before writing

Check all of the following. Fix any that fail before writing the task card:
- [ ] Goal is one sentence and falsifiable
- [ ] Every "Then" clause is observable and testable
- [ ] No criterion duplicates another
- [ ] At least one failure-path criterion for Medium/High complexity
- [ ] Non-goals are explicitly stated (at least one)
- [ ] No open questions remain (surface and resolve before proceeding)
- [ ] `change_class` declared (BREAKING/ADDITIVE/COSMETIC)
- [ ] If BREAKING: `change_summary` and `affected_specs` populated
- [ ] Normative criteria use SHALL or MUST, not "should" or "may"

### Step 5 — Write task card and receipt

Write task card to `.wabblespec/plans/task-card.md`. Receipt to `.wabblespec/receipts/specify-receipt.json`. Report goal statement and criteria count to user, ask for confirmation before locking.

## Output contract

**task-card.md** (`.wabblespec/plans/task-card.md`):

```markdown
# Task Card

**goal:** <one sentence — falsifiable>
**target:** <from recipe.json>
**complexity:** Low|Medium|High
**locked_at:** ISO-8601-timestamp

## Non-Goals

- <from scope.md — verbatim>

## Assumptions

- <from scope.md — verbatim>

## Acceptance Criteria

### Criterion 1: <short name>

Given <precondition>
When <action>
Then <expected outcome>

### Criterion 2: <short name>

Given <precondition>
When <action>
Then <expected outcome>
```

**receipt** (`.wabblespec/receipts/specify-receipt.json`): base receipt schema. Extension fields per `_shared/schemas/specify-receipt.extension.schema.json`:
- `criteria_count` (integer — minimum 1)
- `gwt_violations` (integer — target 0; non-zero = PARTIAL)
- `open_questions_resolved` (boolean — must be true for PASS)
- `delta_class` (string — `BREAKING`|`ADDITIVE`|`COSMETIC` — required)
- `change_summary` (array of strings — required when BREAKING)
- `affected_specs` (array of strings — required when BREAKING)

task-card.md must include a `change_class:` field matching `delta_class`. Schema contract: `_shared/schemas/task-card.schema.json`.

## A note on common failure modes

1. **Untestable "Then" clauses.** "Then the user experience is improved" cannot be verified. Rewrite: "Then the page loads in under 1 second on a 3G connection." Every Then must be checkable.

2. **Missing failure paths.** Happy-path-only criteria are incomplete. For every key action, ask: what should happen when it fails? Add at least one failure-path criterion for Medium/High tasks.

3. **Goal inflation.** A goal with "and" in it is two goals. Split it. Each task card covers one deliverable.
