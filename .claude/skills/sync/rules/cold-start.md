# Cold-Start Behavior — Sync

Defines what Sync does when its divergence sources or merge policy are absent.

## Absent: sync target declaration

Condition: Sync invoked without declaring what to synchronize.
Action: Surface: "Sync requires a declared target: two spec versions, a spec and implementation, or two module states."
Do NOT: Infer what to sync from context.

## Absent: divergence-detection.md

Condition: `rules/divergence-detection.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md divergence detection rules. Log: "divergence-detection.md missing — using SKILL.md defaults."

## Absent: merge-policy.md

Condition: `rules/merge-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md merge policy rules. Log: "merge-policy.md missing — using SKILL.md defaults."

## Absent: one side of the sync pair

Condition: Sync target A exists but target B (the second item to sync against) is absent or 404.
Action: BLOCK Sync. Surface: "Sync requires both targets. [B] not found at declared path."
Do NOT: Proceed with one-sided sync.

## Absent: conflict resolution policy

Condition: Divergence detected between A and B but no declared winner or merge strategy.
Detection: Conflicting declarations with no resolution rule.
Action: Surface each conflict individually for human resolution. Do NOT auto-resolve conflicts.
Do NOT: Silently prefer one side.

## Default state on cold start

| Field | Default |
|---|---|
| `source_a` | Not declared — must be specified |
| `source_b` | Not declared — must be specified |
| `conflict_count` | 0 — populated during divergence detection |
| `auto_merge` | false — conflicts require human resolution |
| `diff_required` | true — divergences shown before any merge action |
| `idempotent` | true — syncing already-synced targets produces no changes |
