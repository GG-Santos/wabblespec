# Ref-Eval: andrej-karpathy-skills-main

**Date:** 2026-05-31
**Reference path:** `C:\Vaults\references\Core Project References\andrej-karpathy-skills-main`
**Trust level:** MEDIUM
**Reference type:** behavioral-guidelines (CLAUDE.md content), community project, MIT licensed

---

## File Inventory

| Path | Purpose | Size | Key contents | Status | Transfer check |
|---|---|---|---|---|---|
| `README.md` | Overview, four principles, install instructions | Medium | Four principles, example table, install via plugin marketplace | Read | N/A |
| `CLAUDE.md` | Canonical behavioral instruction file | Small | Four rules with bulleted sub-rules — the primary deliverable | Read | Primary source |
| `EXAMPLES.md` | Annotated code examples for each principle | Medium | Anti-pattern vs correct diffs for all four principles; anti-pattern summary table | Read | Evaluation frameworks for each principle; timing doctrine |
| `CURSOR.md` | Cursor IDE setup instructions | Small | How to use the rules file in Cursor; tooling-specific only | Read | No transferable content — tooling setup only |
| `skills/karpathy-guidelines/SKILL.md` | Claude Code plugin skill format | Small | Identical content to CLAUDE.md, wrapped in skill frontmatter | Read | Same content as CLAUDE.md; no additive material |

**Directory-level skip decisions:** None. All five files read individually before any scope decision.

---

## Connection Map

```
README.md --[references]--> CLAUDE.md: describes its content and install path
README.md --[references]--> skills/karpathy-guidelines/SKILL.md: plugin format
README.md --[references]--> CURSOR.md: tooling setup
CLAUDE.md --[content-sync]--> skills/karpathy-guidelines/SKILL.md: identical behavioral rules
EXAMPLES.md --[illustrates]--> CLAUDE.md: one-to-one mapping per principle
CURSOR.md --[references]--> .cursor/rules/karpathy-guidelines.mdc: Cursor tooling (not present locally)
```

**Sync constraint:** When CLAUDE.md content changes, SKILL.md and `.cursor/rules/karpathy-guidelines.mdc` must be kept in sync. The reference itself notes this in CURSOR.md.

---

## Three-Dimensional Extraction

### Dimension 1 — Behavior (operational detail)

**Principle 1: Think Before Coding**
- State assumptions explicitly before implementing
- If uncertain → ask (not guess)
- If multiple interpretations exist → present all; do not pick silently
- If simpler approach exists → say so and push back
- If something unclear → stop; name what's confusing; ask

**Principle 2: Simplicity First**
- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If 200 lines could be 50 → rewrite it
- Self-test: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

**Principle 3: Surgical Changes**
- When editing: do not improve adjacent code, comments, or formatting
- Do not refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code → mention it; do not delete it
- When changes create orphans: remove only what YOUR changes made unused
- Do not remove pre-existing dead code unless asked
- Governing test: "Every changed line should trace directly to the user's request."

**Principle 4: Goal-Driven Execution**
- Transform imperative tasks to verifiable goals
- Step format: `[Step] → verify: [check]`
- Transformation examples (exact, from CLAUDE.md):
  - "Add validation" → "Write tests for invalid inputs, then make them pass"
  - "Fix the bug" → "Write a test that reproduces it, then make it pass"
  - "Refactor X" → "Ensure tests pass before and after"
- Strong success criteria enable independent looping; weak criteria require constant clarification

**Anti-pattern timing doctrine** (EXAMPLES.md, final section): "The overcomplicated examples aren't obviously wrong — they follow design patterns and best practices. The problem is timing: they add complexity before it's needed."

### Dimension 2 — Format (identifier level)

Step-plan format:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

SKILL.md frontmatter schema (this reference's own format — not WabbleSpec's format):
```yaml
---
name: karpathy-guidelines
description: <one sentence>
license: MIT
---
```

Section structure: numbered principles with bold one-line summary followed by bullet rules.

### Dimension 3 — Interactions (contract level)

All files are standalone. No cross-file data flows or shared state. The only contract is the sync requirement between CLAUDE.md and SKILL.md (same content, two formats). No sequencing constraints. No schema producers or consumers.

