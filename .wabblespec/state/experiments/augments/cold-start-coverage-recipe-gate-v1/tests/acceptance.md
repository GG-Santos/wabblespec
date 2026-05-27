# Recipe (Augment) — Acceptance Criteria

Includes all original acceptance criteria plus new criteria for Step 2d cold-start verification.

---

## PASS: cold-start files present for all selected modules

Given all modules selected in Step 2b have `rules/cold-start.md` at their expected paths,
When Recipe executes Step 2d,
Then no MISSING_COLD_START is emitted.
Then Recipe proceeds to write recipe.json with `cold_start_verified: true`.
Then the recipe receipt records `cold_start_verified: true`.

---

## BLOCK: one or more selected modules missing cold-start file

Given at least one module selected in Step 2b lacks `rules/cold-start.md`,
When Recipe executes Step 2d,
Then Recipe emits MISSING_COLD_START.
Then Recipe surfaces all missing cold-start paths to the user in a single message.
Then Recipe does not write recipe.json.
Then the session does not advance past Recipe.

---

## BLOCK: multiple modules missing cold-start files are all surfaced in one message

Given three modules are selected and two lack cold-start files,
When Recipe executes Step 2d,
Then Recipe surfaces both missing paths in the same message (not sequentially, not one at a time).
Then Recipe does not emit two separate MISSING_COLD_START events.

---

## PASS: excluded module bypasses cold-start check

Given a module is explicitly excluded from session activation by the user after a MISSING_COLD_START,
When Recipe re-evaluates Step 2d with the reduced selection,
Then Recipe does not check the excluded module's cold-start path.
Then if remaining selected modules all have cold-start files, Recipe proceeds to write recipe.json.

---

## PASS: Step 1 exit bypasses Step 2d

Given a valid, non-expired recipe.json already exists for this session,
When Recipe loads the existing recipe (Step 1 exit),
Then Recipe does not execute Step 2d.
Then `cold_start_verified` value from the loaded recipe.json is used as-is.

---

## DO NOT suppress MISSING_COLD_START

Given any session where a selected module lacks cold-start.md,
Then Recipe does not write recipe.json regardless of task urgency or human override request.
Then the missing file must be resolved before the session can advance.
