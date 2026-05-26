# Spec Folder — {{project_or_task_name}}

This folder contains specification artifacts for `{{project_or_task_name}}`.

## What lives here

| File | Written by | Purpose |
|---|---|---|
| `task-card.md` | Specify | Acceptance criteria, scope, wave plan |
| `scope.md` | ScopeFrame | Boundary definition |
| `plan-artifact.json` | Plan | Strategic options and chosen approach |
| `wave-plan.md` | Decompose | Step-by-step execution breakdown |
| `receipts/` | All modules | Immutable execution records |

## How to read this spec

Start with `task-card.md`. It contains the goal, acceptance criteria, and wave plan. Every other artifact in this folder is downstream of the task card.

Receipts are append-only. Do not edit receipts.

## Spec lifecycle

```
ScopeFrame → Specify → [Brainstorm] → [Plan] → Decompose → Execute
```

The task card is locked after Decompose approval. Changes to acceptance criteria after that point require a new task card or an explicit amendment with Guard review.

## Ground truth

The task card is the ground truth for this task. If a receipt contradicts the task card, the task card wins. Surface the contradiction to the human before proceeding.