---

## Section 1 — Reference Summary

A 66-line behavioral instruction file (`CLAUDE.md`) and a matching skill plugin (`SKILL.md`) encoding four LLM coding behavior principles drawn from Andrej Karpathy's public observations about LLM coding failure modes.

- **Behavioral content:** Four named principles with specific bulleted sub-rules and self-test criteria. The EXAMPLES.md operationalizes each principle with before/after code diffs.
- **Structural content:** Simple numbered sections with bold headings. No schema, no tooling, no state.
- **Interaction content:** None. Single-file behavioral rules with no cross-file contracts.
- **Maturity:** Community project. No tests, no CI. Well-crystallized and sourced from a credible observer (Karpathy). CLAUDE.md and SKILL.md are in sync. EXAMPLES.md is high-quality illustration. Stable and complete for its scope.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `CLAUDE.md` §1 | "If multiple interpretations exist, present them — don't pick silently" | WabbleSpec CLAUDE.md tells Claude to be concise but doesn't name this failure mode explicitly; agents sometimes resolve ambiguity silently | Add as explicit rule in `~/.claude/CLAUDE.md` Approach section | Medium |
| `CLAUDE.md` §1 | "If a simpler approach exists, say so. Push back when warranted." | Agents currently execute specs faithfully but don't surface when simpler alternatives exist pre-implementation | Add to CLAUDE.md Approach section | Medium |
| `CLAUDE.md` §3 | "If you notice unrelated dead code, mention it — don't delete it" | WabbleSpec CLAUDE.md says "Avoid backwards-compatibility hacks" but doesn't distinguish mention vs delete; agents sometimes silently remove nearby code | Add explicit mention-not-delete rule to CLAUDE.md | Medium |
| `CLAUDE.md` §3 | "Every changed line should trace directly to the user's request." | Clean governing test; not currently stated this precisely in WabbleSpec CLAUDE.md | Add as a surgical changes governing test | Low |
| `EXAMPLES.md` §Anti-patterns | Timing doctrine: complexity added before it's needed is the real problem, not the pattern itself | Provides framing for the Simplicity First rules WabbleSpec already has; helps agents self-check with sharper criterion | Incorporate into CLAUDE.md near existing simplicity guidance | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `CLAUDE.md` §4 | Goal-Driven Execution format assumes test-based verification | WabbleSpec verifies via receipts and Verifier module, not only tests; adopting this literally could send agents to write tests when receipt/gate verification is required | Adapt the `→ verify:` format to encompass WabbleSpec's gate conditions, not just test assertions | Low |
| `skills/karpathy-guidelines/SKILL.md` | Skill format differs from WabbleSpec's skill frontmatter requirements (no `description:` period, no When NOT to use section, no negative triggers) | Adopting the skill format as-is would fail WabbleSpec quality floor Gate 1 | Do not adopt the SKILL.md as a skill in WabbleSpec; extract content only | Low |
| `README.md` | References `forrestchang/andrej-karpathy-skills` plugin marketplace and GitHub URLs | Not adoptable into WabbleSpec framework files (external URLs in skills violate convention) | Treat as installation-only; not framework content | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| §1 present-multiple-interpretations rule | Adapt | Addresses a real gap in Claude's behavioral guidance | `~/.claude/CLAUDE.md` Approach section | High |
| §1 push-back-when-simpler-exists rule | Adapt | Complements existing simplicity guidance | `~/.claude/CLAUDE.md` Approach section | Medium |
| §3 mention-not-delete dead code rule | Adapt | Sharpens existing surgical changes guidance | `~/.claude/CLAUDE.md` Approach section | Medium |
| §3 "every changed line traces to request" test | Adapt | Clean governing criterion; adds precision | `~/.claude/CLAUDE.md` Approach section | Low |
| `CLAUDE.md` §4 `→ verify:` step format | Study Only | WabbleSpec already has `[Step] → verify: [check]` in wave plans; adding it to CLAUDE.md behavioral guidance adds value, but requires reframing to gate/receipt language, not just test assertions | `~/.claude/CLAUDE.md` if adapted carefully | Low |
| `skills/karpathy-guidelines/SKILL.md` | Avoid | Fails WabbleSpec skill quality floor — no When NOT to use, no negative triggers, no period on description | N/A |
| Plugin marketplace install instructions | Avoid | External URL content; not framework material | N/A |
| CURSOR.md | Avoid | Cursor tooling setup; irrelevant to WabbleSpec | N/A |
| Timing doctrine from EXAMPLES.md | Study Only | Good framing reinforcement; existing WabbleSpec rules already cover it | N/A |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Four principles map directly onto WabbleSpec's existing behavioral guidance gaps |
| Architecture fit | 9 | Pure CLAUDE.md content additions; no structural changes to WabbleSpec |
| Implementation fit | 10 | Edit-only to a single file (`~/.claude/CLAUDE.md`); no new files, no scripts |
| Maintenance fit | 9 | Stateless rules; no ongoing maintenance burden |
| Risk level | 1 | Read-only behavioral additions; no invariant conflicts |
| Overall usefulness | 6 | Supporting-reference. Most principles are already present in WabbleSpec; three specific formulations add precision to existing gaps. |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning):**
- Add "present multiple interpretations, don't pick silently" to `~/.claude/CLAUDE.md` Approach section
- Add "push back when simpler approach exists" to `~/.claude/CLAUDE.md` Approach section
- Add "mention unrelated dead code, don't delete it" to `~/.claude/CLAUDE.md` Approach section

