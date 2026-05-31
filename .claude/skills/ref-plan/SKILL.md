---
name: ref-plan
description: Integration planning from reference research. Takes ref-eval output and produces a phased, prioritized integration plan covering what to adopt, in what order, with risk scoring, explicit exclusions, and execution notes ready for Specify hand-off. Use after ref-eval has run and before implementation begins. ref-comp audits implementation afterward. Triggers on /ref-plan, "plan the integration", "what should we adopt from X", "prioritize the reference learnings", "build an integration plan from ref-eval results", "turn the ref analysis into a work plan", any time the user wants to convert reference research into actionable implementation phases. Do NOT invoke if ref-eval has not yet run for this reference (evaluation must precede planning); do not invoke when the user wants to evaluate whether a reference is worth adopting at all (that is ref-eval, which runs before ref-plan); do not invoke when implementation is already complete and the user wants an audit (that is ref-comp, which runs after implementation).
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
- Section 2 (Benefits We Can Get) -- all High and Medium impact items, plus their `Literal extract` values
- Section 6 (Extraction Plan) -- Phases 1 and 2 items with their exact reference locations
- Low-impact Section 2 items directly relevant to the current project goal

For each candidate item:

| ID | Item | Type | Ref-eval impact | Project fit | Risk | Has literal values |
|---|---|---|---|---|---|---|

**Project fit** -- High = directly serves current active goal. Low = interesting but orthogonal.

**Risk** -- Consider: breaking existing behavior, scope creep, architectural churn, licensing, maintenance burden.

**Has literal values** -- Yes if the ref-eval `Literal extract` field for this item contains specific values (thresholds, enumerations, schemas, rule orderings) that must be preserved exactly. These carry forward into the plan item's `Literal values` field and into ref-comp's fidelity check.

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

### Step 4 -- Assign tiers

Tiers describe what *kind* of change an item is, which determines both risk and effort. Assign each non-excluded item to exactly one tier.

**Tier 1 — Behavioral additions** (no new files, no restructuring): Add a rule, a section, a behavioral constraint to an existing skill or reference file. The target file already exists; the change is purely additive. Lowest risk.

**Tier 2 — Module-level augmentation**: Substantively extend an existing module — new step in the workflow, new sub-protocol, meaningful behavior change. The module's interface is unchanged; its depth increases.

**Tier 3 — New shared infrastructure**: Create a new reference file, schema, or shared script that multiple modules will route to. No new skills; the infrastructure serves existing ones.

**Tier 4 — New module candidates**: Entirely new skill, hook, daemon, or standalone script. Adds capability that does not exist anywhere in the project.

**Tier 5 — Architecture-level**: Cross-cutting changes — new system layers, changed module interfaces, restructured state schemas, additions to the registry. Requires adversarial review before Specify.

**Tier 6 — Synthesis**: Novel patterns that require both the reference's logic AND the current project's existing infrastructure. Not derivable from the reference alone. Requires the intersection. Treat as Tier 5 risk until a prototype validates feasibility.

**Tier 7 — Expansion Roadmap**: Net-new capabilities the project has no version of at all. Sourced from ref-eval Section 9. These are not integration items — they require their own recipe → specify → decompose → executor cycle. Tier 7 items are not implemented by ref-adopt; they are planned, documented, and handed off as future session seeds. Every ref-eval Section 9 "Tier 7 candidate: Yes" item must appear here. Items that appear here without a ref-eval Section 9 source are invalid.

Within each tier, sort by integration_score descending. Tiebreak: lower risk first, then higher project_fit.

Cap guidance: if more than 5 items land in Tier 1, sequence them — do not lower the bar for Tier 2. Tier 5+ items each require explicit user confirmation before implementation starts.

### Step 5 -- Write the integration plan

**Plan path:** `research/ref-plan/<slug>.md`

