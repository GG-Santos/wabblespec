# Worktree Rollback Policy (Type 4)

Worktree isolation is the fourth rollback target type. Instead of restoring files after a failed wave, worktree isolation runs a high-risk wave in an isolated git branch from the start. If the wave fails or is rejected, the worktree is discarded — no restoration needed because main was never touched.

## Trigger conditions

Worktree isolation activates when ALL of the following are true:

1. Decompose complexity score ≥ 0.7 (High or Critical scale level)
2. Wave contains at least one irreversible operation: schema migration, data deletion, deploy, or destructive file rename
3. Wave is declared BREAKING (change_class: BREAKING in task card)
4. Git is available in the project environment (RuntimeProbe confirms)

## Creation process

```
1. Decompose declares wave as worktree-eligible (complexity ≥ 0.7 + irreversible operations)
2. Executor creates isolated worktree:
   git worktree add .worktrees/<wave-id> -b wabble/<wave-id>
3. All wave execution occurs inside .worktrees/<wave-id>/
4. Main branch: untouched throughout wave execution
5. If wave passes Verifier: merge to main
   git -C .worktrees/<wave-id> checkout main
   git merge --no-ff wabble/<wave-id>
   git worktree remove .worktrees/<wave-id>
6. If wave fails: discard worktree
   git worktree remove .worktrees/<wave-id> --force
   git branch -D wabble/<wave-id>
   No restoration needed — main was never modified
```

## When worktree is unavailable

If git is not available (RuntimeProbe: no git detected) or the project is not a git repository:
- Fall back to Type 1 (wave checkpoint): write checkpoint before wave, restore after failure
- Note fallback in wave plan and guard receipt
- Do not proceed without some rollback mechanism — wave is blocked if neither worktree nor checkpoint is possible

## Merge policy

Worktree merge to main requires:
- Verifier PASS for the wave
- No CRITICAL findings from Reviewer
- Guard PASS on merge artifacts
- Attestation for BREAKING changes before merge

Never auto-merge a worktree branch. Merge is an explicit action after all gates pass.

## Worktree lifecycle

| State | Action |
|---|---|
| Created | Wave execution begins in worktree |
| Wave passed | Merge to main, remove worktree |
| Wave failed (HARD error) | Discard worktree — no merge |
| Wave partially complete, abandoned | Discard worktree — no merge |
| Merge conflict detected | Surface conflict to human — do not auto-resolve |

## Receipt fields

Rollback receipt for worktree type:
```json
{
  "rollback_type": "worktree",
  "worktree_path": ".worktrees/<wave-id>",
  "branch": "wabble/<wave-id>",
  "wave_id": "<wave-id>",
  "outcome": "merged|discarded",
  "merge_sha": "<sha or null>",
  "attestation_received": true
}
```

## Constraint

Worktree branches must never be pushed to remote without explicit human action. They are local execution sandboxes. Pushing a worktree branch is a SPEC_VIOLATION unless explicitly authorized.
