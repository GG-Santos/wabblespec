# Ref-Plan: anthropic-skills-main

**Date:** 2026-05-31  
**Slug:** anthropic-skills-main  
**Classification:** supporting-reference (7/10)

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk | Integration score |
|---|---|---|---|---|---|---|
| A | Grader dual mandate (pressure scenario quality check) | Behavioral addition | High | High | Low | 8 |
| B | WHY over MUST writing guidance | Behavioral addition | High | High | Low | 8 |
| C | Three-level loading reasoning | Format addition | High | High | Low | 8 |
| D | Undertrigger calibration note | Behavioral addition | High | High | Low | 8 |
| E | 60/40 train/test anti-overfitting rule | Behavioral addition | Medium | Medium | Low | 5 |
| F | Subagent timing capture note | Behavioral addition | Low | Medium | Low | 3 |

---

## Exclusion List

| Item | Reason |
|---|---|
| All model name strings from claude-api/SKILL.md | I6: vendor-neutral runtime — no model names in framework files |
| run_loop.py `--model <model-id>` flag | I6 adjacent — embeds vendor model ID in framework operation |
| AskUserQuestion tool patterns | Prior ref-adopt directive (oh-my-claudecode evaluation, 2026-05-30) |
| skill-creator viewer/server infrastructure | Browser + Node.js dependency; incompatible with WabbleSpec CLI context |
| agentskills.io / modelcontextprotocol.io live URLs | External dependency in SKILL.md files |
| brand-guidelines Anthropic colors | Anthropic-specific; non-transferable |

---

## Tier 1 — Behavioral Additions (additive to existing files, no new files)

### Item A: Pressure Scenario Quality Check in skill-tdd

**What:** Add `## Pressure Scenario Quality Check` section to skill-tdd SKILL.md (and engine module), immediately after Step 4 (Compute delta and verdict). Three checks after delta is computed.

**Where:** `.claude/skills/skill-tdd/SKILL.md` (and `.wabblespec/engine/modules/l6/skill-tdd/SKILL.md`)

