# Ref-Plan: hermes-agent-main

**Reference slug:** hermes-agent-main
**Date:** 2026-05-30
**Based on:** `research/ref-eval/hermes-agent-main.md`
**Overall verdict:** supporting (6/10 overall usefulness)

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| C1 | "Do NOT capture" anti-pattern list → Dream SKILL.md | Behavioral | High | High — Dream has zero signal discrimination guidance | Low |
| C2 | Description period-ending requirement → Gate 2 | Format | Medium | High — Gate 2 already checks description length | Low |
| C3 | Intro must state "does AND doesn't do" → CLAUDE.md | Format | Low-Medium | Medium — additive authoring note | Low |
| C4 | `## Pitfalls` as recommended section → CLAUDE.md | Format | Low-Medium | Medium — complements `## When NOT to use` | Low |
| C5 | Priority-ordered error taxonomy → wave-fix reference | Behavioral | Medium | Medium — wave-fix prose lacks structured vocabulary | Low-Medium |
| C6 | Dependency pinning policy → CLAUDE.md | Format | Low | Low — WabbleSpec scripts don't install deps at runtime | Low |
| C7 | "Frustration = Instinct signal" heuristic (Synthesis 1) | Behavioral synthesis | Medium | High — Instinct chain exists for exactly this | Low-Medium |
| C8 | Priority-ordered error routing table for wave-fix (Synthesis 2) | Behavioral synthesis | Medium | Medium — wave-fix exists, reference doc needed | Medium |

---

## Exclusion Filter

| Item | Excluded | Reason |
|---|---|---|
| Description ≤60 char limit | Excluded | Calibrated for Hermes' skill-listing density; WabbleSpec descriptions are richer and legitimately longer |
| Model names from any code path | Excluded | I6 hard violation — do_not_copy |
| Author/contributor credits convention | Excluded | WabbleSpec modules have no "human contributor" — architectural misfit |
| Agent-created vs bundled skill curator distinction | Excluded | WabbleSpec has no runtime-created modules; concept maps to nothing |
| Background review fork architecture | Excluded | Architectural mismatch — WabbleSpec is single-agent per session |
| Gateway/ACP/LSP/TUI infrastructure | Excluded | No overlap with WabbleSpec use case |

---

## Integration Scores

```
integration_score = (impact × 2) + project_fit - risk
Map: High=3, Medium=2, Low=1
```

| ID | Impact | Project Fit | Risk | Score |
|---|---|---|---|---|
| C1 | 3 | 3 | 1 | **8** |
| C7 | 2 | 3 | 1 | **6** |
| C2 | 2 | 3 | 1 | **6** |
| C3 | 1.5 | 2 | 1 | **4** |
| C4 | 1.5 | 2 | 1 | **4** |
| C5 | 2 | 2 | 1.5 | **4.5** |
| C8 | 2 | 2 | 2 | **4** |
| C6 | 1 | 1 | 1 | **2** |

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive to existing file, no new files)

**T1.1 — Dream SKILL.md: Signal anti-pattern list**
- What: Add a `## Signal Anti-Patterns` subsection enumerating four categories of observations that MUST NOT be distilled to Instinct
- Where: `.wabblespec/engine/modules/l5/dream/SKILL.md` (and `.claude/skills/dream/SKILL.md` via sync)
- How: After the existing `## When to use` / `**Do not use:**` block, add `## Signal Anti-Patterns` with four named categories, quoted verbatim from hermes `_SKILL_REVIEW_PROMPT` lines 96–146: (1) environment-dependent failures, (2) negative tool claims, (3) transient session errors that resolved, (4) one-off task narratives
- Gate: Dream SKILL.md contains `## Signal Anti-Patterns` with all four category names
- Reference location: `agent/background_review.py:96–146`
- Literal values: Category names must be: "Environment-dependent failures", "Negative tool claims", "Transient errors that resolved", "One-off task narratives"

**T1.2 — CLAUDE.md: Skill intro must state "does AND doesn't do"**
- What: Add one sentence to the "Skill Authoring Conventions" section of CLAUDE.md stating the intro must declare both what the skill does and what it explicitly does not do in 2–3 sentences
- Where: `CLAUDE.md` "Skill Authoring Conventions" section
- How: Append after the existing `**Reference routing over inline documentation.**` bullet
- Gate: CLAUDE.md Skill Authoring Conventions section contains a note about "does AND doesn't do" intro
- Reference location: `AGENTS.md:613–618`

