# Ref-Plan: OpenSpec Integration

**Reference:** openspec
**Session:** agent-creator-integration-20260529
**Planned:** 2026-05-30
**Based on:** research/ref-eval/openspec.md

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Delta acceptance criteria format in `specify` SKILL.md | Behavioral | Medium | High (most tasks are brownfield) | Low |
| A2 | `<context>` / `<rules>` injection convention in `scope-frame` SKILL.md | Format | Low | Medium (pattern documentation) | Low |
| B1 | Per-wave instruction embedding in `wave-plan-writer.py` | Behavioral | Medium | Low (active task is different) | Low |
| B2 | BLOCKED/READY/DONE labels in wave plan status output | Format | Low | Low | Low |
| C1 | Multi-tool skill generation | Expansion | High | Low (no active need) | Medium |
| C2 | Parallel session conflict detection | Expansion | Medium | Medium | Low |
| C3 | Schema-defined custom workflow initialization | Expansion | Medium | Low | High |

---

## Exclusion Filter

| Item | Excluded | Reason |
|---|---|---|
| "Fluid not rigid" philosophy | EXCLUDED | I1 hard conflict — no phase gates contradicts P2 blocked until P1 locked |
| Filesystem-as-state model | EXCLUDED | I10 hard conflict — receipt chain is non-negotiable |
| Model name verbatim copy (README line 161) | EXCLUDED | I6 violation |
| Workspace/initiative beta features | EXCLUDED | Incompatible with WabbleSpec session model; beta-flagged |
| "Lite spec" / progressive rigor | EXCLUDED | I10 conflict — explicit receipts at every non-trivial step |
| Multi-tool adapters | EXCLUDED | Risk=Low but Project fit=Low; defer to Tier 7 |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
Map: High=3, Medium=2, Low=1
```

| ID | impact×2 | fit | risk | score | Tier |
|---|---|---|---|---|---|
| A1 | 4 | 3 | 1 | 6 | Tier 1 |
| A2 | 2 | 2 | 1 | 3 | Tier 1 |
| B1 | 4 | 1 | 1 | 4 | Watch Only |
| B2 | 2 | 1 | 1 | 2 | Watch Only |
| C1 | — | — | — | — | Tier 7 |
| C2 | — | — | — | — | Tier 7 |
| C3 | — | — | — | — | Tier 7 |

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive to existing files)

**A1 — Delta Acceptance Criteria Format**

- **What:** Add a `## Delta Acceptance Criteria` subsection to `.claude/skills/specify/SKILL.md` documenting the ADDED/MODIFIED/REMOVED structure for brownfield task cards
- **Where:** `.claude/skills/specify/SKILL.md` — after the existing GWT acceptance criteria section (Step 3)
- **How:** Insert a new subsection `### Delta format (for ADDITIVE or REMOVAL change_class)` explaining: when `change_class` is `ADDITIVE`, organize criteria under `## ADDED Criteria` (new behaviors) and `## MODIFIED Criteria` (changed behaviors); when `change_class` is `REMOVAL`, add a `## REMOVED Criteria` block with the deprecated behavior and migration note. Each criterion still uses GWT format within its section. This is optional — use flat GWT for simple tasks, delta format for complex brownfield changes.
- **Literal values:** Section headers `## ADDED Criteria`, `## MODIFIED Criteria`, `## REMOVED Criteria` (adapted from OpenSpec's `## ADDED Requirements` etc. to match WabbleSpec's acceptance criteria vocabulary)
- **Gate:** Grep `specify/SKILL.md` for `## ADDED Criteria` returns a match; existing GWT content unchanged
- **Reference location:** `OpenSpec/schemas/spec-driven/templates/spec.md`, `OpenSpec/docs/concepts.md` §Delta Specs

**A2 — Context/Rules Injection Convention**

- **What:** Add a notation to `.claude/skills/scope-frame/SKILL.md` documenting the `<context>` / `<rules>` XML tag convention for structuring scope output for downstream artifact generation
- **Where:** `.claude/skills/scope-frame/SKILL.md` — at end of Step 2 or as a new `## Output Convention` subsection
- **How:** Add 4-6 lines noting that when scope.md content is injected into downstream artifact generation (e.g., by Specify), it should be wrapped in `<context>...</context>` for project standards/assumptions and `<rules>...</rules>` for session-specific constraints. This makes the scope content machine-parseable by the receiving skill. No behavior change to existing output format — documentation only.
- **Literal values:** `<context>`, `</context>`, `<rules>`, `</rules>` XML tags
- **Gate:** Grep `scope-frame/SKILL.md` for `<context>` returns a match
- **Reference location:** `OpenSpec/docs/customization.md` §How It Works (Context and rules injection)

