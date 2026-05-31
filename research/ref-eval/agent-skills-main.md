# Ref-Eval: agent-skills-main

**Reference:** `C:\Vaults\references\Other Projects References\agent-skills-main\agent-skills-main`
**Date:** 2026-05-31
**Evaluator:** ref-adopt
**Trust level:** MEDIUM (third-party, MIT, Vercel Engineering authorship — production-quality but domain-specific)

---

## Section 1 — Reference Summary

**Type:** Production skill collection for Claude Code / Claude AI. Solves the problem of giving AI agents structured, authoritative knowledge for React/Next.js development and Vercel deployment workflows.

**Behavioral content:** 7 skills encoding real engineering decisions — performance rule prioritization (CRITICAL → LOW), async waterfall elimination, bundle optimization, server/client boundary discipline, React Native list and animation best practices, View Transitions 7-step implementation workflow, multi-path Vercel deployment decision tree (4 states × 3 agent environments), token security protocol.

**Structural content:** Consistent 3-tier SKILL.md pattern (description → quick-reference index → link to full compiled AGENTS.md), individual rule files in `rules/` subdirectories with YAML frontmatter (title, impact, impactDescription, tags), Category × Impact × Prefix matrix table, TypeScript build toolchain that compiles rule files → AGENTS.md.

**Interaction content:** `rules/*.md` → `build.ts` + `_sections.md` + `metadata.json` → `AGENTS.md`. SKILL.md references rule files individually and links to AGENTS.md for full doc. View transitions SKILL.md routes four concerns to four reference files (implementation.md, css-recipes.md, patterns.md, nextjs.md).

**Maturity:** Active CI (`.github/workflows/react-best-practices-ci.yml`), versioned (`1.0.0` on all skills), real usage evidence (Vercel Labs repo), MIT. Mature.

**File inventory:**

