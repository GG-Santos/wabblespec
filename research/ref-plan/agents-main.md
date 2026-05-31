# Ref-Plan: agents-main

**Reference:** agents-main (Claude Code plugin marketplace + plugin-eval quality framework)
**Date:** 2026-05-31
**Based on:** ref-eval/agents-main.md (supporting-reference, 7/10)
**Risk appetite:** balanced

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Anti-pattern taxonomy (ORPHAN_REFERENCE, DEAD_CROSS_REF, BLOATED_SKILL name, confirm OVER_CONSTRAINED threshold) in quality-floor-check.py | Behavioral addition | High | High | Low |
| A2 | 200-600 line sweet spot + BLOATED_SKILL authoring rule in CLAUDE.md | Behavioral addition | Medium | High | Low |
| A3 | `--score` mode for quality-floor-check.py (10 dimensions, badge, letter grade) | Module augmentation | High | High | Medium |
| A4 | Parser regex cross-check: MNA pattern, cross_ref detection, has_troubleshooting | Behavioral addition | Medium | Medium | Low |
| A5 | F1 calculation in skill-tdd SKILL.md eval harness | Behavioral addition | Medium | Medium | Low |
| A6 | Task-type capability classification criteria in model-router | Behavioral addition | Low | Medium | Low |

## Exclusion List

| Item | Reason |
|---|---|
| Agent frontmatter examples with model: opus\|sonnet\|haiku | I6 violation — model names in framework files |
| agentskills.io URL as specification citation | Unverified URL, may be dead or speculative |
| tdd-orchestrator agent style (capability list without decision rules) | Violates CLAUDE.md "description must not summarize workflow" rule |
| Plugin-eval Layers 2+3 (LLM judge, Monte Carlo) | claude-agent-sdk dependency; our skill-tdd is the existing analog |
| Conductor full adoption | Conflicts with wave-plan/task-card approach |
| Agent Teams full adoption | Experimental API flag required |

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Impact | Fit | Risk | Score | Tier |
|---|---|---|---|---|---|
| A1 | 3 | 3 | 1 | 8 | Tier 1 |
| A2 | 2 | 3 | 1 | 7 | Tier 1 |
| A3 | 3 | 3 | 2 | 7 | Tier 2 |
| A4 | 2 | 2 | 1 | 5 | Tier 1 |
| A5 | 2 | 2 | 1 | 5 | Tier 1 |
| A6 | 1 | 2 | 1 | 3 | Tier 1 |

---

## Tier Assignments

### Tier 1 — Behavioral Additions (additive to existing files)

**A1 — Anti-pattern taxonomy additions to quality-floor-check.py**
- What: Add 4 named anti-pattern checks: ORPHAN_REFERENCE, DEAD_CROSS_REF (net-new), confirm OVER_CONSTRAINED threshold at >15 MNA, codify BLOATED_SKILL at >800 lines without refs/
- Where: `.wabblespec/engine/shared/scripts/quality-floor-check.py`
- How: Find the section that handles existing INLINE_DANGER and similar checks. Add new check classes:
  - `ORPHAN_REFERENCE`: for each path referenced in a `references/` cross-link in SKILL.md, verify the file exists. Flag if dead.
  - `DEAD_CROSS_REF`: for each `[[skill-name]]` link in SKILL.md, verify a matching skill module exists in wabblespec.yaml. Flag if missing.
  - `OVER_CONSTRAINED`: count `\b(MUST|NEVER|ALWAYS)\b` occurrences (case-sensitive). Flag if >15.
  - `BLOATED_SKILL`: if line_count >800 AND no `references/` subdirectory exists, flag.
  - Report each flag with severity and file location in `--verbose` output.
- Literal values: >15 for OVER_CONSTRAINED, >800 for BLOATED_SKILL, threshold floor 0.5, penalty 0.05 per flag
- Gate: `quality-floor-check.py --verbose` on a skill with >15 MNA occurrences shows OVER_CONSTRAINED flag; running on a skill with a dead references/ link shows ORPHAN_REFERENCE
- Reference location: `docs/plugin-eval.md` anti-pattern table; `engine.py` penalty formula

