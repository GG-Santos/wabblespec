# Ref-Plan: agent-rules-main

**Based on:** `research/ref-eval/agent-rules-main.md`
**Planned:** 2026-05-31

---

## Integration signal extracted

From ref-eval Section 2 (Benefits) and Section 6 (Extraction Plan):

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | LLM-optimized doc format (parallel dispatch, timestamps, no-duplication, concrete refs, token-efficient) | Behavioral | Medium | High — document SKILL.md lacks these constraints | Low |
| A2 | "3+ files" skill creation threshold | Behavioral | Medium | High — no trigger signal in CLAUDE.md | Low |
| A3 | Rule quality checklist (Actionable/Specific/Tested/Complete/Current/Linked) | Behavioral | Medium | Medium — useful pre-publish gate | Low |
| A4 | "Use actual codebase examples, not theoretical examples" | Behavioral | Low-Medium | High — directly applicable to skill authoring | Low |
| A5 | Cross-reference related skills (DRY) | Behavioral | Low | Medium — reduces content duplication | Low |

---

## Exclusion filter

| Item | Excluded | Reason |
|---|---|---|
| All Swift/Apple platform docs | Excluded | Domain-specific, no WabbleSpec relevance |
| `commit-fast.mdc` auto-skip confirmation | Excluded | Violates I10 (implied completion) |
| `steipete-mcps.md` model name references | Excluded | Violates I6 (vendor-neutral runtime) |
| MCP server development practices | Excluded | We consume MCP tools, do not build them |
| AppleScript automation (safari, screenshot) | Excluded | macOS GUI domain |
| Tool-specific setup scripts | Excluded | Hardcoded personal paths; external dependencies |
| `continuous-improvement.mdc` monthly/quarterly cadence | Excluded | Time-sensitive content — violates CLAUDE.md "no time-sensitive info in descriptions" rule |

---

## Scoring and ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Impact | Project fit | Risk | Score | Tier |
|---|---|---|---|---|---|
| A1 | 2 (Medium) | 3 (High) | 1 (Low) | 6 | 1 |
| A2 | 2 (Medium) | 3 (High) | 1 (Low) | 6 | 1 |
| A3 | 2 (Medium) | 2 (Medium) | 1 (Low) | 5 | 1 |
| A4 | 1 (Low-Med → Low) | 3 (High) | 1 (Low) | 4 | 1 |
| A5 | 1 (Low) | 2 (Medium) | 1 (Low) | 3 | 1 |

---

## Tier assignments

### Tier 1 — Behavioral additions to existing files

**A1 — LLM-optimized documentation format**

- **What:** Add a `## LLM-optimized output format` section to the `document` SKILL.md
- **Where:** `.wabblespec/engine/modules/l6/document/SKILL.md` (engine source) + `.claude/skills/document/SKILL.md` (synced copy)
- **How:** Add after the existing `## Rules` section. New section contains five named constraints from `update-docs.mdc`:
  1. Token-efficient writing — no redundant explanations, concrete info only
  2. Concrete file references — include specific paths, line numbers when helpful
  3. No-duplication — each piece of information in exactly one output file; cross-reference with "See [path]"
  4. Parallel agent dispatch — when producing multi-section documentation (architecture, build, testing, development, deployment), issue section agents in parallel rather than sequentially
  5. Timestamp header — generated docs start with `<!-- Generated: YYYY-MM-DD HH:MM:SS UTC -->`
- **Gate:** After edit, document SKILL.md contains a `## LLM-optimized output format` section with all 5 constraints named
- **Reference location:** `project-rules/update-docs.mdc` → "LLM-OPTIMIZED FORMAT", "NO DUPLICATION", "PRACTICAL EXAMPLES", "Specific File Requirements" parallel task calls

**A2 — "3+ files" skill creation threshold**

- **What:** Add one rule to CLAUDE.md skill authoring conventions
- **Where:** `C:\Users\Kirsten\.claude\CLAUDE.md` — in the `## Skill Authoring Conventions` section, after "Tool descriptions must answer four questions"
- **How:** Add: `**Create a new skill when a behavior repeats without guidance in 3+ distinct execution contexts.** If an agent performs the same behavioral pattern three or more times across unrelated tasks without being prompted by a skill, that is the signal to formalize the behavior as a skill. Repeating in fewer contexts indicates an ad-hoc pattern, not a generalizable workflow.`
- **Gate:** The rule appears in CLAUDE.md's skill authoring section
- **Reference location:** `project-rules/continuous-improvement.mdc` → "Create New Rules When: A new technology/pattern is used in 3+ files"

**A3 — Rule quality checklist (6 criteria)**

