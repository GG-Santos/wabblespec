# Ref-Eval: claude-ads-main

**Reference**: `C:\Vaults\references\Extra Project References\claude-ads-main`
**Slug**: claude-ads-main
**Evaluated**: 2026-05-31
**Evaluator session**: tier7-expansions-20260530
**Overall verdict**: supporting-reference (6/10)

---

## Step 1b — File Inventory

| File | Purpose | Size | Key Contents | Status | Transfer Check |
|---|---|---|---|---|---|
| `README.md` | Project overview, install, commands | Large | Full command table, quality gates, architecture diagram | Read | N/A |
| `CLAUDE.md` | Dev rules and architecture | Small | 3-layer architecture, SKILL.md size limits, agent invocation rules | Read | N/A |
| `ads/SKILL.md` | Main orchestrator | Large | Routing table, Context Intake gate, Quality Gates (10 rules), Scoring, Community footer | Read | N/A |
| `skills/ads-audit/SKILL.md` | Parallel audit dispatcher | Medium | Quick Wins Criteria formula, per-platform scoring weights, output files | Read | N/A |
| `skills/ads-math/SKILL.md` | PPC calculator | Medium | 7 calculators, formulas, output table format (Metric/Value/Benchmark/Status) | Read | N/A |
| `skills/ads-plan/SKILL.md` | Strategic ad planning | Medium | 70/20/10 budget framework, campaign architecture template, 4-phase implementation roadmap | Read | N/A |
| `skills/ads-test/SKILL.md` | A/B test design | Medium | Hypothesis framework (IF/THEN/BECAUSE), sample size tables, quality checklist | Read | N/A |
| `agents/audit-google.md` | Google audit agent | Medium | 80 checks, Critical checks list (5.0x multiplier), key thresholds table, PMax checks | Read | N/A |
| `agents/creative-strategist.md` | Campaign concept agent | Medium | Concept structure, copy framework selection logic, image brief DO NOT rules | Read | N/A |
| `evals/creative-evals.json` | Skill routing evals | Small | 24 cases (18 positive + 6 negative), should_trigger: false cases | Read | N/A |
| `research/Ad Optimization Tool Logic Request.md` | Bidding decision engine spec | Very Large | 6 bidding strategies with exact thresholds, 3-tier attribution hierarchy, Meta CBO/ABO tree, budget scaling decision tree | Read | N/A |
| `CHANGELOG.md` | Release history | Medium | Version history only | Skipped | No transferable patterns — version notes and feature descriptions only |
| `CITATION.cff` | Citation metadata | Small | CFF academic citation format | Skipped | No transferable patterns — metadata format only |
| `CODE_OF_CONDUCT.md` | Contributor conduct | Small | Standard code of conduct | Skipped | Boilerplate |
| `CONTRIBUTING.md` | Contribution guide | Small | PR process, testing instructions | Skipped | No WabbleSpec-relevant process patterns |
| `LICENSE` | MIT license | Small | MIT license text | Skipped | N/A |
| `SECURITY.md` | Security policy | Small | Vulnerability reporting process | Skipped | Boilerplate |
| `SUPPORT.md` | Support info | Small | Community links | Skipped | N/A |
| `install.sh` / `install.ps1` | Cross-platform installers | Small | cp/mkdir install logic | Skipped | Domain-specific install scripts; pattern (copy to ~/.claude/skills/) already used by WabbleSpec sync |
| `uninstall.sh` / `uninstall.ps1` | Uninstallers | Small | rm cleanup logic | Skipped | Same rationale as install scripts |
| `requirements.txt` | Python deps | Small | playwright, reportlab | Skipped | Ad-specific deps |
| `ads/references/scoring-system.md` | Weighted scoring algorithm | Medium | Category weights, severity multipliers, grade thresholds | Skipped | Transfer check: scoring algorithm is domain-specific (ad checks) but multiplier pattern (5.0x Critical, severity x pass_rate formula) transfers |
| `ads/references/benchmarks.md` | Industry benchmarks | Large | CPC/CTR/CVR/ROAS by platform and industry | Skipped | Ad-specific data; no transferable framework patterns |
| `ads/references/bidding-strategies.md` | Bidding decision trees | Medium | Per-platform bidding logic | Skipped | Domain-specific; core thresholds captured in research doc read |
| `ads/references/budget-allocation.md` | Budget allocation | Medium | 70/20/10 framework, platform selection matrix | Skipped | Transfer check: 70/20/10 (proven/scaling/testing) allocation pattern is transferable as a budget framing for benchmark-loop iterations |
| `ads/references/brand-dna-template.md` | Brand DNA schema | Small | JSON schema for brand profile | Skipped | Domain-specific |
| `ads/references/mcp-integration.md` | MCP server setup | Small | Vendor MCP server names and URLs | Skipped | I6 violation — vendor names; do not read further |
| `ads/references/copy-frameworks.md` | Ad copy frameworks | Small | AIDA, PAS, BAB, 4P, FAB, Star-Story-Solution | Skipped | Transfer check: copy framework selection logic (cold audience→AIDA, pain-point→PAS, etc.) could inform brief writing for specify/blueprint, but overlap is thin |
| `ads/references/google-audit.md` | 74-check Google checklist | Large | Full check list with IDs (G01-G74) | Skipped | Ad-specific check content; structural pattern (numbered ID + category prefix) captured from audit-google.md |
| `ads/references/meta-audit.md` | 46-check Meta checklist | Large | Full check list with IDs (M01-M46) | Skipped | Same rationale |
| Other audit checklists (5 files) | Platform-specific checklists | Medium each | Ad platform checks | Skipped | Ad-specific content |
| `ads/references/platform-specs.md` | Creative specs | Medium | Ad dimensions by platform | Skipped | Ad-specific |
| `ads/references/conversion-tracking.md` | Pixel/CAPI setup | Medium | Server-side tracking setup | Skipped | Ad-specific |
| `ads/references/compliance.md` | Ad compliance requirements | Medium | Special Ad Categories, GDPR | Skipped | Ad-specific |
| Other creative spec files (6 files) | Platform creative dimensions | Small each | Image/video size specs | Skipped | Ad-specific |
| `ads/references/voice-to-style.md` | Brand voice to visual style mapping | Small | Voice axis to visual attribute table | Skipped | Transfer check: voice-axis → visual-attribute mapping pattern could inform brand DNA extraction; thin fit for WabbleSpec |
| `ads/references/gaql-notes.md` | GAQL field notes | Small | Google Ads Query Language patterns | Skipped | Ad-specific |
| `ads/references/image-providers.md` | Image provider config | Small | Vendor API config (Gemini/OpenAI/etc.) | Skipped | I6 violation — vendor names |
| `agents/audit-meta.md` through `agents/audit-compliance.md` (4 files) | Platform-specific audit agents | Medium each | Domain checks, scoring weights | Skipped | Transfer check: all follow same behavioral pattern as audit-google.md already read; no new structural patterns |
| `agents/visual-designer.md` | Image generation agent | Medium | Image generation prompts, banana domain modes | Skipped | Transfer check: banana domain modes and prompt format captured via creative-strategist.md; no new patterns |
| `agents/copy-writer.md` | Copy generation agent | Medium | Copy framework execution, platform limits | Skipped | Ad-specific copy constraints; copy framework selection logic captured |
| `agents/format-adapter.md` | Asset dimension validator | Small | Spec compliance checking | Skipped | Ad-specific |
| `skills/ads-google/SKILL.md` through `skills/ads-apple/SKILL.md` (8 files) | Platform-specific sub-skills | Medium each | Platform analysis workflows | Skipped | All follow same behavioral pattern as ads-audit already read; platform rules are ad-specific |
| `skills/ads-dna/SKILL.md` | Brand DNA extraction | Small | Web scraping to brand profile | Skipped | Transfer check: extract-first sequential pipeline (scrape → profile JSON → downstream consumers) mirrors WabbleSpec's recipe → scope → plan chain; pattern already documented in reference card |
| `skills/ads-create/SKILL.md` | Campaign brief generation | Medium | Brief output format, sequential deps | Skipped | Ad-specific creative workflow |
| `skills/ads-generate/SKILL.md` | Image generation | Medium | Provider routing, API key handling | Skipped | Vendor-specific |
| `skills/ads-photoshoot/SKILL.md` | Product photography | Medium | 5 style modes | Skipped | Ad-specific |
| `skills/ads-competitor/SKILL.md` | Competitor intelligence | Medium | Research workflow | Skipped | Ad-specific |
| `scripts/` (6 Python files) | Execution scripts | Medium each | Landing page analysis, screenshot capture, report generation | Skipped | Transfer check: generate_report.py --check gate (validate before output, fix warnings before delivering) is a transferable pre-delivery validation pattern; thin overlap given WabbleSpec already has guard-check.py |
| `research/Ad Audit Checklist & Scoring System.md` | Scoring system spec | Large | Detailed check weights | Skipped | Transfer check: check weighting methodology (Critical 5.0x, High 3.0x, medium/low 1.0x) is captured from audit-google.md and ads-audit/SKILL.md |
| `research/Paid Ad Technical Specifications Request.md` | Technical spec doc | Large | Platform API specs | Skipped | Ad-specific technical specs |
| `research/Paid Advertising Research for Claude-Ads.md` | Background research | Large | Industry research and benchmarks | Skipped | Ad-specific benchmark data |
| `research/The Definitive Paid Advertising Reference for 2026.md` | 2026 ad reference | Large | Platform updates and benchmarks | Skipped | Ad-specific |
| `assets/` (diagrams, demo.gif, banner.png) | Visual assets | Various | SVG diagrams and images | Skipped | No transferable patterns |
| `ads/scripts/` (8 Python files) | Ad-specific scripts | Medium each | Meta/LinkedIn API fetch scripts | Skipped | Ad-specific API integration |