**A2 — CLAUDE.md skill authoring: 200-600 line sweet spot + BLOATED_SKILL name**
- What: Add two sentences to the "Skill content has three loading tiers" convention in CLAUDE.md
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md` skill authoring conventions section
- How: After the existing "Tier 2 — SKILL.md body: loaded when skill activates, budget <500 lines" line, add: "The sweet spot for SKILL.md body length is 200–600 lines. Below 200 lines is usually underpowered. Above 800 lines without a Tier 3 references/ directory is BLOATED_SKILL — promote content to Tier 3 rather than extending the body further."
- Literal values: 200 (lower bound), 600 (sweet spot upper), 800 (BLOATED_SKILL threshold)
- Gate: CLAUDE.md contains the phrase "BLOATED_SKILL" and explicit 200/600/800 thresholds
- Reference location: `docs/plugin-eval.md` progressive_disclosure sub-check; Layer 1 sweet spot description

**A4 — Parser regex cross-check**
- What: Cross-check quality-floor-check.py MNA counting, cross-reference detection, and troubleshooting section detection against plugin-eval parser.py patterns. Update any divergences.
- Where: `.wabblespec/engine/shared/scripts/quality-floor-check.py`
- How: Compare existing patterns against: MNA `r"\b(MUST|NEVER|ALWAYS)\b"`, cross_ref `r"(?:skill|skills)/([a-z0-9-]+)"`, troubleshooting `r"(## troubleshoot|## common issue|## faq)"`. Update to match if divergent.
- Gate: INLINE_DANGER check and MNA counting use the exact regex from parser.py
- Reference location: `plugins/plugin-eval/src/plugin_eval/parser.py` lines 93-96, 76-77

**A5 — F1 triggering accuracy metric in skill-tdd**
- What: Add a "Triggering Accuracy F1" reporting step to skill-tdd SKILL.md when an eval set contains both positive and negative cases
- Where: `.claude/skills/skill-tdd/SKILL.md` (and engine module)
- How: In the eval reporting section, add: "When the eval set has both should_trigger: true and should_trigger: false entries, compute F1 over activation decisions: precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2×precision×recall/(precision+recall). Report alongside pass/fail counts. Target F1 ≥ 0.80 for a well-calibrated description."
- Literal values: F1 formula, target threshold ≥0.80
- Gate: skill-tdd SKILL.md contains "F1" and "precision" and "recall" in the eval reporting section
- Reference location: `docs/plugin-eval.md` Layer 2 triggering_accuracy method

**A6 — Task-type capability classification in model-router**
- What: Add a task-type capability classification table to model-router SKILL.md (capability descriptors only, no model names)
- Where: `.claude/skills/model-router/SKILL.md` (and engine module)
- How: Add a `## Task Capability Classification` section with a table mapping task types to capability tiers (using WabbleSpec's capability descriptor vocabulary, not model names): "highest-capability" tasks (architecture decisions, security audits, code review across entire codebase, synthesis of ambiguous requirements); "analysis-capable" tasks (complex reasoning, multi-file refactors, LLM pipeline design); "fast-execution" tasks (deterministic code generation, test boilerplate, docs from templates, deployment operations, SEO tasks, simple formatting)
- Gate: model-router SKILL.md contains a task classification table with capability tiers and no model names
- Reference location: `docs/architecture.md` Model Configuration Strategy section (selection criteria)

### Tier 2 — Module-Level Augmentation