**How:** Insert a new section `## Pressure Scenario Quality Check` with three checks:
1. **Non-discriminating check:** If baseline_pass_rate > 0 for a scenario, flag it — a scenario that passes without the skill is non-discriminating and inflates baseline, compressing the apparent delta.
2. **Coverage gap check:** After reviewing baseline transcripts, note any compliance failures observed that had no pressure scenario explicitly targeting them — those failures are signal the scenario set is incomplete.
3. **Verifiability check:** For each scenario, confirm the compliance judgment can be made from observable behavior (not just from the model's stated intent).

**Gate:** Section present in SKILL.md with three named checks; engine module updated to match.

**Reference location:** `skills/skill-creator/agents/grader.md §6: Critique the Evals`

---

### Item B: WHY over MUST Writing Guidance

**What:** Add authoring guidance paragraph to CLAUDE.md under the existing skill authoring conventions section.

**Where:** `~/.claude/CLAUDE.md` — append to the existing `## Skill Authoring Conventions` block

**How:** Insert after the existing "Negative triggers are mandatory" entry: "**Prefer explaining reasoning over capitalized directives.** When writing SKILL.md instructions, explain *why* a rule matters rather than issuing capitalized MUST/ALWAYS/NEVER/CRITICAL commands. Empirical evidence from Anthropic's skill-creator: models given the WHY handle edge cases that flat directives miss; ALWAYS/NEVER in all caps is a yellow flag that the rule needs better motivation, not stronger emphasis."

**Gate:** New paragraph present in CLAUDE.md under skill authoring conventions; contains "yellow flag" phrasing.

**Reference location:** `skills/skill-creator/SKILL.md §Writing Style`

---

### Item C: Three-Level Loading Reasoning

**What:** Add loading tier reasoning to CLAUDE.md skill authoring, reinforcing the existing 500-line guideline.

**Where:** `~/.claude/CLAUDE.md` — append to skill authoring conventions block

**How:** Insert after the "description: must end with a period" entry: "**Skill content has three loading tiers with distinct budget rules.** Tier 1 — frontmatter metadata (name + description): always in context, budget ~100 words; this is the only thing the routing decision reads. Tier 2 — SKILL.md body: loaded when skill activates, budget <500 lines; put the operational instructions here. Tier 3 — bundled resources (scripts/, references/, assets/): loaded or executed on demand, unlimited; offload reference material, large schemas, and scripts here rather than inlining them. When the SKILL.md body approaches 500 lines, promote content to Tier 3 with an explicit routing pointer — do not simply truncate."

**Gate:** Paragraph present with three tiers named and the 500-line promote-to-Tier-3 rule stated.

**Reference location:** `skills/skill-creator/SKILL.md §Progressive Disclosure`

---

### Item D: Undertrigger Calibration Note

**What:** Add one sentence to CLAUDE.md description authoring guidance explaining WHY descriptions need to describe complex use cases.

**Where:** `~/.claude/CLAUDE.md` — append to description guidance (near the existing "description: must end with a period" rule)

**How:** Add: "**Description must describe complex multi-step use cases, not simple single-step queries.** The triggering mechanism only activates when the model judges it would benefit from consulting the skill. A description calibrated for a simple one-step query ('apply brand guidelines') will undertrigger — the model handles simple requests directly without loading skills. Describe the complex or specialized scenario where the skill is necessary."

**Gate:** Sentence present referencing complex multi-step use cases; engine module scan clean.

**Reference location:** `skills/skill-creator/SKILL.md §How skill triggering works`

---

## Tier 1 continued — Item E

### Item E: 60/40 Train/Test Anti-Overfitting Rule

**What:** Add one sentence to CLAUDE.md description optimization guidance.

**Where:** `~/.claude/CLAUDE.md` — append to skill authoring conventions block

**How:** Add: "**When evaluating description effectiveness against an eval set, split 60% train / 40% held-out test; always select the best description by test score, not train score.** Selection by train score overfits the description to the eval set and produces a description that triggers on the test queries but not on real user queries."

**Gate:** Sentence present with 60/40 split and "test score not train score" stated.

**Reference location:** `skills/skill-creator/SKILL.md §Description Optimization §Step 3`

---

## Tier 2 — Module-level Augmentation

### Item F: Subagent Timing Capture in skill-tdd

**What:** Add a note to skill-tdd SKILL.md Step 5 (Report) about capturing subagent timing from task notifications.

**Where:** `.claude/skills/skill-tdd/SKILL.md` (and engine module)

**How:** Add to Step 5 — Report: "Also capture `total_tokens` and `duration_ms` from each subagent's task completion notification immediately upon receipt. These are not persisted elsewhere and are permanently lost if not captured at notification time. Include in the report as `baseline_tokens`, `baseline_duration_ms`, `compliance_tokens`, `compliance_duration_ms`."

**Gate:** Note present in Step 5; references `total_tokens`/`duration_ms` from task notification.

**Reference location:** `skills/skill-creator/SKILL.md §Step 3: As runs complete, capture timing data`

---

## Tier 6 — Synthesis (Watch Only — require prototype before implementing)

| Synthesis Idea | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Pressure scenario quality gate in skill-tdd | grader dual mandate: critique assertions | skill-tdd two-pass infrastructure | skill-tdd SKILL.md | Already captured as Item A above (Tier 1) — partially a synthesis item |
| Undertrigger score in quality-floor-check | Undertrigger empirical pattern: simple queries don't trigger | quality-floor-check.py Gate 1 | `.wabblespec/engine/shared/scripts/quality-floor-check.py` | Gate 1 checks structure but not trigger effectiveness |
| Iteration lineage receipt in evolution chain | history.json: version/parent/pass_rate/is_current_best chain | receipt-writer.py receipt chain | New `skill-iteration` receipt type | Skill improvements have no chain linking version-to-version |

---

## Tier 7 — Expansion Roadmap

| Capability | Effort | Session seed |
|---|---|---|
| Description optimization pipeline | weeks | Build vendor-neutral description eval runner: given skill path + 20-query eval set (should_trigger bool), run each with/without skill using subagent, compute trigger rate, iterate 5x with Guard-proposed improvements, enforce 60/40 train/test split, return best_description by test score. Store in `.wabblespec/state/experiments/desc-opt/<skill-name>/`. Drawer: `anthropic-skills-main/description-optimization-pipeline.json` |
| Aggregate benchmark viewer | weeks | Build CLI-compatible benchmark summary reporter: read benchmark.json schema (with_skill vs without_skill, mean ± stddev, delta), produce static Markdown or HTML report comparing iterations. Does NOT require browser or Node.js — static file output. Drawer: pending |

---

## Do-Not-Copy List

| Item | Invariant | Source |
|---|---|---|
| `claude-opus-4-7`, `claude-sonnet-4-6`, and all model ID strings | I6: no model names in framework files | `skills/claude-api/SKILL.md` throughout |
| `--model <model-id-powering-this-session>` in run_loop.py | I6 adjacent: vendor-specific runtime assumption | `skills/skill-creator/SKILL.md §Description Optimization §Step 3` |
| AskUserQuestion tool patterns | Prior ref-adopt directive (2026-05-30 oh-my-claudecode evaluation) | `skills/claude-api/SKILL.md §Language Detection`, `skills/doc-coauthoring/SKILL.md` |
| agentskills.io external URL | External dependency in skill files | `spec/agent-skills-spec.md`, `skills/skill-creator/SKILL.md` |

---

## Priority Implementation Order

| Order | Item | Why first |
|---|---|---|
| 1 | B: WHY over MUST | Highest leverage — affects all future SKILL.md authoring; pure CLAUDE.md addition with zero risk |
| 2 | C: Three-level loading reasoning | Reinforces existing rule with WHY; CLAUDE.md addition; zero risk |
| 3 | D: Undertrigger calibration | Hardens description authoring; CLAUDE.md addition; zero risk |
| 4 | E: 60/40 train/test | Forward-looking rule for description eval; CLAUDE.md addition |
| 5 | A: Pressure scenario quality check | skill-tdd SKILL.md addition; requires engine module sync |
| 6 | F: Timing capture note | skill-tdd SKILL.md addition; requires engine module sync |

---

## Execution Notes

- Items B, C, D, E all target `~/.claude/CLAUDE.md` — apply in one pass to avoid multiple reads
- Items A and F both target `skill-tdd/SKILL.md` — apply in one pass; sync engine module immediately after each `.claude/skills/` edit (engine path: `.wabblespec/engine/modules/l6/skill-tdd/SKILL.md`)
- Items B-E do not depend on each other and can be written as one compound edit to CLAUDE.md
- Item A and F can be written as one compound edit to skill-tdd SKILL.md
- No items conflict with each other