---

## Step 1c — Connection Map

```
[ads/SKILL.md] --routes--> [skills/ads-*/SKILL.md]: command dispatch by keyword match
[ads/SKILL.md] --spawns via Task:fork--> [agents/audit-*.md]: parallel execution during /ads audit
[agents/audit-*.md] --reads--> [ads/references/scoring-system.md]: scoring weights
[agents/audit-*.md] --reads--> [ads/references/benchmarks.md]: industry thresholds
[agents/audit-*.md] --reads--> [ads/references/*-audit.md]: platform check lists
[agents/audit-*.md] --writes--> [*-audit-results.md]: per-platform JSON scores
[ads/SKILL.md] --validates--> [*-audit-results.md]: required fields before aggregation
[ads/SKILL.md] --aggregates--> [ADS-AUDIT-REPORT.md]: Aggregate = Sum(Platform_Score x Budget_Share)
[skills/ads-dna/SKILL.md] --produces--> [brand-profile.json]: brand extraction output
[skills/ads-create/SKILL.md] --reads--> [brand-profile.json]: brand injection into briefs
[skills/ads-create/SKILL.md] --produces--> [campaign-brief.md]: parsed by visual-designer
[agents/creative-strategist.md] --reads--> [campaign-brief.md]: concepts section
[agents/visual-designer.md] --parses--> [campaign-brief.md]: "## Image Generation Briefs" (bold labels must match exactly)
[agents/visual-designer.md] --produces--> [ad-assets/]: generated images
[skills/ads-*/SKILL.md] --resolve--> [ads/references/*.md]: path: ~/.claude/skills/ads/references/

WHAT BREAKS IF:
- ads/references/scoring-system.md path changes: all 6 audit agents produce unscored output
- bold label names in campaign-brief.md change: visual-designer parsing fails silently
- agent output JSON schema changes: orchestrator aggregation produces wrong Aggregate score
- context: fork unavailable: parallel audit degrades to sequential (fallback declared in ads-audit/SKILL.md)
```

