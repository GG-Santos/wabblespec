# Ref-Eval: agent-toolkit

**Reference path:** `C:\Vaults\references\Other Projects References\agent-toolkit`
**Date:** 2026-05-31
**Evaluator:** ref-adopt pipeline
**Trust level:** MEDIUM

---

## File Inventory

| File | Purpose | Size | Key Contents | Status | Transfer Check |
|---|---|---|---|---|---|
| `content-experimentation-best-practices/SKILL.md` | Skill entry point for A/B testing guidance | Small | Core concepts, resource routing | Read | Descriptions contain workflow steps — negative example for WabbleSpec description authoring rule |
| `content-experimentation-best-practices/resources/experiment-design.md` | Hypothesis framework, metrics, sample size | Small | "We believe [X] will [Y] because [Z]" template, Test Priority Matrix, Sanity schema | Read | Hypothesis structure + Impact/Effort matrix are transferable |
| `content-experimentation-best-practices/resources/statistical-foundations.md` | Stats concepts for A/B testing | Small | p-value, confidence intervals, power analysis, 6-item "When to Trust Results" checklist | Read | Pre-commit checklist format is transferable |
| `content-experimentation-best-practices/resources/cms-integration.md` | CMS variant management patterns | Small | TypeScript Sanity schema, GROQ queries, frontend assignment algorithm | Read | Architecture patterns domain-specific; cookie-based assignment not transferable |
| `content-experimentation-best-practices/resources/common-pitfalls.md` | 17 numbered experimentation mistakes | Medium | Problem/Why/Fix structure for each pitfall; SRM, novelty/primacy effects | Read | Pitfall format (numbered, Problem/Why/Fix) is directly transferable to WabbleSpec `## Pitfalls` sections |
| `content-modeling-best-practices/SKILL.md` | Skill entry point for content schema design | Small | 4 core principles, resource routing | Read | Descriptions contain workflow steps — negative example |
| `content-modeling-best-practices/resources/separation-of-concerns.md` | Content vs. presentation separation | Small | Meaning-focused vs presentation-focused naming, test question, Sanity examples | Read | "Test your model" heuristic is transferable to skill naming conventions |
| `content-modeling-best-practices/resources/reference-vs-embedding.md` | When to reference vs embed content | Small | Decision criteria table, hybrid pattern | Read | Reference-vs-embed decision criteria transferable to any modular design context |
| `content-modeling-best-practices/resources/content-reuse.md` | 4 reuse patterns + anti-pattern | Small | Over-abstraction detection signals (references used once, complex joins rarely-shared) | Read | Over-abstraction anti-pattern signals are transferable |
| `content-modeling-best-practices/resources/taxonomy-classification.md` | Flat/hierarchical/faceted taxonomy | Small | 3-4 levels max rule, governance principle, GROQ examples | Read | Taxonomy design principles partially transferable; GROQ domain-specific |
| `seo-aeo-best-practices/SKILL.md` | SEO and AEO skill entry point | Small | Core concepts, resource routing | Read | Descriptions contain workflow steps — negative example |
| `seo-aeo-best-practices/resources/eeat-principles.md` | EEAT framework implementation | Small | 4 pillars (Experience/Expertise/Authoritativeness/Trustworthiness), author schema, YMYL | Read | EEAT as an evaluation taxonomy has loose analog to receipt quality; author schema domain-specific |
| `seo-aeo-best-practices/resources/structured-data.md` | JSON-LD schema patterns | Small | Article/FAQ/Product/Breadcrumb schemas, @graph pattern, XSS note in dangerouslySetInnerHTML | Read | All domain-specific web/SEO; @graph deduplication pattern non-transferable |
| `seo-aeo-best-practices/resources/technical-seo.md` | Technical SEO checklist | Small | Core Web Vitals thresholds (LCP<2.5s, INP<200ms, CLS<0.1), hreflang, robots.txt AI crawler note | Read | AI crawler management decision framework transferable conceptually; specific thresholds web-only |
| `seo-aeo-best-practices/resources/aeo-considerations.md` | AI answer engine optimization | Small | 5 AI evaluation dimensions, Direct Answers First, FAQ format, AEO vs SEO table | Read | "Direct Answers First" and content structure for AI extraction directly transferable to skill documentation quality |

All 15 files read. No directory-level skips.

---

## Connection Map

