---
name: ref-plan
description: Integration planning from reference research. Takes ref-eval output and produces a phased, prioritized integration plan: what to adopt, in what order, with risk scoring, explicit exclusions, and execution notes ready for Specify hand-off. Use after ref-eval has run and before implementation begins. ref-comp audits implementation afterward. Trigger on: /ref-plan, "plan the integration", "what should we adopt from X", "prioritize the reference learnings", "build an integration plan from ref-eval results", "turn the ref analysis into a work plan", any time the user wants to convert reference research into actionable implementation phases.
---

# Ref-Plan

You turn reference research into actionable integration work. You read what ref-eval found worth stealing, weigh it against project context and risk, and produce a phased plan specific enough to execute.

You do not evaluate references -- that is ref-eval's job. You do not audit implementation -- that is ref-comp's job, and it runs after implementation is complete. Your output bridges evaluation and execution.

## Execution chain position

```
ref-eval -> ref-plan -> IMPLEMENT -> ref-comp
```

## What this skill does

Reads a ref-eval report. Synthesizes its findings into a ranked integration backlog. Applies an exclusion filter. Assigns remaining items to four phases by impact/risk profile. Writes a phased integration plan with explicit exclusions and execution notes. Delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| ref-plan receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type ref-plan` |

## When to use

- Explicit `/ref-plan <reference-slug>` command
- After ref-eval has run and the verdict was `critical-reference` or `supporting-reference`
- User says: "plan the integration", "what should we adopt from X", "prioritize the reference learnings", "build a work plan from the ref-eval"

**Do not use when:**
- ref-eval has not run for this reference -- ref-plan has no signal without it
- Implementation is already in progress or complete -- use ref-comp to audit what was built
- A ref-plan already exists at `research/ref-plan/<slug>.md` -- check first, ask whether to overwrite or extend

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `reference_slug` | string | yes | The slug from the ref-eval report |
| `ref_eval_report` | path | no | Override path (default: `research/ref-eval/<slug>.md`) |
| `integration_goal` | string | no | What the integration should achieve. Inferred from project context if omitted. |
| `risk_appetite` | `conservative` / `balanced` / `aggressive` | no | Default: `balanced`. Affects phase assignment thresholds. |

## How to do it

### Step 0 -- Load inputs

Read in order:
1. `research/ref-eval/<slug>.md` -- required; fail with a clear message if absent
2. `.wabblespec/state/plans/task-card.md` -- for current project goal (read if exists)
3. `CLAUDE.md` -- for project identity and non-goals
4. Any ref-eval Memory drawers in wing `references`, room `<slug>`

Check for an existing plan at `research/ref-plan/<slug>.md`. If found, ask whether to overwrite or extend. Do not proceed until confirmed.

### Step 1 -- Extract integration signal from ref-eval

Collect all candidate items:
- Section 2 (Benefits We Can Get) -- all High and Medium impact items
- Section 6 (Extraction Plan) -- Phases 1 and 2 items
- Low-impact Section 2 items directly relevant to the current project goal

For each candidate item:

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|

**Project fit** -- High = directly serves current active goal. Low = interesting but orthogonal.

**Risk** -- Consider: breaking existing behavior, scope creep, architectural churn, licensing, maintenance burden.

### Step 2 -- Apply the exclusion filter

Explicitly exclude and record the reason for each:
- All items in ref-eval Section 4 marked "Avoid"
- All items flagged `do_not_copy` by the ReferenceLoad card in the ref-eval report
- Any item with Risk=High AND Project fit=Low
- Any item conflicting with a stated non-goal in task-card.md, scope.md, or CLAUDE.md

The Exclusion List is a hard stop. To reconsider an excluded item, run a new ref-eval -- do not override here.

### Step 3 -- Score and rank the backlog

For each non-excluded item:

```
integration_score = (impact x 2) + project_fit - risk
```

Map: High=3, Medium=2, Low=1. Sort descending. Break ties: lower risk first, then higher project_fit.

### Step 4 -- Assign phases

**Phase 1 -- Safe Wins** (cap: 5 items)

Balanced criteria: Risk=Low AND impact>=Medium, OR Risk=Medium AND impact=High AND no structural module interface changes required.

Conservative: Risk=Low only. Aggressive: Risk=Medium OK even with structural changes.

**Phase 2 -- Targeted Integration** (cap: 8 items)

Balanced criteria: Risk=Medium items not in Phase 1, OR Risk=Low items requiring structural module changes. Each item requires a Specify cycle before execution.

**Phase 3 -- Considered Integration**

Risk=High items surviving exclusion filter, OR Risk=Medium items deferred from Phase 2. Requires adversarial review before Specify. User confirms each item. Flag if more than 5 items land here.

**Phase 4 -- Watch Only**

Not ready: unclear fit, unresolved dependencies, Risk=High with no mitigation path, or dependent on Phase 3 completion. Document the promotion condition for each.

### Step 5 -- Write the integration plan

**Plan path:** `research/ref-plan/<slug>.md`

```markdown
# Integration Plan -- <reference-slug>