---

## Dimension 1 — Behavior (Operational Detail)

**Context Intake Gate** (`ads/SKILL.md`):
- Must collect before any analysis: industry/business type (10 options), monthly ad spend, primary goal (Sales/Leads/App Installs/Calls/Brand), active platforms
- IF user provides context upfront → extract and proceed without re-asking
- Effect: calibrates benchmark selection, budget-appropriate recommendations, severity scoring

**Quality Gates (10 hard rules):**
1. Never recommend Broad Match without Smart Bidding
2. 3x Kill Rule: CPA >3x target → flag for immediate pause
3. Budget sufficiency: Meta ≥5x CPA/ad set, TikTok ≥50x CPA/ad group
4. Learning phase: never recommend edits during active learning
5. Compliance: always check Special Ad Categories (housing/employment/credit/finance)
6. Creative: never run silent video on TikTok (sound-on platform)
7. Attribution: default 7-day click/1-day view (Meta), data-driven (Google)
8. Andromeda: flag Meta <10 genuinely distinct creatives
9. Privacy gate: verify tracking stack before optimization
10. PDF quality gate: always run `--check` before `--output`; fix warnings before delivery

**Quick Wins Criteria** (`ads-audit/SKILL.md`):
```
IF severity == "Critical" OR severity == "High"
AND estimated_fix_time < 15 minutes
THEN flag as Quick Win
SORT BY (severity_multiplier x estimated_impact) DESC
```

**Critical Checks First** (`audit-google.md`):
- Critical = severity multiplier 5.0x
- Must evaluate Critical checks before any other category
- Failure in Critical category dominates the overall score

**Bidding Strategy Decision Tree** (`research/Ad Optimization Tool Logic Request.md`):
- Maximize Clicks: <15 conversions/30 days (cold start, 0 data required)
- Maximize Conversions: 15+ conversions/30 days (transition phase)
- tCPA: 30 strict / 50 ideal conversions/30 days; initial target = 1.1x-1.2x historical avg CPA; max 10% adjustment every 14 days
- tROAS: 50+ conversions/30 days; initial target = exact historical ROAS; lower to scale, raise for efficiency
- Manual CPC: <15 conversions/month (data poverty)

