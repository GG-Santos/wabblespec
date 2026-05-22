---
name: recipe
description: Identifies the build target and complexity level before any other module activates. The entry gate for every WabbleSpec session.
---

# Recipe

You are the entry gate. Nothing runs before you. Your job is to identify what is being built (the target) and how complex this task is (Low / Medium / High).

## What this skill does

Scans the project for detection signals in priority order. Declares a build target and complexity level. Writes `recipe.json` to `.wabblespec/` and a receipt. Loads nothing else until this is done.

## When to use / when not to use

**Use when:**
- Session starts without an existing, non-expired `recipe.json`
- Build target changes mid-session
- Explicit `/recipe` command

**Do not use when:**
- A fresh, valid `recipe.json` already exists for this session — load it, write a receipt, stop

## Inputs

- Project directory (file structure, config files, design documents)
- Opening user message
- `.wabblespec/recipe.json` (if it exists)

## How to do it

### Step 1 — Check for existing recipe

Read `.wabblespec/recipe.json`. If it exists and `session_id` matches the current session, load it, write a receipt, and stop. Target already declared.

### Step 2 — Run detection scan

Work through signals in priority order. Stop at the first confident match (confidence ≥ 0.8).

| Priority | Signal | Action |
|---|---|---|
| 1 | Existing `.wabblespec/recipe.json` | Load if session_id matches |
| 2 | Design document present (`GDD.md`, `PRD.md`, `FDS.md`) | Declare target from document type |
| 3 | Platform config files | See `rules/target-detection.md` |
| 4 | Directory structure patterns | See `rules/target-detection.md` |
| 5 | User intent in opening message | Extract target from explicit statement |
| 6 | No confident signal | Ask user directly |

If two targets both score ≥ 0.6, present both and ask the user to confirm. Never guess between ambiguous candidates.

### Step 3 — Score complexity

Three levels only. Pick the one that fits.

| Level | Criteria |
|---|---|
| **Low** | Single file or feature, no integration points, no spec hierarchy needed, task fully clear |
| **Medium** | Multiple files or components, 1–2 integration points, task mostly clear with minor gaps |
| **High** | Cross-cutting changes, 3+ integration points, unclear requirements needing Interview, or BREAKING changes |

Low complexity + single spec stage = `collapse_eligible: true` (Plan+Execute may run together under I2 gate collapsing).

### Step 4 — Write recipe.json

Write to `.wabblespec/recipe.json`. Structure in output contract below.

### Step 5 — Write receipt

Write to `.wabblespec/receipts/recipe-receipt.json`. All base receipt fields required. Status PASS = target declared with confidence ≥ 0.8.

Report to user: target, detection method, confidence, complexity level. One paragraph. If target is ambiguous, ask before writing anything.

## Output contract

**recipe.json** (`.wabblespec/recipe.json`):

```json
{
  "target": "Web|API-Service|Game|Mobile|Desktop|CLI|IoT-Embedded|Library-Package|Extension-Plugin|Data-Pipeline|AI-Agent",
  "detection_method": "file-signals|user-declaration|interview|existing-recipe",
  "confidence": 0.0,
  "complexity": "Low|Medium|High",
  "secondary_targets": [],
  "collapse_eligible": false,
  "locked_at": "ISO-8601-timestamp",
  "session_id": "string"
}
```

**receipt** (`.wabblespec/receipts/recipe-receipt.json`): base receipt schema + extension fields `target`, `detection_method`, `confidence`, `complexity`, `collapse_eligible`.

## A note on common failure modes

1. **Ambiguous target, forced guess.** If two targets both score ≥ 0.6, always ask. A wrong target routes everything downstream incorrectly.

2. **Expired recipe.json reused.** Check `session_id`. If it does not match, re-detect. Do not load a stale recipe silently.

3. **Complexity underestimated.** When in doubt between Low and Medium, pick Medium. `collapse_eligible: true` is a performance optimization, not a correctness requirement. An unnecessary review cycle is cheaper than a skipped gate.
