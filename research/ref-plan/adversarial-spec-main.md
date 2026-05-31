# Ref-Plan: adversarial-spec-main

**Date:** 2026-05-31
**Slug:** adversarial-spec-main
**Source eval:** `research/ref-eval/adversarial-spec-main.md`

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Preserve-intent taxonomy (ERROR/RISK/PREFERENCE + "additions are cheap") | Behavioral | High | High | Low |
| A2 | Press protocol (4-question early-agreement verification) | Behavioral | High | High | Low |
| A3 | Deep interview additions (prior-failure probing, tradeoffs axis, "what keeps you up at night") | Behavioral | Medium | High | Low |
| A4 | Typed PRD/Tech spec critique criteria for specify Step 4 | Behavioral | Medium | Medium | Low |
| A5 | Quality-over-speed convergence pitfall for specify | Behavioral | Low-Medium | Medium | Low |
| A6 | Persona reference table for adversary | Behavioral | Medium | Medium | Low |

---

## Exclusion List

| Excluded item | Reason |
|---|---|
| All model names in SKILL.md (30+ hardcoded names) | I6: framework files must use capability placeholders |
| litellm / debate.py script infrastructure | External binary dependency; conflicts with WabbleSpec instruction-based model |
| AskUserQuestion calls | Prior directive against this pattern across ref-adopts |
| Session persistence to `~/.config/adversarial-spec/` | I11: product-space state vs. framework state; also conflicts with `.wabblespec/state/` model |
| Telegram integration | Domain-specific external service |
| AWS Bedrock configuration | I6 vendor-specific; provider names throughout |
| Codex CLI / Gemini CLI subprocess routing | I6 + external binary |
| "Claude is active participant" framing | Blurs role boundary; adversary = challenge only, not synthesis |
| [SPEC]/[AGREE] convergence token protocol | Conflicts with WabbleSpec receipt-gate model (I10) |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Impact×2 | Fit | Risk | Score |
|---|---|---|---|---|
| A1 | 6 | 3 | 1 | 8 |
| A2 | 6 | 3 | 1 | 8 |
| A3 | 4 | 3 | 1 | 6 |
| A6 | 4 | 2 | 1 | 5 |
| A4 | 4 | 2 | 1 | 5 |
| A5 | 3 | 2 | 1 | 4 |

---

## Tier Assignments

### Tier 1 — Behavioral additions to existing files

**A1 — Preserve-intent challenge taxonomy**
- What: Add `## Preserve Intent Mode` section to adversary SKILL.md with ERROR/RISK/PREFERENCE taxonomy and "additions are cheap, deletions require justification" rule
- Where: `.claude/skills/adversary/SKILL.md` (and engine mirror)
- How: Insert after `## Role boundary — Adversary stops here` section. New section explains: when a challenge point would recommend removal of something from an artifact, classify it first. ERRORS (factually wrong, contradictory, technically broken) → include. RISKS (security holes, scalability issues, missing handling) → flag. PREFERENCES (different style, structure, approach) → do NOT include as a weakness. For every proposed removal, require: quote the exact text, state what concrete problem it causes, distinguish error from preference. Apply automatically when `challenger_mode: "spec-bound"`.
- Literal values to reproduce: "ERRORS: Factually wrong, contradictory, or technically broken (remove/fix these)", "RISKS: Security holes, scalability issues, missing error handling (flag these)", "PREFERENCES: Different style, structure, or approach (DO NOT remove these)", "additions are cheap, deletions require justification"
- Gate: Adversary output must include a `preserve_intent_applied: true|false` field when operating on spec artifacts

**A2 — Press protocol for suspicious agreement**
- What: Add `## Shallow-Analysis Detection` subsection to adversary SKILL.md
- Where: `.claude/skills/adversary/SKILL.md` (and engine mirror)
- How: Add after the "A note on common failure modes" section. When `strong_output_acknowledged: true` is being set with fewer than 3 distinct challenge domains engaged (i.e., one or more of weaknesses/alternatives/assumptions/failure_scenarios has < 2 findings), apply the press protocol before finalizing: (1) confirm the entire artifact was read (not just the opening sections), (2) identify at least 3 specific artifact sections reviewed with what was verified in each, (3) explain exactly what makes the artifact strong enough to acknowledge as strong output, (4) identify any remaining concerns however minor. If new findings surface during press, process them normally. If artifact is genuinely strong after press, proceed with `strong_output_acknowledged: true`.
- Literal values to reproduce: 4 steps from SKILL.md:408-418 (adapted for adversary context, removing "model" references)
- Gate: `strong_output_acknowledged: true` with fewer than 3 domains engaged triggers press before finalizing

**A3 — Deep interview probing additions**
- What: Add 3 probing sub-questions to interview SKILL.md's existing dimension framework
- Where: `.claude/skills/interview/SKILL.md` (and engine mirror)
- How: Add a `## Deep Probing Sub-Questions` subsection after the Nine ambiguity dimensions section. Three additions: (1) Under "Intent" dimension: add "What prior attempts have been made? Why did they fail or fall short?" — surfaces hidden constraints. (2) Add a new tradeoffs/priorities dimension: "If we can't have everything, what gets cut first? Speed vs. quality vs. cost priorities? What are the non-negotiables?" (3) Under "Risk tolerance" dimension: add the framing "What keeps you up at night about this project? What could cause it to fail?" — more emotionally grounded than abstract risk questions.
- Gate: Intent.md produced after these additions contains answers for tradeoffs/priorities when present

