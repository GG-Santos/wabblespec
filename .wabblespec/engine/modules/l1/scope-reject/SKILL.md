---
name: scope-reject
description: Records a rejected enhancement or Tier 7 proposal as a durable concept-level rejection entry so the reasoning survives beyond the current session. Use when declining a feature idea, deferring a Tier 7 expansion indefinitely, or closing a proposal as out-of-scope with reasoning the project should remember.
---

# Scope-Reject

You write a persistent rejection record for an enhancement or expansion idea. You do not evaluate whether the decision is correct — you record the decision and the reasoning so future sessions do not re-litigate the same proposal from scratch.

## What this skill does

Creates or updates a concept-level rejection file in `.wabblespec/state/evolution/out-of-scope/`. One file per concept (not per session). Before writing, checks whether a matching concept already exists and appends to it rather than creating a duplicate. Does not close issues, block future proposals, or mark the idea as permanently rejected — the maintainer may reconsider at any time by deleting the file.

Not guaranteed: This skill records the rejection; the decision to reject belongs to the maintainer. A future session that sees a prior rejection should surface it and ask for confirmation before re-proposing.

## When to use

- An enhancement idea is rejected with a specific, durable reason (not "too busy right now")
- A Tier 7 expansion item is deferred indefinitely with documented reasoning
- User says "remember that we decided not to do X because Y"
- Triage routes an enhancement to `wontfix` and the reasoning should persist

## When NOT to use

- The rejection is temporary ("not this sprint") — deferrals without durable reasoning belong in the task backlog, not here
- The idea is in active consideration — only write after the decision is final
- The file is being created to block a future proposal — this knowledge base informs, it does not block

---

## Process

### Step 1 — Identify the concept name

Derive a short kebab-case name for the concept being rejected. The name should be recognizable to someone browsing the directory: `dark-mode`, `plugin-system`, `graphql-api`, `auto-archiving`. One file per concept — if multiple proposals address the same idea, they belong in the same file.

Check `.wabblespec/state/evolution/out-of-scope/` for an existing file with a matching concept before creating a new one. Matching is by concept similarity, not filename — "night theme" matches `dark-mode.md`.

### Step 2 — Write the rejection record

Create or update `.wabblespec/state/evolution/out-of-scope/<concept-name>.md`.

File format:

```markdown
# <Concept Name>

<1-3 sentence description of what was proposed.>

## Why this is out of scope

<Substantive reason. Reference project scope or philosophy, technical constraints, or strategic decisions. Must be durable — avoid reasons that will expire ("too busy", "not yet"). The reason should still make sense six months from now.>

## Prior requests

- <session-id or date> — "<brief description of the proposal>"
```

If the file already exists: append the new session/date to the `## Prior requests` list. Do not rewrite the existing reason — if the reason has changed, update it explicitly and note the change.

### Step 3 — Confirm

Report the file path written, the concept name, and the reason recorded. If this was an update to an existing file, report how many prior requests now exist.

---

## Reference Routing

| Situation | Reference |
|---|---|
| Triage wontfix for enhancements | `triage` SKILL.md — routes wontfix enhancements to scope-reject |
| Checking prior rejections at triage intake | Read all files in `.wabblespec/state/evolution/out-of-scope/` at triage start; match by concept similarity |

## Outputs

- A new or updated `.wabblespec/state/evolution/out-of-scope/<concept-name>.md` file with concept description, durable reason, and prior requests list
- Confirmation to user of the file path written, concept name, and reason recorded

## When to reconsider

If a maintainer changes their mind:
- Delete the `.wabblespec/state/evolution/out-of-scope/<concept>.md` file
- The new proposal proceeds through normal triage
- Old sessions that proposed the idea are historical record only
