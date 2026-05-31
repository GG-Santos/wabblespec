# Ref-Plan: vibecode-pro-max-kit

**Reference slug:** `vibecode-pro-max-kit`
**Plan date:** 2026-05-30
**Overall verdict:** supporting-reference (8/10)

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| C1 | Subagent status codes (DONE_WITH_CONCERNS) | Behavioral | High | High | Low |
| C2 | Post-execute closeout packet (8-point format, 3 classifications) | Behavioral | High | High | Low |
| C3 | Drift signal scoring (LOW/MEDIUM/HIGH) | Behavioral | High | High | Low |
| C4 | 50% mid-wave check-in gate | Behavioral | Medium | High | Low |
| C5 | High-risk evidence pack schema (6 classes, 5 JSON) | Behavioral | Medium | High | Low |
| C6 | Compaction recovery warning (exact wording) | Behavioral | Medium | Medium | Low |
| C7 | Parallel fan-out signal scoring + per-agent output format | Behavioral/Format | Medium | Medium | Low |
| C8 | Intent clarification tiered protocol (as reference doc) | Behavioral | Medium | Medium | Low |
| C9 | Autonomy mode boundary definition | Behavioral | Low | Medium | Low |
| T7-A | Autonomous optimization loop skill | Net-new | — | — | Medium |
| T7-B | Session handoff scanner script | Net-new | — | — | Low |

---

## Exclusion Filter

| Item | Reason Excluded |
|---|---|
| RIPER-5 as named methodology | I1 — WabbleSpec is the spec system; importing RIPER-5 would split authority |
| AskUserQuestion tool calls | I6 — tool name violates vendor-neutral rule; use capability placeholder form |
| Delegation-only orchestrator philosophy | Conflicts with WabbleSpec Executor model where the active agent does the work |
| `process/` directory conventions | Product-space collisions — these are for users, not for WabbleSpec framework |
| Literal trivial-fix thresholds (15 lines) | Study-only; calibration values should come from WabbleSpec's own complexity scoring |

---

## Integration Score Table

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | Impact | Project fit | Risk | Score | Tier |
|---|---|---|---|---|---|
| C1 | High(3) | High(3) | Low(1) | 8 | Tier 1 |
| C2 | High(3) | High(3) | Low(1) | 8 | Tier 1 |
| C3 | High(3) | High(3) | Low(1) | 8 | Tier 1 |
| C4 | Medium(2) | High(3) | Low(1) | 6 | Tier 1 |
| C5 | Medium(2) | High(3) | Low(1) | 6 | Tier 2 |
| C6 | Medium(2) | Medium(2) | Low(1) | 5 | Tier 1 |
| C7 | Medium(2) | Medium(2) | Low(1) | 5 | Tier 2 |
| C8 | Medium(2) | Medium(2) | Low(1) | 5 | Tier 3 |
| C9 | Low(1) | Medium(2) | Low(1) | 3 | Watch Only |

---

## Tier Assignments

### Tier 1 — Behavioral Additions (additive to existing files)

**C1: Subagent status codes**
- What: Add DONE_WITH_CONCERNS to the verifier verdict set; add handling rules for BLOCKED/NEEDS_CONTEXT
- Where: `.claude/agents/wabblespec-verifier.md` + `.claude/agents/wabblespec-guard.md`
- How: Add a `## Subagent Status Protocol` section with the 4-state vocabulary and handling rules (never ignore BLOCKED/NEEDS_CONTEXT; correctness concerns = action items; never retry same blocked approach 3x). Add the recommended status footer format.
- Literal values to preserve: `"DONE"`, `"DONE_WITH_CONCERNS"`, `"BLOCKED"`, `"NEEDS_CONTEXT"`, footer structure `**Status:** / **Summary:** / **Concerns/Blockers:**`
- Gate: Status codes appear verbatim in at least one agent spec; handling rules are present.
- Reference location: `orchestration.md:38-57` + `vc-execute-agent.md:311-318`