- **What:** Add skill readiness checklist to CLAUDE.md
- **Where:** `C:\Users\Kirsten\.claude\CLAUDE.md` — immediately after A2 rule
- **How:** Add: `**Before publishing a new skill, verify six readiness criteria.** Actionable (provides clear implementable guidance, not vague recommendations), Specific (names exact files, thresholds, or conditions), Tested (examples drawn from actual project code, not invented), Complete (covers common edge cases including failure modes), Current (no version numbers, dates, or counts in description), Linked (cross-references at least one related skill by name). A skill that fails any criterion should be revised rather than published.`
- **Gate:** The six criteria are named in CLAUDE.md
- **Reference location:** `project-rules/continuous-improvement.mdc` → "Quality Checklist" section

**A4 — "Use actual codebase examples" rule**

- **What:** Add one rule to CLAUDE.md skill authoring conventions
- **Where:** `C:\Users\Kirsten\.claude\CLAUDE.md` — immediately after A3
- **How:** Add: `**Skill examples must reference actual project artifacts, not theoretical constructs.** When a SKILL.md includes an example command, file path, code snippet, or workflow, the example must be drawn from something that exists in the codebase (a real script path, a real SKILL.md section, a real receipt type). Invented example paths and fake filenames teach incorrect mental models.`
- **Gate:** The rule appears in CLAUDE.md
- **Reference location:** `project-rules/cursor-rules-meta-guide.mdc` → "Reference existing code when possible" and "Reference actual code over theoretical examples"

**A5 — Cross-reference related skills (DRY)**

- **What:** Add one rule to CLAUDE.md skill authoring conventions
- **Where:** `C:\Users\Kirsten\.claude\CLAUDE.md` — immediately after A4
- **How:** Add: `**Cross-reference related skills by name rather than duplicating their content.** When a SKILL.md section would repeat content already in another skill, add a reference pointer ("See the `guard` skill for invariant enforcement details") instead of copying the block. Duplicated content creates two maintenance targets and diverges over time. The `## Reference Routing` table is the correct location for these pointers.`
- **Gate:** The rule appears in CLAUDE.md
- **Reference location:** `project-rules/cursor-rules-meta-guide.mdc` → "Keep rules DRY by referencing other rules"

---

## Do-Not-Copy list

| Item | Invariant reason |
|---|---|
| Model names: `gpt-4o`, `llava:latest` | I6 — runtime is vendor-neutral |
| `commit-fast.mdc` auto-skip | I10 — no implied completion |
| `--dangerously-skip-permissions` flag in `cly` function | Security — explicit bypass |
| Monthly/Quarterly/Annually review cadence | CLAUDE.md rule — no time-sensitive info in descriptions |
| AppleScript/Safari/screencapture patterns | Out of scope — macOS GUI domain |

---

## Priority implementation order

| Order | ID | Item | Target file | Why first |
|---|---|---|---|---|
| 1 | A1 | LLM-optimized doc format | document SKILL.md (both copies) | Highest integration score; adds 5 concrete constraints to an existing module |
| 2 | A2 | "3+ files" creation threshold | CLAUDE.md | High project fit; fills a named gap in skill authoring |
| 3 | A3 | Rule quality checklist | CLAUDE.md | Builds directly on A2 — same reference file, logical sequence |
| 4 | A4 | Codebase examples rule | CLAUDE.md | Low risk, direct application |
| 5 | A5 | Cross-reference DRY | CLAUDE.md | Lowest impact, but groups naturally with A4 as same-turn edit |

**Sequencing constraint:** A2–A5 are all edits to CLAUDE.md; they can be applied in a single response turn as one contiguous block insertion. A1 requires two file edits (engine module + skills copy) but both can be parallel.

**Execution notes:**
- CLAUDE.md target is `C:\Users\Kirsten\.claude\CLAUDE.md` (global, not project-level)
- document SKILL.md engine path: `.wabblespec/engine/modules/l6/document/SKILL.md`
- document SKILL.md skills path: `.claude/skills/document/SKILL.md`
- Both document copies must receive identical additions (I11 is not violated here — document SKILL.md is framework space, but the sync script would overwrite `.claude/skills/` from `engine/modules/` on next run)

---

## Tier 7 — Expansion Roadmap

No Tier 7 items identified. Reference has no net-new capabilities absent from WabbleSpec. All transferable items are augmentations to existing modules.

---

## Phase 1 (immediate) / Phase 2 (deferred) / Watch Only

**Phase 1 (implement now):** A1, A2, A3, A4, A5

**Phase 2 (deferred):** None

**Watch Only:** Five Whys method (`five.mdc`) — not implemented because `diagnose` SKILL.md already has a structured hypothesis generation protocol (Phase 3: "Generate 3–5 ranked hypotheses before testing any"). Adding Five Whys would overlap without clear additive value. Monitor for user requests to the `diagnose` skill where structured drill-down is explicitly requested.

**PR review 6-role taxonomy** — Study only. `reviewer` and `adversary` skills already cover multi-perspective review. The PM/DevOps roles from `pr-review.mdc` are orthogonal to security/quality review and would widen scope beyond current `reviewer` charter.
