# Ref-Plan: continuous-claude-v3

**Based on:** `research/ref-eval/continuous-claude-v3.md`
**Planned:** 2026-05-30
**Status:** Phase 1 items ready for Gate B

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| C1 | Claim verification markers (✓ VERIFIED / ? INFERRED / ✗ UNCERTAIN) | Behavioral | High | High | Low |
| C2 | Checkpoint state symbols (○ → ✓ ✗) + JSON validation state | Behavioral | High | High | Low |
| C3 | Erotetic Check E(X,Q) framing | Behavioral | Medium | High | Low |
| C4 | YAML handoff `goal:`/`now:` contract | Interaction | Medium | Medium | Medium |
| C5 | Proactive delegation threshold table | Behavioral | Medium | Medium | Low |
| C6 | 7-type memory learning taxonomy | Format | Low | Medium | Low |

---

## Exclusion List

| Item | Reason |
|---|---|
| Model name frontmatter (`model: opus`, `model: haiku`, `model: sonnet`) | I6 — no model names in framework files |
| `no-haiku.md` rule | I6 — model name in file name and content |
| `agent-model-selection.md` rule body | I6 — names Haiku/Opus/Sonnet |
| `rp-cli` tool calls | External binary not available |
| PostgreSQL/BGE memory backend | Heavy dependency; WabbleSpec uses DuckDB + file drawers |
| `CLAUDE_OPC_DIR` env var | Project-specific, not portable |
| Agent output file protocol (`.claude/cache/agents/`) | Conflicts with receipt model (I10) |
| Orchestration pattern table (maestro.md) | Study-only; needs reconciliation with WabbleSpec execution-mode model |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
Map: High=3, Medium=2, Low=1
```

| ID | impact×2 | project_fit | risk | score |
|---|---|---|---|---|
| C1 | 6 | 3 | 1 | **8** |
| C2 | 6 | 3 | 1 | **8** |
| C3 | 4 | 3 | 1 | **6** |
| C5 | 4 | 2 | 1 | **5** |
| C4 | 4 | 2 | 2 | **4** |
| C6 | 2 | 2 | 1 | **3** |

---

## Tier Assignment

### Tier 1 — Behavioral Additions (additive to existing files)

**T1-A: Claim Verification Markers → adversary/SKILL.md**
- What: Add `## Claim Confidence Protocol` section with 3 markers and two-pass audit pattern
- Where: `.wabblespec/engine/modules/l2/adversary/SKILL.md` + `.claude/skills/adversary/SKILL.md`
- How: Insert section between the findings generation section and the scoring section. Content: define ✓ VERIFIED (file read, code traced), ? INFERRED (grep/search basis, must verify), ✗ UNCERTAIN (not checked). Two-pass audit: Pass 1 produces ? INFERRED hypotheses from search; Pass 2 reads each file and upgrades or downgrades. Every finding output must carry one marker.
- Literal values: `✓ VERIFIED`, `? INFERRED`, `✗ UNCERTAIN`
- Gate: adversary SKILL.md contains all 3 literal marker strings and `## Claim Confidence Protocol` section header
- Reference location: `continuous-claude-v3/.claude/rules/claim-verification.md`