---

### Watch Only

**B1 — Per-wave instruction embedding in wave-plan-writer.py**
Unclear fit with active task; wave plans reference task card goals and executor derives per-wave action adequately. Promote when Executor skill exceeds 300 lines and per-wave context re-derivation is identified as a pain point.

**B2 — BLOCKED/READY/DONE state labels**
Low integration score; no active consumer of this label format in WabbleSpec. Promote when a wave status dashboard is planned.

---

### Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| "Fluid not rigid" / no phase gates | I1: SPEC IS SINGLE SOURCE OF TRUTH; P2 blocked until P1 locked |
| Filesystem-as-state model (DONE = file exists) | I10: Every non-trivial execution writes a receipt |
| Model name recommendations (README line 161) | I6: No model names in framework files |
| Workspace/initiative beta features | Incompatible with WabbleSpec session model |

---

### Tier 6 — Synthesis Items

**S1 — Delta-Keyed Acceptance Criteria**

This is the synthesis version of A1 above. A1 is the additive documentation step; S1 is the deeper integration where the Verifier skill reads `change_class` and routes acceptance criteria by ADDED/MODIFIED/REMOVED section headers to select different verification modes (presence check vs. replacement check vs. absence check).

- **Watch Only** in this session; requires Verifier augmentation to be meaningful.
- Promote when: Verifier skill is extended to distinguish presence vs. replacement verification.

**S2 — Instruction-Embedded Wave Plan**

Wave plan YAML embeds per-wave `instruction:` field (from OpenSpec's schema YAML pattern), making the wave plan self-contained. Executor reads `instruction:` if present, falls back to task card synthesis if absent.

- **Watch Only** in this session; wave plan format change is architecture-level (needs Decompose + Executor + wave-plan-writer.py coordination).
- Promote when: Decompose or Executor is up for a refactor wave.

---

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why lacks it | Unlocks | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| Multi-tool skill generation | `src/core/command-generation/adapters/*.ts` | wabblespec-sync-skills.py targets Claude Code only | Framework portability to Cursor/Windsurf/Copilot/etc. | Abstract SKILL.md format; write per-tool adapters | weeks | "Build WabbleSpec multi-tool skill adapters. Start with Cursor (.cursor/rules/*.mdc) and Windsurf (.windsurfrules). Adapter interface: input = SKILL.md frontmatter + body, output = tool-specific file." |
| Parallel session conflict detection | `docs/commands.md` §bulk-archive | Session model is single-agent; no cross-session conflict check | Team-scale WabbleSpec usage without silent overwrites | session-registry.py (exists); receipt target-file extraction | days | "Build session-conflict-check.py: read session-registry, extract changed file sets from execution receipts, detect overlapping targets, emit conflict report. Wire to archive skill as pre-condition." |
| Schema-defined custom workflow init | `src/commands/schema.ts` | WabbleSpec phase sequence hardcoded in SKILL.md prose | Teams can fork and customize execution phase sequence | Externalize phase sequence into YAML; make Executor schema-aware | months | "Design WabbleSpec workflow schema format (YAML): phase IDs, dependencies, skill bindings. Build schema init wizard. Make Executor consume schema instead of hard-coded phase order." |

---

## Priority Implementation Order (Tier 1 items)

| Order | Item | Why first |
|---|---|---|
| 1 | A1 — Delta acceptance criteria format in `specify` SKILL.md | Higher integration score (6); directly addresses brownfield task card quality; Verifier already consumes specify output |
| 2 | A2 — Context/rules injection convention in `scope-frame` SKILL.md | Documentation-only; builds on A1 context; lower risk |

---

## Execution Notes

- A1 and A2 are independent; can run in parallel
- Do NOT alter existing GWT acceptance criteria format — both additions are additive only
- Do NOT change scope-frame output format — A2 is documentation of convention, not a behavioral change
- S1 and S2 (Tier 6 synthesis) are Watch Only — do not promote to implementation this session without an explicit user confirm
- All Tier 7 items are documentation-only in this session (drawers written during Phase 1)
