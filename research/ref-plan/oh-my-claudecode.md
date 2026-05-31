# Ref-Plan: oh-my-claudecode Integration

**Reference:** oh-my-claudecode (v4.14.4)
**Session:** agent-creator-integration-20260529
**Planned:** 2026-05-30
**Based on:** research/ref-eval/oh-my-claudecode.md

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Adversary: severity vocabulary + self-audit + realist check + adversarial escalation | Behavioral | High | High (agent-creator task is hardening adversary/grader/guard/verifier) | Medium |
| A2 | Verifier: independent-reviewer constraint + VERIFIED/PARTIAL/MISSING per-criterion vocabulary | Behavioral | High | High (directly addresses wabblespec-verifier hardening in active task) | Low |
| A3 | Verifier: VERIFIED/PARTIAL/MISSING + delta-format section header routing (synthesis S2) | Behavioral | High | High | Low |
| B1 | Commit: decision trailer convention (Constraint/Rejected/Directive/Confidence/Scope-risk/Not-tested) | Format | Medium | Medium (commit skill exists; not part of active task) | Low |
| B2 | Interview: "never ask codebase facts of user" companion rule | Behavioral | Low | Medium | Low |

---

## Exclusion Filter

| Item | Excluded | Reason |
|---|---|---|
| `model: claude-opus-4-6` in harsh-critic.md | EXCLUDED | I6 violation |
| haiku/sonnet/opus tier names in CLAUDE.md | EXCLUDED | I6 violation |
| `.omc/` state directory model | EXCLUDED | I10 conflict — receipt chain is non-negotiable |
| Magic keywords (ralph/ultrawork/ralplan) | EXCLUDED | I1 conflict — WabbleSpec requires Recipe before execution |
| MCP server tools (omc-state, notepad, project-memory) | EXCLUDED | Hard binary dependency; not portable |
| ralphthon PRD format | EXCLUDED | OMC-specific; no equivalent receipt type |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
Map: High=3, Medium=2, Low=1
```

| ID | impact×2 | fit | risk | score | Tier |
|---|---|---|---|---|---|
| A2 | 6 | 3 | 1 | 8 | Tier 1 |
| A1 | 6 | 3 | 2 | 7 | Tier 2 |
| B1 | 4 | 2 | 1 | 5 | Tier 1 |
| B2 | 2 | 2 | 1 | 3 | Watch Only |

Note: A3 (delta-format criterion routing) is a synthesis item and appears in Tier 6.

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive to existing files)

**A2 — Verifier: Independent-Reviewer Constraint + VERIFIED/PARTIAL/MISSING**

- **What:** Add (a) the independent-reviewer constraint and (b) per-criterion status vocabulary to `.claude/skills/verifier/SKILL.md`
- **Where:** `.claude/skills/verifier/SKILL.md` — (a) in `## When to use / when not to use` section, (b) in `## How to do it` before Step 2 (mode-specific check), referencing the acceptance criteria table from the task card
- **How:**
  - (a) Add to "Do not use when" list: "The same active context that executed the wave is attempting verification — use a separate reviewer pass; never self-approve work produced in your own context"
  - (b) Add a subsection "### Per-criterion status" before or within Step 2: document three status values with exactly these labels: `VERIFIED` (criterion confirmed with evidence), `PARTIAL` (criterion partially confirmed — test exists but doesn't cover all edge cases or evidence is incomplete), `MISSING` (criterion has no corresponding evidence — cannot be confirmed). Verifier must assign one status per acceptance criterion and include the evidence source.
- **Literal values:** `VERIFIED`, `PARTIAL`, `MISSING` (exact labels)
- **Gate:** Grep `verifier/SKILL.md` for `VERIFIED` returns a match in the per-criterion section; "same active context" phrase present in When not to use
- **Reference location:** `agents/verifier.md` — `<Constraints>` block + `<Output_Format>` acceptance criteria table

**B1 — Commit: Decision Trailer Convention**

- **What:** Add an optional decision trailer convention to `.claude/skills/commit/SKILL.md`
- **Where:** `.claude/skills/commit/SKILL.md` — append a new subsection to Mode: write section, after Step 5 (breaking change footer), titled "### Step 5b — Write decision trailers (when applicable)"
- **How:** Add 4-6 lines documenting the six trailer types with exactly these labels: `Constraint:`, `Rejected:`, `Directive:`, `Confidence:`, `Scope-risk:`, `Not-tested:`. Convention: include when the commit encodes a non-obvious architectural decision; skip for trivial commits. Format: one trailer per line after a blank line following the body.
- **Literal values:** `Constraint:`, `Rejected:`, `Directive:`, `Confidence:`, `Scope-risk:`, `Not-tested:`
- **Gate:** Grep `commit/SKILL.md` for `Constraint:` returns a match in the trailer section
- **Reference location:** `CLAUDE.md` — `<commit_protocol>` section

---

### Tier 2 — Module-level augmentation

**A1 — Adversary: Severity Vocabulary + Protocol Extension**

- **What:** Extend `.claude/skills/adversary/SKILL.md` with (a) severity vocabulary for findings, (b) pre-commitment prediction step, (c) self-audit step, (d) realist check step, (e) adversarial escalation condition
- **Where:** `.claude/skills/adversary/SKILL.md` — within and after Step 2 (Challenge across four domains)
- **How:**
  - (a) In Step 2, add requirement: each finding must carry severity: `CRITICAL` (breaks integration goal or blocks execution), `MAJOR` (causes significant rework or degrades important functionality), `MINOR` (suboptimal but functional). This applies within all four domains.
  - (b) Before Step 1 (anchoring prevention), insert Step 0: "Before reading the artifact, based on the artifact type and domain, predict 2-3 most likely weakness areas. Record these. Then deliberately investigate each prediction during Step 2." Label this "Step 0 — Pre-commitment predictions"
  - (c) After Step 2, insert Step 2.5: "Self-audit (mandatory). For each CRITICAL or MAJOR finding: (1) rate confidence HIGH/MEDIUM/LOW; (2) ask 'could the author immediately refute this with context I might be missing?'; (3) distinguish genuine flaw vs. stylistic preference. Rules: LOW confidence → move finding to `open_questions` in the receipt, not `counter_analysis`. Author-refutable with no hard evidence → move to `open_questions`. Stylistic preference → downgrade to MINOR."
  - (d) After Step 2.5, insert Step 2.75: "Realist Check (mandatory). For each CRITICAL or MAJOR finding that survived self-audit: (1) what is the realistic worst case — not theoretical maximum? (2) what mitigating factors exist? (3) how quickly would this be detected in practice? (4) am I inflating severity due to review momentum? Rules: if realistic worst case is minor with easy recovery → downgrade CRITICAL to MAJOR; if mitigating factors substantially contain blast radius → downgrade accordingly. Every downgrade MUST include a 'Mitigated by:' statement. NEVER downgrade findings involving data loss, security breach, or correctness violation."
  - (e) After Step 2.75, add escalation rule: "If findings include 1 or more CRITICAL findings, or 3 or more MAJOR findings: escalate to ADVERSARIAL mode. In ADVERSARIAL mode: assume there are more hidden problems, actively hunt for them in adjacent scope, challenge every design decision. Record `adversarial_mode_triggered: true` in the receipt."
- **Literal values:** `CRITICAL`, `MAJOR`, `MINOR`, `Mitigated by:`, `adversarial_mode_triggered`
- **Gate:** Grep `adversary/SKILL.md` for `CRITICAL` and `Mitigated by:` both return matches; `adversarial_mode_triggered` appears in output contract
- **Reference location:** `agents/critic.md` — phases 4.5, 4.75, and escalation section

---

### Watch Only

**B2 — Interview: "Never ask codebase facts"**

WabbleSpec interview limits batching to max-3 per batch and prohibits leading questions. OMC's planner adds "never ask the user about codebase facts — spawn explore agent instead." This companion rule is useful but the active task card does not include interview hardening. Promote when: interview is up for a revision wave or a future ref-adopt targets an interview-focused reference.

---

### Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| `model: claude-opus-4-6` in harsh-critic.md | I6: no model names in framework files |
| haiku/sonnet/opus capability tier names | I6: model-family names, not capability descriptors |
| `.omc/state/` directory model | I10: receipt chain is non-negotiable |
| Magic keyword detection (ralph/ultrawork/ralplan) | I1: requires spec-first, not trigger-first |
| MCP server tools (omc-state, notepad, project-memory) | External binary dependency; not portable |

---

### Tier 6 — Synthesis Items

**S1 — Receipt-Gated Adversarial Protocol**

Adversary receipt schema gains `severity_distribution` field (`critical_count`, `major_count`, `minor_count`). Grader reads this field and routes: ≥1 CRITICAL → request re-challenge in ADVERSARIAL mode; ≥3 MAJOR without CRITICAL → request targeted re-examination of top MAJOR findings; else → proceed to ACCEPT-WITH-RESERVATIONS or ACCEPT verdict.

- **Watch Only** in this session; requires both adversary SKILL.md augmentation (A1) AND grader SKILL.md extension AND schema update.
- Promote when: A1 is implemented and verified PASS; then grader extension is the natural follow-on wave.

**S2 — Verifier Delta-Format Criterion Routing**

Verifier reads task card delta section headers (ADDED/MODIFIED/REMOVED from OpenSpec ref-adopt) and applies VERIFIED/PARTIAL/MISSING status differently per section: ADDED criteria → presence check, MODIFIED criteria → replacement check (old behavior gone), REMOVED criteria → absence check.

- **Partial implementation**: A2 adds VERIFIED/PARTIAL/MISSING vocabulary; the delta-section routing logic is the second half.
- Promote when: A2 is implemented and the verifier SKILL.md is being updated for a delta-task cycle.

---

### Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it would unlock | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| Per-plan knowledge notebooks | `docs/ARCHITECTURE.md` §Plan Notepad | WabbleSpec drawers are project-scoped; no plan-scoped capture | Task-scoped learnings persist across compaction; auto-inject into next same-task session | session-registry.py exists | weeks | "Build per-session plan notebook: extend session-registry.py to create state/notepads/{session-id}/; add notebook-writer.py for learnings/decisions/issues entries; update executor SKILL.md to append learnings after each wave; wire on_archive daemon to index into entity-graph." |
| Compaction-resistant session memo | `docs/ARCHITECTURE.md` §Notepad | stop-hook.py fires on_stop events; no pre-compaction memo mechanism | Critical in-flight state survives compaction without user re-stating context | stop-hook.py exists | days | "Add compaction-resistant session memo: extend stop-hook.py with on_precompact event; build memo-writer.py saving critical state to state/session/memo.md; extend wabblespec-session-start.js to inject memo.md as system-reminder when present." |

---

## Priority Implementation Order (Tier 1–2 items)

| Order | Item | Tier | Why first |
|---|---|---|---|
| 1 | A2 — Verifier independent-reviewer constraint + VERIFIED/PARTIAL/MISSING | Tier 1 | Highest score (8); directly addresses wabblespec-verifier hardening in active task; lowest risk; additive only |
| 2 | A1 — Adversary severity + self-audit + realist check + escalation | Tier 2 | Second-highest score (7); directly addresses wabblespec-guard/verifier hardening; substantive but bounded to adversary SKILL.md |
| 3 | B1 — Commit decision trailers | Tier 1 | Score 5; low risk; additive to commit SKILL.md; can run in parallel with A1 |

---

## Execution Notes

- A2 and B1 are independent — can run in parallel (different target files)
- A1 must run after A2 is complete only if adversary → verifier interaction is involved; otherwise independent
- Do NOT alter existing adversary challenge domain structure (weaknesses/missed-alternatives/unstated-assumptions/failure-scenarios) — A1 adds severity to existing domains, does not replace them
- Do NOT alter existing verifier verification modes (Test/Observation/Audit/Review/Measurement/Attestation/Demonstration/Async-Review) — A2 is additive only
- S1 and S2 (Tier 6) are Watch Only — do not promote without explicit user confirm and A1/A2 complete
- Tier 7 items are documentation-only this session (drawers already written during Phase 1)
