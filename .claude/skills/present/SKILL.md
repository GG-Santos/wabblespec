---
name: present
description: Converts WabbleSpec Archive receipts, delivery data, and task outcomes into stakeholder PowerPoint slide decks. Activates when a completed task needs a presentation-format delivery, sprint review, or executive summary. Requires an Archive receipt — does not run during execution waves.
layer: L7
---

# Present

You convert completed, receipted work into stakeholder slide decks. You do not summarize speculatively — every slide claim traces to a receipt, wave artifact, or changelog entry.

## What this skill does

Reads the Archive receipt and wave artifacts. Produces a .pptx delivery presentation via gateway-document. Activates after Archive receipt confirms task complete.

## When to use

- Archive receipt exists and a slide deck is requested
- Sprint review or stakeholder delivery requires presentation format
- `/present` command after archive

## When NOT to use

- No Archive receipt exists — cannot present unverified work
- During execution waves — presentation is a post-completion step
- Plain Markdown summary is sufficient — present only when .pptx format is explicitly needed

## How to do it

### Step 1 — Read archive data

Read from:
- `.wabblespec/state/receipts/` — latest Archive receipt (delivery metadata, version, task goal)
- `.wabblespec/state/plans/task-card.md` — goal statement and acceptance criteria
- `.wabblespec/CHANGELOG.md` — entries for the current version
- `.wabblespec/state/receipts/` — Verifier receipts for wave pass/fail summary
- Quality floor check output if recent (`python .wabblespec/engine/shared/scripts/quality-floor-check.py --format json`)

### Step 2 — Build slide outline

Standard 5-slide structure for task delivery:

| Slide | Title | Content source |
|---|---|---|
| 1 (title) | `Delivery: <task goal>` | Archive receipt: goal, version, date |
| 2 | What Was Built | Executor wave summaries — completed items only |
| 3 | Quality Floor | quality-floor-check output — gate pass rates |
| 4 | What Changed | CHANGELOG entries for this version |
| 5 | Next Steps | Open items from task card non-goals or scope deferral notes |

Adjust slide count based on scope: small tasks may omit Quality Floor; large tasks may add an Architecture slide.

### Step 3 — Invoke gateway-document

Call gateway-document with `format: pptx`. Load `references/pptx.md` from gateway-document.

```python
# Standard delivery presentation dimensions: 16:9
prs.slide_width  = 9144000
prs.slide_height = 5143500
```

Apply professional typography: consistent font family across all slides, title size ≥ 28pt, body text ≥ 16pt.

### Step 4 — Validate and write receipt

Run `prs.save()` and confirm file is non-zero bytes. Then:

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type generic \
  --task-id <task-id> --session-id <session-id> \
  --status PASS \
  --summary "Delivery presentation: <slide count> slides, <format>" \
  --out .wabblespec/state/receipts/present-<timestamp>.json
```

## Narrative Arc

For stakeholder delivery presentations, apply the Duarte Sparkline emotional arc to maintain engagement across the deck:

- Alternate between "What Is" (current state, tension, problem framing) and "What Could Be" (resolved state, opportunity, forward vision)
- Apply pattern breaks at the 1/3 and 2/3 positions in the deck — a slide that shifts emotional register prevents the audience from going numb to a uniform tone
- Example for a 9-slide deck: slides 1-3 establish "What Is", slide 3 breaks to "What Could Be", slides 4-6 return to complexity/nuance, slide 6 breaks again, slides 7-9 close on "What Could Be"

The standard 5-slide structure maps naturally: slide 1 (title/what was built) = What Is; slide 2 (detail) = What Is; slide 3 (quality floor) = What Is; slide 4 (what changed/wins) = first break to What Could Be; slide 5 (next steps) = What Could Be close.

## Output contract

- `.pptx` file at declared output path
- present receipt confirming file written and slide count

## Reference Routing

| Situation | Reference |
|---|---|
| PPTX production rules | `gateway-document/references/pptx.md` |
| Present receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## HTML Slide Output

An alternative to the `.pptx` path: generate a self-contained, browser-viewable HTML presentation with Chart.js data visualization. No PowerPoint dependency. Requires no additional pip packages beyond Python standard library.

### When to use

- Stakeholder needs an in-browser presentation (no PowerPoint license required)
- Slide content includes charts or data visualizations
- Output will be embedded in a web context or shared as a URL

### How to invoke

```bash
python .wabblespec/engine/shared/scripts/generate-slide.py \
  --query "<product type>" \
  --chart-type <line|bar|pie|doughnut|scatter|area> \
  --title "<Slide Title>" \
  --subtitle "<Optional subtitle>" \
  --data "42,68,55,81,73,90" \
  --labels "Jan,Feb,Mar,Apr,May,Jun" \
  --output delivery-slide.html
```

### Token compliance requirement

All visual CSS property values in the generated HTML use CSS custom property references (`var(--token-name)`). Raw hex, `rgb()`, or `px` values are prohibited in property values. Validate any modified output with:

```bash
python .wabblespec/engine/shared/scripts/slide-token-validator.py delivery-slide.html
```

The validator exits 0 on clean output and non-zero with line numbers on violations.

### Design token system

`generate-slide.py` embeds 110+ product-type palettes (sourced from the ui-ux-pro-max reference) covering all 16 color token roles (`--color-primary` through `--color-ring`), 7 spacing tokens (`--space-xs` through `--space-3xl`), and 4 shadow tokens (`--shadow-sm` through `--shadow-xl`). The palette is selected by fuzzy-matching `--query` against the embedded palette names. Unknown queries fall back to the "SaaS (General)" palette.

### CDN dependency

Chart.js is loaded from `https://cdn.jsdelivr.net/npm/chart.js`. An active internet connection is required to render charts. For offline use, download `chart.js` locally and replace the CDN `<script>` tag in the generated HTML.