**T1-B: Checkpoint State Symbols → executor/SKILL.md**
- What: Add `## Wave State Symbols` section defining ○ PENDING, → IN_PROGRESS, ✓ VALIDATED, ✗ FAILED and the state transition rule
- Where: `.wabblespec/engine/modules/l3/executor/SKILL.md` + `.claude/skills/executor/SKILL.md`
- How: Insert section in the wave execution loop, after the checkpoint-write step. Define symbols, allowed transitions, and the rule "NEVER advance to next wave without Verifier PASS for the current wave" (maps to WabbleSpec's existing rule but reinforced with symbols)
- Literal values: `○ PENDING`, `→ IN_PROGRESS`, `✓ VALIDATED`, `✗ FAILED`
- Gate: executor SKILL.md contains all 4 literal state symbol strings
- Reference location: `continuous-claude-v3/.claude/agents/kraken.md` Step 5

**T1-C: Erotetic Check → guard/SKILL.md**
- What: Add `## Pre-Check Question Frame` section with E(X,Q) pattern (X = wave target, Q = invariant questions to enumerate)
- Where: `.wabblespec/engine/modules/l2/guard/SKILL.md` + `.claude/skills/guard/SKILL.md`
- How: Insert at the start of the guard execution section (before the Layer 1–5 checks). Frame: X = the files/operations declared in the wave plan; Q = the list of invariant questions Guard must answer (authority, command risk, receipt chain, staleness, scope). Output the Q inventory explicitly in Guard's stdout before issuing PASS/FAIL.
- Gate: guard SKILL.md contains `E(X,Q)` in the pre-check section
- Reference location: `continuous-claude-v3/.claude/agents/phoenix.md`, `agents/aegis.md`

### Tier 2 — Module-Level Augmentation

**T2-A: Proactive Delegation Threshold Table → autopilot/SKILL.md**
- What: Add a delegation decision table to autopilot SKILL.md with explicit thresholds for spawning subagents vs. keeping in main context
- Where: `.wabblespec/engine/modules/l8/autopilot/SKILL.md` + `.claude/skills/autopilot/SKILL.md`
- How: Insert `## Delegation Thresholds` table after the wave dispatch section. Columns: Pattern / Signal / Action. Rows: reading 3+ files (research phase) → spawn separate research wave; parallel independent subtasks → parallel wave dispatch; validation only → executor handles inline
- Gate: autopilot SKILL.md contains `## Delegation Thresholds` with at least 3 threshold rows
- Reference location: `continuous-claude-v3/.claude/rules/proactive-delegation.md`
- Specify required: No
- Breaking change risk: None (additive)

**T2-B: 7-Type Memory Taxonomy → memory/SKILL.md**
- What: Add the named learning taxonomy to the memory skill's drawer-writing guidance
- Where: `.wabblespec/engine/modules/l5/memory/SKILL.md` + `.claude/skills/memory/SKILL.md`
- How: Insert `## Observation Types` section after the drawer structure section. List 7 named types with descriptions: ARCHITECTURAL_DECISION, WORKING_SOLUTION, CODEBASE_PATTERN, FAILED_APPROACH, ERROR_FIX, USER_PREFERENCE, OPEN_THREAD. Note: these map to drawer `type` field values for categorized retrieval.
- Literal values: `ARCHITECTURAL_DECISION`, `WORKING_SOLUTION`, `CODEBASE_PATTERN`, `FAILED_APPROACH`, `ERROR_FIX`, `USER_PREFERENCE`, `OPEN_THREAD`
- Gate: memory SKILL.md contains all 7 type names
- Reference location: `continuous-claude-v3/.claude/rules/dynamic-recall.md`
- Specify required: No
- Breaking change risk: None (additive; drawer type field already exists)

### Tier 6 — Synthesis (implement after Tier 1–2 validated)

**T6-A: E(X,Q) + Guard Receipt Output**
- What: Guard's E(X,Q) question inventory is exposed in the guard receipt JSON under `question_inventory: [...]` field
- Why it requires both inputs: E(X,Q) provides the question structure; guard-check.py and receipt-writer.py provide the structured receipt format
- Target: `.wabblespec/engine/shared/scripts/guard-check.py` + `receipt-writer.py` schema
- Status: Deferred (requires Tier 5 risk level — changes receipt schema)

**T6-B: Checkpoint State Symbols + Wave Plan Receipts**
- What: Wave plan receipt entries include current state symbol and JSON validation block
- Why it requires both inputs: state symbols from C2; receipt-writer.py `--type execution` provides the receipt container
- Target: `.wabblespec/engine/modules/l3/executor/SKILL.md` (already covered by T1-B) + receipt-writer.py schema extension
- Status: T1-B covers the executor side; schema extension deferred (Tier 5)

**T6-C: Claim Markers + Verifier Receipt**
- What: Verifier receipt annotates each criterion check with its claim confidence marker before issuing PASS/FAIL
- Why it requires both inputs: claim markers from C1; verifier receipt format from receipt-writer.py `--type verifier`
- Target: `.wabblespec/engine/modules/l2/verifier/SKILL.md` + receipt-writer.py verifier schema
- Status: Claim markers added to adversary (T1-A) cover most of this value; verifier receipt schema extension deferred (Tier 5)

### Tier 7 — Expansion Roadmap

| Capability | Effort | Session Seed |
|---|---|---|
| Epistemic reminder hook (PostToolUse/Grep) | days | See drawer `expansion-epistemic-reminder-hook.json` |
| Transcript-based auto-handoff (PreCompact) | weeks | See drawer `expansion-transcript-auto-handoff.json` |
| Pattern inference module (task → orchestration pattern) | weeks | See drawer `expansion-pattern-inference-module.json` |

---

## Do-Not-Copy List

| Item | Invariant |
|---|---|
| `model: opus`, `model: sonnet`, `model: haiku` in frontmatter | I6 — no model names |
| `no-haiku.md` rule file | I6 — model name in file name and content |
| `agent-model-selection.md` rule body | I6 — names Haiku/Opus/Sonnet |
| `rp-cli` tool references | External binary |
| `CLAUDE_OPC_DIR` env var | Project-specific |
| `.claude/cache/agents/` output convention | Conflicts with I10 receipt model |

---

## Priority Implementation Order

| Order | ID | Item | Why First |
|---|---|---|---|
| 1 | C1 → T1-A | Claim verification markers → adversary/SKILL.md | Highest impact, lowest risk; strengthens an active and frequently invoked module |
| 2 | C2 → T1-B | Checkpoint state symbols → executor/SKILL.md | Highest impact, lowest risk; makes wave state machine observable |
| 3 | C3 → T1-C | Erotetic Check → guard/SKILL.md | Medium impact; forces pre-check question inventory before guard execution |
| 4 | C5 → T2-A | Delegation thresholds → autopilot/SKILL.md | Medium impact; clarifies an existing but informal decision point |
| 5 | C6 → T2-B | 7-type taxonomy → memory/SKILL.md | Low impact but zero risk; improves drawer categorization |

---

## Execution Notes

- T1-A and T1-B can run in parallel (no shared file targets)
- T1-C must wait until T1-A is verified (guard uses adversary's findings; want claim markers established first)
- T2-A and T2-B can run in parallel after T1-A/B/C verified
- T6 items deferred — require receipt schema changes which are Tier 5 risk
- Sync engine modules immediately after each `.claude/skills/` edit (wabblespec-sync-skills.py overwrites on next run)
