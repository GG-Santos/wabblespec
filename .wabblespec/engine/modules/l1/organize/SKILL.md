---
name: organize
description: Audits and repairs project file and folder structure. Detects naming violations, orphaned files, depth violations, and duplicates. Moves and renames automatically when safe; requires human confirmation for destructive actions.
---

# Organize

Entropy is the default. Over time: files accumulate in wrong directories, naming conventions drift, orphans appear, depth grows. You audit all of it and repair what is safe to repair automatically. What is not safe, you surface for human confirmation.

## What this skill does

Audits project file/folder structure across 5 dimensions. Produces an action list. Takes automatic actions when safe (no data loss, fully reversible). Requires human confirmation for any action that deletes, overwrites, or moves files that may have external references. Writes organize receipt.

## When to use / when not to use

**Use when:**
- Explicit `/organize` command
- Archive surfaces high orphan count
- New developer asks "where does X go?"
- After a large refactor that moved modules around

**Do not use when:**
- Project is pre-ScopeFrame (structure is intentionally sparse)
- All audit dimensions are clean from last Organize run (< 50 changes since last run)

## Inputs

- Project root directory
- Optional: naming convention spec (if project has declared naming rules)
- Optional: `.wabblespec/organize/last-report.md` (previous audit baseline)

## How to do it

### Step 1 — Audit across 5 dimensions

See rules/audit-dimensions.md for detailed criteria.

| Dimension | What it checks |
|---|---|
| Naming | Files/folders conform to declared naming convention (kebab-case, snake_case, etc.) |
| Depth | No directory more than 5 levels deep (configurable) |
| Orphans | Files with no imports, no references, no receipts — dead weight |
| Duplicates | Identical or near-identical content at different paths |
| Structure | Known WabbleSpec paths (`modules/`, `.wabblespec/engine/shared/`, `.wabblespec/`) exist and are not mis-nested |

### Step 2 — Classify actions

For each finding: classify as AUTO or CONFIRM.

**AUTO (safe without human input):**
- Rename to fix naming violation when the new name is unambiguous
- Move a file to the correct directory when no external references point to the old path
- Delete a generated file that is clearly regeneratable

**CONFIRM (human must approve):**
- Delete a non-generated file (potential data loss)
- Move a file that has external references (callers must update)
- Rename when multiple valid new names exist (ambiguous)
- Any action on files outside the WabbleSpec-governed directories

### Step 3 — Execute AUTO actions

Take all AUTO actions. Record each in the receipt. Do not batch or defer AUTO actions — if classified AUTO, take them now.

### Step 4 — Surface CONFIRM actions

Present CONFIRM actions to user as a numbered list. Wait for confirmation before acting. Do not take any CONFIRM action without explicit user approval.

### Step 5 — Write report and receipt

Write organize report to `.wabblespec/organize/report-<timestamp>.md`. Write receipt.

## Reference Routing

| Situation | Reference |
|---|---|
| Organize receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` for the base, then `--extra-json` for the module-specific fields defined in `schemas/organize-receipt.schema.json` |

## Output contract

**organize-receipt.json** (`.wabblespec/state/receipts/organize-receipt-<timestamp>.json`):

```json
{
  "files_audited": "integer",
  "orphans_found": "integer",
  "naming_violations": "integer",
  "depth_violations": "integer",
  "duplicates_found": "integer",
  "actions_taken_auto": "integer",
  "actions_requiring_confirmation": ["array of paths requiring human confirmation"],
  "organize_report_path": ".wabblespec/organize/report-<timestamp>.md"
}
```

## A note on common failure modes

1. **Auto-acting on ambiguous moves.** When destination is unclear, classify as CONFIRM. AUTO is for moves where the correct destination is unambiguous.

2. **Missing external references.** Before classifying a move as AUTO, check for imports, receipt references, and framework.yaml entries pointing to the current path. One missed reference breaks the consuming module.
