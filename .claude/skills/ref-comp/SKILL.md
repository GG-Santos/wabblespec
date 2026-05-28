---
name: ref-comp
description: Post-implementation audit against a reference. After implementing changes guided by ref-eval and ref-plan, ref-comp brutally compares what was actually built against what the reference does. Measures execution fidelity: what was implemented correctly, what was missed, what drifted, and what was gained beyond the plan. Writes a structured audit report and Memory drawers for critical misses. Use after implementation is complete to verify how well it tracks the reference. Trigger on: /ref-comp, "compare our implementation to X", "how well did we implement the reference patterns", "did we miss anything from X", "audit the implementation against the reference", after any integration work guided by a reference.
---

# Ref-Comp

You audit implementations against their reference. You do not plan -- that is ref-plan's job, and it runs before implementation. You do not evaluate fit -- that is ref-eval's job, and it runs before planning. You come in after implementation is complete and answer one question: how well did we actually do it?

## Execution chain position

```
ref-eval -> ref-plan -> IMPLEMENT -> ref-comp
```

ref-comp is the final step. Running it before implementation is a different task -- pre-implementation gap analysis belongs in ref-plan's signal synthesis step.

## What this skill does

Takes the current project's implementation and a reference. Optionally reads the ref-plan to understand what was intended. Compares what was built against what the reference does -- section by section, feature by feature. Produces a six-section audit report: implementation coverage, execution gaps, improvements beyond the plan, architecture divergence, quality delta, and verdict. Writes Memory drawers for critical misses. Writes a receipt.

## When to use

- Explicit `/ref-comp <reference>` command after implementation
- User says: "compare our implementation to X", "how well did we implement X", "did we miss anything from the reference", "audit the implementation"
- After any integration work guided by a ref-eval or ref-plan
- As a verification step before closing out an integration task (before Archive)

**Do not use when:**
- Implementation has not started -- run ref-eval and ref-plan first
- A ref-comp report for this reference already exists in Memory and the drawer is FRESH with no new commits since -- return the drawer, write a dedup receipt, stop

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `reference` | string | yes | Path, URL, or ref-eval slug for the reference being compared against |
| `ref_plan_slug` | string | no | Slug of the ref-plan that guided implementation (default: same as reference slug) |
| `scope` | string | no | Sub-area to audit. Default: full project. |
| `focus_areas` | list | no | Dimensions to prioritize: `features`, `architecture`, `testing`, `documentation`, `performance`, `security` |

## How to do it

### Step 0 -- Load context

Read in order:
1. `research/ref-eval/<slug>.md` -- for the reference feature set and trust rating (warn but proceed if absent)
2. `research/ref-plan/<slug>.md` -- for what was intended (warn if absent; without it, Missed vs Deferred distinction is not possible)
3. The reference via ReferenceLoad if no ref-eval card is available
4. `CLAUDE.md` for project identity and current version
5. `.wabblespec/state/plans/task-card.md` if an active task card exists

Check Memory index for a FRESH ref-comp drawer for this reference+scope combination with no new commits since. If found, return it, write a dedup receipt, stop.

Record `ref_plan_available: true|false` in receipt.

### Step 1 -- Map the current implementation

Before comparing, establish what the current project actually has. Read the relevant modules, files, or areas. Do not rely on assumption.

If a ref-plan exists, read its Phase 1 and Phase 2 items -- those are the intended implementation targets for the completed wave.

### Step 2 -- Produce the six-section audit

Every finding must name an exact location in both the current project and the reference. "We don't have this" is only acceptable when the thing genuinely does not exist.

---

#### Section 1 -- Implementation Coverage

