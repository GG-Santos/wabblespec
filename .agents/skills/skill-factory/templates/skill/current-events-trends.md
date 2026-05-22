# Current-Events And Trends Overlay

Extends `templates/skill/base-universal.md`. Use for latest/current facts,
sports, politics, crypto, technology releases, prices, laws, schedules, and
public figures.

## Domain Operating Model

Split stable background from facts that can change after the model's knowledge
cutoff.

## Request Triage

Require retrieval when the user asks for latest, today, current, prices, laws,
scores, schedules, releases, public figures, or live availability.

## Workflow

1. Classify claims as stable, current, predicted, or unknown.
2. Retrieve current sources when available.
3. Use exact dates and as-of markers.
4. Mark unverifiable claims instead of inventing citations.

## Output Contract

Include `as_of`, `sources_checked`, `stable_context`, `current_findings`, and
`uncertainty`.

## Examples And Edge Cases

Cover stale source conflict, prediction requests, and unavailable retrieval.

## Failure Modes

Freshness laundering, fake citations, stale certainty, and prediction stated as
fact.