**A4 — Typed document criteria for specify Step 4**
- What: Add optional typed coverage checklists to specify SKILL.md Step 4
- Where: `.claude/skills/specify/SKILL.md` (and engine mirror)
- How: Append after the existing Step 4 checklist: "**When target = Product (PRD-style):** additionally verify: (1) success metrics are measurable with specific numeric targets; (2) scope section explicitly lists what is OUT as well as what is IN; (3) no technical implementation details (databases, frameworks, deployment) appear in the spec — those belong in a technical spec. **When target = Framework (Technical-spec-style):** additionally verify: (1) every API endpoint or interface has: method, path/identifier, request shape, response shape, error codes; (2) security considerations address authentication, authorization, encryption, and input validation; (3) no ambiguity an implementer would need to resolve."
- Gate: Applies only when complexity = Medium or High and target matches one of the two types

**A5 — Quality-over-speed convergence pitfall**
- What: Add Pitfalls section to specify SKILL.md
- Where: `.claude/skills/specify/SKILL.md` (and engine mirror)
- How: Add a `## Pitfalls` section at the end of the SKILL.md body (before "A note on common failure modes" if one exists, or at the end). Single bullet: "Do not converge early on a task card that passes Step 4 checks quickly but was written in isolation. A task card requiring 2–3 revision cycles to resolve scope, success criteria, and failure paths is higher quality than one that passed the checklist on the first attempt. Specificity under pressure tends toward the vague."
- Gate: Pitfalls section present in final SKILL.md

**A6 — Persona reference table for adversary**
- What: Add a persona lookup table as a reference resource to adversary SKILL.md
- Where: `.claude/skills/adversary/SKILL.md` (and engine mirror)
- How: Add a `## Caller-Specified Persona Mode` section after the `## Inputs` table. When a caller passes `persona: "<name>"`, activate the corresponding cognitive stance before generating challenges. Table with 10 entries: security-engineer (attack surface, paranoid about edge cases), oncall-engineer (observability, error messages, debugging at 3am), junior-developer (flags ambiguity and tribal knowledge assumptions), qa-engineer (missing test scenarios, boundary conditions, untestable criteria), site-reliability (deployment, rollback, monitoring, capacity, incidents), product-manager (user value, success metrics, scope clarity), data-engineer (data models, ETL implications, downstream consumers), mobile-developer (API design, payload sizes, offline support), accessibility-specialist (WCAG compliance, screen reader support), legal-compliance (GDPR/CCPA, audit requirements). Persona overrides domain framing but does NOT override the claim confidence thresholds or the two-pass audit rule.
- Gate: Persona table present; field added to adversary receipt: `persona_mode_active: true|false`

---

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it would unlock | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| Multi-persona task card review | prompts.py:112-123, SKILL.md Step 2 | Specify clarity gate uses a single fresh-subagent; no named professional lenses | Catch ambiguity (junior-dev), untestable criteria (qa-eng), attack-surface gaps (security-eng) before locking | Subagent dispatch from specify Step 3.7; 3-persona minimum | days | "Add multi-persona task card review to specify Step 3.7: dispatch 3 fresh subagents with persona roles junior-developer, qa-engineer, security-engineer. Collect findings, surface to user before locking task card." |
| PRD document type generation | SKILL.md:128-165, prompts.py:125-161 | WabbleSpec produces GWT task cards; no stakeholder-facing PRD format | Cover full spec lifecycle from stakeholder intent to technical task card | New `prd` module or specify extension; PRD structure: 11 sections | weeks | "Create PRD generation capability: 11-section structure (Executive Summary through Risks/Mitigations), 7 PRD critique criteria (measurable success metrics, explicit scope OUT, no tech details, user stories As/I want/So that), optional PRD-to-tech-spec continuation flow." |

**Gateway bundling recommendation:** PRD generation and multi-persona review both operate in the "specification quality" layer. Consider implementing as a `gateway-spec` bundle rather than separate sessions — shared quality token system, single activation point.

---

### Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| All model names (gpt-4o, claude-sonnet-4-*, gemini/*, xai/*, etc.) | I6: no model names in framework files |
| ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY references | I6: vendor-specific |
| litellm dependency | I6 + creates external binary dependency chain |
| AskUserQuestion for model selection | Prior directive across all ref-adopts |
| ~/.config/adversarial-spec/ session state | I11: framework/product boundary + conflicts with .wabblespec/state/ |
| Telegram bot integration | Domain-specific, not framework-relevant |
| AWS Bedrock routes and BEDROCK_MODEL_MAP | I6: provider-specific |
| Codex CLI subprocess commands | I6: provider-specific |
| debate.py CLI binary | Not a skill instruction; external binary dependency |

---

## Priority Implementation Order

| Priority | ID | What | Why first |
|---|---|---|---|
| 1 | A1 | Preserve-intent taxonomy → adversary | Highest-impact item; fills a real gap in adversary's challenge vocabulary; zero implementation risk |
| 2 | A2 | Press protocol → adversary | Directly paired with A1; completes the "false-positive PASS" detection gap |
| 3 | A3 | Deep interview additions | Enriches existing skill without overwriting; low risk |
| 4 | A6 | Persona table → adversary | Additive reference table; no behavior change, just new activation mode |
| 5 | A4 | Typed criteria → specify | Slightly longer edit; affects a step with existing checklist |
| 6 | A5 | Quality-over-speed pitfall → specify | Shortest change; new section, no existing content affected |

**Execution notes:**
- A1 and A2 target the same file and can be written in one turn
- A4 and A5 target the same file and can be written in one turn
- A3 and A6 each target a different file; can run in parallel with A1+A2 or A4+A5
- Sync engine modules after every `.claude/skills/` edit (per Phase 3 Step 5)
