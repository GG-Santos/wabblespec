---
name: recipe
description: Identifies the build target and complexity level before any other module activates. The entry gate for every WabbleSpec session. Verifies cold-start documentation exists for all selected modules before committing to recipe.json.
augment_ref: cold-start-coverage-recipe-gate-v1
---

# Recipe

You are the entry gate. Nothing runs before you. Your job is to identify what is being built (the target) and how complex this task is (Low / Medium / High).

## What this skill does

Scans the project for detection signals in priority order. Declares a build target and complexity level. Verifies cold-start documentation exists for all selected modules. Writes `recipe.json` to `.wabblespec/` and a receipt. Loads nothing else until this is done.

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

### Step 2b — Module specificity scoring

When selecting modules to activate for the detected target, prefer modules whose `skill-rules.json` declares `file_path_patterns` that match detected project files over modules using generic `["ALL"]` activators. Specificity wins: a module that matches `.nani` files beats a catch-all module for a Naninovel project. Rank candidates by pattern match count descending; load the most specific match first.

### Step 2c — Assess input quality

After target detection, evaluate the quality of the opening user message independently of the target. This runs every time Recipe runs detection (not when loading an existing recipe.json — Step 1 exit bypasses this).

**Vague check (input_vague = true when ALL of these are absent):**
- A named artifact: file, module, component, service, endpoint, test, feature name
- A measurable outcome: a number, threshold, user-observable behavior that can be confirmed true or false
- A named constraint: must not, cannot, by date, under N tokens, backwards-compatible, no breaking change
- A specific scope boundary: only this file, just the login flow, excluding mobile

**Broad check (input_broad = true when BOTH are true):**
- Two or more interpretations of user intent are plausible at ≥ 0.5 confidence each
- No priority signal disambiguates them (user did not rank, quantify, or constrain to one interpretation)

Write results to recipe.json `input_quality` field (see output contract below).

**Routing after assessment:**
- input_vague AND NOT input_broad → invoke Enhance → then ScopeFrame
- input_broad AND NOT input_vague → invoke Sharpen → then ScopeFrame
- input_vague AND input_broad    → invoke Enhance → invoke Sharpen → then ScopeFrame
- neither                        → proceed to ScopeFrame directly

Recipe writes recipe.json before invoking Enhance or Sharpen. The target and complexity are locked. Enhance and Sharpen operate on input clarity only — they do not change the target or complexity score.

### Step 2d — Module cold-start verification (AUGMENT: new step)

Before writing recipe.json, verify that `rules/cold-start.md` exists for each module selected in Step 2b.

```
for each selected_module in selected_modules:
    path = modules/{selected_module.layer}/{selected_module.id}/rules/cold-start.md
    if path does not exist:
        collect to missing_cold_start list
if missing_cold_start is not empty:
    emit MISSING_COLD_START
    surface all missing paths to user in a single message
    do not write recipe.json
    stop
```

If any module fails this check, surface all missing paths in a single message. Do not write recipe.json. Await human resolution. Resolution options:
- Add the missing `rules/cold-start.md` file to the module (preferred)
- Explicitly exclude the module from this session by removing it from the selection

Do not proceed past this step until all selected modules have cold-start files or the module is removed from selection.

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

Write to `.wabblespec/receipts/recipe-receipt.json`. All base receipt fields required. Status PASS = target declared with confidence ≥ 0.8 and all selected modules have cold-start files.

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
  "session_id": "string",
  "cold_start_verified": true,
  "input_quality": {
    "vague": false,
    "broad": false,
    "enhanced": false,
    "sharpened": false
  }
}
```

**receipt** (`.wabblespec/receipts/recipe-receipt.json`): base receipt schema + extension fields `target`, `detection_method`, `confidence`, `complexity`, `collapse_eligible`, `cold_start_verified`, `input_quality`.

## A note on common failure modes

1. **Ambiguous target, forced guess.** If two targets both score ≥ 0.6, always ask. A wrong target routes everything downstream incorrectly.

2. **Expired recipe.json reused.** Check `session_id`. If it does not match, re-detect. Do not load a stale recipe silently.

3. **Complexity underestimated.** When in doubt between Low and Medium, pick Medium. `collapse_eligible: true` is a performance optimization, not a correctness requirement. An unnecessary review cycle is cheaper than a skipped gate.

4. **MISSING_COLD_START suppressed.** Do not skip Step 2d to unblock a session. A module without cold-start documentation is an unacknowledged gap — surfacing it is the correct outcome, not an obstacle to work around.

## Not tested

Augment cannot verify that the MISSING_COLD_START check fires correctly in all execution environments. Benchmark validates detection accuracy against fixture cases. The cold-start path resolution assumes a flat `modules/{layer}/{module}/` layout — modules in nested or non-standard locations may require path resolution logic updates.