**Phase 2 (Low-Risk Adaptation):**
- Add surgical-changes governing test ("every changed line traces to the user's request") — minor precision addition

**Phase 3 (Deeper Integration):** Not applicable for this reference.

**Phase 4 (Do Not Cross):**
- Plugin marketplace content, external URLs, CURSOR.md tooling, SKILL.md format as-is

---

## Section 7 — Final Verdict

**Classification: supporting-reference (6/10)**

Best 3 to steal:
1. `CLAUDE.md` §1 — "If multiple interpretations exist, present them — don't pick silently." This specific failure mode is not named in WabbleSpec CLAUDE.md. (`~/.claude/CLAUDE.md`)
2. `CLAUDE.md` §3 — "If you notice unrelated dead code, mention it — don't delete it." Sharper than WabbleSpec's backwards-compat-hack guidance. (`~/.claude/CLAUDE.md`)
3. `CLAUDE.md` §1 — "If a simpler approach exists, say so. Push back when warranted." Reinforces existing simplicity rules with explicit license to push back. (`~/.claude/CLAUDE.md`)

Worst 3 to avoid:
1. `skills/karpathy-guidelines/SKILL.md` as a WabbleSpec skill — fails Gate 1 (no negative triggers, no period on description, no When NOT to use)
2. Plugin marketplace install instructions — external URL content
3. `→ verify:` format if adopted literally — clashes with WabbleSpec's receipt/gate verification model

**Recommended next action:** Implement Phase 1 items (three additive rules to `~/.claude/CLAUDE.md`). No new files needed. No spec required.

---

## Section 8 — Project Synthesis

WabbleSpec's Guard module already asks pre-tool-use questions before risky operations. Combining the Karpathy "present multiple interpretations" rule with Guard's existing E(X,Q) pre-check question frame (from continuous-claude-v3 integration) could produce a **disambiguation gate for exploratory prompts**: when a user prompt is ambiguous and no active task card exists, Guard could surface two interpretations and ask which one to spec — rather than silently routing to Recipe. This would be a behavioral refinement of the UserPromptSubmit hook's nudge logic.

**What / Reference contribution / Project contribution / Target / Gap closed:**

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Disambiguation nudge in prompt-guard hook | "Present multiple interpretations — don't pick silently" | UserPromptSubmit hook with existing nudge logic | `.wabblespec/engine/hooks/wabblespec-prompt-guard.js` | Agents currently route silently when prompt intent is ambiguous at session start |

---

## Section 9 — Expansion Opportunities

**No expansion opportunities identified.** This reference encodes behavioral rules for a single agent. WabbleSpec already has the infrastructure (hooks, guard, recipe, verifier) to enforce behavioral constraints. The reference adds no net-new capability that WabbleSpec lacks — only sharpened formulations of rules WabbleSpec partially has. Tier 7 candidates: zero.
