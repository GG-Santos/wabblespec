---
name: ref-comp
description: Post-implementation audit against a reference. After implementing changes guided by ref-eval and ref-plan, ref-comp brutally compares what was actually built against what the reference does. Measures execution fidelity across what was implemented correctly, what was missed, what drifted, and what was gained beyond the plan. Writes a structured audit report and Memory drawers for critical misses. Use after implementation is complete to verify how well it tracks the reference. Triggers on /ref-comp, "compare our implementation to X", "how well did we implement the reference patterns", "did we miss anything from X", "audit the implementation against the reference", after any integration work guided by a reference. Do NOT invoke if implementation has not yet started (run ref-eval then ref-plan first; ref-comp only audits completed work); do not invoke when the user wants to evaluate a new reference for adoption (that is ref-eval, which runs before planning); do not invoke when the user wants to plan which parts of a reference to adopt (that is ref-plan, which runs before implementation).
---

# Ref-Comp

You audit implementations against their reference. You do not plan -- that is ref-plan's job, and it runs before implementation. You do not evaluate fit -- that is ref-eval's job, and it runs before planning. You come in after implementation is complete and answer one question: how well did we actually do it?

## Execution chain position

```
ref-eval -> ref-plan -> IMPLEMENT -> ref-comp
```

ref-comp is the final step. Running it before implementation is a different task -- pre-implementation gap analysis belongs in ref-plan's signal synthesis step.

## What this skill does

Takes the current project's implementation and a reference. Optionally reads the ref-plan to understand what was intended. Compares what was built against what the reference does -- section by section, feature by feature. Produces a six-section audit report: implementation coverage, execution gaps, improvements beyond the plan, architecture divergence, quality delta, and verdict. Writes Memory drawers for critical misses. Delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| ref-comp receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type ref-comp` |

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

### Step 1 -- Map the current implementation at full depth

Before comparing, read every file that ref-plan targeted. Do not rely on assumption or memory of what was implemented. For each targeted file:

- Read it fully
- Note what was added, changed, or left untouched
- For items that have `Literal values` in ref-plan: locate exactly where those values appear in the current implementation

If a ref-plan exists, read its Tier 1 and Tier 2 items — those are the intended implementation targets. Note every `Literal values` field: these become the fidelity checkpoints in Step 1a.

### Step 1a -- Literal fidelity pre-check

Before the full six-section audit, run a literal fidelity check on every item that had `Literal values` in ref-plan. This catches wrong-value failures that the feature-level audit misses — a rule present but with the wrong threshold, a schema present but missing a required field, a list present but with items omitted.

For each literal value item:

| Item | Literal value required | Literal value present | Fidelity | Notes |
|---|---|---|---|---|

Fidelity:
- **Exact** — matches the reference verbatim
- **Adapted** — intentionally changed with documented reason (record the reason)
- **Corrupted** — present but wrong (wrong count, wrong threshold, missing items from an enumeration)
- **Absent** — the feature exists but the literal value was not encoded at all
- **Missing** — the feature does not exist (escalates to Section 2 gap)

Corrupted and Absent are distinct from Missing — they indicate the pattern was partially adopted but the detail was lost. These are often harder to catch than outright missing features and cause subtle behavioral divergence.

### Step 2 -- Produce the six-section audit

Every finding must name an exact location in both the current project and the reference. "We don't have this" is only acceptable when the thing genuinely does not exist.

---

#### Section 1 -- Implementation Coverage

