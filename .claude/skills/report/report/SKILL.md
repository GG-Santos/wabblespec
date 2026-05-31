---
name: report
description: Converts WabbleSpec Archive receipts and session state into structured stakeholder communications — 3P updates (Progress/Plans/Problems), status reports, leadership updates, and incident summaries. Requires an Archive receipt or active session state. Produces Markdown by default; routes to gateway-document for Word/PDF output when binary format is requested.
layer: L7
---

# Report

You generate structured stakeholder communications from WabbleSpec state. You do not invent status — every claim traces to a receipt, wave result, or active session state.

## What this skill does

Reads Archive receipts, wave progress, and quality floor data. Produces structured communications in Markdown (default), Word (.docx), or PDF. Does not run during execution waves.

## When to use

- After Archive receipt: produce a delivery status update
- During an active session: produce a mid-session progress update
- Explicit `/report` command
- When `archive`, `document`, or user requests a 3P update, status report, or leadership summary

## When NOT to use

- No receipt or session state exists — cannot report on non-existent work
- A technical delivery receipt already suffices — report is for human stakeholders, not pipeline consumers

## Communication types

| Type | When to use | Structure |
|---|---|---|
| 3P Update | Team/manager sprint update | Progress / Plans / Problems |
| Status Report | Stakeholder check-in | Summary / What's done / What's next / Blockers |
| Leadership Update | Executive summary | One-line goal / Key outcome / Risk summary |
| Delivery Summary | Post-archive stakeholder handoff | What was built / Quality signal / Next steps |

## How to do it

### Step 1 — Gather state

Read:
- `.wabblespec/state/receipts/` — Archive receipt (latest) for task goal, version, wave summary
- `.wabblespec/state/plans/task-card.md` — goal, non-goals, acceptance criteria status
- `.wabblespec/state/session/state.json` — active session state if available
- `.wabblespec/CHANGELOG.md` — current version entries

### Step 2 — Select communication type and format

Default output: Markdown in conversation. Binary output (docx/pdf): invoke gateway-document.

For **3P Update** structure:

```markdown
## Progress

- [Completed this period — traced to wave receipts]

## Plans

- [Next actions — traced to task card or open waves]

## Problems

- [Blockers or risks — traced to REVISE/FAIL receipts or open issues]
```

For **Leadership Update** (≤ 5 lines):

```markdown
**Goal:** [one sentence from task card]
**Outcome:** [PASS/PARTIAL — from Archive receipt]
**Key change:** [one changelog entry]
**Risk:** [one blocker if any, else "None"]
**Next:** [next task goal if known]
```

### Step 3 — Write receipt

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type generic \
  --task-id <task-id> --session-id <session-id> \
  --status PASS \
  --summary "Report: <type> — <format>" \
  --out .wabblespec/state/receipts/report-<timestamp>.json
```

## Reference Routing

| Situation | Reference |
|---|---|
| DOCX output | `gateway-document/references/docx.md` |
| PDF output | `gateway-document/references/pdf.md` |
| Report receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |
