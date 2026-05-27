# Merge Policy

Sync may auto-merge MINOR divergences. MAJOR divergences require human review or explicit escalation.

## Auto-merge rules (MINOR only)

Auto-merge is allowed when all of the following are true:
- Divergence class is MINOR
- One spec is a strict superset of the other (no contradictions, only additions)
- The superset spec has a more recent timestamp
- No field is being removed from the merged result

**Auto-merge action:** Take the superset spec as the merged result. Record `auto_merged: true`, `conflicts_resolved: N`.

## Manual merge rules (MAJOR)

When divergence is MAJOR, Sync produces a conflict report and halts. `human_review_required: true`.

The conflict report lists for each conflict:
- Location A (file + section)
- Location B (file + section)
- Nature of conflict (type mismatch / contradictory rule / missing required field)
- Recommended resolution (if determinable)

Sync does not choose between two contradictory required behaviors. That is a human decision.

## Escalation

If more than 5 MAJOR conflicts exist across the reconciled spec set, escalate rather than listing each individually. `merge_strategy: escalated`. Surface to human with a summary: N major conflicts across M files require decisions before merge can proceed.

## Post-merge validation

After any merge (auto or manual), run a basic consistency check:
- All required fields still present in merged result
- No duplicate field declarations
- No contradictory enum values
- Timestamps updated on merged artifacts

Record `conflicts_resolved: N` and `conflicts_escalated: N` in receipt.

## Merge order precedence

When merging specs of the same type with overlapping scope:
1. Locked decisions (PHASE-0-DECISIONS.md or equivalent) — always win
2. More recent timestamp — wins over older on non-locked items
3. More specific scope (module-level spec) — wins over broader (framework-level spec) for module-specific claims
4. Explicit supersedes annotation in frontmatter — overrides timestamp order
