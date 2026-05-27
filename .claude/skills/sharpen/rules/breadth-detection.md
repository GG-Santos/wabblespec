# Breadth Detection

Input is broad when two or more genuinely different interpretations of user intent each score ≥ 0.5 confidence AND no priority signal disambiguates them.

## Breadth conditions (both must be true)

**Condition 1:** Two or more distinct, actionable interpretations of the user's message each score ≥ 0.5 confidence when read independently.

**Condition 2:** No priority signal resolves the ambiguity. Priority signals that resolve breadth:
- User explicitly ranked interpretations ("most important is...", "start with...")
- User named a specific artifact (narrows to one interpretation)
- User stated a constraint that rules out one interpretation ("no database changes")
- User quantified the scope ("just one endpoint", "only the frontend")

If a priority signal is present: breadth = false. Proceed without Sharpen.

## What counts as a genuinely different interpretation

Different = different course of action, different outcome, different affected artifacts.

**Genuinely different:**
- "Add authentication" → could mean: (a) build new auth system, (b) add auth to an existing endpoint, (c) document auth requirements
- "Improve the API" → could mean: (a) add new endpoints, (b) improve performance, (c) add versioning, (d) improve documentation

**Not genuinely different (rewordings):**
- "Fix the login bug" vs "repair the login issue" → same interpretation, different words

## Confidence scoring for interpretations

Score each interpretation by: how many tokens in the user message support it, how well it fits the recipe.json target, how actionable it is given declared complexity.

Threshold: ≥ 0.5 for inclusion. If only one interpretation scores ≥ 0.5, input is not broad.

## Boundary with Enhance

Breadth is about competing interpretations at equal weight. Vagueness is about missing specifics. An input can be both (vague AND broad) — Enhance runs first, then Sharpen on the enhanced input.

A broad input may have perfectly clear dimensions in Enhance's sense — the specifics are clear, but there are multiple valid targets for those specifics.