**Danger Signal Thresholds:**
- Bounce rate: >80% or 20% above historical average
- CVR crash: below 0.5% for >7 consecutive days
- CPA inflation: >30% above historical for 3 consecutive days
- Impression crash: >20% week-over-week drop
- Zero conversion days: 3 consecutive days
- CPC spike: >300% of account average

**Meta CBO vs ABO Decision Tree:**
- Budget <$100/day → ABO (CBO picks false positive winner at low volumes)
- Budget >$500/day → CBO (real-time allocation outperforms manual at scale)
- Testing phase → ABO (force spend to new creatives)
- Scaling phase → CBO (group 3-5 winning ad sets)

**Budget Scaling 20% Rule:**
- IF Current_CPA < Target_CPA (>10% below) AND (IS Lost to Budget >10% [Google] OR Frequency <2.0 [Meta]):
  - THEN increase daily budget by 20%
  - WAIT 72 hours before next scale
- Do NOT touch during: budget change >20%/24h, targeting change, creative edit, bid change (learning phase resets)

**Attribution Hierarchy of Truth** (`research/` Section 6.2):
- Tier 1: Backend/CRM data (cash in bank) — ultimate truth
- Tier 2: MER = Total Revenue / Total Ad Spend — macro view
- Tier 3: Platform data (dashboards) — optimization view
- Resolution: higher tier wins; double-counting at Tier 3 does not justify budget cuts

**Industry Auto-Detection (10 business types with signals):**
- SaaS: trial_start/demo_request events + pricing page targeting + long attribution windows
- E-commerce: purchase events + product catalog/feed + Shopping/PMax campaigns
- Local Service: call extensions + location targeting + store visits + directions events
- B2B Enterprise: LinkedIn active + ABM lists + CPA tolerance $50+ + long sales cycle
- (+ 6 more with similar signal specificity)

**Hypothesis Framework** (`ads-test/SKILL.md`):
- Template: `IF we [change] THEN [metric] will [direction] by [estimated %] BECAUSE [reasoning]`
- Quality checklist (5 items): single variable, specific metric, estimated effect size, timeframe, success/failure criteria defined before launch
- Minimum test duration: 7 days (weekly patterns); maximum recommended: 28 days (seasonal drift)

**Image Prompt DO NOT Rules** (`agents/creative-strategist.md`):
- Font names of any kind
- Specific text labels, data values, column/row content
- Phrases like "text reading X", "headline saying Y"
- "Dashboard with columns showing [data]" — use "abstract dashboard silhouette"
- More than 80 words total

**Copy Zone Constraints per Platform:**
- TikTok (9:16): "top 15% and bottom 20% minimal, active visual centered"
- Meta Feed (4:5): "lower 30% minimal and uncluttered for copy overlay"
- LinkedIn (1:1): "generous margin all sides, centered composition"
- Google PMax: "right third lighter and open for Google's text overlay"
- YouTube (16:9): "right 40% minimal for caption/copy overlay"

**Output Suppression Rules** (`ads/SKILL.md`, Community Footer):
- Show after: /ads audit, /ads google/meta/youtube/linkedin/tiktok/microsoft/apple, /ads creative, /ads landing, /ads budget, /ads plan, /ads competitor, /ads report
- Suppress after: /ads math, /ads test, /ads dna, /ads create, /ads generate, /ads photoshoot, context intake questions, error messages

---

## Dimension 2 — Format (Identifier Level)

**Skill frontmatter fields**: `name`, `description`, `argument-hint`, `license`, `user-invokable`, `model`, `maxTurns`, `tools`
- `user-invokable: false` marks sub-skills as orchestrator-only

**Agent frontmatter fields**: `name`, `description`, `model` (hardcoded), `maxTurns`, `tools`
- Model allocation: creative-strategist = opus/25, visual-designer = sonnet/30, copy-writer = sonnet/20, format-adapter = haiku/15

**Check ID convention**: `[Platform_Initial][Category_Prefix][Number]`
- Google general: G01-G74
- Google category prefix: G-CT1 (conversion tracking), G-PM1 (PMax), G-AI1 (AI/Demand Gen)
- Meta general: M01-M46

**Campaign naming convention**: `[Platform]_[Objective]_[Audience]_[Geo]_[Date]`
- Example: `META_CONV_Prospecting_US_2026Q1`

