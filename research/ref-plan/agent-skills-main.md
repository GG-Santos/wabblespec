# Ref-Plan: agent-skills-main

**Reference:** agent-skills-main
**Date:** 2026-05-31
**Based on:** research/ref-eval/agent-skills-main.md

---

## Candidate Extraction Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Incorrect/Correct as standard code example label pair | Behavioral (convention) | Medium | High | Low |
| A2 | Category × Impact × Prefix matrix table in gateway-* SKILL.md | Format | Medium | Medium | Low |
| A3 | Rule file authoring `_template.md` reference doc | Format (infrastructure) | Low | Medium | Low |
| A4 | ImpactLevel enum for rule annotation in CLAUDE.md authoring guidance | Behavioral | Low | Medium | Low |
| T7-1 | Rule compiler build system (Python analog) | Tier 7 | High | High | Low |
| T7-2 | React/Next.js perf rules as platform-web Tier 3 reference | Tier 7 | High | Medium | Low |
| T7-3 | React Native rules as platform-mobile Tier 3 reference | Tier 7 | Medium | Medium | Low |
| T7-4 | React View Transitions as gateway-aesthetic Tier 3 reference | Tier 7 | Low | Low | Low |

---

## Exclusion List

| Item | Reason |
|---|---|
| All React/Next.js/RN domain rules (inline in SKILL.md) | Domain mismatch — I11 scope, React content not applicable to framework authoring |
| web-design-guidelines live-URL fetch pattern | External dependency risk; pattern violates WabbleSpec's Tier 3 self-containment principle |
| Vercel CLI deployment commands | Vercel-vendor-specific; not part of WabbleSpec's framework domain |
| TypeScript build system (build.ts) | Wrong runtime; Python is the standard; copying TS would introduce incompatible toolchain |
| deploy-to-vercel / vercel-cli-with-tokens skill content | Vendor-specific; deploy skill already exists in WabbleSpec |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Score | Tier |
|---|---|---|
| A1 | (2×2) + 3 - 1 = 6 | Tier 1 |
| A2 | (2×2) + 2 - 1 = 5 | Tier 2 |
| A3 | (1×2) + 2 - 1 = 3 | Tier 3 |
| A4 | (1×2) + 2 - 1 = 3 | Watch Only (adjacent to A1) |

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive, no new files)