**T1.3 — CLAUDE.md: `## Pitfalls` recommended section**
- What: Add `## Pitfalls` to the list of recommended SKILL.md sections in the authoring conventions
- Where: `CLAUDE.md` "Skill Authoring Conventions" section
- How: Add after the existing `## When NOT to use` requirement: "Skill bodies may also include a `## Pitfalls` section for operational gotchas that would surprise a reader during execution (distinct from `## When NOT to use`, which is about trigger boundaries)"
- Gate: CLAUDE.md mentions `## Pitfalls` as a recognized optional section
- Reference location: `AGENTS.md:668`

### Tier 2 — Module-level augmentation

**T2.1 — Dream SKILL.md: Frustration-signal routing note (Synthesis 1)**
- What: Add a note that user frustration/correction signals (style, tone, format, workflow complaints) route to Instinct observation candidates, not general memory drawers
- Where: `.wabblespec/engine/modules/l5/dream/SKILL.md`
- How: Add a `## Instinct Signal Routing` subsection after `## Signal Anti-Patterns` specifying that user corrections to framework behavior are Instinct candidates
- Gate: Dream SKILL.md contains `## Instinct Signal Routing` with mention of frustration signals
- Reference location: `agent/background_review.py:49–73` (`_SKILL_REVIEW_PROMPT` preference order + "first-class skill signals" language)
- Literal values: Must include the phrase "first-class Instinct candidate" to distinguish from general memory

### Tier 3 — New shared infrastructure (Deferred)

**T3.1 — `_shared/references/wave-error-taxonomy.md` (Synthesis 2)**
- What: New reference doc enumerating WabbleSpec-adapted error classes for wave-fix routing
- Why deferred: Requires reading wave-fix SKILL.md in full first and mapping hermes' 16 FailoverReason values to WabbleSpec's actual wave failure modes — a non-trivial translation requiring a separate session
- Promote when: wave-fix SKILL.md has been reviewed and its failure-mode vocabulary is documented

### Tier 4 — New module candidates

None identified. All extractable patterns fit within existing modules.

### Tier 5 — Architecture-level

None identified.

### Tier 6 — Synthesis

Already merged into T2.1 (Synthesis 1 — frustration routing). Synthesis 2 (error taxonomy for wave-fix) is deferred to Tier 3.

### Watch Only

**W1 — Gate 2: enforce `## When NOT to use`**
- CLAUDE.md asserts this is enforced but `quality-floor-check.py` has no `WHEN_NOT_TO_USE` check
- Unclear how many of the 105 modules would fail this check — must run against current module set before enabling
- Promote when: a pass-rate audit confirms the majority of modules already have the section

**W2 — Dependency pinning policy for scripts**
- WabbleSpec's scripts declare no runtime dependencies (they import from stdlib + pyyaml/duckdb, which are required globally)
- Low impact — no `pyproject.toml` or `requirements.txt` in the scripts directory
- Watch if scripts begin accepting installable packages

---

## Do-Not-Copy List

| Item | Reason |
|---|---|
| Any model name string (claude-sonnet-4-6, gpt-4o, gemini, etc.) | I6 — vendor names are banned in framework files |
| `description: ≤60 characters` as a Gate 2 limit | Calibrated for Hermes; WabbleSpec descriptions legitimately exceed 60 chars |
| `created_by: "agent"` provenance distinction | Architectural mismatch |
| Background review daemon thread | Architectural mismatch |

---

## Priority Implementation Order

| Rank | ID | Item | Why first |
|---|---|---|---|
| 1 | T1.1 | Dream signal anti-patterns | Highest impact; Dream has zero signal discrimination; purely additive |
| 2 | T1.2 | CLAUDE.md "does AND doesn't do" intro note | Low effort; clarifies authoring intent |
| 3 | T1.3 | CLAUDE.md `## Pitfalls` recommended section | Low effort; complements existing conventions |
| 4 | T2.1 | Dream Instinct signal routing | Requires T1.1 context to be in place first |

---

## Execution Notes

- T1.1 and T1.2 are independent; both can be applied in the same response turn.
- T1.3 is independent of T1.1/T1.2.
- T2.1 depends on T1.1 being written first (references `## Signal Anti-Patterns`).
- `.wabblespec/engine/modules/l5/dream/SKILL.md` is the canonical source; `.claude/skills/dream/SKILL.md` is the sync copy. After editing the engine source, run `wabblespec-sync-skills.py` to propagate.
- All changes are to framework files owned by the framework; no product-space writes (I11 safe).
