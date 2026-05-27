# Explore — Acceptance Criteria

## BLOCK: absent recipe.json

Given no `recipe.json` is present or it is stale,
When Explore is invoked,
Then Explore surfaces a DEPENDENCY error naming Recipe.
Then Explore does not explore the entire project without a target.
Then no project-map.md is written.

## BLOCK: absent recipe receipt

Given `recipe-receipt.json` is absent,
When Explore is invoked,
Then Explore surfaces a DEPENDENCY error naming Recipe.
Then Explore does not proceed without the receipt chain started.

## Happy path: traversal from high-value nodes

Given a valid recipe.json with a declared target,
When Explore runs,
Then traversal begins at high-value nodes: dependency manifests, entry points, configuration files, test files, high-churn files.
Then traversal does not scan every file blindly.
Then findings are written to Memory as FRESH drawers (one per distinct finding, not one per file).
Then EntityGraph is notified with entity candidates after drawers are written.
Then `project-map.md` is written to `.wabblespec/plans/project-map.md`.
Then a receipt is written to `.wabblespec/receipts/`.

## project-map.md required fields

Given any completed Explore run,
Then `project-map.md` contains: `freshness_state`, `valid_until`, `Build target`, `Entry points`, Tech Stack table, Spec Artifacts Found, Conventions Observed, Risk Files, Impact Slices, Git State, Gaps.
Then `freshness_state` is set to `FRESH`.
Then `valid_until` is `explored_at + 24h` for standard targets.
Then the Gaps section contains at least one entry — Explore does not claim zero gaps.

## Freshness states: STALE blocks consumption

Given `project-map.md` has `freshness_state: STALE` (72h+ elapsed or new packages added),
When a downstream module (ReferenceLoad, Decompose, Guard) attempts to consume the map,
Then the consumer is notified to trigger an Explore re-run before planning.

Given `project-map.md` has `freshness_state: EXPIRED` (entry-points or tech-stack changed since last map),
When a downstream module attempts to consume the map,
Then consumption is blocked and Explore re-run is required.

## Drawer limit: stop at 50

Given Explore has written 50 new drawers in a session,
When additional findings are identified,
Then Explore stops drawer writes and declares the limit in the Gaps section.

## Do NOT: run during active execution waves

Given an Executor wave is active,
When Explore is invoked,
Then Explore surfaces a warning that it is a Research phase module and does not run during active execution waves.

## Do NOT: one drawer per file

Given Explore finds multiple files that represent one tech stack component,
When drawers are written,
Then one drawer is written for the tech stack component, not one per file.

## Do NOT: claim full coverage

Given any Explore run (regardless of how thorough the traversal),
Then the Gaps section in project-map.md is never empty.
Then at least one gap entry is present.

## Impact slices as consumption unit

Given project-map.md is written,
Then named impact slices (entry-points, api-surface, test-coverage, risk, conventions) are present.
Then downstream modules consume slices rather than raw file lists.
