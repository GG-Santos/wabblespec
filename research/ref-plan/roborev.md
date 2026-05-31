# Ref-Plan: roborev

**Reference:** roborev
**Based on:** `research/ref-eval/roborev.md`
**Planned:** 2026-05-30
**Session:** agent-creator-integration-20260529

---

## Integration Signal

From ref-eval Section 2 (HIGH/MEDIUM impact) and Section 6 (Phases 1–2):

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| R1 | Negative trigger clauses per skill | Behavioral | HIGH | HIGH | LOW |
| R2 | Severity sort + file-group ordering | Behavioral | HIGH | HIGH | LOW |
| R3 | Closure ordering mandate | Behavioral | HIGH | HIGH | LOW |
| R4 | Context-first + skip-if-satisfied | Behavioral | MEDIUM | HIGH | LOW |
| R5 | Full-scope re-review after REVISE | Behavioral | MEDIUM | HIGH | LOW |
| R6 | Heredoc injection guard | Behavioral | MEDIUM | HIGH | LOW |
| R7 | Security analysis rubric (6 areas) | Format | MEDIUM | MEDIUM | LOW |
| R8 | Workflow config naming pattern | Format | LOW | LOW | LOW |
| R9 | Daemon-backed Verifier mode (synthesis) | Synthesis | — | HIGH | HIGH |
| R10 | Negative-trigger library synthesis | Synthesis | — | HIGH | MEDIUM |
| R11 | Severity-keyed finding schema synthesis | Synthesis | — | HIGH | LOW |
| R12 | Scope-preserving REVISE synthesis | Synthesis | — | HIGH | LOW |
| R13 | Heredoc as framework invariant (synthesis) | Synthesis | — | MEDIUM | MEDIUM |

---

## Exclusion Filter

**Hard excluded:**
- Agent vendor names from fallback cascade → I6 violation (ref-eval Section 4 "Avoid")
- Mandatory push mandate (CLAUDE.md:213-232) → conflicts with WabbleSpec no-push convention
- Phase-free session completion → conflicts with I1 spec-gating
- roborev CLI commands embedded in skills → creates roborev dependency in WabbleSpec
- Go implementation patterns (SQLite, goroutines) → not portable

**R8 (workflow config naming):** Interesting but orthogonal to current task focus (agent-creator integration). Downgraded to Watch Only.

---

## Scoring and Ranking

`integration_score = (impact × 2) + project_fit - risk` (High=3, Medium=2, Low=1)

| ID | Impact | Project fit | Risk | Score | Tier |
|---|---|---|---|---|---|
| R1 | 3 | 3 | 1 | 8 | Tier 1 |
| R2 | 3 | 3 | 1 | 8 | Tier 1 |
| R3 | 3 | 3 | 1 | 8 | Tier 1 |
| R4 | 2 | 3 | 1 | 6 | Tier 1 |
| R5 | 2 | 3 | 1 | 6 | Tier 1 |
| R6 | 2 | 3 | 1 | 6 | Tier 1 |
| R7 | 2 | 2 | 1 | 5 | Tier 2 |
| R11 | — | 3 | 1 | — | Tier 6 |
| R12 | — | 3 | 1 | — | Tier 6 |
| R10 | — | 3 | 2 | — | Tier 6 |
| R13 | — | 2 | 2 | — | Tier 6 |
| R9 | — | 3 | 3 | — | Tier 6 |
| R8 | 1 | 1 | 1 | 2 | Watch Only |

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive to existing files)

**R1: Negative trigger clauses per skill**
- What: Add explicit "When NOT to use" section to each review-type SKILL.md
- Reference location: `internal/skills/claude/roborev-fix/SKILL.md:17-29`, `roborev-refine/SKILL.md:36-42`, `roborev-review/SKILL.md:13-19`
- Target: `.claude/skills/reviewer/SKILL.md`, `.claude/skills/verifier/SKILL.md`, `.claude/skills/code-review/SKILL.md`, `.claude/skills/adversary/SKILL.md`, `.claude/skills/grader/SKILL.md`
- How: After the `description:` frontmatter block, add a `## When NOT to use` section listing at least 2 counterexamples (pasted findings = not a trigger; already-reviewed artifact = not a trigger)
- Gate: Each targeted SKILL.md has a "When NOT to use" section with ≥2 negative examples; grep for "When NOT to use" returns ≥5 matches across `.claude/skills/`
- Literal values: Section header must be exactly `## When NOT to use`

**R2: Severity sort + file-group ordering**
- What: Add explicit fix-ordering rule to Reviewer SKILL.md finding output contract
- Reference location: `internal/skills/claude/roborev-fix/SKILL.md:113-119`
- Target: `.claude/skills/reviewer/SKILL.md` (output contract section)
- How: In the `findings` array description, add: "Order findings HIGH → MEDIUM → LOW. Within each severity tier, group by file to minimize context switches. Multi-file findings at the same severity appear together."
- Gate: Reviewer SKILL.md findings description contains severity sort rule + file-group rule
- Literal values: "HIGH → MEDIUM → LOW", "group by file"

