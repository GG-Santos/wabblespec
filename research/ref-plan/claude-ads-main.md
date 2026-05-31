# Ref-Plan: claude-ads-main

**Reference**: claude-ads-main (supporting-reference, 6/10)
**Session**: tier7-expansions-20260530
**Written**: 2026-05-31

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk | Score |
|---|---|---|---|---|---|---|
| A | 3-tier evidence hierarchy → verifier/SKILL.md | Behavioral | High | High | Low | 8 |
| B | Quick Wins filter → guard/SKILL.md | Behavioral | High | High | Low | 8 |
| C | Hard Gates block → executor/SKILL.md | Behavioral | High | High | Low | 8 |
| D | Hypothesis framework → benchmark-loop/SKILL.md + skill-tdd/SKILL.md | Behavioral | High | High | Low | 8 |
| E | Severity multipliers + Critical-first → guard/SKILL.md | Behavioral | Medium | High | Low | 6 |
| F | Negative eval cases guidance → CLAUDE.md | Structural | Medium | Medium | Low | 5 |
| G | Output suppression enumeration → archive/SKILL.md + executor/SKILL.md | Behavioral | Medium | Medium | Low | 5 |

**Score formula**: (impact × 2) + project_fit - risk. High=3, Medium=2, Low=1.

---

## Exclusion List

| Item | Reason |
|---|---|
| Community footer rule (`ads/SKILL.md`) | Section 4 Avoid — commercial promotion embedded in skill rules |
| `model: opus/sonnet/haiku` in agent frontmatter | I6 violation — vendor model names |
| `context: fork` verbatim API syntax | Section 4 Study Only — vendor-specific Task tool parameter |
| Any MCP vendor names from `references/mcp-integration.md` | I6 violation |

---

## Tier Assignments

### Tier 1 — Behavioral Additions (additive to existing files)

#### T1-A: 3-Tier Evidence Hierarchy
- **What**: Add `## Evidence Hierarchy` section to verifier/SKILL.md declaring conflict resolution rule: Tier 1 = execution artifacts (files on disk) > Tier 2 = receipt chain > Tier 3 = agent text assertions
- **Where**: `.wabblespec/engine/modules/l2/verifier/SKILL.md` (and mirror: `.claude/skills/verifier/SKILL.md`)
- **How**: Add a new `## Evidence Hierarchy` section after the existing verification methodology. Section declares three tiers by name with examples. Include resolution rule: "When sources disagree, higher tier wins. A file absent from disk overrides a receipt claiming it was written."
- **Gate**: `verifier/SKILL.md` contains `## Evidence Hierarchy` section with all 3 tier labels present
- **Reference location**: `research/Ad Optimization Tool Logic Request.md`, Section 6.2 — Hierarchy of Truth
- **Literal values to encode**: "Tier 1 (Ultimate Truth): execution artifacts — files actually written to disk", "Tier 2 (Macro View): receipt chain — verifier/executor receipts", "Tier 3 (Optimization View): agent text assertions — what the agent claims it did"

#### T1-B: Quick Wins Filter
- **What**: Add `## Quick Wins Filter` section to guard/SKILL.md with algorithmic triage rule separating Immediate (high-severity + fast-fix) findings from Backlog findings
- **Where**: `.wabblespec/engine/modules/l2/guard/SKILL.md` (and mirror: `.claude/skills/guard/SKILL.md`)
- **How**: Add section after guard check output declaration. Encode the IF/SORT formula adapted for WabbleSpec context: IF severity is Critical (I-class) or High (H-class) AND estimated_wave_count_to_fix <= 1 THEN flag as Quick Win. SORT BY (severity_multiplier × estimated_scope_impact) DESC.
- **Gate**: `guard/SKILL.md` contains `## Quick Wins Filter` with IF/SORT logic and the `estimated_wave_count_to_fix` threshold
- **Reference location**: `skills/ads-audit/SKILL.md`, Quick Wins Criteria section
- **Literal values to encode**: "IF severity == Critical OR severity == High AND estimated_wave_count_to_fix <= 1 THEN flag as Quick Win", "SORT BY (severity_multiplier × estimated_scope_impact) DESC"

