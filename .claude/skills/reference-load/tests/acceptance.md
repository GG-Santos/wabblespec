# ReferenceLoad — Acceptance Criteria

## BLOCK: absent reference file

Given a required reference file is not found at its declared path in `.wabblespec/engine/shared/references/`,
When ReferenceLoad is invoked,
Then ReferenceLoad surfaces a DEPENDENCY error naming the specific missing reference file.
Then ReferenceLoad does not substitute defaults for missing authoritative references.
Then no reference card is written.

## BLOCK: absent recipe receipt

Given `recipe-receipt.json` is absent,
When ReferenceLoad is invoked,
Then ReferenceLoad surfaces a DEPENDENCY error naming Recipe.
Then ReferenceLoad does not load references speculatively without a declared target.

## Dedup check: FRESH drawer already exists

Given a FRESH drawer already exists in `index.json` whose topic matches the requested source + purpose,
When ReferenceLoad runs,
Then ReferenceLoad returns the existing drawer id and does not reload.
Then the receipt records `dedup_hit: true`.
Then no duplicate drawer is written to Memory.

## Happy path: new reference loaded

Given no matching FRESH drawer exists and the source path is valid,
When ReferenceLoad runs,
Then the source is mapped (top-level directory listed, README/project-map/CLAUDE.md read — at most 3 files).
Then concepts relevant to `purpose` are extracted from at most 5 files.
Then a reference card drawer is written to `.wabblespec/state/memory/wings/references/rooms/<source-slug>/drawers/<id>.json`.
Then `index.json` is updated with the new drawer entry.
Then Provenance is notified of the write.
Then a receipt is written to `.wabblespec/state/receipts/reference-load-<source-slug>-<timestamp>.json`.

## File read limit: maximum 5

Given the `purpose` would require more than 5 files to satisfy fully,
When ReferenceLoad runs,
Then only 5 files are read.
Then ReferenceLoad surfaces the limitation: scope down the purpose or invoke again for additional concepts.
Then remaining concepts are noted in `not_tested` in the receipt.

## Trust level assignment

Given a source is an external community project (not an official specification or canonical SDK),
When trust level is assigned,
Then trust level is MEDIUM at most unless explicit rationale for HIGH is provided.
Then trust level is never inflated without rationale.

## Do NOT: load generated or private artifacts

Given the reference path leads to generated artifacts (dist/, build/, .npmrc) or private journals,
When ReferenceLoad encounters them,
Then those paths are recorded in `do_not_copy` and not read.
Then ReferenceLoad proceeds with available non-excluded paths.

## Pointer mode: drawer written, content not injected

Given `output_mode: "pointer"` is specified,
When ReferenceLoad runs,
Then the reference card drawer is written to Memory (evidence chain is preserved).
Then drawer content is NOT loaded into current context.
Then the receipt records `output_mode: "pointer"` and `cited_as: "@<drawer_path>"`.
Then a one-sentence summary is returned alongside the citation path.

## Pointer mode: citation format

Given `output_mode: "pointer"` and a successful drawer write,
When ReferenceLoad returns,
Then the output is: `Reference loaded. Cite as: @<drawer_path> — <one-sentence summary>`.
Then this output is usable as a direct citation in a task card, wave plan, or spec artifact.

## Pointer mode use in high-context-budget scenarios

Given `output_mode: "pointer"` is requested,
And context budget tier is PEAK or GOOD,
When ReferenceLoad runs,
Then pointer mode still applies — mode is caller-specified, not auto-selected by context tier.
Then the caller decides whether to use pointer or inline based on their artifact construction needs.

## One source, one purpose, one drawer

Given any ReferenceLoad invocation,
Then exactly one drawer is written per invocation.
Then concepts from multiple sources are not mixed into one drawer.

## Reference card required fields

Given any successfully written reference card,
Then the drawer contains: `id`, `topic`, `wing: "references"`, `staleness_state: "FRESH"`, `trust_level`, `source_path`, `purpose`, `evidence_files`, `concepts` (with name/summary/wabble_adaptation), `risks`, `do_not_copy`, `confidence`, `written_at`.

## Confidence scoring

Given a source where all relevant files were read and no ambiguity exists,
Then confidence is >= 0.9 (approaching 1.0).

Given a source with clear gaps or partially stale content,
Then confidence is 0.6–0.8 and flagged as such.

Given confidence is below 0.6,
Then trust is flagged LOW in the receipt and the gaps are noted.