```
content-experimentation-best-practices/SKILL.md --[routes-to]--> resources/experiment-design.md
content-experimentation-best-practices/SKILL.md --[routes-to]--> resources/statistical-foundations.md
content-experimentation-best-practices/SKILL.md --[routes-to]--> resources/cms-integration.md
content-experimentation-best-practices/SKILL.md --[routes-to]--> resources/common-pitfalls.md

content-modeling-best-practices/SKILL.md --[routes-to]--> resources/separation-of-concerns.md
content-modeling-best-practices/SKILL.md --[routes-to]--> resources/reference-vs-embedding.md
content-modeling-best-practices/SKILL.md --[routes-to]--> resources/content-reuse.md
content-modeling-best-practices/SKILL.md --[routes-to]--> resources/taxonomy-classification.md

seo-aeo-best-practices/SKILL.md --[routes-to]--> resources/eeat-principles.md
seo-aeo-best-practices/SKILL.md --[routes-to]--> resources/structured-data.md
seo-aeo-best-practices/SKILL.md --[routes-to]--> resources/technical-seo.md
seo-aeo-best-practices/SKILL.md --[routes-to]--> resources/aeo-considerations.md
```

All routing is one level deep from SKILL.md — compliant with WabbleSpec's 1-level reference depth rule. No cross-skill dependencies. No shared state between the three skill clusters. Resource files are standalone with no internal imports.

---

## Section 1 — Reference Summary

**Type:** Domain-specific skill/behavioral spec collection (3 skills, 12 resource files) targeting headless CMS development (Sanity), web experimentation, and SEO/AEO.

**Behavioral content:** A/B testing workflow (hypothesis → metrics → sample size → analysis), content modeling decision rules (reference-vs-embed, separation of concerns), EEAT quality evaluation framework, AI answer engine content structure guidelines. The common-pitfalls.md encodes 17 production-hardened failure modes with Problem/Why/Fix structure.

**Structural content:** Consistent SKILL.md → resources/ routing pattern, resource files use H2 headings, decision tables, and numbered lists. TypeScript and GROQ code examples throughout.

**Interaction content:** One-level routing only. No cross-skill imports. Each skill is self-contained. Resource files do not reference each other.