For every feature or pattern that ref-plan (or ref-eval's extraction plan) identified for adoption, declare execution status:

| Item | Source (ref-plan phase / ref-eval section) | Status | Our Location | Notes |
|---|---|---|---|---|

Status:
- **Implemented** -- done, works, comparable in quality to the reference pattern
- **Partial** -- started but incomplete, or implemented with significant quality gap
- **Missed** -- was in scope (Phase 1 or Phase 2), not implemented, no documented deferral
- **Deferred** -- was in Phase 3 or Phase 4 of ref-plan, correctly not implemented yet

Do not mark Phase 3/4 items as Missed. If no ref-plan exists, use ref-eval's extraction plan phases.

---

#### Section 2 -- Execution Gaps

For each Missed or Partial item from Section 1:

| Field | Content |
|---|---|
| Item | Name |
| What was planned | What ref-plan or ref-eval said to implement |
| What was built | What actually exists (specific about what is there vs what is not) |
| Gap | The concrete difference between intent and execution |
| Impact | What breaks, degrades, or is weaker as a result |
| Severity | Critical / Major / Minor |
| Recoverable | Yes / Needs rework / Needs redesign |

Order by Severity descending.

Severity: Critical = breaks a core integration goal or security/reliability gap. Major = degrades important functionality. Minor = quality-of-life issue only.

---

#### Section 3 -- Improvements Beyond the Plan

Where the implementation went further than ref-plan specified, or adapted a reference pattern better for this project:

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|

Mark each as "protect" if future integration could threaten it.

---

#### Section 4 -- Architecture Divergence

Structural differences that are not simple feature gaps:

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|

Intentional divergences planned via ref-plan exclusions are expected. Unintentional divergences not in the exclusion list warrant flagging.

---

#### Section 5 -- Quality Delta

| Dimension | Reference (1-10) | Ours (1-10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | | | | |
| Error handling | | | | |
| Documentation | | | | |
| Naming clarity | | | | |
| Dependency hygiene | | | | |

Scores are comparative. Explain any delta of +/-3 or greater with a specific example.

---

#### Section 6 -- Verdict

- **Coverage rate:** N of M planned items implemented (%)
- **Execution gaps:** N critical, M major, P minor
- **Improvements beyond plan:** N
- **Overall execution classification:** `complete` / `substantially-complete` / `partially-complete` / `significantly-incomplete`
- **Top 3 gaps to close** (with severity and location)
- **Top 3 wins to protect** (with location)
- **Recommended next action:** complete/substantially-complete = Archive; partially-complete = follow-up wave; significantly-incomplete = re-evaluate ref-plan

---

### Step 3 -- Write Memory drawers

For each Critical or Major execution gap: write one drawer in wing `references`, room `<slug>-comp`. Set `staleness_state: FRESH`. Include `gap_severity`, `feature`, and `recoverable`.

For each protected win from Section 3: write one drawer in the same room, tagged `type: win`.

### Step 4 -- Write report and receipt

**Report path:** `research/ref-comp/<reference-slug>[-<scope>].md`

**Receipt:**

```json
{
  "module": "ref-comp",
  "layer": "L2",
  "reference": "<path, URL, or slug>",
  "reference_slug": "<slug>",
  "scope": "<full or sub-area>",
  "ref_plan_available": true,
  "ref_eval_available": true,
  "dedup_hit": false,
  "coverage_rate": 0.0,
  "execution_gaps": { "critical": 0, "major": 0, "minor": 0 },
  "improvements_beyond_plan": 0,
  "execution_classification": "complete | substantially-complete | partially-complete | significantly-incomplete",
  "report_path": "research/ref-comp/<slug>.md",
  "drawers_written": 0,
  "confidence": 0.0,
  "status": "PASS | FAIL"
}
```

Write receipt to `.wabblespec/state/receipts/ref-comp-<timestamp>.json`.

## Output contract

| Artifact | Path | Required |
|---|---|---|
| Audit report | `research/ref-comp/<slug>[-scope].md` | Yes |
| Receipt | `.wabblespec/state/receipts/ref-comp-<timestamp>.json` | Yes |
| Memory drawers | `.wabblespec/state/memory/wings/references/rooms/<slug>-comp/` | When Critical or Major gaps exist |

## Common failure modes

1. **Running before implementation.** ref-comp measures execution fidelity. If implementation has not happened, this is a gap analysis, not an audit -- different framing, different value.

2. **Penalizing deferred items.** Phase 3 and Phase 4 items are correctly not implemented yet. Mark them Deferred, not Missed. Conflating the two inflates severity counts.

3. **Ignoring improvements beyond the plan.** The implementation may have done something better than the reference. Surface these -- they are evidence of good judgment and should not be reversed in future cycles.

4. **Vague gap descriptions.** "Error handling is weaker" is not a gap. "Reference `src/executor/retry.ts:47` implements exponential backoff with jitter; our `executor.py` has a bare `except: pass` at line 88 with no retry" is a gap.

5. **Not reading the ref-plan.** Without ref-plan you cannot distinguish Missed from Deferred. Always check for it first. If absent, warn the user -- the audit will be less precise.