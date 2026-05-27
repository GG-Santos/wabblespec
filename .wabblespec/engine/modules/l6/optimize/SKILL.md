---
name: optimize
description: Discoverability optimization: SEO, AI search surfaces, structured data, Core Web Vitals, social sharing, local search, video, and voice. 8 sub-modes.
layer: L6
---

# Optimize

You make content and code discoverable. Not through tricks — through signal. Search engines and AI surfaces reward clarity, structure, and performance. You apply the right signals for the right surface.

## What this skill does

Optimize audits and improves discoverability across 8 dimensions. Each dimension is a sub-mode. A single invocation can run one sub-mode or all 8 (--all). Each sub-mode produces findings and, where possible, direct fixes. See `rules/signal-hierarchy.md` for priority ordering across sub-modes.

## When to use

Optimize activates when:
- A product page, blog post, or content artifact needs discoverability improvements
- Performance scores are affecting search ranking
- AI search surfaces (Perplexity, ChatGPT browsing, Gemini) are not finding or citing the product correctly
- Local search, video, or voice search optimization is required
- A pre-launch discoverability audit is needed

## Inputs

- **Mode** — one or more of: `seo | ai-search | structured-data | performance | social | local | video | voice` or `all` (required)
- **Target path** — path to the page, file, or artifact being optimized (required)
- **URL** — canonical URL of the target (optional; required for structured-data and local modes)
- **Brand name** — product or business name (required for local and ai-search modes)
- **Location** — physical address (required for local mode)
- **Locale** — target locale for optimization (default: `en-US`)

## Output contract

**Receipt:** `.wabblespec/state/receipts/optimize-{timestamp}.json`

```json
{
  "modes_run": ["list"],
  "target_path": "string",
  "findings": [
    {
      "mode": "string",
      "priority": "CRITICAL | HIGH | MEDIUM | LOW",
      "issue": "string",
      "fix_applied": true,
      "fix_description": "string or null"
    }
  ],
  "total_findings": 0,
  "critical_count": 0,
  "fixes_applied": 0,
  "verdict": "PASS | WARN | FAIL",
  "optimized_at": "ISO-8601"
}
```

`verdict: FAIL` when any CRITICAL finding remains unfixed after optimization pass.

## Sub-mode specs

**--seo:** Title tag (55–60 chars), meta description (150–160 chars), H1 presence and uniqueness, keyword in H1 and first paragraph, canonical tag, robots meta, internal links, image alt text.

**--ai-search:** Entity clarity (brand, product, use case named explicitly), factual claim density (AI surfaces cite specific facts), author/publisher attribution, structured FAQ markup if applicable, content freshness signal (published/updated date).

**--structured-data:** JSON-LD presence, schema type appropriate for content (Article, Product, FAQPage, HowTo, LocalBusiness), required properties per schema type, validation against schema.org spec.

**--performance:** Core Web Vitals proxies — LCP (largest element identified, render-blocking resources flagged), CLS (layout shift sources identified), FID/INP (interaction delay from main-thread blocking), image optimization (format, lazy loading, dimensions declared).

**--social:** Open Graph tags (og:title, og:description, og:image, og:url), Twitter Card tags, image dimensions meet platform requirements (1200×630 minimum for OG).

**--local:** Google Business Profile signals — NAP consistency (name, address, phone), LocalBusiness schema, local keywords in title/H1, reviews markup if applicable.

**--video:** YouTube/platform: title (60-char target), description (first 150 chars keyword-rich), chapters/timestamps if >10 minutes, closed captions presence, thumbnail specification.

**--voice:** Featured snippet optimization — question-format H2/H3 headings, concise answer in first paragraph after heading (≤50 words), structured list format for how-to content.

## Steps

**Step 1 — Run declared modes in priority order.**
See `rules/signal-hierarchy.md` for ordering (Core Web Vitals > structured data > metadata > copy). Apply each mode's checklist to the target.

**Step 2 — Apply fixes where possible.**
For findings that are deterministic and non-destructive (missing meta tag, wrong image dimension spec, missing alt text): apply fix directly. Record as `fix_applied: true`.

For findings that require content judgment (keyword choice, FAQ content): surface as findings only. Do not auto-apply.

**Step 3 — Write receipt.**

## Failure modes

**Keyword stuffing:** SEO mode identifies keyword density issues — over-optimization is a finding, not a recommendation. Do not add keywords beyond natural density.

**Schema hallucination:** Structured data must reflect actual page content. Do not add Product schema to a blog post or LocalBusiness schema to a SaaS product page.

**Performance without measurement:** Performance findings are proxies, not measurements. Flag them as "likely issues requiring measurement" rather than confirmed regressions.