**C2: Post-execute closeout packet**
- What: Add structured closeout section to executor SKILL.md with 3 classification labels and 8-point format
- Where: `.claude/skills/executor/SKILL.md`
- How: Add `## Closeout Packet` section after the execution receipt block. List the 3 classification labels verbatim. List the 8 content fields. Add rules: keep plan path explicit; no auto-archive; do recommend next valid state; do recommend commit checkpoint when validated.
- Literal values to preserve: Classification labels: `"Ready for archival"` / `"Keep in active/testing"` / `"Needs reconciliation"`. All 8 content field names.
- Gate: All 3 classification labels and all 8 content fields appear in executor SKILL.md.
- Reference location: `orchestration.md:165-208`

**C3: Drift signal scoring**
- What: Add drift signal scoring block to archive SKILL.md
- Where: `.claude/skills/archive/SKILL.md`
- How: Add `## Drift Signal Scoring` section. List 3 signals (files touched / framework file changes / 3+ memory-worthy observations). Map to LOW/MEDIUM/HIGH urgency with exact wording for each level.
- Literal values to preserve: LOW wording: `"Archive available if you want."` / MEDIUM: `"Recommend Archive -- significant changes detected."` / HIGH: `"Strongly recommend Archive -- framework files touched."`
- Gate: All 3 signals listed; all 3 urgency levels with exact wording present.
- Reference location: `orchestration.md:211-217`

**C4: 50% mid-wave check-in gate**
- What: Add mid-wave check-in instruction to executor SKILL.md
- Where: `.claude/skills/executor/SKILL.md`
- How: Add `## Mid-Wave Check-In` section. At approximately 50% completion: provide status update, list completed items, list remaining items, ask "Continue with current approach or pause and return to wave plan?" If user indicates hesitation, immediately pause.
- Gate: Check-in instruction at 50% milestone present in executor SKILL.md; "Continue or return to wave plan?" question present verbatim.
- Reference location: `vc-execute-agent.md:79-85`

**C6: Compaction recovery warning**
- What: Add compaction-specific approval gate re-confirmation warning to session-start hook
- Where: `.wabblespec/engine/hooks/wabblespec-session-start.js`
- How: In the SessionStart hook output, after session state display, add a block that fires only when `source === 'compact'`: output a warning that approval gates must be re-confirmed before proceeding.
- Literal values to preserve: Exact warning concept: "CONTEXT COMPACTED - APPROVAL STATE CHECK: If you were waiting for user approval at any gate, you MUST re-confirm with the user before proceeding."
- Gate: Compaction recovery warning appears in hook output when source is compact.
- Reference location: `session-init.cjs:339-347`

---

### Tier 2 — Module-Level Augmentation

**C5: High-risk evidence pack schema**
- What: Add high-risk class taxonomy and evidence pack requirement to guard SKILL.md
- Where: `.claude/skills/guard/SKILL.md`
- How: Add `## High-Risk Execution Classes` section. List the 6 risk classes. Specify the 5-JSON evidence pack schema. Add gate rule: if `mustStopBeforeFinalize: true`, classify wave as Keep or Reconcile, not complete.
- Breaking change risk: None — additive to guard checks.
- Gate: All 6 risk classes listed; all 5 JSON artifact names present; mustStopBeforeFinalize rule present.
- Reference location: `orchestration.md:243-265` + `vc-execute-agent.md:199-209`

**C7: Parallel fan-out signal scoring + per-agent output format**
- What: Add fan-out signal scoring to decompose SKILL.md; add per-agent structured output format to wabblespec-verifier.md
- Where: `.claude/skills/decompose/SKILL.md` + `.claude/agents/wabblespec-verifier.md`
- How: In decompose, add `## Parallel Fan-Out Signals` section with 5 signals and LOW/MEDIUM/HIGH thresholds. In verifier, add `## Parallel Agent Output Format` section with the structured format (Dimension/Status/Findings/Confidence/Notes).
- Breaking change risk: None — additive.
- Gate: All 5 signals listed in decompose; per-agent output format with all 5 fields in verifier agent spec.
- Reference location: `parallel-fan-out.md`

