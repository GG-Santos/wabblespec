# Ref-Plan: mattpocock-skills-main

**Date:** 2026-05-31  
**Slug:** mattpocock-skills-main  
**Source:** ref-eval/mattpocock-skills-main.md  
**Trust level:** MEDIUM

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| M1 | HITL/AFK execution_mode field in wave plan | Behavioral addition | High | High | Low |
| M2 | No file paths / no line numbers in acceptance criteria | Behavioral addition | Medium | High | Low |
| M3 | No time-sensitive info in skill descriptions | Rule addition | Medium | Medium | Low |
| M4 | Hard/soft setup pointer naming convention | Rule addition | Low | Medium | Low |
| M5 | Inline documentation discipline in interview | Behavioral note | Low | Medium | Low |
| M6 | diagnose feedback loop skill | New skill | High | High | Low |
| M7 | prototype skill | New skill | Medium | Medium | Low |
| M8 | out-of-scope KB skill | New skill | Medium | Medium | Low |
| M9 | handoff skill | New skill | Medium | Medium | Low |

---

## Exclusion Filter

**Do not copy (I6):** None — no vendor/model names in this reference.

**Avoid items from ref-eval Section 4:**
- LANGUAGE.md depth vocabulary — conflicts with WabbleSpec's L0–L8 layer vocabulary (seam, adapter, locality have different meanings)
- issue tracker integration — domain-specific product tooling incompatible with WabbleSpec's framework-internal triage
- in-progress writing skills — low maturity
- TDD patterns for product code — not framework skills
- caveman mode, git-guardrails, setup-matt-pocock-skills — no fit or duplication

**Low project fit deferred:** M4 (hard/soft pointer naming) — WabbleSpec already does this intuitively; naming it adds marginal value as a CLAUDE.md note. Moving to Watch Only.

---

## Integration Scores

Formula: `integration_score = (impact × 2) + project_fit - risk`  
Map: High=3, Medium=2, Low=1

| ID | Impact | Project fit | Risk | Score |
|---|---|---|---|---|
| M1 | 3 | 3 | 1 | 8 |
| M2 | 2 | 3 | 1 | 6 |
| M3 | 2 | 2 | 1 | 5 |
| M5 | 1 | 2 | 1 | 3 |
| M4 (Watch) | 1 | 2 | 1 | 3 |

---

## Tier Assignment

### Tier 1 — Behavioral additions

**M1 — HITL/AFK execution_mode in wave plan**  
What: Add `execution_mode: HITL|AFK` field to each wave in the wave plan output contract.  
Where: `.claude/skills/decompose/SKILL.md` + `.wabblespec/engine/modules/l1/decompose/SKILL.md`  
How: In the `## Output contract` section, add `execution_mode` to the wave template (after `verification_mode`). In Step 3c (declare verification command), add guidance: AFK waves can use Test/Observation verification; HITL waves require Attestation or human Review. Add to the "A note on common failure modes" or as a rule in Step 3. Also add `execution_mode` summary to the receipt `waves_json` example.  
Literal values: Field name `execution_mode`, values `HITL` and `AFK`. AFK criterion: verification can be automated (Test or Observation mode). HITL criterion: human judgment required mid-execution, maps to Attestation or Review verification mode.  
Gate: `execution_mode` field appears in the wave plan output contract template and at least one example wave. No existing wave plan fields removed.  
Reference location: `skills/engineering/to-issues/SKILL.md` (HITL/AFK classification with criteria)

**M2 — No file paths / no line numbers in acceptance criteria**  
What: Add two anti-stale-path items to specify Step 4 validation checklist.  
Where: `.claude/skills/specify/SKILL.md` + `.wabblespec/engine/modules/l1/specify/SKILL.md`  
How: In Step 4 "Validate before writing" checklist, append two items: `- [ ] No acceptance criterion references a specific file path (file paths go stale on rename/move)` and `- [ ] No acceptance criterion references a line number (line numbers go stale on every edit)`.  
Literal values: The two checklist items verbatim above.  
Gate: Both checklist items appear in the Step 4 checklist. No existing checklist items removed.  
Reference location: `skills/engineering/triage/AGENT-BRIEF.md` — "Don't reference file paths — they go stale" + "Don't reference line numbers"