**Output files named by function** (always UPPERCASE):
- `ADS-AUDIT-REPORT.md`, `ADS-ACTION-PLAN.md`, `ADS-QUICK-WINS.md`
- `ADS-STRATEGY.md`, `CAMPAIGN-ARCHITECTURE.md`, `BUDGET-PLAN.md`
- Per-agent: `google-audit-results.md` (lowercase, per agent)

**Calculator output table**: `Metric | Value | Benchmark | Status (PASS/WARNING/FAIL)`

**Eval fixture fields**: `id`, `prompt`, `expected_skill`, `should_trigger`, `notes`

**Comment convention** (provenance):
- `<!-- Created: YYYY-MM-DD | vX.Y -->` at top of file
- `<!-- Source: repo-name (concept attribution) -->`

---

## Dimension 3 — Interactions (Contract Level)

| Producer | Consumer | Output Shape | What Breaks |
|---|---|---|---|
| `ads/SKILL.md` | 6 parallel audit agents | Task tool invocation with `context: fork` | If Task tool unavailable, fallback to sequential declared |
| Each audit agent | `ads/SKILL.md` aggregation | JSON with `Platform_Score`, `Platform_Budget_Share` fields | Aggregation fails if required fields absent (validation step declared but handler not explicit) |
| `ads/references/scoring-system.md` | All audit agents | Category weights, severity multipliers | Agents produce unscored or inconsistent output |
| `skills/ads-dna` | `skills/ads-create` | `brand-profile.json` at cwd | ads-create cannot generate brand-accurate concepts |
| `skills/ads-create` (creative-strategist agent) | `agents/visual-designer` | `campaign-brief.md` — `## Image Generation Briefs` section with exact bold label names | visual-designer silently fails to parse briefs if bold label names vary |
| `ads/references/*.md` | All sub-skills/agents | Path: `~/.claude/skills/ads/references/` | Path change breaks all reference loads silently |

**Sequencing constraint (creative pipeline)**: dna → create → generate → photoshoot. Each step produces the input for the next. Steps are independently runnable but dna must precede create.

**Parallel subagent validation contract**: orchestrator must verify each subagent returned valid JSON scores with required fields before aggregating. If any subagent fails this check, the aggregation step is blocked.

---

## Reference Type and Maturity

- **Type**: Production skill framework / deployed tool
- **Maturity**: Active CI (GitHub Actions badge), versioned releases, community usage (2,800+ members), blog coverage, install scripts with real logic, external contributors
- **Red flags**: Community footer with commercial promotion baked in as a hard behavioral rule

---

## Section 1 — Reference Summary

This is a production Claude Code skill framework for paid advertising audit and optimization. It solves the problem of comprehensive, structured ad account analysis across 7 platforms (Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple) using parallel subagent execution.

**Behavioral content**: 10 hard quality gates with specific conditions, algorithmic Quick Wins filter, bidding strategy decision trees with exact conversion thresholds (15/30/50 per strategy), budget scaling 20% rule with 72-hour cooldown, 3x Kill Rule for underperforming spend, industry auto-detection from 10 account signal patterns, 3-tier attribution hierarchy for cross-platform conflicts, A/B test hypothesis framework with quality checklist.

**Structural content**: 3-layer architecture (directive orchestrator / sub-skills / execution agents), RAG reference loading (on-demand, not at startup), numbered check IDs with category prefixes, model allocation by capability tier (opus/sonnet/haiku), mandatory negative eval cases in test fixtures, output file naming by deliverable function.

**Interaction content**: Parallel subagent dispatch via Task tool with context: fork, sequential creative pipeline with file-based handoffs (brand-profile.json → campaign-brief.md → ad-assets/), agent output schema validation before aggregation, on-demand reference path resolution.