**A3 — `--score` mode for quality-floor-check.py**
- What: New `--score` invocation mode that produces a continuous quality score (0-100), dimension breakdown across 6 static-measurable dimensions, badge (Bronze/Silver/Gold/Platinum), and letter grade
- Where: `.wabblespec/engine/shared/scripts/quality-floor-check.py`
- How: Add a `score` subcommand (or `--score` flag). Map existing static checks onto the 6 static-measurable dimensions:
  - triggering_accuracy (static weight 0.15): description has "Use when" phrase + sufficient length
  - orchestration_fitness (static weight 0.10): has output/input documentation + code examples
  - scope_calibration (static weight 0.30): line count in 200-600 range
  - progressive_disclosure (static weight 0.80): references/ present if >600 lines
  - token_efficiency (static weight 0.40): MNA count ≤15, no excessive duplication
  - structural_completeness (static weight 0.90): has H2 headings, code blocks, examples section
  - Apply DIMENSION_WEIGHTS for the 6 measurable dims, renormalized. Apply anti-pattern penalty.
  - Output format: dimension table, composite score, badge, letter grade
- Literal values: DIMENSION_WEIGHTS (triggering_accuracy=0.25, orchestration_fitness=0.20, scope_calibration=0.12, progressive_disclosure=0.10, token_efficiency=0.06, structural_completeness=0.03); badge thresholds Platinum=90, Gold=80, Silver=70, Bronze=60; only 6 of 10 dimensions measurable from static analysis
- Gate: `python quality-floor-check.py skill-path --score` outputs a score/100, a badge, and a dimension table
- Specify required: No — this is a new mode of an existing script, not a new module
- Breaking change risk: Low — additive to existing script, existing modes unchanged
- Reference location: `engine.py` DIMENSION_WEIGHTS + LAYER_BLENDS; `docs/plugin-eval.md` static sub-checks

### Tier 3 — New Shared Infrastructure

None identified for this reference.

### Tier 4 — New Module Candidates

None for immediate implementation. See Tier 7 for expansion candidates.

### Tier 5 — Architecture-Level

None.

### Tier 6 — Synthesis

**S1 — Ref-eval composite scoring (synthesis: plugin-eval scoring formula + ref-eval Section 5 output format)**
- What: Add a reproducible composite score to ref-eval Section 5 (Integration Fit) by applying a simplified DIMENSION_WEIGHTS formula to the 6 existing 1-10 subjective scores
- Reference contribution: DIMENSION_WEIGHTS, badge thresholds, composite math from engine.py
- Project contribution: ref-eval Section 5 already produces 6 dimension scores (Concept/Architecture/Implementation/Maintenance fit + Risk + Overall)
- Target: `.claude/skills/ref-eval/SKILL.md` (and engine module)
- Gap closed: Section 5 scores are currently subjective estimates; formula makes them reproducible
- Risk: Tier 5 until validated — mapping our 6 dimensions to the 10-dimension framework requires design work

**S2 — Wave-review anti-pattern gate (synthesis: anti-pattern flags + wave-review diff parsing)**
- What: Before verifier writes PASS on a wave that modifies SKILL.md files, run anti-pattern checks against the modified skill
- Reference contribution: OVER_CONSTRAINED, MISSING_TRIGGER, BLOATED_SKILL, ORPHAN_REFERENCE flags
- Project contribution: wave-review.py already parses skill diffs; verifier has REVISE cycle for failures
- Target: `.claude/skills/verifier/SKILL.md` (and engine module) — add anti-pattern gate step
- Gap closed: Verifier checks semantic correctness, not skill-quality structural properties
- Risk: Tier 5 until validated — need to confirm wave-review.py output format supports anti-pattern checking

