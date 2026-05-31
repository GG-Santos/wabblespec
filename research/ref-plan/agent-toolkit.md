# Ref-Plan: agent-toolkit

**Reference:** agent-toolkit
**Date:** 2026-05-31
**Based on:** research/ref-eval/agent-toolkit.md
**Classification:** inspiration-only (3/10)

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Problem/Why/Fix pitfall format spec | Behavioral addition | Medium | High | Low |
| A2 | Hypothesis template for benchmark-loop | Behavioral addition | Medium | High | Low |
| A3 | Hypothesis template for skill-tdd | Behavioral addition | Low | Medium | Low |
| A4 | `## When to Trust Results` checklist structure in benchmark-loop | Behavioral addition | Low | Medium | Low |

---

## Exclusion List

| Item | Reason |
|---|---|
| All TypeScript/GROQ code examples | Domain-specific Sanity CMS vendor code; I6 violation risk if introduced to framework |
| All 3 SKILL.md `description:` fields | Negative examples — violate WabbleSpec description authoring rule |
| `cms-integration.md` full content | Sanity CMS architecture; no transferable abstractions |
| `structured-data.md` full content | Web SEO schemas; domain-specific |
| `technical-seo.md` full content | Web performance thresholds, hreflang; domain-specific |
| `eeat-principles.md` Sanity schema | CMS schema; domain-specific |
| `taxonomy-classification.md` GROQ queries | Domain-specific |
| Content modeling principles (4 core) | Analogs already covered by WabbleSpec I1 and CLAUDE.md spec conventions |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Impact | Project fit | Risk | Score | Tier |
|---|---|---|---|---|---|
| A1 | Medium(2) | High(3) | Low(1) | 6 | Tier 1 |
| A2 | Medium(2) | High(3) | Low(1) | 6 | Tier 1 |
| A3 | Low(1) | Medium(2) | Low(1) | 4 | Tier 1 |
| A4 | Low(1) | Medium(2) | Low(1) | 4 | Tier 1 |

---

## Tier Assignments

### Tier 1 — Behavioral Additions

**A1 — Problem/Why/Fix pitfall format spec**
- What: Add a format specification to CLAUDE.md's `## Pitfalls` section description, stating that each entry should include: Problem (what the agent does), Why it happens (the root cause or failure mode), and Fix (the corrective action)
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md` — find the line beginning "`**\`## Pitfalls\`** is a recognized optional section.`"
- How: Extend the existing sentence to add: "Each bullet should follow the Problem / Why / Fix structure: what the agent does wrong, why that failure mode occurs, and how to correct it. This mirrors the WHY-over-directives convention."
- Literal values: "Problem", "Why", "Fix"
- Gate: The `## Pitfalls` convention in CLAUDE.md names all three structural elements explicitly
- Reference location: `content-experimentation-best-practices/resources/common-pitfalls.md` — all 17 entries

**A2 — Hypothesis template for benchmark-loop**
- What: Add a required hypothesis format to benchmark-loop's SKILL.md
- Where: `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md` (and mirror to `.claude/skills/benchmark-loop/SKILL.md`)
- How: Find the section where benchmark hypothesis is discussed. Add: "State the hypothesis in the form: 'We believe [change] will [impact metric] because [reasoning].' A hypothesis missing any of these three components (what changes, what metric changes, why) is incomplete and should be challenged before the run starts."
- Literal values: "We believe [change] will [impact metric] because [reasoning]"
- Gate: The hypothesis template appears verbatim in benchmark-loop SKILL.md with all three components named
- Reference location: `content-experimentation-best-practices/resources/experiment-design.md` — "Structure: We believe [change] will [impact metric] because [reasoning]"

**A3 — Hypothesis template for skill-tdd**
- What: Mirror the same hypothesis template to skill-tdd
- Where: `.wabblespec/engine/modules/l8/skill-tdd/SKILL.md` (and mirror to `.claude/skills/skill-tdd/SKILL.md`)
- How: Same as A2 — add the hypothesis format to the test hypothesis/rubric section
- Literal values: "We believe [change] will [impact metric] because [reasoning]"
- Gate: Template appears in skill-tdd SKILL.md
- Reference location: same as A2

**A4 — When to Trust Results checklist in benchmark-loop**
- What: Add a 4-item pre-commit checklist to benchmark-loop before declaring a benchmark verdict
- Where: `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md`
- How: After the hypothesis section, add a `## Before Declaring a Verdict` checklist. Adapt from statistical-foundations.md's 6-item checklist, keeping only the ones relevant to benchmark-loop (not web traffic concepts): reached target run count, ran full eval cycle, effect size is meaningful (not just noise), results consistent across major prompt variants
- Gate: Checklist section present in benchmark-loop with at least 3 items
- Reference location: `content-experimentation-best-practices/resources/statistical-foundations.md` — "When to Trust Results" checklist

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why the project lacks it | What it would unlock | Dependencies | Effort signal | Session seed |
|---|---|---|---|---|---|---|
| Structured L8 experiment document format | `experiment-design.md`, `cms-integration.md` | WabbleSpec L8 has no receipt type linking hypothesis→benchmark runs→winner→learnings | Auditable hypothesis-to-conclusion trail for skill evolution | benchmark-loop SKILL.md A2, new receipt type spec | weeks | Specify a new receipt type 'experiment' for L8 benchmark runs with fields: hypothesis (required, "We believe..." template), variants (skill versions), primary_metric, winner, learnings |

### Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| TypeScript `defineType`/`defineField` patterns | I6: vendor-specific API |
| GROQ query syntax | I6: vendor-specific query language |
| All 3 SKILL.md description fields | CLAUDE.md: description must not summarize workflow |
| Sanity CMS architecture patterns | I11: domain-specific, not framework-relevant |
| sameAs/socialLinks author schema | I6: web platform specific |

### Priority Implementation Order

| Order | Item | Why first |
|---|---|---|
| 1 | A1 — Pitfall format spec in CLAUDE.md | CLAUDE.md is foundational; all future SKILL.md pitfall sections benefit from this standard |
| 2 | A2 — Hypothesis template in benchmark-loop | benchmark-loop is the higher-traffic L8 skill; hypothesis quality directly affects benchmark reliability |
| 3 | A3 — Hypothesis template in skill-tdd | Lower traffic than benchmark-loop; same change, lower priority |
| 4 | A4 — Trust checklist in benchmark-loop | Depends conceptually on A2 being in place first |

---

## Execution Notes

- A1 through A4 are independent. They can be applied in parallel but ordered per the priority table for editorial coherence.
- A2 and A3 are nearly identical changes to different files — apply A2 first to establish the wording, then mirror to A3.
- Every `.claude/skills/` edit requires a matching `.wabblespec/engine/modules/` edit immediately after (sync contract).
- No breaking changes in any item. All additive.