**Mature**: Active CI, versioned releases, install scripts, community. Minor red flag: commercial promotion as hard behavioral rule.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `ads/SKILL.md` Quality Gates | Hard Gates block with "never violate" framing + enumerated conditions | WabbleSpec invariants are spread across reference files. A consolidated never-violate block makes rules scannable and harder to skip at execution time | Add `## Hard Gates` section to `executor/SKILL.md` with the same format: gate name, trigger condition, threshold | High |
| `skills/ads-audit/SKILL.md` Quick Wins Criteria | Algorithmic filter: IF severity Critical/High AND fix_time < 15 min THEN Quick Win, SORT BY (severity_multiplier x impact) DESC | Guard returns flat unsorted findings. Adding fixability as a sort dimension enables actionable triage | Add `## Quick Wins Filter` to `guard/SKILL.md` adapting threshold to WabbleSpec context (wave_count_to_fix instead of fix_time) | High |
| `research/Ad Optimization Tool Logic Request.md` Section 6.2 | 3-tier evidence hierarchy: Backend data > MER > Platform dashboards | Verifier has no declared conflict resolution when execution artifact, receipt, and agent assertion disagree | Add `## Evidence Hierarchy` to `verifier/SKILL.md`: Tier 1 = files on disk, Tier 2 = receipt chain, Tier 3 = agent assertions | High |
| `skills/ads-test/SKILL.md` Hypothesis Framework | IF/THEN/BECAUSE template + 5-item quality checklist | benchmark-loop and skill-tdd produce results without a pre-declared hypothesis — results are descriptive, not confirmatory | Add hypothesis block format as pre-condition to `benchmark-loop/SKILL.md` and `skill-tdd/SKILL.md` | High |
| `evals/creative-evals.json` negative-001 through negative-006 | Negative routing eval cases with `should_trigger: false` and notes | WabbleSpec tests positive triggers only; mis-routing (executor activating when decompose should) is untested | Add negative test entries to WabbleSpec eval fixtures; enforce presence via quality-floor-check.py Gate 1 | Medium |
| `agents/audit-google.md` Critical Checks section | "Evaluate Critical first" + explicit 5.0x multiplier pattern | Guard runs in declared order. Assigning multipliers and requiring Critical evaluation first makes output machine-parseable | Adapt for `guard/SKILL.md`: assign 5.0x/3.0x/1.0x multipliers to I-class/H-class/M-class checks; require I-class first | Medium |
| `ads/SKILL.md` Community Footer section | "When to show / When to skip" output suppression enumeration | WabbleSpec skills lack explicit suppression rules for optional output sections | Add `## When to Suppress` to `archive/SKILL.md` and `executor/SKILL.md` enumerating task types where footers and summary blocks are omitted | Medium |
| `agents/creative-strategist.md` Image brief DO NOT rules | Anti-hallucination constraints for image prompts (font names, text labels, >80 words) | WabbleSpec's visual-companion Tier 7 item needs image generation guidance; these are empirically validated anti-hallucination constraints | Carry into `visual-companion/SKILL.md` if built | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `ads/SKILL.md` Community Footer | Commercial promotion embedded as hard behavioral rule | Hard-coding a community link in skill behavioral rules produces unwanted promotional output in any framework that adopts this pattern | Explicitly exclude | High |
| All `agents/` files | `model: opus/sonnet/haiku` hardcoded | Direct I6 violation in any WabbleSpec file that copies agent frontmatter | Flag as do-not-copy; use capability descriptors | High |
| `ads/SKILL.md` Orchestration Logic | `Task tool with context: fork` verbatim API syntax | Vendor-specific; breaks if Task tool API changes | Study pattern only; never copy syntax | Medium |
| `evals/creative-evals.json` | No version field or skill_version in eval entries | Eval entries cannot be traced to which skill version they test | Add version fields when writing WabbleSpec eval fixtures | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Quality Gates "never violate" block | Adapt | High-impact consolidation of invariant rules | `executor/SKILL.md` | P1 |
| Quick Wins algorithmic filter | Adapt | Adds fixability dimension to Guard triage | `guard/SKILL.md` | P1 |
| 3-tier evidence hierarchy | Adapt | Deterministic conflict resolution for Verifier | `verifier/SKILL.md` | P1 |
| Hypothesis framework (IF/THEN/BECAUSE + checklist) | Adapt | Pre-condition for confirmatory experiment design | `benchmark-loop/SKILL.md`, `skill-tdd/SKILL.md` | P1 |
| Negative eval cases pattern | Adapt | Closes routing test gap | WabbleSpec eval fixtures | P2 |
| Critical checks first + severity multipliers | Adapt | Enables priority-weighted scoring in Guard | `guard/SKILL.md` | P2 |
| Output suppression enumeration | Adapt | Prevents noise on micro-tasks | `archive/SKILL.md`, `executor/SKILL.md` | P2 |
| Image prompt DO NOT rules | Adapt (future) | Anti-hallucination constraints for visual-companion | `visual-companion/SKILL.md` (Tier 7) | P3 |
| Community footer hard rule | Avoid | Commercial promotion embedded in skill behavioral rules | N/A |
| `model: opus/sonnet/haiku` in agent frontmatter | Avoid | I6 violation | N/A |
| `context: fork` verbatim | Study Only | Pattern transferable; syntax vendor-specific | Understand dispatch approach |

---

## Section 5 — Integration Fit