**Maturity:** Well-organized, clearly written. No tests, no CI, no versioning. TypeScript examples appear production-realistic (Sanity v3 `defineType`/`defineField` API). Reference domain is web/CMS — entirely separate from WabbleSpec's SDLC framework domain.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `common-pitfalls.md` | Numbered Problem/Why/Fix pitfall format | WabbleSpec CLAUDE.md defines `## Pitfalls` as an optional section targeting 3–6 bullets but gives no internal structure. The Problem/Why/Fix format produces pitfall entries that explain causality, not just state mistakes — matching the WHY-over-MUST-ALWAYS convention | Add a format spec for `## Pitfalls` to CLAUDE.md: each bullet = Problem, Why it's wrong, Fix. | Medium |
| `experiment-design.md` | "We believe [change] will [impact metric] because [reasoning]" hypothesis template | WabbleSpec benchmark-loop and skill-tdd require hypotheses but give no structured template. This format enforces measurable impact + explicit reasoning — the two components most commonly missing from vague hypotheses | Add the hypothesis template to `benchmark-loop/SKILL.md` and `skill-tdd/SKILL.md` | Medium |
| `aeo-considerations.md` | Direct Answers First content structure principle | AEO guidance establishes that AI systems extract content that leads with the answer before context. WabbleSpec skills are loaded and acted on by AI agents — the same extraction dynamic applies. Skills that bury the actionable rule after two paragraphs of context cause the agent to miss it. | Add a note to CLAUDE.md skill authoring conventions: skill body sections should lead with the actionable rule before explaining context | Low-Medium |
| `statistical-foundations.md` | 6-item "When to Trust Results" checklist structure | WabbleSpec benchmark verdict thresholds exist but no pre-commit gate for benchmark conclusions. The checklist pattern (reach sample, run full cycle, significance met, effect meaningful, segments consistent, no contamination) maps to a structured benchmark trust gate | Add a `## When to Trust Results` checklist section to `benchmark-loop/SKILL.md` | Low |
| `separation-of-concerns.md` | "Test your model" naming heuristic | The heuristic ("If we completely redesigned the site, would these field names still make sense?") maps to skill naming — if the skill was renamed or repurposed, would its internal section headings still make sense? | Reference as a negative example in CLAUDE.md skill naming guidance | Low |
| `content-reuse.md` | Over-abstraction detection signals | The three signals (references only used once, editors navigating multiple documents for one page, complex queries joining rarely-shared content) map to skill cross-referencing anti-patterns | Reference in CLAUDE.md's cross-reference DRY rule | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| All 3 SKILL.md descriptions | Description field anti-pattern | All three description fields contain workflow steps ("covering experiment design, hypotheses, metrics, sample size..."), violating WabbleSpec's CLAUDE.md rule that descriptions must state triggering conditions only, not workflow content | Do not adopt any description field patterns from this reference; treat as negative examples | Low |
| `cms-integration.md`, `structured-data.md`, `technical-seo.md`, `taxonomy-classification.md` | Domain-specific implementation code | TypeScript/GROQ schema patterns are Sanity CMS-specific. Adopting them would introduce domain noise and potentially violate I6 (vendor names in framework files) | Exclude all code examples; extract only format/behavioral principles | Low |
| `eeat-principles.md`, `seo-aeo-best-practices/` | Web SEO concept mismatch | EEAT (Experience, Expertise, Authoritativeness, Trustworthiness) applied to WabbleSpec would be a stretch analogy that adds confusion without precision | Extract only the 4-pillar taxonomy label as inspiration; do not map it directly to receipt quality | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| `common-pitfalls.md` — Problem/Why/Fix format | Adapt | Strong, transferable pitfall documentation structure | CLAUDE.md `## Pitfalls` format spec | High |
| `experiment-design.md` — hypothesis template | Adapt | Enforces measurable + reasoned hypothesis structure | `benchmark-loop/SKILL.md`, `skill-tdd/SKILL.md` | Medium |
| `aeo-considerations.md` — Direct Answers First | Study Only | Reinforces existing WabbleSpec convention; not novel enough to warrant a new rule | Internal validation | Low |
| `statistical-foundations.md` — trust checklist structure | Adapt | Adds pre-commit gate structure to benchmark verdicts | `benchmark-loop/SKILL.md` | Low |
| All 3 SKILL.md `description:` fields | Avoid | Negative example — violate WabbleSpec description authoring rule | N/A |
| All TypeScript/GROQ code blocks | Avoid | Domain-specific, vendor-locked, I6 violation risk | N/A |
| `cms-integration.md` — full file | Avoid | Sanity CMS architecture; no transferable abstract | N/A |
| `structured-data.md` — full file | Avoid | Web SEO schemas; no transferable content | N/A |
| `technical-seo.md` — full file | Avoid | Web performance thresholds (LCP/INP/CLS), hreflang; no transferable content | N/A |
| `eeat-principles.md` — full Sanity schema | Avoid | CMS schema; domain-specific | N/A |
| `taxonomy-classification.md` — GROQ queries | Avoid | Domain-specific | N/A |
| `content-reuse.md` — over-abstraction signals | Study Only | Validates existing WabbleSpec DRY guidance | Internal validation |
| `separation-of-concerns.md` — naming heuristic | Study Only | Validates existing WabbleSpec naming guidance | Internal validation |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 3 | WabbleSpec is an SDLC agent framework; agent-toolkit targets Sanity CMS web development. Overlap exists only at the meta-level (documentation quality, format conventions) |
| Architecture fit | 2 | Skill-with-resources pattern matches WabbleSpec structure; specific implementation entirely mismatched |
| Implementation fit | 2 | TypeScript/GROQ code is inapplicable. Only prose sections transfer |
| Maintenance fit | 4 | The behavioral principles (hypothesis format, pitfall structure) are stable conventions that won't rot |
| Risk level | 2 | Very low risk — nothing to adopt is load-bearing; domain mismatch prevents accidental harmful adoption |
| Overall usefulness | 3 | inspiration-only; 2-3 small behavioral format patterns worth extracting from 15 files |

Overall usefulness: **3/10 — inspiration-only**

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — implement now):**
- `common-pitfalls.md`: Adopt Problem/Why/Fix pitfall format spec into CLAUDE.md. Target: existing `## Pitfalls` section description. Add format spec: each entry should state the Problem, Why it happens, and Fix, rather than a flat bullet.
- `experiment-design.md`: Add "We believe [change] will [impact metric] because [reasoning]" as the required hypothesis template to `benchmark-loop/SKILL.md`.

**Phase 2 (Low-Risk Adaptation — defer):**
- `statistical-foundations.md`: Add `## When to Trust Results` checklist pattern to benchmark-loop after the Phase 1 hypothesis change is stable.

**Phase 3 (Deeper Integration — do not pursue):**
- No items qualify.