#### T1-C: Hard Gates Block
- **What**: Add `## Hard Gates` section to executor/SKILL.md consolidating the invariants that must never be violated into a named, scannable block — distinct from the general invariant list
- **Where**: `.wabblespec/engine/modules/l2/executor/SKILL.md` (and mirror: `.claude/skills/executor/SKILL.md`)
- **How**: Add section near the top of executor/SKILL.md (before wave execution steps). List 4-6 hard gates as named rules: gate name, trigger condition, specific violation action. Format: "Gate name: condition → action". Gates to include: locked-spec-only (I1), receipt-required (I10), no-framework-writes (I11), max-revise-3 (I4).
- **Gate**: `executor/SKILL.md` contains `## Hard Gates` section with at least 4 named gate entries using the "name: condition → action" format
- **Reference location**: `ads/SKILL.md`, Quality Gates section — "Hard rules (never violate these)"

#### T1-D: Hypothesis Framework
- **What**: Add hypothesis pre-condition block to both `benchmark-loop/SKILL.md` and `skill-tdd/SKILL.md` — require a structured IF/THEN/BECAUSE statement before iteration begins; classify outcomes as Confirmed/Refuted/Inconclusive
- **Where (file 1)**: `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md` (and mirror)
- **Where (file 2)**: `.wabblespec/engine/modules/l8/skill-tdd/SKILL.md` (and mirror)
- **How (benchmark-loop)**: Add `## Hypothesis (Required)` section before the iteration loop. Template: "IF we [change to artifact X] THEN [quality metric Y] will [direction] by [estimated delta] BECAUSE [evidence from drawer or receipt]". Add `hypothesis_confirmed` column to the TSV log. After each iteration, classify vs declared hypothesis: Confirmed (delta >= estimate), Refuted (wrong direction), Inconclusive (delta within 5% noise floor).
- **How (skill-tdd)**: Add `## Hypothesis (Required)` section before subagent dispatch. Same template. Add to report: "Hypothesis outcome: Confirmed/Refuted/Inconclusive".
- **Gate (benchmark-loop)**: `benchmark-loop/SKILL.md` contains `## Hypothesis (Required)` with template; TSV log columns include `hypothesis_confirmed`
- **Gate (skill-tdd)**: `skill-tdd/SKILL.md` contains `## Hypothesis (Required)` with template; report includes hypothesis outcome classification
- **Reference location**: `skills/ads-test/SKILL.md`, Hypothesis Framework section + quality checklist
- **Literal values to encode**: "IF we [change/action] THEN [metric] will [increase/decrease] by [estimated %] BECAUSE [reasoning based on data or insight]", quality checklist items: "Single variable being tested", "Specific metric defined", "Estimated effect size stated", "Timeframe defined", "Success/failure criteria clear before launch"

#### T1-E: Severity Multipliers + Critical-First Order
- **What**: Add severity multiplier assignments to guard/SKILL.md: I-class checks = 5.0x, H-class = 3.0x, M-class/L-class = 1.0x. Add rule requiring I-class checks be evaluated first.
- **Where**: `.wabblespec/engine/modules/l2/guard/SKILL.md` (same file as T1-B, add to the same section or adjacent)
- **How**: In the `## Quick Wins Filter` section (from T1-B) or a new `## Severity Scoring` sub-section, declare the multiplier table. Add a rule: "Evaluate I-class checks before H-class or lower. I-class failure dominates the session severity score."
- **Gate**: `guard/SKILL.md` contains multiplier table with values 5.0x/3.0x/1.0x for I/H/M classes and the evaluation order rule
- **Reference location**: `agents/audit-google.md`, Critical Checks section ("severity multiplier 5.0x; failure here dominates the score")
- **Literal values to encode**: "Critical checks: severity multiplier 5.0x", "High: 3.0x", "Medium/Low: 1.0x"

#### T1-G: Output Suppression Enumeration
- **What**: Add `## When to Suppress Optional Output` section to both `archive/SKILL.md` and `executor/SKILL.md` listing exact task types where optional output blocks (receipt footers, summary sections) are omitted
- **Where (file 1)**: `.wabblespec/engine/modules/l2/archive/SKILL.md` (and mirror)
- **Where (file 2)**: `.wabblespec/engine/modules/l2/executor/SKILL.md` (and mirror — same as T1-C)
- **How**: Add section enumerating suppress conditions: "Suppress optional output blocks when: task complexity is L0, executor run is error-recovery path (rollback in progress), wave is context-only (no artifact writes), run is a dry-run or --check flag invocation."
- **Gate**: Both `archive/SKILL.md` and `executor/SKILL.md` contain `## When to Suppress` with at least 3 enumerated conditions
- **Reference location**: `ads/SKILL.md`, Community Footer section — "When to skip: /ads math, /ads test, [etc]" — the enumeration pattern

### Tier 2 — Module-Level Augmentation