```markdown
# Integration Plan -- <reference-slug>

**generated_at:** <ISO-8601>
**ref_eval_report:** research/ref-eval/<slug>.md
**risk_appetite:** conservative|balanced|aggressive
**integration_goal:** <stated or inferred>

## Signal Summary

<2-3 sentences. What did ref-eval find? What is the scope? State the verdict classification, how many items were found, how many excluded, and which tiers are populated.>

## Do-Not-Copy List

Items explicitly excluded and the reason. Where the reason is a project invariant, name it.

| Item | Source in ref-eval | Reason | Invariant |
|---|---|---|---|

## Integration Backlog (ranked)

| Rank | ID | Item | Tier | Impact | Risk | Score |
|---|---|---|---|---|---|---|

## Tier 1 — Behavioral Additions

**[Item name]**
- **What:** what to integrate — one sentence, operationally specific
- **Target:** exact file path — `skills/executor/SKILL.md` not "the executor skill"
- **How:** specific enough to act on without re-reading ref-eval or the reference; name the exact section to add, the exact rule to insert, the exact field to append
- **Literal values:** exact thresholds, enumerations, rule orderings, schema fields, or named constants from the reference that must be reproduced verbatim. Quote the source. If none, write "none."
- **Gate:** how to verify this was done correctly — the specific thing ref-comp will check (becomes a fidelity checkpoint)
- **Reference location:** exact file + section heading or line range in the reference

## Tier 2 — Module-Level Augmentation

Same structure as Tier 1.

## Tier 3 — New Shared Infrastructure

Same structure as Tier 1, plus:
- **Consumers:** which existing modules will route to this new file

## Tier 4 — New Module Candidates

Same structure as Tier 1, plus:
- **New artifacts:** list every file to be created with its purpose

## Tier 5 — Architecture-Level

Same structure, plus:
- **Adversarial review required:** yes
- **Breaking change risk:** none / possible / likely
- **Promotion condition:** what must be true before this moves to execution

## Tier 6 — Synthesis

Same structure as Tier 1, plus:
- **Reference contribution:** which exact reference mechanism (file + section) enables this
- **Project contribution:** which exact current project capability (file + artifact) makes this worth doing
- **Feasibility gate:** what would need to be true for this to move to Tier 4 or 5

## Tier 7 — Expansion Roadmap

Items sourced from ref-eval Section 9. Not implemented during this pipeline. Each item is a seed for a future session.

**[Capability name]**
- **What:** one sentence — the net-new capability this would add to the project
- **Reference location:** exact file + section in the reference where this capability lives
- **Why the project lacks it:** the architectural gap or missing module at root cause
- **What it would unlock:** concrete new behavior — not "more flexibility"
- **Dependencies:** what must exist first before this can be built
- **Effort signal:** `days` / `weeks` / `months`
- **Session seed:** one sentence a future session could use as a Recipe input to start this work
- **Memory drawer required:** Yes — call `drawer-writer.py` (do not construct JSON inline):
  ```bash
  python .wabblespec/engine/shared/scripts/drawer-writer.py \
    --topic "OPEN_THREAD: expansion: <capability-name>" \
    --wing references \
    --room <slug> \
    --evidence "capability: <what>; effort: days|weeks|months; session_seed: <seed>; unlocks: <what it would unlock>" \
    --confidence 0.8 \
    --staleness-state FRESH \
    --source "<reference slug>" \
    --source-module ref-plan \
    --actor ref-plan
  ```

After writing all Tier 7 entries, produce an **Expansion Roadmap** summary table:

| Capability | Effort | Dependencies | Session seed |
|---|---|---|---|

Group by effort: near-term (days), medium-term (weeks), long-term (months).

## Watch Only

Not ready: unclear fit, unresolved dependencies, no mitigation path, or dependent on a Tier 5/6 item completing first.

- **Item:** name
- **Why deferred:** concrete reason
- **Promote when:** specific, testable condition

## Priority Implementation Order

Ordered list of all Tier 1–4 items ready to implement now. Includes `Why first` for each.

| Priority | Item | Tier | Target | Why first |
|---|---|---|---|---|

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
  "tier_1_items": 0,
  "tier_2_items": 0,
  "tier_3_items": 0,
  "tier_4_items": 0,
  "tier_5_items": 0,
  "tier_6_items": 0,
  "tier_7_items": 0,
  "watch_only_items": 0,
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

Tier 1–2 items in the Priority table are Specify-ready — run `/recipe` then `/specify` for each, in priority order.
Tier 3–4 items: use `/scope-frame` before `/specify`.
Tier 5–6 items: adversarial review before scoping; user confirms each before implementation starts.

After implementation, run `/ref-comp <slug>` to audit execution fidelity.

## Output contract

| Artifact | Path | Required |
|---|---|---|
| Integration plan | `research/ref-plan/<slug>.md` | Yes |
| Receipt | `.wabblespec/state/receipts/ref-plan-<timestamp>.json` | Yes |

## Common failure modes

1. **Running without ref-eval.** ref-plan has no signal without ref-eval. Do not fabricate a signal pool from first principles.

2. **Vague Target.** "The executor skill" is not a target. `skills/executor/SKILL.md` is. Every item must name the exact file that changes.

3. **Treating exclusions as suggestions.** If a ref-eval "Avoid" item looks valuable, run a new ref-eval with updated context -- do not override the exclusion here. The Do-Not-Copy list is a hard stop.

4. **Vague "how" descriptions.** "Adopt the routing pattern" is not a how. "Add a `## Deviation Rules` section to `skills/executor/SKILL.md` with four rules mapping trigger conditions to actions" is a how.

5. **Misassigning tiers.** Tier 1 = additive to existing file, no new files. If the item creates a new file, it is at least Tier 3. If it creates a new skill, Tier 4. Tier 6 is not a catch-all for hard items — it is specifically for patterns that require both the reference's logic AND the current project's existing infrastructure.

6. **Skipping the Synthesis tier.** Tier 6 items are the most distinctive output of the pipeline. If ref-eval produced a Section 8 with synthesis ideas, every one of those must appear in Tier 6 of ref-plan. Do not drop them.

7. **Scoring before filtering.** Apply exclusion filter before scoring. Items might score high but still be excluded for policy reasons.

8. **No priority table.** The priority table is what turns a tier list into an execution sequence. Without it, the plan has no actionable order.