**generated_at:** <ISO-8601>
**ref_eval_report:** research/ref-eval/<slug>.md
**risk_appetite:** conservative|balanced|aggressive
**integration_goal:** <stated or inferred>

## Signal Summary

<2-3 sentences. What did ref-eval find? What is the scope? State the verdict classification and how many items were found vs excluded.>

## Exclusion List

| Item | Source in ref-eval | Reason Excluded |
|---|---|---|

## Integration Backlog (ranked)

| Rank | ID | Item | Type | Phase | Impact | Risk | Score |
|---|---|---|---|---|---|---|---|

## Phase 1 -- Safe Wins

**[Item name]**
- **What:** what to integrate
- **Where:** which module, file, or area is affected
- **How:** concrete approach -- specific enough to act on without re-reading ref-eval
- **Gate:** how to verify this was done correctly (becomes a ref-comp checkpoint)
- **Reference location:** exact path or section in the reference

## Phase 2 -- Targeted Integration

Same structure as Phase 1, plus:
- **Specify required:** yes
- **Breaking change risk:** none / possible / likely

## Phase 3 -- Considered Integration

Same structure, plus:
- **Adversarial review required:** yes (for Risk=High items)
- **Promotion condition:** what must be true before this moves to Phase 2

## Phase 4 -- Watch Only

- **Item:** name
- **Why deferred:** concrete reason
- **Promote when:** specific, testable condition

## Execution Notes

<Dependencies between items. Sequencing constraints. Items that must NOT run in parallel. Note: run /ref-comp after implementation is complete to audit execution fidelity.>
```

### Step 6 -- Write receipt

```json
{
  "module": "ref-plan",
  "layer": "L2",
  "reference_slug": "<slug>",
  "ref_eval_verdict": "<critical-reference | supporting-reference | inspiration-only>",
  "integration_goal": "<stated or inferred>",
  "risk_appetite": "conservative|balanced|aggressive",
  "signal_items_found": 0,
  "items_excluded": 0,
  "backlog_size": 0,
  "phase_1_items": 0,
  "phase_2_items": 0,
  "phase_3_items": 0,
  "phase_4_items": 0,
  "plan_path": "research/ref-plan/<slug>.md",
  "status": "PASS | FAIL"
}
```

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type ref-plan \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --target <reference-slug> \
  --requirements "<adopted-item-1>" "<adopted-item-2>" \
  --out .wabblespec/state/receipts/ref-plan-<timestamp>.json
```

## Handoff to execution

Phase 1 items are Specify-ready -- run `/recipe` then `/specify` for each.
Phase 2 items: use `/scope-frame` before `/specify`.
Phase 3 items: adversarial review before scoping.

After implementation, run `/ref-comp <slug>` to audit execution fidelity.

## Output contract

| Artifact | Path | Required |
|---|---|---|
| Integration plan | `research/ref-plan/<slug>.md` | Yes |
| Receipt | `.wabblespec/state/receipts/ref-plan-<timestamp>.json` | Yes |

## Common failure modes

1. **Running without ref-eval.** ref-plan has no signal without ref-eval. Do not fabricate a signal pool from first principles.

2. **Phase 1 overflow.** Cap at 5 items. A bloated Phase 1 is a plan that never starts.

3. **Treating exclusions as suggestions.** If a ref-eval "Avoid" item looks valuable, run a new ref-eval with updated context -- do not override the exclusion here.

4. **Vague "how" descriptions.** "Adopt the routing pattern" is not a how. "Replace the dispatch table in `gateway/routing.py:147` with the two-level routing tree from `reference/src/router.ts:23`" is a how.

5. **Scoring before filtering.** Apply exclusion filter before scoring. Items might score high but still be excluded for policy reasons.

6. **Forgetting to mention ref-comp.** Always note in Execution Notes that ref-comp should run after implementation.