**A1 — Incorrect/Correct label pair convention**
- What: Add a CLAUDE.md skill authoring rule specifying "Incorrect"/"Correct" as the preferred code example label pair in SKILL.md rule files and inline rule documentation
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md` — skill authoring conventions section
- How: Add one bullet point after the existing skill content three-tier loading rule: "Use Incorrect/Correct as the preferred label pair in code example blocks within SKILL.md files. This is more precise than Before/After (which implies temporal change) and clearer than Bad/Good (which is evaluative). Match the label case exactly: **Incorrect:** and **Correct:**"
- Reference location: `skills/react-best-practices/rules/*.md` — every rule file uses `## Incorrect:` / `## Correct:` heading convention, and AGENTS.md consistently formats as `**Incorrect:**` / `**Correct:**`
- Gate: CLAUDE.md contains the sentence "Use Incorrect/Correct as the preferred label pair in code example blocks"
- Literal values: "**Incorrect:**", "**Correct:**"

### Tier 2 — Module-level augmentation

**A2 — Category × Impact × Prefix matrix in gateway-* SKILL.md**
- What: Add a Priority | Category | Impact | Prefix table to gateway-aesthetic SKILL.md as a quick-reference scan aid for the 30+ rules
- Where: `.wabblespec/engine/modules/l4/gateway-aesthetic/SKILL.md` and `.claude/skills/gateway-aesthetic/SKILL.md`
- How: After the existing intro paragraph and before the first section, insert a `## Rule Categories by Priority` table with columns (Priority, Category, Impact, Prefix) listing the existing rule categories in descending impact order. Gateway-aesthetic's categories: Anti-monoculture (HIGH), Token compliance (HIGH), Background layer (MEDIUM-HIGH), Animation (MEDIUM), Typography (MEDIUM), Shadow philosophy (MEDIUM), Mobile platform (MEDIUM), Layout (LOW)
- Reference location: `skills/react-best-practices/SKILL.md` lines 24-34 (the Priority matrix table)
- Gate: gateway-aesthetic SKILL.md contains `## Rule Categories by Priority` section with a markdown table
- Specify required: No
- Breaking change risk: None — additive

### Tier 3 — New shared infrastructure

**A3 — Rule authoring `_template.md` reference doc**
- What: New reference file documenting the standard format for authoring individual rule files within a skill's rules/ or references/ subdirectory
- Where: `.wabblespec/engine/shared/references/rule-template.md`
- How: Create a template showing YAML frontmatter (title, impact, impactDescription, tags), the Incorrect:/Correct: label pair structure, and the reference URL convention
- Reference location: `packages/react-best-practices-build/src/types.ts` (Rule interface), `skills/react-best-practices/rules/_template.md` (authoring template), `skills/composition-patterns/rules/architecture-avoid-boolean-props.md` (example)
- Gate: File exists at target path containing YAML frontmatter schema and Incorrect/Correct example structure
- Specify required: No

### Tier 6 — Synthesis

None. The Section 8 synthesis items (impact-ordered gateway audits, structured rule authoring for quality floor) are both achievable through the Tier 1-3 items above without a separate synthesis artifact.

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| Rule compiler (Python) | packages/react-best-practices-build/ (build.ts, parser.ts, types.ts, config.ts) | No Python analog exists for compiling rule files → consolidated docs | SKILL.md authors maintain individual rule .md files; quality-floor checks can validate per-rule metadata | Python 3 stdlib only | weeks | "Build a Python rule compiler in .wabblespec/engine/shared/scripts/rule-compiler.py that reads rules/*.md files with YAML frontmatter (title/impact/tags) and compiles to a consolidated AGENTS.md or reference doc. Follow react-best-practices-build architecture: parse _sections.md for section metadata, read metadata.json for version info, sort rules by impact level." |
| React/Next.js perf reference for platform-web | skills/react-best-practices/rules/*.md (69 rules, 8 categories) | platform-web has no structured impact-ordered React perf reference | Agents working on React web projects apply CRITICAL rules first | platform-web SKILL.md update | days | "Create .wabblespec/engine/modules/l6/platform-web/references/react-best-practices.md as a Tier 3 reference summarizing the 69 react-best-practices rules organized by Priority/Category/Impact (CRITICAL→LOW), with the 5 most important rules per category. Add a ## Reference Routing entry in platform-web SKILL.md pointing to this file for React/Next.js tasks." |
| React Native reference for platform-mobile | skills/react-native-skills/rules/*.md (30+ rules) | platform-mobile has no RN-specific structured reference | Agents on Expo/RN projects apply correct list virtualization and animation patterns | platform-mobile SKILL.md update | days | "Create .wabblespec/engine/modules/l6/platform-mobile/references/react-native-best-practices.md as a Tier 3 reference summarizing the react-native-skills rules (list-performance-*, animation-*, ui-*, navigation-*) with brief rationale per rule. Add Reference Routing entry in platform-mobile SKILL.md." |
| React View Transitions reference for gateway-aesthetic | skills/react-view-transitions/SKILL.md + references/ | gateway-aesthetic covers animation theory; no VT implementation guide exists | Agents implementing React UI get CSS recipes and 7-step workflow | gateway-aesthetic SKILL.md routing update | days | "Create .wabblespec/engine/modules/l4/gateway-aesthetic/references/react-view-transitions.md as a Tier 3 reference with the 7-step implementation workflow (audit → CSS recipes → isolation → page transitions → Suspense → shared elements → verify) and the CSS token naming conventions from react-view-transitions references/." |

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| All React/Next.js domain rules | I11: Framework and product never mix — React domain content is not framework content |
| `web-design-guidelines` live-URL rule fetch | I10: Implied completion — if URL is down, the skill silently fails without a receipt |
| TypeScript build toolchain | I6: Runtime is vendor-neutral — TypeScript/Node.js is a runtime-specific dependency |
| Model/tool name references | I6: None found in this reference (compliant), but do not add any |

---

## Priority Implementation Order

| Order | ID | Item | Why first |
|---|---|---|---|
| 1 | A1 | Incorrect/Correct label pair → CLAUDE.md | Smallest, highest-fit, affects all future skill authoring immediately |
| 2 | A2 | Category×Impact matrix → gateway-aesthetic SKILL.md | Medium effort, improves agent navigability for complex gateway |
| 3 | A3 | Rule authoring `_template.md` reference doc | Infrastructure for future skill authors |

---

## Execution Notes

- A1 and A3 can run in parallel (different target files)
- A2 depends on reading gateway-aesthetic first to verify current format
- Tier 7 items require separate recipe sessions; do not implement in this pipeline
- gateway-aesthetic has both engine module and .claude/skills/ copies; update both (Phase 3 Step 5)
