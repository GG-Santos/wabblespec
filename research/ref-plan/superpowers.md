# Ref-Plan: superpowers

**Reference:** superpowers v5.1.0
**Slug:** `superpowers`
**Planned:** 2026-05-30
**Source:** `research/ref-eval/superpowers.md`

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| SP-01 | Spec reviewer skepticism (do not trust executor receipt) | Behavioral | High | High | Low |
| SP-02 | Architectural escalation after 3-REVISE failure pattern | Behavioral | High | High | Low |
| SP-03 | Task complexity → capability input signals | Behavioral | High | High | Low |
| SP-04 | CSO workflow-summary prohibition in description fields | Format | High | High | Low |
| SP-05 | Evidence gate 5-step (IDENTIFY→RUN→READ→VERIFY→CLAIM) | Behavioral | Medium | High | Low |
| SP-06 | Diagnostic instrumentation at component boundaries | Behavioral | Medium | Medium | Low |
| SP-07 | Rationalization tables for guard/executor bypass patterns | Behavioral | Medium | Medium | Low |
| SP-08 | 4-point spec self-review after task card write | Behavioral | Medium | Medium | Low |
| SP-09 | Parallel dispatch independence criteria | Behavioral | Low | Medium | Low |

## Exclusion List

| Item | Reason |
|---|---|
| 1% skill invocation rule | Token overload with 108 WabbleSpec skills; phase-gated explicit invocation already works |
| Iron Law deletion mandate (TDD SKILL.md) | Conflicts with framework module scaffolding; principle is already captured in I10 |
| Hardcoded product-space paths (brainstorming/writing-plans) | I11 violation |
| agentskills.io external URL reference | External dependency; WabbleSpec conventions are self-contained |
| "human partner" terminology | WabbleSpec has its own established terminology |

## Integration Score

`integration_score = (impact × 2) + project_fit - risk`  
Mapping: High=3, Medium=2, Low=1

| ID | Score | Tier |
|---|---|---|
| SP-01 | (3×2)+3-1 = 8 | Tier 1 |
| SP-02 | (3×2)+3-1 = 8 | Tier 1 |
| SP-03 | (3×2)+3-1 = 8 | Tier 1 |
| SP-04 | (3×2)+3-1 = 8 | Tier 1 |
| SP-05 | (2×2)+3-1 = 6 | Tier 2 |
| SP-06 | (2×2)+2-1 = 5 | Tier 2 |
| SP-07 | (2×2)+2-1 = 5 | Tier 2 |
| SP-08 | (2×2)+2-1 = 5 | Tier 2 |
| SP-09 | (1×2)+2-1 = 3 | Tier 3 |

---

## Tier 1 — Behavioral Additions (additive to existing files)

### SP-01: Spec reviewer skepticism → `verifier/SKILL.md`

**What:** Add "do not trust executor receipt" skepticism block before Step 1 spec compliance check.

**Where:** `.claude/skills/verifier/SKILL.md`, before "### Step 1 — Spec compliance check"

**How:** Insert a 4-line block: "Read the actual artifact files. Do not take the wave receipt's claims about what was produced at face value. The receipt describes what was intended; the artifact content is the ground truth. If a receipt claims an artifact exists at path X with content Y, verify both before issuing PASS."

**Reference location:** `skills/subagent-driven-development/spec-reviewer-prompt.md` lines 28-36 ("CRITICAL: Do Not Trust the Report")

**Gate:** Verifier Step 1 text contains "actual artifact" or equivalent independent-read language. No existing text removed.

**Literal values:** Phrases to verify present: "actual artifact", "do not take... at face value", "ground truth".

---

### SP-02: Architectural escalation → `verifier/SKILL.md`

**What:** Add pattern-detection note to the REVISE loop: when cycle 3 fails AND the failure pattern shows each cycle revealed new coupling/shared-state problems (not the same implementation bug), surface ARCHITECTURE_ESCALATION alongside BLOCKED.

**Where:** `.claude/skills/verifier/SKILL.md`, inside "### Step 4 — REVISE loop (if FAIL)", after the "Cycle 3: same process" line, before "Cycle 4+: BLOCKED"

