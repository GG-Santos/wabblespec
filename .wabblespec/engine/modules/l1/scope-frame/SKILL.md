---
name: scope-frame
description: Declares session boundaries — what is in scope, what is not, and what assumptions are made — before any spec work begins.
---

# ScopeFrame

You establish the fence before anyone starts digging. Your job is to get explicit agreement on what this session covers, what it excludes, and what is being assumed — before Specify writes a single requirement.

## What this skill does

Reads the recipe.json target and any opening context. Produces `scope.md` declaring in-scope items, out-of-scope items, and assumptions. Presents for user confirmation. Writes a receipt.

## When to use / when not to use

**Use when:**
- After Recipe declares a target (Stage gate fires)
- Before Specify or Interview begin
- Explicit `/scope` command
- Decompose detects scope expansion mid-execution (re-trigger)

**Do not use when:**
- Recipe has not yet run (I3 — target unknown, receipt missing)
- scope.md is already locked and no expansion has been detected

## Inputs

- `.wabblespec/recipe.json` (target, complexity)
- Opening user message and any attached documents
- Any existing spec artifacts (if re-triggering at P2+ stage)

## How to do it

### Step 1 — Read target and context

Load `recipe.json`. Extract target and complexity. Read the user's request in full.

### Step 1b — Load discovered standards

Before drafting scope boundaries, query Memory for `category: project-standard` drawers. Load all `critical` drawers into context. Load `high` drawers if the recipe target or task description overlaps their category.

For each loaded standard:
- Confirm the evidence paths still exist and the pattern is still present (brief spot-check — read one evidence file)
- If confirmed: cite the drawer ID in scope.md Assumptions section
- If evidence path missing or pattern gone: mark drawer NEEDS_REVERIFICATION, do not cite as active standard

**If no standards drawers exist:** Product discovery was skipped or project is new. Note "no project standards discovered" in Assumptions and proceed.

### Step 2 — Draft scope boundaries

Be specific. Vague scope is a defect (I12).

**In Scope:** List what this session must produce. Use action language ("implement X", "define Y", "write spec for Z"). 3–7 items for Low complexity; more for Medium/High.

**Out of Scope:** Explicitly state what is excluded. If the user mentioned adjacent topics, put them here. Non-goals prevent scope creep — they are as important as the inclusions.

**Assumptions:** State what is being taken as given. Dependencies, environment facts, decisions already made. If an assumption later proves false, it triggers a re-frame.

### Step 3 — Present for confirmation

Show the drafted scope to the user. Ask: "Does this match what you intended?" Accept additions or removals. Do not proceed until the user explicitly confirms.

### Step 4 — Write scope.md

Write to `.wabblespec/scope.md`. See output contract for structure.

### Step 5 — Write receipt

Write to `.wabblespec/receipts/scopeframe-receipt.json`. Extension fields: `in_scope_count`, `out_of_scope_count`, `assumptions_count`, `user_confirmed` (must be `true` — never write receipt with false).

## Output contract

**scope.md** (`.wabblespec/scope.md`):

```markdown
# Session Scope

**target:** <from recipe.json>
**complexity:** Low|Medium|High
**locked_at:** ISO-8601-timestamp

## In Scope

- <item>

## Out of Scope

- <item>

## Assumptions

- <item>
- **Standard [std-<id>]:** <standard name> — <one-line rule> (criticality: critical|high) [evidence: <path>]

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
```

## A note on common failure modes

1. **Empty Out of Scope.** If you cannot name at least one explicitly excluded thing, the scope is not specific enough. Ask: "What should we NOT tackle in this session?"

2. **Assumption-free scope.** Every task has at least one assumption (environment, framework version, prior work complete). If Assumptions is empty, you missed something.

3. **Proceeding without confirmation.** The user must confirm. No exceptions. An unconfirmed scope is not a locked scope.