**R3: Closure ordering mandate**
- What: Add closure ordering rule to Verifier SKILL.md inter-wave contract
- Reference location: `internal/skills/claude/roborev-fix/SKILL.md:133-150`
- Target: `.claude/skills/verifier/SKILL.md` (Step 4 REVISE loop, Step 5 receipt write, or a new inter-wave note)
- How: Add a note: "Write the wave receipt and issue the PASS/FAIL signal for the current wave BEFORE invoking any module for the next wave. Do not treat new-wave setup as a prerequisite for closing the current wave's verification record."
- Gate: Verifier SKILL.md contains explicit closure-ordering statement for inter-wave transitions
- Literal values: "BEFORE invoking any module for the next wave"

**R4: Context-first + skip-if-satisfied**
- What: Add context-first protocol note to Executor SKILL.md wave execution header
- Reference location: `internal/skills/claude/roborev-fix/SKILL.md:36-51`, `roborev-refine/SKILL.md:44-46`
- Target: `.claude/skills/executor/SKILL.md` (wave execution preamble)
- How: Add a preamble line: "Check conversation context before re-deriving state. If a prior wave's output or a user message already satisfies a step, skip that step's tool calls."
- Gate: Executor SKILL.md wave execution section contains context-first guidance
- Literal values: "Check conversation context before re-deriving state"

**R5: Full-scope re-verification after REVISE**
- What: Strengthen Verifier REVISE cycle to re-run full wave checks, not only the failing criterion
- Reference location: `internal/skills/claude/roborev-refine/SKILL.md:154-170`
- Target: `.claude/skills/verifier/SKILL.md` (Step 4 REVISE loop, Cycle 1)
- How: In the Cycle 1 description, add: "Re-run from Step 1 (spec compliance check) after each Executor revision. Do not re-check only the failing criterion — a fix may introduce a regression in a passing criterion. The full wave spec-compliance + mode check must re-pass."
- Gate: Verifier SKILL.md REVISE cycle description states full-scope re-run requirement
- Literal values: "Re-run from Step 1", "Do not re-check only the failing criterion"

**R6: Heredoc injection guard**
- What: Add heredoc guidance to Executor SKILL.md for any step that writes spec/receipt-derived content to a shell command
- Reference location: `internal/skills/claude/roborev-refine/SKILL.md:132-147`
- Target: `.claude/skills/executor/SKILL.md` (script delegation section or near receipt-writer calls)
- How: Add: "When passing spec prose, acceptance criteria text, or review-derived content to a shell command, always use a heredoc (not inline string interpolation). Spec content may contain shell metacharacters."
- Gate: Executor SKILL.md contains heredoc guidance for spec-derived shell content
- Literal values: "always use a heredoc", "Spec content may contain shell metacharacters"

### Tier 2 — Module-level augmentation

**R7: Security analysis rubric (6 focus areas)**
- What: Add roborev's security analysis rubric to the gateway-security reference document
- Reference location: `internal/prompt/analyze/security.txt` (full file)
- Target: `.wabblespec/engine/modules/l4/gateway-security/` or an existing reference file under `engine/shared/references/`
- How: Create or augment a `security-analysis-rubric.md` with the 6 focus areas (auth/authz, trust-boundary, injection, file/secret/data, crypto, dependency/config), the confidence threshold rule (only report when pointing to concrete code), and the output format (SECURITY SUMMARY / FINDINGS / NO FINDINGS / FOLLOW-UP CHECKS)
- Specify required: Yes — gateway-security module owns its reference files; check framework-maintenance authority before writing
- Breaking change risk: LOW — additive reference doc
- Gate: Reference doc exists with all 6 focus areas named; output format section present

### Tier 6 — Synthesis items

**R11: Severity-keyed finding schema in Reviewer (synthesis)**
- What: Add `by_severity` count field to Reviewer's `finding_summary` in `finding.schema.json`, plus mandate the HIGH→MEDIUM→LOW sort in the Reviewer output contract
- Reference contribution: roborev's `finding_summary.by_severity: {HIGH, MEDIUM, LOW}` count map in gate receipts
- Project contribution: WabbleSpec Reviewer's `finding.schema.json` already has `severity` as a required field; the schema can be extended without breaking the existing contract
- Target: `engine/modules/l2/reviewer/schemas/finding.schema.json` + `.claude/skills/reviewer/SKILL.md`
- Gap closed: Reviewer currently produces findings but no severity distribution summary; Executor cannot prioritize fixes without counting findings per tier

**R12: Scope-preserving REVISE (synthesis)**
- What: Verifier's REVISE step 1 must re-run ALL wave checks (spec compliance + mode check), not only the failing criterion; and the re-run scope must match the original wave declaration
- Reference contribution: roborev's "explicit full-scope review must pass — not just the post-commit hook review"
- Project contribution: WabbleSpec Verifier's Step 4 REVISE loop structure, which already tracks cycle count and issues BLOCKED at cycle 4
- Target: `.claude/skills/verifier/SKILL.md` (Step 4, Cycle 1 text) — overlaps R5; R12 is the deeper synthesis framing
- Gap closed: A REVISE that passes the originally-failing criterion but silently breaks a previously-passing criterion counts as PASS in the current Verifier; this synthesis prevents silent regression