#### T2-F: Negative Eval Cases Guidance
- **What**: Add a requirement to CLAUDE.md (Skill Authoring Conventions section) that every skill eval fixture must include at least 2 negative routing cases with `should_trigger: false`
- **Where**: `CLAUDE.md` — Skill Authoring Conventions section
- **How**: Add one bullet under Skill Authoring Conventions: "Skill eval fixtures must include negative routing cases. For each skill that has an eval fixture, at least 2 entries must declare `should_trigger: false` with a specific prompt that LOOKS like the skill's trigger but must not activate it. This catches mis-routing regressions when `description:` fields are edited."
- **Gate**: CLAUDE.md Skill Authoring Conventions section contains "negative routing cases" requirement with `should_trigger: false` language
- **Specify required**: No
- **Breaking change risk**: None
- **Reference location**: `evals/creative-evals.json`, negative-001 through negative-006 entries

---

## Tier 6 — Synthesis

### T6-1: Weighted Guard Scoring with Quick Wins Triage
- Reference contribution: Quick Wins filter formula + 5.0x/3.0x/1.0x severity multipliers
- Project contribution: Guard's existing I/H/M check categories + receipt chain
- Watch Only — depends on T1-B and T1-E being implemented first; full scoring integration with receipt-writer.py is Tier 5 risk

### T6-2: Hypothesis-Gated Benchmark Loop with Outcome Classification
- Reference contribution: IF/THEN/BECAUSE template + Confirmed/Refuted/Inconclusive classification
- Project contribution: benchmark-loop's iteration/commit/revert cycle + TSV log
- Watch Only — depends on T1-D being implemented first; extending TSV log schema is T2 risk

### T6-3: Evidence Hierarchy for Verifier Conflict Resolution (Phase 1 seed)
- Implemented as T1-A. Section 8 synthesis is realized by the Tier 1 item.

### T6-4: Negative Routing Eval Fixture (Phase 1 seed)
- Implemented as T2-F. Synthesis requires quality-floor-check.py integration — Watch Only for Gate 1 enforcement.

---

## Tier 7 — Expansion Roadmap

| Capability | Ref location | Effort | Session seed |
|---|---|---|---|
| Skill Eval Runner | `evals/creative-evals.json` | days | Build skill-eval-runner.py that reads JSON eval fixture, checks description: + When NOT to use fields for routing accuracy, outputs fidelity score (N/M). Integrate as optional quality-floor-check.py Gate 3. |
| Deliverable Quality Score | `ads/SKILL.md` Scoring Methodology | weeks | Build wave-score.py: reads acceptance criteria from wave plan, checks receipt completeness, computes weighted 0-100 score (AC coverage 40%, receipt completeness 30%, gate conditions 20%, docs present 10%). Grade A-F. Output as --score flag on verifier or standalone script. |

---

## Do-Not-Copy List

| Item | Invariant |
|---|---|
| Community footer block | Promotional content — never in framework behavioral rules |
| `model: opus/sonnet/haiku` | I6 — vendor-neutral runtime |
| `context: fork` verbatim | I6 — vendor-specific tool parameter |

---

## Priority Implementation Order

| Order | Item | Why First |
|---|---|---|
| 1 | T1-A: Evidence hierarchy → verifier | Highest gap severity; Verifier conflict resolution is a correctness issue |
| 2 | T1-B + T1-E: Quick Wins + multipliers → guard | Both modify guard; batch into one edit pass |
| 3 | T1-C: Hard Gates block → executor | Directly supports active task card invariant enforcement |
| 4 | T1-D: Hypothesis framework → benchmark-loop + skill-tdd | Two files, same pattern; batch |
| 5 | T1-G: Output suppression → archive + executor | Two files; executor already touched in T1-C so batch |
| 6 | T2-F: Negative eval guidance → CLAUDE.md | CLAUDE.md edit; independent |

---

## Execution Notes

- T1-B and T1-E both target `guard/SKILL.md` — implement in a single edit pass
- T1-C and T1-G both target `executor/SKILL.md` — implement in a single edit pass
- T1-D targets two files (benchmark-loop, skill-tdd) but same content — implement in parallel
- All items require syncing `.claude/skills/<name>/SKILL.md` AND `.wabblespec/engine/modules/<layer>/<name>/SKILL.md`
- Engine module paths to locate: run `glob('.wabblespec/engine/modules/**/<name>/SKILL.md', recursive=True)` before each edit
- Do not implement T6 items — they are Watch Only pending T1 completion