---

### Tier 3 — New Shared Infrastructure

**C8: Intent clarification tiered protocol (reference doc)**
- What: Create a new reference doc capturing the 4-signal scoring, 3-tier protocol, and auto-skip conditions
- Where: `.wabblespec/engine/shared/references/intent-clarification.md`
- How: Write the reference doc with the signal table, threshold table, auto-skip conditions list, autonomy mode boundaries, and light research pass budget. Route into guard/skill-rules.json as a reference.
- Gate: Reference doc exists with signal table, threshold table, and auto-skip list.
- Reference location: `process/development-protocols/intent-clarification.md`

---

### Tier 7 — Expansion Roadmap

| Capability | Reference Location | Why WabbleSpec Lacks It | What It Unlocks | Dependencies | Effort | Session Seed |
|---|---|---|---|---|---|---|
| Autonomous metric optimization loop | `vc-autoresearch/SKILL.md` | No autonomous iteration with git-backed rollback | Self-optimizing framework quality metrics (quality-floor scores, receipt chain coverage) without human-per-iteration approval | benchmark skill, active git, verify command outputting single number | weeks | New skill `/benchmark-loop`: Goal=quality-floor gate score, Scope=.claude/skills/**/*.md, Verify=quality-floor-check.py --format json | jq '.summary.passed', Guard=validate-graph.py, Iterations=20, Direction=higher |
| Session handoff scanner | `vc-watzup/SKILL.md` + `watzup-scan.cjs` | No cross-session state inspector | Read-only snapshot of current session, active wave, pending receipts, and recent git activity for any session start | session-state.py, wave-queue.py, git | days | New script `watzup-scan.py` reading session-state.py show + wave-queue.py status + git status + .wabblespec/state/plans/. Output: human-readable handoff report. Expose as /watzup skill. |

---

## Do-Not-Copy List

| Item | Invariant |
|---|---|
| RIPER-5 as a named development methodology | I1 — WabbleSpec owns the spec lifecycle |
| AskUserQuestion tool call in SKILL.md files | I6 — use `~~structured-question` placeholder form |
| Delegation-only orchestrator philosophy | Conflicts with WabbleSpec Executor model |
| `process/` directory structure (general-plans, features, context/) | Product-space conventions not applicable to WabbleSpec framework |
| Literal line-count thresholds for trivial-fix detection | Framework-specific calibration values |

---

## Priority Implementation Order

| Order | ID | Item | Target | Why First |
|---|---|---|---|---|
| 1 | C1 | Subagent status codes | wabblespec-verifier.md, wabblespec-guard.md | Fills missing middle state; zero risk; other items reference it |
| 2 | C2 | Closeout packet format | executor SKILL.md | High-impact structural addition; needed before C3 makes sense |
| 3 | C3 | Drift signal scoring | archive SKILL.md | Directly improves archive trigger quality; easy additive block |
| 4 | C4 | Mid-wave check-in | executor SKILL.md | Same target as C2 — batch the two executor edits |
| 5 | C6 | Compaction recovery warning | wabblespec-session-start.js | Low-risk hook addition; closes approval gate bypass |
| 6 | C5 | High-risk evidence pack | guard SKILL.md | Guard enhancement; builds on C1 status vocabulary |
| 7 | C7 | Fan-out signal scoring + output format | decompose SKILL.md + wabblespec-verifier.md | Additive; benefits from C1 per-agent output format context |
| 8 | C8 | Intent clarification reference doc | .wabblespec/engine/shared/references/ | Infrastructure; lower immediate impact but valuable for future |

---

## Execution Notes

- C2 and C4 both target `executor/SKILL.md` — implement in the same turn, not two separate edits.
- C1 targets both agent specs — both edits can be batched in one turn.
- C6 targets the hook JS file — requires reading the file before editing; check the `source === 'compact'` detection path already exists.
- C8 is a new file write — create at `.wabblespec/engine/shared/references/intent-clarification.md`.
- Tier 7 items are documentation-only in this pipeline — drawers written, no implementation.