| File | Purpose | Size | Key contents | Status | Transfer check |
|---|---|---|---|---|---|
| README.md | Skill overview and install | small | Skill listing, usage examples | Read | Description format conventions |
| CLAUDE.md | Agent guidance | small | `AGENTS.md` stub | Read | Nothing beyond pointer |
| AGENTS.md (root) | Agent file | small | Just `AGENTS.md` | Read | Nothing |
| skills/react-best-practices/SKILL.md | Main skill | medium | 69 rules, 8 categories, priority matrix | Read | Category×Impact matrix, CRITICAL-first ordering |
| skills/react-best-practices/AGENTS.md | Full compiled doc | large (3751 lines) | All 69 rules with incorrect/correct examples | Read (partial) | Incorrect/Correct label convention, LRU/RSC/async patterns |
| skills/react-best-practices/metadata.json | Version metadata | small | version, org, date | Skimmed | N/A |
| skills/react-best-practices/rules/_sections.md | Section metadata | small | Section titles, impact, description | Skimmed | Section schema pattern |
| skills/react-best-practices/rules/_template.md | Rule authoring template | small | Template for writing rules | Skimmed | Rule file template format |
| skills/react-best-practices/rules/*.md (65 files) | Individual rules | small each | Rule frontmatter + incorrect/correct examples | Skimmed (representative) | YAML frontmatter schema: title/impact/impactDescription/tags |
| skills/composition-patterns/SKILL.md | Composition patterns | small | 8 rules, 4 categories | Read | Priority matrix format |
| skills/composition-patterns/rules/architecture-avoid-boolean-props.md | Rule file | small | Boolean prop avoidance pattern | Read | Incorrect/Correct label pair in rule files |
| skills/react-native-skills/SKILL.md | RN best practices | small | 30+ rules, 8 categories | Read | List performance rules, animation GPU rules |
| skills/react-view-transitions/SKILL.md | View transitions | medium | API guide, patterns, placement rules | Read | 7-step workflow pattern, `default="none"` doctrine, priority table |
| skills/react-view-transitions/references/implementation.md | Step-by-step impl | medium | 7 steps + common mistakes | Read | Phased audit-first implementation workflow |
| skills/react-view-transitions/references/css-recipes.md | CSS animations | medium | Keyframe recipes, timing tokens | Skimmed | CSS animation token naming |
| skills/react-view-transitions/references/patterns.md | Advanced patterns | medium | Troubleshooting, events API | Skimmed | N/A |
| skills/react-view-transitions/references/nextjs.md | Next.js integration | small | Config flag, transitionTypes | Skimmed | N/A |
| skills/deploy-to-vercel/SKILL.md | Deployment workflow | medium | 4-state decision tree, 3 agent environments | Read | Multi-environment agent dispatch pattern |
| skills/deploy-to-vercel/resources/deploy.sh | Deploy script | small | No-auth deploy bash script | Skipped | Transfer: environment detection bash pattern |
| skills/deploy-to-vercel/resources/deploy-codex.sh | Codex deploy | small | Codex-specific deploy | Skipped | N/A |
| skills/vercel-cli-with-tokens/SKILL.md | Token auth | medium | Token location protocol, env var discipline | Read | Token security: export-not-flag rule |
| skills/web-design-guidelines/SKILL.md | UI review | small | Live-URL rule fetch pattern | Read | Live document fetch pattern |
| packages/react-best-practices-build/src/build.ts | Rule compiler | medium | Compiles rules/ → AGENTS.md | Read | Rule compiler build system architecture |
| packages/react-best-practices-build/src/types.ts | Type definitions | small | Rule, Section, GuidelinesDocument schemas | Read | Rule schema: ImpactLevel enum, Rule interface |
| packages/react-best-practices-build/src/parser.ts | Rule file parser | small | YAML frontmatter parser | Skipped | Transfer: parsing rule frontmatter |
| packages/react-best-practices-build/src/config.ts | Skill config | small | SKILLS map, paths | Skipped | N/A |
| packages/react-best-practices-build/src/migrate.ts | Migration | small | Old-format migrator | Skipped | N/A |
| packages/react-best-practices-build/src/validate.ts | Validation | small | Rule validation | Skipped | Transfer: rule quality validation approach |
| packages/react-best-practices-build/test-cases.json | Test cases | medium | bad/good pairs per rule | Read (partial) | Test case schema: ruleId, type, code, language, description |
| .github/workflows/react-best-practices-ci.yml | CI | small | CI build | Skipped | N/A |

**Connection map:**
- `rules/*.md` --[parse]--> `build.ts`: YAML frontmatter + markdown body
- `_sections.md` --[parse]--> `build.ts`: section number, title, impact, description
- `metadata.json` --[read]--> `build.ts`: version, org, date, abstract
- `build.ts` --[write]--> `AGENTS.md`: compiled full document
- `SKILL.md` --[reference]--> `rules/*.md`: individual rule lookup
- `SKILL.md` --[reference]--> `AGENTS.md`: full compiled doc
- `react-view-transitions/SKILL.md` --[route]--> `references/implementation.md`, `css-recipes.md`, `patterns.md`, `nextjs.md`
- `web-design-guidelines/SKILL.md` --[live fetch]--> external GitHub URL

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| All SKILL.md files (rules/*.md) | "Incorrect"/"Correct" as standard code example label pair | WabbleSpec skill authoring uses unspecified labels; "Incorrect/Correct" is more precise than "Before/After" (temporal) and clearer than "Bad/Good" (evaluative) | Add one CLAUDE.md rule: "Use Incorrect/Correct as the preferred label pair in code example blocks, not Before/After" | Medium |
| react-best-practices/SKILL.md, composition-patterns/SKILL.md | Category × Impact × Prefix quick-reference matrix table | gateway-aesthetic, gateway-engineering, and gateway-experience have 30+ rules but no ranked matrix; agents can't prioritize | Add matrix table in `## Quick Reference` sections of gateway-* SKILL.md files showing (Priority, Category, Impact, Prefix) | Medium |
| react-best-practices/AGENTS.md Section 1.3 | `better-all` dependency-based parallelization pattern | Describes a non-obvious Promise.all optimization for partial dependencies | gateway-engineering reference doc addition, or platform-web Tier 3 reference | Low |
| react-view-transitions/references/implementation.md | "Audit first" 7-step workflow | Step 1 is always an audit before any code; mirrors WabbleSpec's guard/plan-first invariant; formalizes phased rollout | Not directly adoptable — already captured in executor/decompose. But the "verify each navigation path" Step 7 (checking your own work at end) maps to verifier. | Low |
| deploy-to-vercel/SKILL.md | Multi-environment agent dispatch: detect context first | 4-state × 3-environment decision tree. The "gather state first" Step 1 pattern (run 4 probes before choosing method) is transferable to any multi-path skill | Add "gather state first" principle note to executor SKILL.md for multi-path task planning | Low |
| vercel-cli-with-tokens/SKILL.md | Token security rule: export-not-flag | Never pass secrets as CLI flags; export as env var; explicit bad/good pattern | Could add to gateway-security as a CLI credential handling rule | Low |
| packages/react-best-practices-build/ | Rule compiler build system | A TypeScript (→ Python) compiler that takes individual rule .md files + metadata.json → compiled AGENTS.md. Could be applied to WabbleSpec's gateway-* modules to compile their many rules into structured docs | Tier 7: build a Python analog of this system for WabbleSpec framework authoring | High (Tier 7) |
| skills/react-best-practices/ + react-native-skills/ | Platform-web and platform-mobile Tier 3 reference docs | 69 React/Next.js rules + 30+ React Native rules are production-hardened performance knowledge that platform-web/platform-mobile currently lack as a structured reference | Tier 7: add react-best-practices as Tier 3 reference in platform-web, react-native as reference in platform-mobile | High (Tier 7) |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| web-design-guidelines/SKILL.md | External URL dependency | Skill fetches live rules from `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` — if URL changes or goes offline, skill silently fails | Do not adopt this live-fetch pattern; embed rules as Tier 3 reference file instead | Medium |
| All React/RN rule content | Domain mismatch noise | 95% of the content (React hooks, Next.js routing, RN FlatList, Vercel CLI) is not applicable to WabbleSpec's Python/YAML/Markdown framework domain | Adopt only meta-patterns (label convention, matrix format, build system concept), not domain rules | Low |
| packages/react-best-practices-build/ | TypeScript dependency | Build system is TypeScript + Node.js; WabbleSpec uses Python scripts | Do not copy build.ts; build a Python analog if/when needed | Low |
| deploy-to-vercel/SKILL.md | Vercel vendor lock-in | Deployment skill hardcodes Vercel CLI commands | Do not adopt as-is; adopt only the environment detection pattern abstraction | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Incorrect/Correct label pair convention | Adapt | Cleaner than unspecified; CLAUDE.md addition | CLAUDE.md skill authoring section | High |
| Category × Impact × Prefix matrix table | Adapt | Improves gateway-* navigability | gateway-aesthetic SKILL.md, gateway-engineering SKILL.md | Medium |
| Rule compiler build system | Adapt (Tier 7) | Net-new capability; Python analog needed | New script in shared/scripts | High (deferred) |
| React/Next.js performance rules | Avoid (domain) | Not applicable to WabbleSpec's framework domain | N/A | N/A |
| Vercel deployment skills (deploy-to-vercel, vercel-cli) | Avoid | Vercel-vendor-specific | N/A | N/A |
| React Native skills | Avoid (domain); Tier 7 as reference | Not applicable inline; useful as platform-mobile Tier 3 | platform-mobile skill, Tier 7 | Low |
| web-design-guidelines live URL fetch | Avoid | External dependency risk | N/A | N/A |
| React View Transitions CSS skill | Avoid (domain); Tier 7 as reference | Not applicable to WabbleSpec; useful as platform-web Tier 3 | platform-web Tier 3 reference, Tier 7 | Low |
| Token export-not-flag security rule | Study only | Already implied in gateway-security; no gap | N/A | N/A |
| Multi-environment dispatch pattern | Study only | Already handled by executor; no gap to fill | N/A | N/A |
| _template.md authoring template pattern | Adapt (Tier 3) | WabbleSpec lacks a formal rule-file template | New reference doc | Low |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 4 | Both use skills/SKILL.md; both tier loading; but WabbleSpec's framework is 10× more complex |
| Architecture fit | 3 | Node.js build system vs Python; React domain vs framework-authoring domain |
| Implementation fit | 3 | Most content is React-specific; meta-patterns require extraction, not copy |
| Maintenance fit | 6 | Meta-patterns (label convention, matrix table) are low-maintenance once added |
| Risk level | 2 | Very low risk — only CLAUDE.md additions and optional Tier 7 items |
| Overall usefulness | 5 | A few genuine Tier 1-2 wins; rich Tier 7 seeding for platform skills |

**Overall: supporting-reference (5/10)**. Worth active Phase 1 work for the label convention and matrix table. Tier 7 items have high future value.

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — implement now):**
- Incorrect/Correct label pair → CLAUDE.md (AGENTS.md rules/architecture-avoid-boolean-props.md, all rule files)
- Category × Impact × Prefix matrix table → gateway-aesthetic SKILL.md (react-best-practices/SKILL.md format)

**Phase 2 (Low-Risk Adaptation):**
- Rule authoring `_template.md` reference doc → `.wabblespec/engine/shared/references/rule-template.md`
- ImpactLevel enum values (CRITICAL/HIGH/MEDIUM-HIGH/MEDIUM/LOW-MEDIUM/LOW) as standard for WabbleSpec rule annotation

**Phase 3 (Deeper Integration):**
- React/Next.js rules as platform-web Tier 3 reference (adapt, don't copy; summarize with WabbleSpec receipt conventions)

**Phase 4 (Do Not Cross):**
- Live URL fetch pattern (web-design-guidelines)
- Vercel CLI commands as WabbleSpec framework content
- TypeScript build system (incompatible runtime)

---

## Section 7 — Final Verdict

**Blunt judgment:** Supporting reference. The domain content (React rules, Vercel CLI) is not transferable. The meta-patterns are small but genuine.

**Best 3 to steal:**
1. `rules/architecture-avoid-boolean-props.md` line 1 — "Incorrect"/"Correct" label pair. Add to CLAUDE.md.
2. `react-best-practices/SKILL.md` Priority matrix table format — add to gateway-* SKILL.md files.
3. `packages/react-best-practices-build/` — concept of a rule compiler. Tier 7 Python analog.

**Worst 3 to avoid:**
1. `web-design-guidelines/SKILL.md` — live URL fetch pattern. External dependency risk.
2. All `rules/*.md` React content — zero domain overlap with WabbleSpec.
3. `deploy-to-vercel/SKILL.md` — Vercel-vendor-specific workflow.

**Classification:** supporting-reference (5/10)

**Recommended next action:** Implement Phase 1 (2 items), seed 3 Tier 7 drawers.

---

## Section 8 — Project Synthesis

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Impact-ordered gateway rule audits | CRITICAL-first rule ordering with impact levels; Category×Impact matrix table | WabbleSpec's wave execution + receipt-gated verification | gateway-aesthetic, gateway-engineering SKILL.md | Agents currently have no basis for prioritizing which gateway rule violations to fix first; adding an impact matrix gives them that basis |
| Structured rule authoring for quality floor | Rule file YAML frontmatter schema (title/impact/impactDescription/tags) + _template.md | WabbleSpec's quality-floor-check.py already validates rules | New reference doc + CLAUDE.md convention | Quality floor checks rules for existence but not for completeness of metadata; impact tagging would enable priority-weighted floor checks |

---

## Section 9 — Expansion Opportunities

Per-skill growth scan:

| Skill | Project equivalent? | Tier 7 candidate? |
|---|---|---|
| react-best-practices (69 rules) | platform-web exists but has no structured perf rules | Yes — platform-web Tier 3 reference |
| composition-patterns (8 rules) | gateway-engineering/gateway-aesthetic cover component architecture | No — covered |
| react-native-skills (30+ rules) | platform-mobile exists but has no RN-specific rules | Yes — platform-mobile Tier 3 reference |
| react-view-transitions (API guide + 4 references) | gateway-aesthetic covers animation; no VT-specific doc | Yes — gateway-aesthetic Tier 3 reference |
| deploy-to-vercel (deployment workflow) | deploy skill exists in WabbleSpec | No — WabbleSpec's deploy skill covers same ground |
| vercel-cli-with-tokens (token auth) | No direct equivalent | No — Vercel-specific, out of scope |
| web-design-guidelines (live rules) | gateway-aesthetic, gateway-experience | No — live-fetch anti-pattern; rules already covered |
| Rule compiler build system | No Python equivalent exists | Yes — shared/scripts rule-compiler.py |

**Expansion opportunities:**

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Tier 7? |
|---|---|---|---|---|---|---|
| React/Next.js structured perf rules | react-best-practices/rules/*.md (69 rules, 8 categories, CRITICAL→LOW) | platform-web exists but its Tier 3 has no impact-ordered React perf reference | Agents working on React web projects can apply CRITICAL rules first, reducing wasted effort on low-priority optimizations | platform-web SKILL.md update | days | Yes |
| React Native best practices reference | react-native-skills/rules/*.md (30+ rules) | platform-mobile has no RN-specific structured reference | Agents working on Expo/RN projects apply correct list virtualization, animation, and navigation patterns | platform-mobile SKILL.md update | days | Yes |
| React View Transitions reference | react-view-transitions/references/* (4 files, CSS recipes, 7-step workflow) | gateway-aesthetic covers animation theory; no VT-specific implementation guide | Agents implementing React UI get a production-tested step-by-step guide with CSS recipes | gateway-aesthetic SKILL.md update | days | Yes |
| Rule compiler (Python) | packages/react-best-practices-build/ (build.ts, parser.ts, types.ts) | No Python analog exists in WabbleSpec | SKILL.md authors could maintain individual rule .md files and compile to consolidated AGENTS.md; enables quality floor checks per rule | New Python script in shared/scripts | weeks | Yes |

**Gateway bundling signal:** The three platform Tier 7 items (react-best-practices, react-native, view-transitions) all produce reference documentation for platform-specific skill usage. They could be bundled as a single "platform-web references" session rather than three separate recipes.
