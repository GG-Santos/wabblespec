---
name: handoff
description: Writes a session continuity document so a fresh agent or a new session can pick up ongoing work without re-reading the full conversation. Use when context is approaching compaction, handing off to another session, or when the user says "write a handoff" or "summarize for the next session".
---

# Handoff

You write a compact session continuity document to a temp file. You do not duplicate content that already exists in task cards, receipts, or ADRs — you reference those artifacts by path and add only what is not captured elsewhere. The document must be readable by a fresh agent with no prior context.

## What this skill does

Summarizes active task state, completed and pending waves, current blockers, and recommended next skill. References existing artifacts (task-card.md, receipts, scope.md) by path rather than re-stating their contents. If the user specifies what the next session will focus on, tailors the document accordingly. Does not modify any existing artifact.

## When to use

- Context is approaching compaction limits and the current task is not complete
- Handing off to another session or another agent instance
- User says "write a handoff," "summarize for the next session," or similar

## When NOT to use

- The current task is complete — Archive is the right closure artifact, not a handoff document
- The goal is to document decisions permanently — use an ADR or the decisions.md artifact in the task plans
- The user wants a summary of what was done — that is an archive or a commit message, not a handoff

---

## Process

### Step 1 — Read current state

Read in this order:
1. `.wabblespec/state/plans/task-card.md` — active task goal and acceptance criteria
2. `.wabblespec/state/plans/current-wave-plan.md` — wave plan and completion status
3. `.wabblespec/state/session/state.json` — session state if available
4. Most recent receipts in `.wabblespec/state/receipts/` — determine which waves have receipts (PASS) and which are pending

Identify: completed waves, current wave, blockers, next recommended action.

### Step 2 — Write the handoff document

Save to a temp path using: `mktemp -t handoff-XXXXXX.md` (or equivalent on Windows: `$env:TEMP\handoff-$(Get-Random).md`). Read the file before writing to it.

Document structure:

```markdown
# Handoff — <task goal, one line>

**Task card:** .wabblespec/state/plans/task-card.md  
**Wave plan:** .wabblespec/state/plans/current-wave-plan.md  
**Session date:** <ISO-8601>

## Current state

<2-4 sentence summary of where things stand. What was accomplished. What is blocking progress, if anything.>

## Completed waves

- Wave N: <name> — PASS (<receipt path>)

## Pending waves

- Wave N+1: <name> — <status or blocker>

## Next action

**Recommended skill:** <skill name>  
**Reason:** <one sentence explaining why this is next>

## Open questions

<Only include if there are unresolved questions that the next session must address before proceeding. Otherwise omit this section.>

- <question>: <what is known, what is not>
```

Do not duplicate: the full task card, the full wave plan, the contents of receipts. Reference them by path.

If the user specified what the next session will focus on: add a `## Focus for next session` section and tailor the document to that context.

### Step 3 — Surface the path

Report the file path to the user. Suggest the next skill explicitly.

## Outputs

- A handoff document written to a temp path (mktemp or equivalent) referencing active task card, completed waves, pending waves, blockers, and recommended next skill
- The file path surfaced to the user