**R10: Negative-trigger library as authoring standard (synthesis)**
- What: Add "When NOT to use" as a mandatory section in the WabbleSpec skill-authoring conventions (CLAUDE.md authoring section), not just additive to individual SKILL.md files
- Reference contribution: roborev's consistent "When NOT to invoke" pattern across all 7 skill files — it is a system-level convention, not per-skill decoration
- Project contribution: WabbleSpec's `CLAUDE.md` "Skill Authoring Conventions" section — an existing place to declare framework-wide SKILL.md authoring rules
- Target: `CLAUDE.md` "Skill Authoring Conventions" section
- Gap closed: Without it as a convention, newly created skills will omit negative triggers; with it as a mandatory section, all future skill authors include it by default

**R13: Heredoc injection guard as framework invariant candidate (synthesis)**
- What: Propose adding a new invariant (I12 candidate) to the invariants reference: "FRAMEWORK SCRIPTS SHALL NOT INTERPOLATE SPEC OR REVIEW CONTENT DIRECTLY INTO SHELL STRINGS — use heredoc or parameter file passing"
- Reference contribution: roborev's explicit mandate for heredoc use with review-derived content
- Project contribution: WabbleSpec's `invariants.md` invariant registry + `guard-check.py` COMMAND_RISK taxonomy
- Target: `.wabblespec/engine/shared/references/invariants.md` (candidate addition) + `guard-check.py` (new COMMAND_RISK category: `CONTENT_INJECTION`)
- Gap closed: No current invariant covers shell injection from trusted-but-unescaped spec content; guard-check catches external command risk but not content interpolation risk
- Note: Propose as candidate; Adversary review recommended before promoting to binding invariant

**R9: Daemon-backed Verifier mode (synthesis, Tier 5 risk)**
- What: Add a `Daemon` mode to Verifier's Step 2 mode table: "Run `~~review-daemon wait` for HEAD; PASS = daemon review passes; FAIL = daemon findings feed the REVISE loop"
- Reference contribution: roborev daemon's `roborev wait` + continuous post-commit review; the `roborev refine` loop proves the daemon can drive the verify-fix-reverify cycle
- Project contribution: WabbleSpec Verifier's pluggable `verification_mode` table + Executor's wave commit pattern (each completed wave produces artifacts that could be committed)
- Target: `.claude/skills/verifier/SKILL.md` (Step 2 mode table, new `Daemon` row)
- Gap closed: WabbleSpec Executor commits wave output but no module reviews that commit before the next wave begins; a `Daemon` mode would add live external review as a verification gate
- Adversary review required before promoting: YES — this is a cross-cutting change that wires an external daemon into the verification contract
- Promote when: roborev is installed and confirmed running in the WabbleSpec environment

### Watch Only

**R8: Workflow config naming pattern** — interesting naming discipline but orthogonal to current agent-creator integration task; revisit when recipe.json schema documentation is planned.

---

## Do-Not-Copy List

| Item | Reason |
|---|---|
| Agent fallback cascade vendor names | I6: no model/vendor names in framework files |
| "Landing the Plane" push mandate | Contradicts WabbleSpec no-push-unless-asked |
| "Complete ALL steps without stopping" session rule | Contradicts I1 spec-gating |
| roborev CLI commands in adopted skills | Creates undeclared external dependency |
| Go SQLite/goroutine implementation | Not portable to Python/JSON recipe layer |

---

## Priority Implementation Order (Phase 1: Tier 1–2)

| Order | ID | What | Why first |
|---|---|---|---|
| 1 | R1 | Negative triggers in review-type skills | Highest misfire risk; lowest implementation complexity; pure additive |
| 2 | R2 | Severity sort + file-group in Reviewer | Directly complements R1; Reviewer is the module most likely to produce unsorted findings |
| 3 | R5 | Full-scope re-verification in Verifier REVISE | Closes the silent-regression gap before R3 adds more inter-wave contract language |
| 4 | R3 | Closure ordering in Verifier | Depends on REVISE cycle changes being settled first |
| 5 | R4 | Context-first in Executor | Additive note; no dependency on other items |
| 6 | R6 | Heredoc guard in Executor | Additive note; no dependency; lower urgency than behavioral changes |
| 7 | R7 | Security rubric → gateway-security ref | Tier 2; requires framework-maintenance authority check first |

**Execution notes:**
- R1 targets 5 files; all can be edited in parallel (no conflicts)
- R2 and R3 both target Reviewer/Verifier; edit sequentially to avoid conflict on same file
- R7 requires framework-maintenance authority check (`guard-check.py authority`) before any write — do not edit gateway-security files without verifying authority PASS
- Tier 6 items (R9-R13) are Watch Only for this implementation pass; all are Deferred pending adversary review or external tooling availability