**Phase 4 (Do Not Cross):**
- All TypeScript/GROQ code. All Sanity-specific schema patterns. All description field patterns from this reference.

---

## Section 7 — Final Verdict

**Verdict: inspiration-only (3/10)**

**Best 3 to steal/adapt:**
1. Problem/Why/Fix pitfall structure (`common-pitfalls.md`, all 17 entries use this pattern) — standardizes WabbleSpec's underdefined `## Pitfalls` format
2. Hypothesis template ("We believe [change] will [impact metric] because [reasoning]") from `experiment-design.md` — directly applicable to benchmark-loop and skill-tdd hypothesis fields
3. The description field violations in all 3 SKILL.md files — these are the clearest real-world negative examples of WabbleSpec's "description must not summarize workflow" rule; document as the canonical counterexample

**Worst 3 to avoid:**
1. All TypeScript/GROQ code blocks — Sanity CMS vendor-locked, violates I6 if introduced to framework files
2. The three SKILL.md description fields — contain workflow steps, the exact anti-pattern WabbleSpec prohibits
3. `cms-integration.md` — pure Sanity CMS architecture, zero transferable abstractions

**Reference classification: inspiration-only**

**Recommended next action:** Implement Phase 1 items (2 small CLAUDE.md/SKILL.md edits). No Tier 7 expansion opportunities identified.

---

## Section 8 — Project Synthesis

**What novel patterns become possible by combining this reference's approaches with WabbleSpec's specific capabilities?**

1. **Benchmark hypothesis gate with "We believe" format + WabbleSpec's receipt chain**
   - What: A formal hypothesis receipt field that must follow the "We believe [change] will [impact metric] because [reasoning]" template before a benchmark run can be authorized
   - Reference contribution: Structured hypothesis format with explicit impact + reasoning requirement
   - Project contribution: WabbleSpec's receipt-gated enforcement — the format can be validated as a required field at benchmark-loop invocation
   - Target: `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md`
   - Gap closed: Currently benchmark-loop can start with a vague or missing hypothesis; this gates execution on hypothesis quality

2. **Pitfall section quality gate in quality-floor-check.py**
   - What: Add a format check to quality-floor-check.py that detects `## Pitfalls` sections containing flat bullets (no "Why" or "Fix" language) and flags them below the floor
   - Reference contribution: The Problem/Why/Fix format clarity
   - Project contribution: WabbleSpec's existing Gate 1 quality floor check infrastructure
   - Target: `.wabblespec/engine/shared/scripts/quality-floor-check.py`
   - Gap closed: `## Pitfalls` sections currently pass Gate 1 regardless of format quality

Zero other meaningful synthesis opportunities — the domain gap is too large for productive combination outside these two.

---

## Section 9 — Expansion Opportunities

**Per-skill growth scan:**

- `content-experimentation-best-practices`: WabbleSpec has benchmark, benchmark-loop, skill-tdd but no dedicated experimentation tracking document (hypothesis + variants + status + winner + learnings). Could be a Tier 7 expansion. However, the WabbleSpec context is SDLC experimentation (skill evolution, benchmark runs, L8 candidates) not content marketing A/B testing. The structured experiment-document format could serve the L8 evolution cycle. Tier 7 candidate: Yes (weak) — the format is applicable but the domain crossing requires careful scoping.

- `content-modeling-best-practices`: WabbleSpec doesn't do content modeling. The reference-vs-embedding and taxonomy patterns are entirely domain-specific. Tier 7 candidate: No.

- `seo-aeo-best-practices`: WabbleSpec doesn't produce web content. SEO/AEO optimization is entirely out of scope for a SDLC framework. Tier 7 candidate: No.

**Expansion Opportunities Table:**

| Capability | Reference location | Why the project lacks it | What it would unlock | Dependencies | Effort signal | Tier 7 candidate |
|---|---|---|---|---|---|---|
| Structured L8 experiment document format (hypothesis + variants + status + winner + learnings) | `experiment-design.md` Sanity schema + `cms-integration.md` status lifecycle | WabbleSpec L8 evolution tracks evolution cycle artifacts (candidates, blueprints, augments) but has no standardized experiment-document receipt with hypothesis/winner/learnings fields | Formal hypothesis-to-conclusion trail for skill evolution experiments; auditable learning record per benchmark run | benchmark-loop SKILL.md update, new receipt type | weeks | Yes (weak signal) |

Gateway bundling: Only one Tier 7 candidate identified. No bundling recommendation.