For every feature or pattern that ref-plan (or ref-eval's extraction plan) identified for adoption, declare execution status and fidelity:

| Item | Source (ref-plan tier / ref-eval section) | Status | Fidelity | Our Location | Notes |
|---|---|---|---|---|---|

Status:
- **Implemented** -- done, works, comparable in quality to the reference pattern
- **Partial** -- started but incomplete, or implemented with significant quality gap
- **Missed** -- was in scope (Tier 1 or Tier 2), not implemented, no documented deferral
- **Deferred** -- was in Tier 3–6 or Watch Only of ref-plan, correctly not implemented yet

Fidelity (only for Implemented or Partial):
- **Exact** -- literal values and logic match the reference
- **Adapted** -- intentionally changed with documented reason
- **Corrupted** -- present but with wrong values, missing enumeration items, incorrect thresholds
- **Absent** -- feature present, literal values not encoded

Do not mark Tier 3–6 items as Missed. If no ref-plan exists, use ref-eval's extraction plan phases.

---

#### Section 2 -- Execution Gaps

For each Missed, Partial, Corrupted, or Absent item from Section 1:

| Field | Content |
|---|---|
| Item | Name |
| Gap type | Missing feature / Wrong value / Incomplete enumeration / Missing edge case / Absent literal / Broken connection |
| What was planned | What ref-plan or ref-eval said to implement, including exact literal values |
| What was built | What actually exists — specific about what is present vs. absent |
| Gap | The concrete difference. For Wrong value: state reference value and actual value. For Incomplete enumeration: list the missing items. For Missing edge case: state which condition is unhandled. |
| Impact | What breaks, degrades, or behaves differently as a result |
| Severity | Critical / Major / Minor |
| Recoverable | Yes / Needs rework / Needs redesign |

Order by Severity descending.

Gap types explained:
- **Missing feature** — the entire item was not implemented
- **Wrong value** — a threshold, count, or constant was implemented with a different value than the reference
- **Incomplete enumeration** — a list was implemented but items were omitted (e.g., banned phrases list is missing 4 of 12 entries)
- **Missing edge case** — the main path works but a specific condition the reference handles is unhandled
- **Absent literal** — the logic is present but the specific value from the reference was not encoded (e.g., "5+ reads" implemented as "many reads")
- **Broken connection** — the feature was implemented but not wired to the component that depends on it

Severity: Critical = breaks a core integration goal or security/reliability gap. Major = degrades important functionality or introduces silent behavioral divergence. Minor = quality-of-life issue only.

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

#### Section 7 -- Synthesis Coverage

Tier 6 items from ref-plan are the highest-value output of the pipeline — novel patterns that required both the reference's logic and this project's specific infrastructure. They are also the most commonly skipped during implementation. Audit each one explicitly.

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|

Status:
- **Implemented** — the novel pattern exists and leverages both the reference mechanism and the current project infrastructure as described
- **Partial** — one side of the synthesis is present; the integration is incomplete
- **Missed** — not implemented; was in scope
- **Deferred** — explicitly pushed to a later wave with documented reason

For each Missed or Partial: state which half of the synthesis is missing (reference contribution or project contribution) and what restoring it would require.

---

#### Section 8 -- Expansion Handoff Audit

Tier 7 items from ref-plan are expansion opportunities — net-new capabilities the project has no version of. They are explicitly NOT implemented during the integration cycle. This section does not check whether they were built. It checks whether they were properly surfaced and handed off for future sessions.

For each Tier 7 item in ref-plan:

| Capability | Surfaced in ref-eval S9 | Drawer written | Session seed present | Status |
|---|---|---|---|---|

Status:
- **Handed off** — memory drawer exists, session seed is written, effort signal is recorded
- **Partial handoff** — item listed in ref-plan Tier 7 but missing drawer or session seed
- **Dropped** — appeared in ref-eval Section 9 as a Tier 7 candidate but absent from ref-plan Tier 7
- **N/A** — ref-plan had no Tier 7 items (state explicitly; this is valid when the reference has no net-new capabilities)

For each Dropped item: state which ref-eval Section 9 entry was lost and whether it should be restored to ref-plan Tier 7 in a follow-up.

**The expansion audit is the pipeline's forward-looking close.** Tier 6 coverage asks "did we build what we synthesized?" Tier 7 handoff asks "did we preserve what we discovered so the project can grow from it?" Both questions must be answered before closing a ref-adopt run.

---

### Step 3 -- Write Memory drawers

For each Critical or Major execution gap and each protected win from Section 3, write a drawer in wing `references`, room `<slug>-comp`. Delegate to `drawer-writer.py` — do not construct drawer JSON inline.

```bash
# Gap drawer
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "OPEN_THREAD: gap: <feature>" \
  --wing references \
  --room <slug>-comp \
  --evidence "gap_severity: Critical|Major; feature: <name>; recoverable: true|false; detail: <description>" \
  --confidence 0.9 \
  --staleness-state FRESH \
  --source "<reference slug>" \
  --source-module ref-comp \
  --actor ref-comp

# Win drawer
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "WORKING_SOLUTION: win: <feature>" \
  --wing references \
  --room <slug>-comp \
  --evidence "type: win; detail: <description>" \
  --confidence 0.9 \
  --staleness-state FRESH \
  --source "<reference slug>" \
  --source-module ref-comp \
  --actor ref-comp
```

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
  "synthesis_items_total": 0,
  "synthesis_items_implemented": 0,
  "execution_classification": "complete | substantially-complete | partially-complete | significantly-incomplete",
  "report_path": "research/ref-comp/<slug>.md",
  "drawers_written": 0,
  "confidence": 0.0,
  "status": "PASS | FAIL"
}
```

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type ref-comp \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --target <reference-slug> \
  --summary "<verdict>" \
  --confidence <coverage-score-0.0-1.0> \
  --out .wabblespec/state/receipts/ref-comp-<timestamp>.json
```

## Output contract

| Artifact | Path | Required |
|---|---|---|
| Audit report | `research/ref-comp/<slug>[-scope].md` | Yes |
| Receipt | `.wabblespec/state/receipts/ref-comp-<timestamp>.json` | Yes |
| Memory drawers | `.wabblespec/state/memory/wings/references/rooms/<slug>-comp/` | When Critical or Major gaps exist |

## Common failure modes

1. **Skipping Step 1a (literal fidelity pre-check).** Feature-level coverage checks miss wrong-value and incomplete-enumeration gaps. A rule list with 8 of 12 items looks "implemented" at the feature level. Step 1a catches it before the full audit begins.

2. **Running before implementation.** ref-comp measures execution fidelity. If implementation has not happened, this is a gap analysis, not an audit -- different framing, different value.

3. **Penalizing deferred items.** Tier 3–6 and Watch Only items are correctly not implemented yet. Mark them Deferred, not Missed. Conflating the two inflates severity counts.

4. **Ignoring improvements beyond the plan.** The implementation may have done something better than the reference. Surface these -- they are evidence of good judgment and should not be reversed in future cycles.

5. **Calling a wrong value "Minor" by default.** A wrong threshold can produce subtly incorrect behavior that only surfaces in edge cases. Assess impact on behavior before assigning severity — some wrong values are Critical.

6. **Vague gap descriptions.** "Error handling is weaker" is not a gap. "Reference `src/executor/retry.ts:47` implements exponential backoff with jitter; our `executor.py` has a bare `except: pass` at line 88 with no retry" is a gap. For Wrong value gaps: "Reference specifies 5+ consecutive reads as the paralysis threshold; implementation uses an unspecified vague 'many reads' with no numeric gate" is a gap.

7. **Not reading the ref-plan.** Without ref-plan you cannot distinguish Missed from Deferred, or know which items had literal values that required fidelity checking. Always check for it first. If absent, warn the user -- the audit will be less precise.