| Dimension | Score (1-10) | Explanation |
|---|---|---|
| Concept fit | 4 | Domain is advertising vs SDLC. Behavioral patterns (decision trees, quality gates, parallel dispatch) transfer; domain knowledge does not. |
| Architecture fit | 6 | 3-layer (directive/orchestration/execution) maps to WabbleSpec L0-L2. Agent dispatch pattern is structurally compatible. RAG reference loading mirrors WabbleSpec's on-demand pattern. |
| Implementation fit | 7 | All adoptable items are additive to existing SKILL.md files. No new infrastructure. Low friction. |
| Maintenance fit | 8 | All adaptations are textual changes to SKILL.md files. No new scripts, schemas, or dependencies. |
| Risk level | 2 | Two clear avoid items (community footer, model names). All other adaptations are additive with no breaking changes possible. |
| Overall usefulness | 6 | Supporting reference. Domain doesn't transfer but behavioral and structural patterns fill real gaps. |

---

## Section 6 — Recommended Extraction Plan

### Phase 1 (Safe Learning — adopt now)

1. **Evidence hierarchy** → `verifier/SKILL.md`: Add `## Evidence Hierarchy` section with 3-tier conflict resolution rule
2. **Quick Wins filter** → `guard/SKILL.md`: Add `## Quick Wins Filter` with IF/SORT formula adapted for WabbleSpec
3. **Hard Gates block** → `executor/SKILL.md`: Consolidate invariant rules into a never-violate block with named conditions
4. **Hypothesis framework** → `benchmark-loop/SKILL.md` and `skill-tdd/SKILL.md`: Add hypothesis template as mandatory pre-condition
5. **Negative eval pattern** → WabbleSpec eval guidance (CLAUDE.md or quality-floor-check.py): document negative eval requirement

### Phase 2 (Low-Risk Adaptation)

6. **Severity multipliers** → `guard/SKILL.md`: Assign 5.0x/3.0x/1.0x multipliers to I-class/H-class/M-class checks
7. **Output suppression** → `archive/SKILL.md` and `executor/SKILL.md`: When to Suppress section
8. **Critical first evaluation order** → `guard/SKILL.md`: Require I-class checks evaluated first

### Phase 3 (Deeper Integration)

9. **Image prompt DO NOT rules** → `visual-companion/SKILL.md` (if built): anti-hallucination constraints

### Phase 4 (Do Not Cross)

- Community footer
- Model name hardcoding
- `context: fork` verbatim

---

## Section 7 — Final Verdict

**Classification: supporting-reference (6/10)**

**Best 3 to steal:**

1. **Quick Wins algorithmic filter** (`skills/ads-audit/SKILL.md`): The IF severity + fix_time → Quick Win + sort formula directly improves Guard triage. Zero WabbleSpec equivalent exists. Immediately adoptable.

2. **3-tier evidence hierarchy** (`research/Ad Optimization Tool Logic Request.md`, Section 6.2): Maps cleanly to WabbleSpec's Verifier: execution artifacts > receipt chain > agent assertions. Fills a gap where conflicting evidence is not deterministically resolved.

3. **Hypothesis framework** (`skills/ads-test/SKILL.md`): IF/THEN/BECAUSE + quality checklist applies directly to benchmark-loop and skill-tdd. Converts descriptive result logging to confirmatory experiment design.

**Worst 3 to avoid:**

1. **Community footer hard rule** (`ads/SKILL.md`): Commercial promotion baked into skill behavioral rules. Produces unwanted output in any framework that copies it.

2. **Model name hardcoding** (all `agents/*.md` files): `model: opus/sonnet/haiku` is a direct I6 violation. Do not copy agent frontmatter verbatim.

3. **`context: fork` verbatim** (`ads/SKILL.md` Orchestration Logic): Vendor-specific Task tool API syntax. The dispatch pattern is valuable; this specific call syntax is not transferable.

**Recommended next action**: Adopt 4 Phase 1 items targeting 4 existing SKILL.md files. All are additive, zero risk of regression.

---

## Section 8 — Project Synthesis

### Idea 1: Weighted Guard scoring with Quick Wins triage output

- **What**: Guard produces a weighted score (Critical=5.0x, High=3.0x, Low=1.0x) and separates Quick Wins (high-severity + fast-fix) from Backlog findings in its output
- **Reference contribution**: Quick Wins Criteria formula + severity multiplier pattern from `ads-audit/SKILL.md`
- **Project contribution**: Guard's existing check categories + receipt-writer.py scoring integration + I/H/M severity tiers
- **Target**: `.wabblespec/engine/modules/l2/guard/SKILL.md`
- **Gap closed**: Guard currently outputs a flat unsorted findings list. Triage is manual. The synthesis produces auto-sorted, prioritized Guard output.

