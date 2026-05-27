# Signal Hierarchy

Priority ordering for optimization sub-modes. Determines execution order and triage priority.

## Priority order

When running multiple sub-modes, apply in this order:

1. **--performance** — Core Web Vitals directly affect search ranking. A slow page cannot rank regardless of other signals.
2. **--structured-data** — Structured data enables rich results (featured snippets, rich cards). Without it, no enhancement is possible.
3. **--seo** — Foundational metadata and content signals. Required for all organic discovery.
4. **--ai-search** — AI surfaces cite content that is specific, factual, and entity-rich. Overlaps with SEO but has distinct requirements.
5. **--social** — Social sharing metadata. Lower search ranking impact but affects click-through from social discovery.
6. **--local** — Only relevant for location-based businesses. High priority when relevant, irrelevant when not.
7. **--video** — Only relevant for video content. Irrelevant for text content.
8. **--voice** — Voice search optimization. Currently narrower audience than other surfaces.

## Priority rationale

Performance issues block all other optimization. A page with perfect structured data and SEO metadata that loads in 8 seconds will not rank. Fix performance first.

Structured data enables Google's rich results. A page without valid schema.org markup cannot receive featured snippets, knowledge panel inclusion, or rich cards. Fix structured data before copy-level SEO.

## CRITICAL vs HIGH vs MEDIUM vs LOW

| Priority | Condition | Example |
|---|---|---|
| CRITICAL | Missing required element that prevents indexing or rich results | No title tag; invalid structured data blocking rich results |
| HIGH | Element present but non-compliant; likely ranking suppression | Title tag > 60 chars (truncated in SERP); missing H1 |
| MEDIUM | Optimization gap; addressable improvement | Meta description length suboptimal; image alt text generic |
| LOW | Nice-to-have; marginal improvement | Social card image ratio not ideal |

## Sub-mode independence

Each sub-mode is independently applicable. Running --seo does not require --performance. However, for a full discoverability audit before launch, run `--all` to ensure no dimension is missed.

## When to skip sub-modes

- `--local`: skip unless the product has a physical location or service area
- `--video`: skip unless the target page contains or is primarily about video content
- `--voice`: skip unless the product targets smart speaker or voice assistant surfaces specifically
