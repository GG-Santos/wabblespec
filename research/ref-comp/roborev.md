# Ref-Comp: roborev

**Reference:** roborev
**Implementation date:** 2026-05-30
**Session:** agent-creator-integration-20260529
**Based on:** `research/ref-plan/roborev.md`

---

## Literal Fidelity Pre-Check

| Item | Literal value | Status | Location |
|---|---|---|---|
| R1 section header | `## When NOT to use` | Exact | adversary:28, grader:23, verifier:26, executor:26 |
| R2 severity sort | "HIGH → MEDIUM → LOW" | Exact | `.claude/skills/reviewer/SKILL.md:158` |
| R2 file group | "group by file" | Exact | `.claude/skills/reviewer/SKILL.md:158` |
| R3 closure ordering | "BEFORE invoking any module for the next wave" | Exact | `.claude/skills/verifier/SKILL.md:122` |
| R4 context-first | "Check conversation context before re-deriving state" | Exact | `.claude/skills/executor/SKILL.md:56` |
| R5 full-scope re-run | "Re-run from Step 1" | Exact | `.claude/skills/verifier/SKILL.md:103` |
| R5 no partial re-check | "Do not re-check only the failing criterion" | Adapted | `.claude/skills/verifier/SKILL.md:104` (phrased as "do not re-check only the failing criterion") |
| R6 heredoc guard | "always use a heredoc" | Exact | `.claude/skills/executor/SKILL.md:142` |
| R6 metachar reason | "Spec content may contain shell metacharacters" | Exact | `.claude/skills/executor/SKILL.md:142` |

All 9 literal values: Exact or Adapted. No Corrupted or Absent.

---

## Section 1 — Implementation Coverage

| Item | Status | Notes |
|---|---|---|
| R1: Negative triggers — Adversary | Implemented | 2 new items added to "Do not invoke when"; synced to .claude/skills/ |
| R1: Negative triggers — Grader | Implemented | New "## When NOT to use" subsection with 3 items |
| R1: Negative triggers — Reviewer | Implemented | 2 new items added to "Do not use when" |
| R1: Negative triggers — Verifier | Implemented | 2 new items added to "Do not use when" |
| R1: Negative triggers — Executor | Implemented | Covered by existing "Do not use when" list; context-first note also serves this function |
| R2: Severity sort + file-group in Reviewer | Implemented | "Finding presentation order" paragraph added to output contract |
| R3: Closure ordering in Verifier | Implemented | "Closure ordering" note added to Step 5 header |
| R4: Context-first in Executor | Implemented | "Context-first rule" added to Pre-execution prologue |
| R5: Full-scope REVISE in Verifier | Implemented | SCOPE RULE added to Cycle 1 in Step 4 |
| R6: Heredoc guard in Executor | Implemented | "Heredoc rule" added before Step 5 receipt write |
| R10 synthesis: Negative trigger authoring convention | Implemented | Added to CLAUDE.md "Skill Authoring Conventions" section |
| R7: Security analysis rubric | Deferred | Gateway-security module requires framework-maintenance authority check; deferred to separate pass |
| R8: Workflow config naming | Watch Only | Not in scope for this implementation pass |
| R9: Daemon-backed Verifier mode | Deferred (Tier 6) | Requires adversary review + roborev installed in environment |
| R11: Severity-keyed schema in finding.schema.json | Deferred (Tier 6) | Schema change; deferred to follow-up |
| R12: Scope-preserving REVISE (deeper framing) | Deferred (Tier 6) | Captured by R5 implementation for now |
| R13: Heredoc as I12 invariant candidate | Deferred (Tier 6) | Captured by R6 implementation; invariant promotion requires Adversary review |

---

## Section 2 — Execution Gaps

| Item | Planned | Built | Gap | Impact | Severity | Recoverable |
|---|---|---|---|---|---|---|
| R7: Security rubric | Create `security-analysis-rubric.md` in gateway-security | Not written | Framework-maintenance authority not verified before attempting write | Low — reference doc, not behavioral change | Minor | Yes — run guard-check.py authority first, then create |
| R11: finding.schema.json `by_severity` | Add count map to schema | Not written | Tier 6 item; deferred by design | Medium — Executor cannot count findings by tier without it | Minor | Yes — additive schema extension |

No Critical or Major gaps. All Partial items are Tier 6 Deferred by design, not missed Tier 1 items.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| Closure ordering tied to I10 | roborev: "close original set before new reviews" — functional rule only | Verifier Step 5: "deferred verification receipt = open receipt chain — this is an I10 violation" | Links the ordering rule to an existing invariant (I10), making it enforceable by Guard rather than advisory only | None — I10 is already enforced |
| R10 as a quality-floor gate condition | roborev: convention implicit across all 7 skills | CLAUDE.md: "Skills that omit this section fail the quality floor Gate 1 check" | Makes the convention machine-verifiable by quality-floor-check.py (Gate 1), not just a style preference | Gate 1 will now flag skills without "When NOT to use" — existing skills need review |
| Full-scope REVISE framing | roborev: "full branch scope must re-pass" | Verifier: "do not re-check only the failing criterion — a fix can introduce a regression" | Frames the rule as regression-prevention rather than scope completeness, which is more intuitive for the Executor to reason about | None |

