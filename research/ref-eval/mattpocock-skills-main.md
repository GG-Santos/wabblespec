# Ref-Eval: mattpocock-skills-main

**Date:** 2026-05-31  
**Slug:** mattpocock-skills-main  
**Trust level:** MEDIUM  
**Classification:** supporting-reference  
**Overall usefulness:** 7/10

---

## Section 1 — Reference Summary

**Type:** Production-used behavioral skill collection for software engineering teams. Matt Pocock's personal skill set (60k newsletter subscribers), actively maintained. Real usage evidence: ADR files exist, `.out-of-scope/` rejection records with real issue numbers.

**Behavioral content:** Workflow heuristics for debugging (10-strategy feedback loop), spec writing (agent briefs), issue triage (state machine with 2 categories + 5 states), test-driven development (vertical slice anti-pattern), architecture improvement (deep modules, deletion test, seam vocabulary), and session handoff.

**Structural content:** Skill bucket taxonomy (engineering/productivity/misc/personal/in-progress/deprecated), file-level organization with reference routing (ADR-FORMAT.md, CONTEXT-FORMAT.md, LANGUAGE.md), `description:` field with "Use when [triggers]" convention, hard/soft dependency split for setup pointers.

**Interaction content:** `setup-matt-pocock-skills` → `docs/agents/*.md` → all engineering skills (hard contract). `grill-with-docs` → `CONTEXT.md` + `docs/adr/` → tdd/diagnose/improve-codebase-architecture/zoom-out (soft contract). `triage(wontfix enhancement)` → `.out-of-scope/*.md` → future triage (persistence contract). `prototype` → NOTES.md/ADR/issue → real code (handoff contract).

**Maturity:** High. Active ADRs, `.out-of-scope/` rejection records with real issue numbers, deprecated/ directory with documented retirement, in-progress/ directory with explicit "not ready" markers.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `skills/engineering/to-issues/SKILL.md` | HITL/AFK wave classification | WabbleSpec waves have no concept of "requires human presence" vs "can run autonomously." Adding this lets users scan the plan and know which waves need them. | Add `execution_mode: HITL\|AFK` field to each wave in decompose output contract. | High |
| `skills/engineering/triage/AGENT-BRIEF.md` | Anti-stale-path rules: no file paths, no line numbers in acceptance criteria | WabbleSpec's specify Step 4 checklist validates GWT format but doesn't prevent acceptance criteria that reference specific file paths or line numbers, which go stale as the codebase evolves. | Add two checklist items to specify Step 4: "No acceptance criterion references a specific file path" and "No acceptance criterion references a line number." | Medium |
| `docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md` | Hard/soft dependency split naming | Explicit pattern name for when skills must include a setup pointer vs. just referencing docs in vague prose. Prevents cargo-culting setup pointers into skills where they aren't load-bearing. | Add rule to CLAUDE.md skill authoring conventions section. | Low |
| `skills/productivity/write-a-skill/SKILL.md` | "No time-sensitive info" rule | Skill descriptions must not contain version numbers, counts, or dates that will be stale at next session. Currently absent from WabbleSpec's CLAUDE.md authoring conventions. | Add one rule to CLAUDE.md skill authoring conventions. | Medium |
| `skills/engineering/diagnose/SKILL.md` | 10-strategy feedback loop hierarchy | Production-hardened debugging knowledge. The hierarchy (failing test → curl → CLI → headless → replay → throwaway harness → property/fuzz → bisection → differential → HITL script) gives agents a principled escalation path. | Add `diagnose` as Tier 7 expansion (new skill). | High (Tier 7) |
| `skills/engineering/grill-with-docs/SKILL.md`, `CONTEXT-FORMAT.md` | Inline documentation discipline: update CONTEXT.md as terms crystallize, don't batch | Reduces documentation rot. Applies to any interview/specify session. WabbleSpec's interview skill could adopt the "update inline as decisions crystallize" discipline. | Add one behavioral note to interview SKILL.md. | Low |
| `skills/engineering/triage/OUT-OF-SCOPE.md` | Out-of-scope knowledge base concept | WabbleSpec's evolution cycle has no persistent rejection record for deferred/declined enhancement ideas. Re-litigating the same ideas across sessions is a known inefficiency. | Add as Tier 7 expansion (new `scope-reject` skill + `.wabblespec/state/evolution/out-of-scope/` directory). | Medium (Tier 7) |
| `skills/engineering/prototype/SKILL.md`, `LOGIC.md`, `UI.md` | Prototype skill with LOGIC/UI branch | WabbleSpec has no throwaway prototyping skill. Useful for product teams using WabbleSpec to validate design decisions before committing. | Add as Tier 7 expansion (new `prototype` skill). | Medium (Tier 7) |
| `skills/productivity/handoff/SKILL.md` | Session handoff document | WabbleSpec has no handoff skill. This is the second signal for this capability (first: vibecode-pro-max-kit session-handoff-scanner drawer). Second signal validates the gap. | Add as Tier 7 expansion. | Medium (Tier 7) |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `skills/engineering/improve-codebase-architecture/LANGUAGE.md` | Depth vocabulary conflict | WabbleSpec already uses "module," "interface," and "layer" in its own ways (L0–L8 layer system, receipt chain modules). The mattpocock depth vocabulary (seam, adapter, locality) would conflict. | Do not adopt the vocabulary. | Medium |
| `skills/engineering/setup-matt-pocock-skills/SKILL.md` | Issue tracker integration pattern | WabbleSpec's triage operates on framework issues (routing to skills, writing receipts), not GitHub/Linear issues. Adopting the setup pattern would add a second incompatible triage model. | Do not adopt. Keep entirely separate. | High |
| `skills/in-progress/writing-*.md` | Low-maturity writing skills | Marked "not ready to ship — expect rough edges." WabbleSpec already has writer/document/copy/markdown. Adopting in-progress skills adds maintenance risk. | Exclude from adoption. Revisit when graduated. | Low |
| `skills/engineering/tdd/SKILL.md` + `deep-modules.md` | Domain-specific TDD guidance | WabbleSpec is a framework, not a product codebase. TDD concepts (unit/integration test patterns, mocking strategies) are useful for users building products but don't fit framework skill authoring. | Do not adopt TDD patterns into framework skills. They belong in a Tier 7 `tdd` skill for product teams. | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| HITL/AFK classification (to-issues.md) | Adapt | WabbleSpec waves lack execution_mode | decompose SKILL.md | P1 |
| Anti-stale-path rules (AGENT-BRIEF.md) | Adapt | Specify Step 4 checklist gap | specify SKILL.md Step 4 | P1 |
| No time-sensitive info in descriptions (write-a-skill.md) | Adapt | Missing from CLAUDE.md authoring conventions | CLAUDE.md | P2 |
| Hard/soft dependency split naming (ADR-0001) | Study Only | Good vocabulary — WabbleSpec already does this intuitively but naming it could help skill authors | CLAUDE.md (optional note) | P3 |
| Inline documentation discipline (grill-with-docs) | Adapt (light) | Interview skill could use "update inline as decisions crystallize" | interview SKILL.md | P3 |
| ADR triple-gate criteria (ADR-FORMAT.md) | Study Only | Excellent filter — no direct hook in WabbleSpec's framework skill authoring | N/A (conceptual awareness) | Low |
| diagnose feedback loop (diagnose/SKILL.md + hitl-loop.template.sh) | Tier 7 | Net-new capability — WabbleSpec has no debug skill | New skill session | — |
| prototype skill (prototype/SKILL.md + LOGIC.md + UI.md) | Tier 7 | Net-new capability | New skill session | — |
| out-of-scope KB (triage/OUT-OF-SCOPE.md) | Tier 7 | Net-new capability for evolution cycle | New skill session | — |
| handoff skill (handoff/SKILL.md) | Tier 7 | Second signal confirming existing Tier 7 gap | New skill session | — |
| depth vocabulary / LANGUAGE.md | Avoid | Conflicts with WabbleSpec's existing module vocabulary | N/A | — |
| issue tracker integration (to-issues, to-prd, triage publishing) | Avoid | Domain-specific product tooling; WabbleSpec triage is framework-internal | N/A | — |
| in-progress writing skills | Avoid | Low maturity, overlap with existing skills | N/A | — |
| TDD patterns | Avoid (for framework) | Domain-specific; belong in product-team Tier 7 skill | N/A | — |
| caveman mode | Avoid | No added value over WabbleSpec's existing economy/token-budget mechanisms | N/A | — |
| git-guardrails-claude-code | Avoid | WabbleSpec already has more sophisticated hook architecture | N/A | — |
| setup-matt-pocock-skills | Avoid | Incompatible with WabbleSpec's CLAUDE.md/recipe-based config | N/A | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 6 | Many patterns are domain-scoped (issue tracking, product engineering) but behavioral heuristics transfer. HITL/AFK and anti-stale-path fit WabbleSpec's execution model well. |
| Architecture fit | 5 | mattpocock is a flat skill collection; WabbleSpec is a layered receipt-gated framework. Structural patterns (setup skill, domain docs) don't map. Behavioral rules do. |
| Implementation fit | 8 | Identified items are additive one-rule additions to existing checklists and fields. Zero breaking changes, zero new files needed for Tier 1-2. |
| Maintenance fit | 8 | Additive rules with no ongoing maintenance burden. No new dependencies introduced. |
| Risk level | 2 | Very low. Pure rule additions with no cross-cutting architectural implications. |
| Overall usefulness | 7 | Crosses the 7 threshold. Three Tier 1-2 items with real behavioral impact + four Tier 7 expansion seeds. |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — Tier 1):**
1. `AGENT-BRIEF.md` → specify Step 4: add "no file paths, no line numbers" checklist items
2. `to-issues.md HITL/AFK` → decompose wave plan output contract: add `execution_mode` field
3. `write-a-skill.md "No time-sensitive info"` → CLAUDE.md skill authoring conventions

**Phase 2 (Low-Risk Adaptation — Tier 2):**
4. `grill-with-docs/SKILL.md "update inline"` → interview SKILL.md: add one behavioral note about inline-as-decisions-crystallize

**Phase 3 (Deeper Integration):**
5. Re-evaluate in-progress writing skills when they graduate to stable bucket

**Phase 4 (Do Not Cross):**
- depth vocabulary / LANGUAGE.md — conflicts with WabbleSpec's layer vocabulary
- issue tracker integration
- caveman mode
- git-guardrails

---

## Section 7 — Final Verdict

**Classification: supporting-reference (7/10)**

**Best 3 to steal:**
1. `AGENT-BRIEF.md` no-file-paths rule — directly prevents a class of spec rot in specify acceptance criteria
2. `to-issues.md` HITL/AFK classification — adds a genuinely missing field to WabbleSpec's wave plan
3. `write-a-skill.md` "no time-sensitive info" — closes an explicit gap in CLAUDE.md description authoring rules

**Worst 3 to avoid:**
1. `LANGUAGE.md` depth vocabulary — conflicts with WabbleSpec's existing module/layer terminology
2. `setup-matt-pocock-skills` pattern — incompatible with WabbleSpec's config model
3. `skills/in-progress/` writing skills — low maturity, overlap with existing coverage

**Recommended next action:** Implement Phase 1 (3 Tier 1 items). Write 4 Tier 7 drawers. Skip Phase 2 interview-skill edit (minimal ROI — interview skill already has strong behavioral guidance).

---

## Section 8 — Project Synthesis

**Synthesis 1: HITL/AFK + Executor checkpoint behavior**

WabbleSpec's decompose writes `verification_mode: Attestation` when human judgment is required, but this is per-wave verification only — it doesn't communicate whether the wave itself needs a human at the keyboard during execution. Combining mattpocock's HITL/AFK classification with WabbleSpec's wave plan lets Executor surface a "human required" warning before beginning a HITL wave, separate from the post-wave Attestation verification gate. Reference contribution: HITL/AFK binary flag with clear criteria. Project contribution: Executor's pre-wave guard logic + checkpoint file format.

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Pre-execution human-presence signaling in wave plan | HITL/AFK field from to-issues.md | Executor pre-wave guard logic | decompose SKILL.md wave output contract | Users can't tell which waves require their presence without reading each wave's verification_mode |

**Synthesis 2: Anti-stale-path rule + specify Step 4 validation**

Mattpocock's AGENT-BRIEF.md prevents file paths and line numbers in agent specifications because they "go stale." WabbleSpec's specify Step 4 validates GWT format, normative language, and change class but has no gate against acceptance criteria that reference `src/utils/auth.ts:42`. This is a real failure mode — a criterion like "Then the function in auth.ts returns null" becomes unverifiable after a rename. Reference contribution: explicit anti-stale rule. Project contribution: Step 4 validation checklist. Together: prevents spec rot at spec-write time.

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Stale-path prevention in GWT criteria | No-file-paths/no-line-numbers rule | Step 4 validation checklist | specify SKILL.md | Acceptance criteria can currently embed file paths that break verification as the codebase evolves |

---

## Section 9 — Expansion Opportunities

Per-skill growth scan across 17 skills: diagnose, grill-with-docs, triage (product), improve-codebase-architecture, setup-matt-pocock-skills, tdd, to-issues, to-prd, zoom-out, prototype, caveman, grill-me, handoff, write-a-skill, git-guardrails, in-progress/review, in-progress/writing-*.

| Capability | Reference location | Why project lacks it | What it would unlock | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| Structured debugging skill (feedback loop + HITL script template) | `diagnose/SKILL.md`, `diagnose/scripts/hitl-loop.template.sh` | WabbleSpec has no `diagnose` skill; users building products with WabbleSpec have no structured debugging protocol | Disciplined debugging path for product-space bugs encountered during WabbleSpec-guided development | None | days | Yes |
| Throwaway prototype skill (LOGIC/UI branches, TUI, variant switcher) | `prototype/SKILL.md`, `LOGIC.md`, `UI.md` | WabbleSpec has no prototyping skill; users can't validate design questions before committing to full waves | Faster design validation; reduces wasted Executor cycles on wrong designs | None | days | Yes |
| Out-of-scope knowledge base | `triage/OUT-OF-SCOPE.md` | WabbleSpec's evolution cycle (Tier 7 items, deferred features) has no persistent rejection record | Prevents re-litigating the same deferred items across sessions; institutional memory for "we rejected X because Y" | Memory layer | days | Yes |
| Session handoff document | `handoff/SKILL.md` | WabbleSpec has no handoff skill (second signal — first from vibecode-pro-max-kit); context compaction currently has no structured mitigation | Enables graceful context hand-off within long tasks or between sessions | None (standalone) | days | Yes |

**Gateway bundling signal:** `diagnose` and `prototype` both serve product-team engineering workflows. They could be grouped under a `product-engineering` gateway or simply co-seeded in a single "product tooling" skill session. No single gateway is required — they are independent enough to stand alone.