**M3 — No time-sensitive info in skill descriptions**  
What: Add one rule to CLAUDE.md skill authoring conventions.  
Where: `CLAUDE.md` (project CLAUDE.md at root)  
How: In the `## Skill Authoring Conventions` section, after the existing rule "`description:` must end with a period," add: "**Skill descriptions must not contain time-sensitive information.** Version numbers, current counts, and dates embedded in a description field are stale at the next session. State what the skill does and when to trigger it — not facts about the current state of the world."  
Gate: Rule appears in CLAUDE.md under Skill Authoring Conventions.  
Reference location: `skills/productivity/write-a-skill/SKILL.md` — "No time-sensitive info"

---

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it would unlock | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| `diagnose` skill — structured debugging protocol | `skills/engineering/diagnose/SKILL.md` + `hitl-loop.template.sh` | No debug skill in WabbleSpec; product teams using the framework have no structured debugging path | Disciplined 10-strategy feedback loop construction; HITL fallback script template | None | days | "Add a `diagnose` skill that implements the feedback loop construction protocol from the mattpocock-skills-main diagnose skill. Phases: Build feedback loop → Reproduce → Hypothesize → Instrument → Fix + regression test → Cleanup. Include a HITL script template and debug tag convention." |
| `prototype` skill — throwaway design validation | `skills/engineering/prototype/SKILL.md` + `LOGIC.md` + `UI.md` | No prototype skill in WabbleSpec | Validates logic models / UI designs before committing to full execution waves | None | days | "Add a `prototype` skill with LOGIC branch (TUI for state model validation) and UI branch (multi-variant route with floating switcher). Route selection based on the question being answered." |
| `scope-reject` / out-of-scope KB | `skills/engineering/triage/OUT-OF-SCOPE.md` | Evolution cycle has no persistent rejection record for deferred/declined ideas | Prevents re-litigating the same deferred Tier 7 items; institutional memory | Memory layer | days | "Add a `scope-reject` skill that writes concept-level rejection records to `.wabblespec/state/evolution/out-of-scope/`. Check KB at the start of any enhancement intake. File format: concept name, why rejected, prior requests list." |
| `handoff` skill — session continuity document | `skills/productivity/handoff/SKILL.md` | No handoff skill (second signal confirming gap from vibecode-pro-max-kit) | Structured context handoff for long tasks or between sessions | None | days | "Add a `handoff` skill that writes a session continuity document. Summarizes: active task, completed waves, current blockers, suggested next skill. Saves to temp path. Does not duplicate content already in task-card.md or receipts." |

---

### Watch Only

- M4 (hard/soft pointer naming) — WabbleSpec already implements this intuitively; naming it has low marginal value. Promote if a skill author is confused about when to add setup pointers.
- M5 (interview inline documentation discipline) — interview skill already has strong behavioral guidance; adding a "update inline" note is low priority.

---

## Do-Not-Copy List

| Item | Reason |
|---|---|
| LANGUAGE.md depth vocabulary (seam, adapter, depth, locality) | Conflicts with WabbleSpec's existing module/layer terminology — I6 not applicable but vocabulary collision is real |
| Issue tracker integration (to-issues, to-prd, triage state machine with GitHub/Linear publishing) | Domain-specific product tooling; WabbleSpec's triage is framework-internal receipt-gated routing |
| setup-matt-pocock-skills pattern | Incompatible with WabbleSpec's CLAUDE.md/recipe-based config system |
| in-progress writing skills | Low maturity; WabbleSpec already has writer/document/copy/markdown coverage |
| caveman mode | No fit — WabbleSpec's token economy is managed through receipt gating and skill preloading, not conversational compression |
| git-guardrails-claude-code | WabbleSpec already has more sophisticated PreToolUse hook architecture |

---

## Priority Implementation Order

| Order | ID | Item | Why first |
|---|---|---|---|
| 1 | M1 | HITL/AFK execution_mode | Highest integration score (8); fills a genuine behavioral gap in wave plans |
| 2 | M2 | No file paths in acceptance criteria | Medium-high score (6); prevents spec rot at write time |
| 3 | M3 | No time-sensitive info in descriptions | Score (5); straightforward CLAUDE.md rule addition |

---

## Execution Notes

- M1 and M2 target different files — can be written in parallel.
- M3 targets CLAUDE.md — independent of M1/M2, can be written in parallel with both.
- Each edit to `.claude/skills/` must be mirrored to the matching `.wabblespec/engine/modules/` file immediately (sync script overwrites .claude/ on next run).
- No new files needed for Tier 1 items — all are additive edits to existing checklists and output contracts.