**S3 — L8 promotion Bronze gate (synthesis: Bronze threshold + Instinct promotion criteria)**
- What: Before Instinct observation is promoted to Synth candidate, require target SKILL.md to score Bronze (≥60 static quality)
- Reference contribution: Bronze ≥60 threshold from badge system
- Project contribution: L8 evolution chain (Instinct → Synth → Blueprint → Augment) with existing promotion gates
- Target: `.claude/skills/instinct/SKILL.md` (and engine module)
- Gap closed: L8 gates on evidence + attestation, not on resulting skill quality
- Risk: Tier 5 until validated — need quality-floor-check.py --score mode (A3) to exist first

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Drawer written |
|---|---|---|---|---|---|---|
| quality-score.py — Layer 1 static scorer with badge output | docs/plugin-eval.md + engine.py + parser.py | quality-floor-check.py is pass/fail only | CI-gatable quality score for all 121 skills; dimension breakdown for improvement prioritization | None (pure Python) | days | Yes — open-thread-tier-7-expansion-quality-20260531.json |
| quality-rank.py — Elo relative ranking across skill corpus | docs/plugin-eval.md Elo section | No relative quality ranking exists | Identifies lowest-quality skills for L8 evolution targeting | quality-score.py prerequisite | weeks | Yes — included in quality-suite drawer |
| quality-judge.py — LLM semantic eval via rubric | docs/plugin-eval.md Layer 2 | skill-tdd tests triggering only, not output quality | Catches skills that pass structural checks but fail semantically | quality-score.py + agent dispatch | weeks | Yes — included in quality-suite drawer |
| C4 architecture diagram generation | plugins/c4-architecture/agents/*.md | No diagram output capability at any layer | Generates C4 docs from codebase analysis | Glob/Read tools; Mermaid syntax | weeks | Yes — open-thread-tier-7-expansion-c4-20260531.json |

**Session seed for quality-suite:** "Build quality-suite for WabbleSpec: (1) quality-floor-check.py gains --score mode producing continuous quality score (0-100), dimension breakdown, badge (Bronze/Silver/Gold/Platinum), letter grade. (2) New quality-rank.py builds Elo corpus across all SKILL.md files in .wabblespec/engine/modules/, tracks relative rankings. (3) quality-judge.py uses skill-tdd dispatch infrastructure to run LLM-judge eval on triggering_accuracy and orchestration_fitness. Reference: research/ref-eval/agents-main.md Section 9, research/ref-plan/agents-main.md Tier 7."

**Session seed for C4 diagrams:** "Build C4 architecture diagram gateway for WabbleSpec: 4-level skill producing Mermaid C4 diagrams from codebase analysis (context level = system + external actors, container level = processes + databases, component level = module decomposition, code level = key classes). Hook into gateway-document or present SKILL.md. Reference: research/ref-eval/agents-main.md Section 9."

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| model: opus\|sonnet\|haiku in any file | I6 — no model names in framework files |
| agentskills.io URL as citation | Unverified URL; potentially dead |
| tdd-orchestrator-style capability lists | CLAUDE.md: "description must not summarize workflow"; "no multi-paragraph docstrings" |
| Layers 2+3 Python implementation verbatim | claude-agent-sdk external dependency (I6 — runtime vendor) |

---

## Priority Implementation Order

| Priority | ID | Item | Why first |
|---|---|---|---|
| 1 | A2 | CLAUDE.md: 200-600 sweet spot + BLOATED_SKILL | Zero risk, pure additive, immediate authoring guidance impact, takes 2 sentences |
| 2 | A1 | quality-floor-check.py: 4 new anti-pattern checks | High impact, well-defined thresholds, no structural changes to existing checks |
| 3 | A4 | quality-floor-check.py: parser regex cross-check | Quick validation; ensures MNA counting is consistent with production-tested patterns |
| 4 | A5 | skill-tdd: F1 triggering accuracy metric | Adds quantitative signal to eval harness; builds on existing negative routing cases |
| 5 | A6 | model-router: task capability classification table | Low risk, additive only |
| 6 | A3 | quality-floor-check.py --score mode | More complex; depends on A1+A4 being in place first |

---

## Execution Notes

- A1 must precede A3: the --score mode uses the same check infrastructure, so anti-pattern additions should be in place first
- A4 (regex cross-check) can run in parallel with A2 (CLAUDE.md edit) since they target different files
- A5 and A6 are independent of each other and of A1-A4; can run in parallel
- A3 (--score mode) is the most complex item and should run last in Phase 1-2
- Tier 6 items (S1, S2, S3) are Watch Only for this session — they depend on A3 being complete and are Tier 5 risk
- Tier 7 items require their own recipe sessions; no implementation this pipeline

*Plan written: 2026-05-31 | ref-adopt pipeline*