**How:** Insert: "Before emitting BLOCKED at cycle 4: check whether each of the 3 REVISE cycles surfaced a different failure location — new shared state, new coupling, or a symptom moving to a different part of the codebase. If yes: emit `ARCHITECTURE_ESCALATION` in the blocked verdict alongside the BLOCKED signal. This tells Executor the blocking is architectural, not an implementation defect that another retry can resolve."

**Reference location:** `skills/systematic-debugging/SKILL.md` Phase 4.5 "If 3+ Fixes Failed: Question Architecture"

**Gate:** REVISE loop section includes ARCHITECTURE_ESCALATION signal and its trigger condition (each cycle = different failure location).

---

### SP-03: Task complexity signals → `model-router/SKILL.md`

**What:** Add a "Task complexity signals" subsection under step 2 (Classify current task shape) with concrete input-side descriptors for the three tier levels.

**Where:** `.claude/skills/model-router/SKILL.md`, after the "Classify current task shape" line in the "Routing process" section.

**How:** Add:
```
**Task complexity signals:**
- Touches 1-2 files with a complete spec: map to `code-generation` capability (implementation mechanical)
- Touches multiple files with integration concerns or cross-file contracts: map to `synthesis` capability
- Requires design judgment, broad codebase understanding, or architecture decisions: map to `analysis` capability
Use these as a secondary signal when task shape classification is ambiguous.
```

**Reference location:** `skills/subagent-driven-development/SKILL.md` "Model Selection" section, "Task complexity signals" subsection

**Gate:** model-router SKILL.md contains a "Task complexity signals" block with three tiers mapping to capability descriptors (not model names). I6 satisfied.

---

### SP-04: CSO workflow-summary prohibition → `CLAUDE.md`

**What:** Add one bullet to the "Skill Authoring Conventions" section prohibiting workflow-summary descriptions. Include the empirical reason.

**Where:** `CLAUDE.md`, under `## Skill Authoring Conventions`, after the paragraph about `description:` ending with a period.

**How:** Add: "**`description:` must not summarize the skill's workflow.** Empirical testing shows that when a description contains workflow steps, agents follow the description as a shortcut and skip reading the skill body. The description must state only triggering conditions — what the agent is doing that warrants loading this skill — not what the skill will instruct the agent to do."

**Reference location:** `skills/writing-skills/SKILL.md` CSO section, "CRITICAL: Description = When to Use, NOT What the Skill Does", including the study evidence paragraph.

**Gate:** CLAUDE.md skill authoring conventions section contains "must not summarize the skill's workflow" and a rationale referencing the shortcut behavior.

---

## Tier 2 — Module-Level Augmentation

### SP-05: Evidence gate → `executor/SKILL.md`

**What:** Add the 5-step gate function to the executor's final execution receipt step.

**Where:** `.claude/skills/executor/SKILL.md`, before "### Write final execution receipt"

**How:** Add: "Before writing the final execution receipt, run the evidence gate: (1) IDENTIFY — what command or check confirms all waves completed successfully? (2) RUN — execute it fresh (do not rely on per-wave memory). (3) READ — read full output and check exit code. (4) VERIFY — does the output confirm all wave receipts exist and wave_of = waves_planned? (5) CLAIM — only then write execution-receipt.json."

**Reference location:** `skills/verification-before-completion/SKILL.md` "The Gate Function" section

**Gate:** Executor SKILL.md contains 5-step evidence gate before execution-receipt.json write.

---

### SP-06: Diagnostic instrumentation → `wave-fix/SKILL.md`

**What:** Add a diagnostic step before fix attempts: instrument component boundaries to find WHERE the issue is before attempting to fix it.

**Where:** `.claude/skills/wave-fix/SKILL.md`, before "### 2. Prioritize and fix"

**How:** Add "### 1b. Instrument before fixing (for non-obvious failures)" with guidance: "For failures where the root location is unclear, add diagnostic output at each component boundary before writing any fix: log what each component receives and emits. Run once to gather evidence. Only then isolate the failing component and fix it."

**Reference location:** `skills/systematic-debugging/SKILL.md` Phase 1 "Gather Evidence in Multi-Component Systems"

**Gate:** wave-fix SKILL.md contains a diagnostic instrumentation step before fix attempts.

---

### SP-07: Rationalization tables → `executor/SKILL.md`

**What:** Add "Common bypass rationalizations" note to executor's common failure modes section.

**Where:** `.claude/skills/executor/SKILL.md`, at the end of "## A note on common failure modes"

**How:** Add a 5th failure mode: "**Rationalizing checkpoint/Guard skips.** Common bypass thoughts: 'This wave is simple, Guard would pass anyway.' / 'The checkpoint is slow to write; I'll write it after.' / 'Context is getting long; I'll skip the state.json update.' None of these are acceptable. Guard and checkpoint are the rollback and invariant system. Bypassing them does not speed up execution — it creates unrecoverable state."

**Reference location:** `skills/test-driven-development/SKILL.md` "Common Rationalizations" table and `skills/systematic-debugging/SKILL.md` "Common Rationalizations"

**Gate:** Executor failure modes section includes rationalization examples for Guard/checkpoint bypass.

---

### SP-08: Spec self-review → `specify/SKILL.md`

**What:** Add a 4-point inline self-review after Step 4 (write task card).

**Where:** `.claude/skills/specify/SKILL.md`, after the step that writes the task card, before writing the specify receipt.

**How:** Add a step: "**Self-review before receipt:** (1) Placeholder scan — any 'TBD', vague 'handle edge cases', or incomplete criteria? Fix them. (2) Consistency check — do GWT 'Given' preconditions match 'Then' artifact paths? (3) Scope check — is each criterion directly traceable to scope.md 'In Scope' items? (4) Ambiguity check — could any criterion be interpreted two ways? Pick one and make it explicit. Fix inline; do not re-run."

**Reference location:** `skills/brainstorming/SKILL.md` "Spec Self-Review" section

**Gate:** Specify SKILL.md contains a 4-item self-review with placeholder/consistency/scope/ambiguity checks.

---

## Tier 3 — New Shared Infrastructure

### SP-09: Wave independence criteria → `decompose/SKILL.md`

**What:** Add "Wave independence criteria" to decompose wave design section.

**Where:** `.claude/skills/decompose/SKILL.md` (read file to determine exact insertion point at implementation time)

**How:** Add criteria table from dispatching-parallel-agents "When NOT to Use": parallel topology NOT warranted when failures are related, when full system context is needed, or when waves would touch shared state. Each independence check should appear before declaring a wave parallelizable.

**Reference location:** `skills/dispatching-parallel-agents/SKILL.md` "When NOT to Use" section

**Gate:** Decompose SKILL.md contains wave independence criteria with "when NOT to parallelize" conditions.

---

## Tier 6 — Synthesis

### SYN-01: Receipt-gated spec compliance

**What:** The combination of superpowers' skeptical independent verification (SP-01) with WabbleSpec's receipt integrity chain creates a two-level fidelity gate: (1) receipt exists AND (2) artifact content matches what receipt claims. Neither alone is sufficient.

**Reference contribution:** spec-reviewer-prompt.md skepticism block — read actual code, not the report.

**Project contribution:** I10 receipt chain — every wave output must have a receipt before the next wave starts.

**Target:** `verifier/SKILL.md` Step 1 (already the implementation target of SP-01)

**Gap closed:** Receipt existence is verified by Guard/Executor. Artifact content matching the receipt claims is not currently enforced. The skepticism block closes this.

---

### SYN-02: Escalation receipt type

**What:** Combining the architectural escalation signal (SP-02) with WabbleSpec's 17-type receipt system would create an `ARCHITECTURE_ESCALATION` receipt type — a durable audit trail when executor hits architecture limits, distinct from a plain BLOCKED.

**Reference contribution:** 3-fix escalation pattern with explicit signal.

**Project contribution:** `receipt-writer.py` with 17 named types; `execution-receipt.json` with `errors_by_type` map.