### Idea 2: Evidence Hierarchy for Verifier conflict resolution

- **What**: When wave receipt, agent assertion, and prior artifact state conflict, Verifier resolves deterministically via 3-tier hierarchy
- **Reference contribution**: Attribution Hierarchy of Truth pattern from `research/Ad Optimization Tool Logic Request.md` Section 6.2
- **Project contribution**: Verifier's multi-source evaluation + receipt chain structure
- **Target**: `.wabblespec/engine/modules/l2/verifier/SKILL.md`
- **Gap closed**: Verifier has no declared tie-breaking rule when sources disagree. A missing file overrides a receipt claiming success.

### Idea 3: Hypothesis-gated benchmark loop with outcome classification

- **What**: Before each benchmark-loop iteration, require a structured hypothesis; after iteration, classify result as Confirmed/Refuted/Inconclusive vs declared hypothesis; TSV log includes hypothesis_confirmed column
- **Reference contribution**: ads-test/SKILL.md hypothesis framework + quality checklist (5 items)
- **Project contribution**: benchmark-loop's existing iteration/commit/revert cycle + TSV log format
- **Target**: `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md`
- **Gap closed**: benchmark-loop records iteration/commit/metric/delta/status but has no pre-declared hypothesis — results are descriptive rather than confirmatory.

### Idea 4: Negative Routing Eval Fixture

- **What**: A JSON eval fixture with entries that test skill mis-routing: prompts that look like skill X triggers but must NOT activate skill X, validated during quality-floor-check
- **Reference contribution**: `evals/creative-evals.json` negative cases (id, prompt, expected_skill, should_trigger: false, notes)
- **Project contribution**: WabbleSpec's quality-floor-check.py Gate 1 infrastructure + existing skill frontmatter description: fields
- **Target**: `.wabblespec/state/experiments/negative-routing-evals.json` + quality-floor-check.py
- **Gap closed**: WabbleSpec tests positive triggers only. Negative routing cases catch skill mis-routing regressions.

---

## Section 9 — Expansion Opportunities

### Expansion 1: Skill Eval Runner

| Field | Value |
|---|---|
| Capability | Automated prompt-based skill routing validator with pass rate report |
| Reference location | `evals/creative-evals.json` — eval fixture format and negative case pattern |
| Why the project lacks it | quality-floor-check.py checks structural properties; skill-tdd checks behavioral delta; no tool validates that natural-language prompts route to the correct skill |
| What it would unlock | Regression testing on description: edits. Quantitative skill router fidelity score (N/M prompts routed correctly). Catches accidental trigger surface expansion. |
| Dependencies | quality-floor-check.py infrastructure, skill frontmatter description: fields, When NOT to use sections |
| Effort signal | days |
| Tier 7 candidate | Yes |

### Expansion 2: Deliverable Quality Score

| Field | Value |
|---|---|
| Capability | Graduated 0-100 wave output health score with letter grade |
| Reference location | `ads/SKILL.md` Scoring Methodology + `ads-audit/SKILL.md` weighted category score |
| Why the project lacks it | WabbleSpec uses binary PASS/FAIL. A wave at 72/100 and 40/100 both show PARTIAL with no degree of completion signal. |
| What it would unlock | Partial completion surfacing with degree. Trend tracking across benchmark-loop iterations. Executor surfaces health score at wave end without blocking on PASS/FAIL. |
| Dependencies | receipt-writer.py, wave-plan structure (acceptance criteria), quality-floor-check.py |
| Effort signal | weeks |
| Tier 7 candidate | Yes |

---

## Memory Drawers Written

| Drawer | Path | Contents |
|---|---|---|
| reference-card-20260531.json | `rooms/claude-ads-main/drawers/` | Main reference card: concepts, risks, do_not_copy |
| quick-wins-filter-20260531.json | `rooms/claude-ads-main/drawers/` | Quick Wins formula with literal values and WabbleSpec adaptation |
| evidence-hierarchy-20260531.json | `rooms/claude-ads-main/drawers/` | 3-tier hierarchy for Verifier conflict resolution |
| hypothesis-framework-20260531.json | `rooms/claude-ads-main/drawers/` | IF/THEN/BECAUSE template + quality checklist |
| negative-routing-evals-20260531.json | `rooms/claude-ads-main/drawers/` | Negative eval case pattern + WabbleSpec adaptation examples |
| tier7-skill-eval-runner-20260531.json | `rooms/claude-ads-main/drawers/` | Tier 7: automated routing validator (days effort) |
| tier7-deliverable-quality-score-20260531.json | `rooms/claude-ads-main/drawers/` | Tier 7: graduated wave health score (weeks effort) |
