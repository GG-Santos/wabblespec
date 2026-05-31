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

## Output contract

- `.pptx` file at declared output path
- present receipt confirming file written and slide count

## Reference Routing

| Situation | Reference |
|---|---|
| PPTX production rules | `gateway-document/references/pptx.md` |
| Present receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |
