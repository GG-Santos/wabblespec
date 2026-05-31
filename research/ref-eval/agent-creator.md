# Ref-Eval: agent-creator

**Reference:** `C:\Vaults\references\Extra Project References\agent-creator`
**Evaluated:** 2026-05-29
**Evaluated against:** WabbleSpec v6.1 (v0.46.0) — session `foundation-hardening-20260528`
**Trust level:** MEDIUM (no LICENSE in folder; structurally identical to an official Anthropic skill — see Section 3)
**Depth:** deep

---

## Section 1 — Reference Summary

A single Claude Code **skill** named `agent-creator` whose job is to teach the creation of effective Claude Code **subagents**. Two files:

- `SKILL.md` (327 lines, 10 KB) — agents-vs-skills distinction, frontmatter schema (`name`, `description`, `tools`, `model`, `skills`, `color`), a six-step creation process, prompt-engineering rules, common pitfalls, a finalization checklist, and one worked `code-reviewer` example.
- `references/prompt-patterns.md` (356 lines) — a pattern catalogue: role definition, methodology, quality-standard, boundary, description, and tool-selection patterns, each with a fill-in template and a concrete example, plus an anti-patterns section.

**Reference type:** documentation / guidance skill (not an application or library). It produces no code; it is purely prescriptive prose.

**Maturity:** Curated, internally consistent, concrete examples throughout. No tests, no CI, no version field, no changelog, no LICENSE file in the folder. This is expected for a guidance skill — maturity here means "is the advice sound," and it largely is. The content tracks the same conventions as the `skill-creator` skill it cross-references (which is present in this environment as `skill-creator:skill-creator`), strongly suggesting it is the official Anthropic agent-creator skill or a close derivative.

**Mature parts:** the description-as-trigger doctrine, minimal-toolset principle, boundary patterns, anti-patterns. **Soft/unverified parts:** the per-tool token-budget numbers (unsourced), the `skills:` auto-load frontmatter field (not verified against the current agent schema), the hardcoded model names.

---

## Section 2 — Benefits We Can Get

| # | Location | What to adapt | Why it helps | How to adapt | Impact |
|---|----------|---------------|--------------|--------------|--------|
| B1 | `SKILL.md:90-101` (Minimal Viable Toolset + token table) | The principle "grant only the tools the agent's job requires; tool count drives prompt token cost" | WabbleSpec's own subagents `wabblespec-guard` and `wabblespec-verifier` are both declared with **All tools**. That is precisely the tool-overload anti-pattern. Guard validates schema/scope/authority and Verifier runs a verification gate — neither needs Write/Edit/NotebookEdit in the general case. | Audit `.claude/agents/wabblespec-guard` and `wabblespec-verifier` and replace `All tools` with an explicit minimal set (Read, Grep, Glob, Bash, plus the receipt/JSON writers they actually call). Do **not** import the reference's token numbers as fact — use the principle, measure locally. | High |
| B2 | `prompt-patterns.md:241-245` (Negative Trigger Pattern) | `description: ... MUST BE USED for [X]. NOT for [Y — use Z agent instead].` | WabbleSpec has 103 skills with overlapping trigger surfaces (ref-eval vs ref-plan vs ref-comp; reviewer vs adversary vs grader). Explicit negative triggers in descriptions reduce mis-selection. WabbleSpec already does this informally (reviewer's "NOT for implementing fixes"); the pattern formalizes it. | When two skills compete for the same trigger phrase, add a one-line negative trigger to each pointing at the other. Apply to the ref-* trio and the review trio first. | Medium |
| B3 | `SKILL.md:16-22` (Agents vs Skills table) | The decision criteria: isolation / different model / restricted tools / parallelism ⇒ subagent; otherwise skill | Documents *why* WabbleSpec spawns Guard and Verifier as subagents (context isolation + bounded tools) instead of running them inline. A future maintainer deciding whether a new capability should be a skill or a subagent has a crisp rubric. | Lift the four criteria into a short "subagent vs skill" note in the framework's authoring conventions. WabbleSpec adds a fifth axis the reference lacks — receipt/authority boundaries — so extend, don't copy verbatim. | Medium |
| B4 | `SKILL.md:235-240` ("Challenge each paragraph — does this justify its token cost?") | The token-discipline heuristic | Reinforces invariant I12 (no redundant output) and the existing "Reference Routing over inline documentation" convention in CLAUDE.md. Same idea, applied to agent/skill prompt bodies. | No new mechanism needed — this is corroborating evidence for the routing convention WabbleSpec already enforces. Cite it when trimming a SKILL.md. | Low |
| B5 | `prompt-patterns.md:173-217` (Hard Stop / Scope / Handoff boundary patterns) | The three boundary templates | WabbleSpec's role-bounded modules (reviewer, grader, adversary, clean) already use hard stops. The Handoff Pattern ("your output will be used by [next consumer]") maps cleanly to WabbleSpec's receipt-chain handoffs. | Use the Handoff template wording when documenting which downstream module reads each module's receipt. Marginal — WabbleSpec's receipt chain already encodes the handoff. | Low |

---

## Section 3 — Negative Effects / Risks

| # | Location | Risk | Why it hurts | Mitigation | Severity |
|---|----------|------|--------------|------------|----------|
| R1 | `SKILL.md:50, 65, 103-108, 282` ("model: sonnet", haiku/sonnet/opus guidance, example agent) | The reference hardcodes vendor model names everywhere | **Direct collision with invariant I6 (RUNTIME IS VENDOR-NEUTRAL): no model names anywhere in framework files.** Copying the `model:` guidance or the worked example into any WabbleSpec file would violate a core invariant and fail a doctor/Guard check. | Do not copy the model-selection guidance. WabbleSpec already routes by capability descriptor (`code-generation`, `analysis`, `synthesis`, `long-context`) via ModelRouter/runtime-state.json. Treat the reference's model section as the *anti-example* of what I6 forbids. | High |
| R2 | `SKILL.md:98-101` (token-budget table: "3-5 tools ~2-5k tokens", etc.) | Unsourced, precise-looking numbers | Citing these as fact in a WabbleSpec doc would inject unverifiable claims into a framework that prizes evidence (I8). The real cost depends on tool schemas in this harness, not the reference's figures. | Adopt the *principle* (fewer tools = cheaper), discard the *numbers*. If a budget is needed, measure it in this environment. | Medium |
| R3 | `SKILL.md:52, 246-251` (`skills:` auto-load frontmatter field) | The `skills:` field is presented as a real agent-config field but is not verified against the current Claude Code agent schema | Building tooling or docs around a frontmatter key that the harness may not honor produces silent no-ops. | Verify `skills:` against the actual agent loader before relying on it. WabbleSpec controls skill availability through recipe.json `active_skills` + sync `--filter-recipe`, which is the verified mechanism — prefer it. | Medium |
| R4 | Whole reference (no LICENSE file in folder) | Copying text verbatim with unknown license terms | Low legal exposure for a guidance doc, but WabbleSpec's framework files are checked-in product. Verbatim lifting of templates without attribution is a (small) copying risk. | Adapt ideas and structure, never paste prose. The patterns are generic prompt-engineering conventions, so adaptation carries negligible risk; verbatim copying is the only thing to avoid. | Low |
| R5 | `SKILL.md:78-88, 190-191` ("Description is Everything"; **MUST**/**ALWAYS**/**NEVER** emphasis) | Over-reliance on prompt-level capitalized emphasis as the enforcement mechanism | WabbleSpec's enforcement model is *stronger* than prompt emphasis — it uses hooks, Guard layers, and receipt gates. Importing a "just shout MUST in the prompt" mindset would be a regression from mechanical enforcement to hortatory enforcement. | Keep WabbleSpec's hook/Guard enforcement as primary. Use emphasis markers only as secondary reinforcement, not as the control. | Low |

---

## Section 4 — What To Adapt vs What To Avoid

| Reference Part | Adapt / Avoid / Study | Reason | Target Area In My Project | Priority |
|----------------|------------------------|--------|---------------------------|----------|
| Minimal-toolset principle (`SKILL.md:90-101`) | Adapt | Guard & Verifier subagents declare All tools | `.claude/agents/wabblespec-guard`, `wabblespec-verifier` | High |
| Negative Trigger Pattern (`prompt-patterns.md:241-245`) | Adapt | Reduces mis-selection across 103 overlapping skills | ref-eval/ref-plan/ref-comp + reviewer/adversary/grader descriptions | Medium |
| Agents-vs-Skills decision table (`SKILL.md:16-22`) | Adapt | Documents subagent-vs-skill rationale | Framework authoring conventions (CLAUDE.md) | Medium |
| Token-discipline heuristic (`SKILL.md:235-240`) | Study only | Corroborates existing I12 + Reference Routing | (no change — citation only) | Low |
| Boundary / Handoff templates (`prompt-patterns.md:173-217`) | Study only | WabbleSpec receipt chain already encodes handoffs | Module receipt-chain docs | Low |
| `model:` hardcoding (`SKILL.md:50,65,103-108,282`) | Avoid | Violates I6 vendor-neutrality | — (anti-example) | High |
| Token-budget numbers (`SKILL.md:98-101`) | Avoid | Unsourced; conflicts with evidence ethos | — | Medium |
| `skills:` frontmatter field (`SKILL.md:52,246-251`) | Avoid (until verified) | Unverified against agent schema | — | Medium |
| Verbatim prose (whole ref) | Avoid | Unknown license | — | Low |

---

## Section 5 — Integration Fit

| Dimension | Score | Explanation |
|-----------|-------|-------------|
| Concept fit | 8 | The reference is *about* designing agents/skills, which is exactly what WabbleSpec is made of. |
| Architecture fit | 6 | Maps to WabbleSpec's subagent usage, but WabbleSpec's layered/receipt/invariant architecture is far more elaborate than the reference assumes. |
| Implementation fit | 4 | The most concrete, copyable items (model selection, token numbers, `skills:` field) are exactly the ones that conflict with I6 or are unverified. |
| Maintenance fit | 8 | Pure guidance — adopting principles adds zero ongoing maintenance burden. |
| Risk level | 3 | Low overall; the one real hazard (copying model names) is easy to avoid once flagged. |
| Overall usefulness | 6 | A solid checklist for auditing WabbleSpec's own subagent definitions, but WabbleSpec already embodies most of these principles at a higher level. |

Overall 6 ⇒ worth active use for a specific sub-problem (subagent hygiene), not a design driver.

---

## Section 6 — Recommended Extraction Plan

**Phase 1 — Safe Learning (no changes)**
- Read `SKILL.md:16-22` (agents vs skills) and `SKILL.md:90-101` (minimal toolset).
- Note that the reference's model-selection section is an I6 anti-example, not guidance.

**Phase 2 — Low-Risk Adaptation**
- Audit `.claude/agents/wabblespec-guard` and `wabblespec-verifier`: replace `All tools` with an explicit minimal toolset matching what each actually invokes (B1). Validate the subagents still pass their own acceptance checks before committing.
- Add one-line negative triggers to the ref-* trio and review trio descriptions (B2). Cosmetic/additive — no schema change.

**Phase 3 — Deeper Integration**
- Add a short "subagent vs skill" rubric to the framework authoring conventions (B3), extended with WabbleSpec's receipt/authority axis. Touches CLAUDE.md / authoring reference docs — coordinate with the framework-maintenance authority owner (finding #29) since these are shared-infra writes.

**Phase 4 — Do Not Cross**
- Never copy `model: <name>` guidance or the worked `code-reviewer` example verbatim — I6 violation (R1).
- Do not cite the token-budget numbers as fact (R2).
- Do not build on the `skills:` frontmatter field until verified (R3).
- Do not paste reference prose verbatim (R4).

---

## Section 7 — Final Verdict

**Worth using?** Yes, narrowly — as an audit checklist for WabbleSpec's subagent definitions, not as a source of copyable configuration.

**Best 3 things to steal:**
1. Minimal-toolset principle applied to `wabblespec-guard` / `wabblespec-verifier`, which currently declare All tools (`SKILL.md:90-101`).
2. Negative Trigger Pattern for disambiguating overlapping skill descriptions (`prompt-patterns.md:241-245`).
3. Agents-vs-Skills decision table as documented rationale for when to spawn a subagent (`SKILL.md:16-22`).

**Worst 3 things to avoid:**
1. Hardcoded model names — direct I6 violation (`SKILL.md:50,65,103-108,282`).
2. Unsourced token-budget figures (`SKILL.md:98-101`).
3. The unverified `skills:` auto-load frontmatter field (`SKILL.md:52,246-251`).

**Classification:** Supporting reference — useful for the specific sub-problem of subagent/skill hygiene; WabbleSpec is more mature than this reference in nearly every other dimension.

**Recommended next action:** Open the two subagent definitions (`wabblespec-guard`, `wabblespec-verifier`) and scope their toolsets down from All tools to an explicit minimal set (Phase 2, B1). This is the single highest-value, lowest-risk extraction.
