# Recipe — Acceptance Criteria

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

---

## collapse_assessment: Low complexity collapses eligible modules

Given a Low complexity session with activated modules where some have skill_collapse_eligible=true,
When Recipe computes the collapse_assessment in Step 3,
Then each module with skill_collapse_eligible=true has disposition=COLLAPSED.
Then each module with skill_collapse_eligible=false has disposition=ACTIVE.
Then collapse_assessment is written to recipe.json and the recipe receipt.

---

## collapse_assessment: Medium and High complexity — all ACTIVE

Given a Medium or High complexity session regardless of each module's skill_collapse_eligible value,
When Recipe computes the collapse_assessment in Step 3,
Then every module has disposition=ACTIVE.
Then no module is marked COLLAPSED at Medium or High complexity.

---

## collapse_assessment: disposition rule is deterministic

Given any session,
Then disposition=COLLAPSED requires BOTH: complexity==Low AND skill_collapse_eligible==true.
Then a module with skill_collapse_eligible=false is never COLLAPSED regardless of complexity.
Then a module with skill_collapse_eligible=true is COLLAPSED only at Low complexity, ACTIVE otherwise.

---

## collapse_assessment: written even when no modules are collapse_eligible

Given a Low complexity session where all activated modules have skill_collapse_eligible=false,
When Recipe computes the collapse_assessment,
Then collapse_assessment is still written with all entries disposition=ACTIVE.
Then the field is not omitted or null.