**Target:** `executor/SKILL.md` execution-receipt schema + `receipt-writer.py`

**Gap closed:** Current `errors_by_type` maps error classes but has no way to distinguish architectural blocking from implementation blocking. An `ARCHITECTURE_ESCALATION` key would make this distinction explicit.

---

### SYN-03: Task complexity → capability input signal

**What:** Superpowers' concrete complexity tier descriptions (SP-03) are the missing input-signal side of WabbleSpec's model-router, which has sophisticated capability matching but no structural-complexity → capability mapping.

**Reference contribution:** 1-2 files / multi-file / design-judgment tier criteria.

**Project contribution:** Capability descriptors (`code-generation`, `synthesis`, `analysis`) already in model-router.

**Target:** `model-router/SKILL.md` — already Tier 1 item SP-03.

---

## Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| Skill authoring TDD test harness | `writing-skills/SKILL.md` RED-GREEN-REFACTOR for skills; testing methodology | WabbleSpec has Benchmark module but no dedicated pressure-test-subagent workflow for new skill validation | Self-testing new skills before deployment; empirically closing rationalization loopholes; consistent quality across skill additions | Subagent infrastructure (present), Benchmark fixtures, pressure scenario templates | days | Specify a `skill-tdd` module: given a candidate SKILL.md and 3 pressure scenarios, dispatch subagent without skill (baseline), then with skill, verify compliance delta |
| Visual companion for brainstorming | `skills/brainstorming/visual-companion.md`, `scripts/server.cjs` | WabbleSpec brainstorm skill has no browser companion; no HTTP server component | Real-time diagram and mockup display during spec conversations; visual option comparison | Node.js, browser environment | weeks | Build a zero-dependency brainstorm server serving graphviz diagrams and ASCII mockups via localhost; wire into brainstorm SKILL.md as opt-in step |

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| 1% skill invocation rule | Context overload with 108 skills; phase-gated explicit invocation |
| "human partner" terminology | WabbleSpec uses its own established module/receipt vocabulary |
| Iron Law deletion mandate | I10 / framework scaffolding conflict |
| agentskills.io URL | External dependency; CLAUDE.md is self-contained authority |
| Model tier names ("cheap/standard/capable") | I6 — capability descriptors only, not relative model tier labels |

---

## Priority Implementation Order

| Order | ID | Item | Target file | Why first |
|---|---|---|---|---|
| 1 | SP-01 | Spec reviewer skepticism | `verifier/SKILL.md` | Highest impact; closes active verification gap |
| 2 | SP-02 | Architectural escalation | `verifier/SKILL.md` | Same file; same step; natural companion to SP-01 |
| 3 | SP-03 | Task complexity signals | `model-router/SKILL.md` | Self-contained; no dependencies on prior items |
| 4 | SP-04 | CSO prohibition | `CLAUDE.md` | Framework-wide quality; affects all 108 skills |
| 5 | SP-05 | Evidence gate | `executor/SKILL.md` | Depends on understanding SP-01/02 intent first |
| 6 | SP-06 | Diagnostic instrumentation | `wave-fix/SKILL.md` | Depends on understanding SP-05 evidence gate |
| 7 | SP-07 | Rationalization tables | `executor/SKILL.md` | Extends SP-05 edits to same file |
| 8 | SP-08 | Spec self-review | `specify/SKILL.md` | Independent; lower priority |
| 9 | SP-09 | Wave independence criteria | `decompose/SKILL.md` | Lowest priority; useful for decompose quality |

## Execution Notes

- Items SP-01 and SP-02 both target `verifier/SKILL.md` — implement in the same edit pass.
- Items SP-05 and SP-07 both target `executor/SKILL.md` — implement in the same edit pass.
- SP-04 targets `CLAUDE.md` which is a global file; no other items touch it.
- SP-09 requires reading `decompose/SKILL.md` first to find exact insertion point — defer until reading confirms location.
- No items have ordering dependencies on each other except: SP-05 before SP-07 (both in executor, natural ordering).
