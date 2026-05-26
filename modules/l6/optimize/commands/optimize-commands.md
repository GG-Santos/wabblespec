# Optimize Commands

Available sub-modes and their flags.

## Usage

```
optimize --mode <mode> --target <path> [options]
optimize --all --target <path> [options]
```

## Sub-modes

### --seo
SEO fundamentals: title tag, meta description, H1, canonical, robots, internal links, image alt text.

Options:
- `--target <path>` — file or directory to audit (required)
- `--strict` — FAIL on HIGH findings, not only CRITICAL

### --ai-search
AI search surface optimization: entity clarity, factual claim density, author attribution, structured FAQ, freshness signals.

Options:
- `--target <path>` — required
- `--brand-name <name>` — required for entity verification
- `--product <name>` — product name for entity matching

### --structured-data
JSON-LD schema.org validation: type correctness, required properties, no fabricated data.

Options:
- `--target <path>` — required
- `--url <canonical-url>` — required for URL validation in schema
- `--type <schema-type>` — expected schema type for validation (e.g., `Article`, `Product`)

### --performance
Core Web Vitals proxy audit: LCP element, render-blocking resources, layout shift sources, image optimization.

Options:
- `--target <path>` — required
- `--budget-lcp <ms>` — LCP target in milliseconds (default: 2500)
- `--budget-cls <score>` — CLS target (default: 0.1)

### --social
Open Graph and Twitter Card coverage: required tags, image dimensions.

Options:
- `--target <path>` — required
- `--image-path <path>` — OG image path for dimension verification

### --local
Local search optimization: NAP consistency, LocalBusiness schema, local keyword presence.

Options:
- `--target <path>` — required
- `--brand-name <name>` — required
- `--address <address>` — required for NAP verification
- `--phone <phone>` — required for NAP verification

### --video
Video SEO: title, description, timestamps, captions.

Options:
- `--target <path>` — video page or file (required)
- `--duration <seconds>` — video duration (determines timestamp requirement)

### --voice
Voice search optimization: question headings, concise first-paragraph answers, list format for how-to.

Options:
- `--target <path>` — required

## Global options

- `--output <path>` — write receipt to specified path
- `--all` — run all modes in priority order (see `rules/signal-hierarchy.md`)
- `--strict` — FAIL on HIGH findings in addition to CRITICAL (default: FAIL on CRITICAL only)
- `--dry-run` — produce findings report without applying fixes