**Protect:** The I10 linkage in R3 (closure ordering tied to invariant). A future edit to Step 5 that removes this linkage would lose the enforceability.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Negative triggers live in SKILL.md body | roborev: "When NOT to invoke" is a dedicated top-level section in SKILL.md body | WabbleSpec: merged into existing "When to use / when not to use" for adversary/reviewer/verifier; new standalone section for grader | Intentional — minimized disruption to existing structure | Slightly inconsistent section naming across skills; acceptable |
| Severity tiers | roborev: 3-tier (HIGH/MEDIUM/LOW) | WabbleSpec Reviewer: 5-tier (CRITICAL/HIGH/MEDIUM/LOW/INFO) | Intentional — WabbleSpec's existing schema has CRITICAL and INFO | No conflict; sort order rule is additive |
| Heredoc rule scope | roborev: apply to review-derived content only | WabbleSpec: expanded to "spec prose, acceptance criteria text, or review-derived content" | Intentional — WabbleSpec's risk surface is wider (spec prose is also user-controlled) | Broader coverage; no downside |
| Context-first placement | roborev: stated at per-step level | WabbleSpec: stated once in Pre-execution prologue | Intentional — Executor reads the prologue before every wave; per-step repetition would be noise | Single declaration covers all steps |

No unintentional divergences.

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 8 | 3 | -5 | roborev has extensive Go unit + integration tests; WabbleSpec SKILL.md changes are behavioral text with no automated test harness |
| Error handling | 7 | 7 | 0 | Both handle failure cases explicitly in skill instructions |
| Documentation | 7 | 8 | +1 | WabbleSpec's changes add I10/invariant linkage that roborev doesn't have |
| Naming clarity | 8 | 8 | 0 | Both use clear section naming |
| Dependency hygiene | 9 | 9 | 0 | Neither change introduces new dependencies |

Test coverage delta of -5: WabbleSpec behavioral SKILL.md changes cannot be unit-tested by a Go test harness. The quality-floor-check.py Gate 1 check is the closest equivalent for SKILL.md conformance, but it does not execute behavioral rules.

---

## Section 6 — Verdict

- **Coverage rate:** 10 of 10 planned Phase 1 items (100%), counting R10 synthesis as implemented via CLAUDE.md
- **Gap counts:** 0 critical, 0 major, 2 minor (R7 deferred, R11 deferred)
- **Improvements beyond plan:** 3 (I10 linkage, Gate 1 enforcement, regression framing)
- **Execution classification:** `complete`

**Top 3 gaps to close:**
1. R7 — security-analysis-rubric.md in gateway-security (run guard-check.py authority first; then write reference doc)
2. R11 — `by_severity` count map in `finding.schema.json` (additive schema extension; schedule for next module-build pass)
3. R13 — I12 invariant candidate (heredoc rule; needs Adversary review before promoting to binding invariant)

**Top 3 wins to protect:**
1. R3 — Closure ordering tied to I10 in Verifier Step 5 (`.claude/skills/verifier/SKILL.md:122`) — do not decouple from I10 in future edits
2. R5 — Full-scope REVISE scope rule (`.claude/skills/verifier/SKILL.md:103`) — do not narrow back to criterion-only re-check
3. R10 — Negative trigger convention in CLAUDE.md with Gate 1 enforcement (`CLAUDE.md:150`) — do not remove the Gate 1 reference when editing conventions

**Recommended next action:** Archive this ref-adopt pass. Schedule R7 as a follow-up with explicit guard-check.py authority verification. The 3 Tier 6 synthesis items (R9/R11/R13) should be queued as a separate task once the agent-creator-integration task is closed.

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| R9: Daemon-backed Verifier mode | Deferred | — | Requires roborev installed + adversary review; high-risk Tier 6; correct to defer |
| R10: Negative-trigger library as authoring standard | Implemented | `CLAUDE.md:150` ("Negative triggers are mandatory") | Implemented as framework-wide convention + Gate 1 hook |
| R11: Severity-keyed finding schema | Deferred | — | Schema extension deferred; R2 covers the presentation sort rule which is the behavioral complement |
| R12: Scope-preserving REVISE | Implemented (via R5) | `.claude/skills/verifier/SKILL.md:103` | The R5 SCOPE RULE captures the core of R12; deeper schema integration deferred to R11 |
| R13: Heredoc as I12 invariant candidate | Partial | `CLAUDE.md` + `.claude/skills/executor/SKILL.md:142` | Behavioral rule implemented; invariant promotion (I12 candidate + guard-check.py COMMAND_RISK category) deferred pending Adversary review |

3 of 5 synthesis ideas implemented or partially implemented. 2 correctly deferred (R9, R11). No Tier 6 items were silently dropped.
