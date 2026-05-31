# Ref-Eval: roborev

**Reference:** `C:\Users\Kirsten\Downloads\Orchestrator\roborev-main`
**Slug:** `roborev`
**Evaluated:** 2026-05-30
**Trust level:** MEDIUM (production tool, real users, CI/tests, MIT license — vendor names throughout violate I6 if copied directly)

---

## File Inventory

| File / Path | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| `CLAUDE.md` | Project instructions + architecture reference for agents | 19.9 KB | Full arch diagram, package map, API table, worker lifecycle, config system, DB schema, test conventions | Read |
| `AGENTS.md` | Agent-facing navigation guide | 15.1 KB | Package map, command map, follow-the-flow paths, change-impact guide | Read |
| `.roborev.toml` | Canonical project review guidelines | 5.1 KB | Trust model, agent tool permissions, verdict parsing contract, security scope | Read |
| `README.md` | User-facing product overview | 11.2 KB | Feature list, command table, config guide, supported agents | Read |
| `skills/roborev-fix.md` | Human-readable fix skill doc | 1.8 KB | Discovery → fix → comment → close steps | Read |
| `skills/roborev-design-review.md` | Human-readable design review doc | 1.8 KB | PRD + task list review criteria | Read |
| `skills/roborev-respond.md` | Human-readable respond doc | 1.3 KB | Comment + close pattern | Read |
| `internal/skills/claude/roborev-fix/SKILL.md` | Machine-embedded fix skill | 8.8 KB | 7-step fix protocol, closure ordering mandate, heredoc injection guard | Read |
| `internal/skills/claude/roborev-refine/SKILL.md` | Machine-embedded refine skill | 8.5 KB | Iterative review-fix loop, full-scope re-review mandate, iteration cap | Read |
| `internal/skills/claude/roborev-review/SKILL.md` | Machine-embedded review skill | 4.0 KB | Background task launch, result presentation, next-step offers | Read |
| `internal/skills/claude/roborev-review-branch/SKILL.md` | Machine-embedded branch review | 4.2 KB | Branch review scope, background task pattern | Read |
| `internal/skills/claude/roborev-design-review/SKILL.md` | Machine-embedded design review | 4.0 KB | Design-type review, verdict presentation | Read |
| `internal/skills/claude/roborev-design-review-branch/SKILL.md` | Machine-embedded design branch review | 4.2 KB | Branch-scoped design review | Read |
| `internal/skills/claude/roborev-respond/SKILL.md` | Machine-embedded respond skill | 2.4 KB | Comment + close with explicit verification | Read |
| `internal/prompt/analyze/security.txt` | Security analysis prompt | 2.6 KB | 6-focus-area security rubric, output contract with FINDINGS/NO FINDINGS | Read |
| `internal/prompt/analyze/` (7 other types) | Analysis prompt templates | ~800 B each | Named analysis categories with structured output | Summary |
| `cmd/roborev/` (25+ files) | CLI entry point, Cobra commands | varies | review.go, fix.go, refine.go, analyze.go, ci.go | Summary |
| `internal/daemon/` | HTTP server, worker pool, CI poller | varies | server.go (~2000 lines), worker.go, ci_poller.go | Summary |
| `internal/storage/` | SQLite + PostgreSQL, migrations | varies | db.go (18 migrations), models.go, jobs.go | Summary |
| `internal/agent/agent.go` | Agent interface + registry | varies | Agent interface, fallback cascade, availability lookup | Summary |
| `internal/skills/skills.go` | Skill embedding + installer | 10.8 KB | Go embed, skill discovery, install logic | Summary |
| Go source files (all others) | Implementation | varies | Not read — behavioral patterns captured via CLAUDE.md + AGENTS.md | Skipped |

---

## Connection Map

```
CLI (cmd/roborev/) --[HTTP POST /api/enqueue]--> Daemon server.go
                                                    |
                              --[claim]--> Worker pool (worker.go)
                                                    |
                              --[resolve]--> Config hierarchy (config.go)
                                                    |
                              --[build]--> Prompt builder (prompt.go)
                                                    |
                              --[invoke]--> Agent.Review() interface
                                                    |
                              --[store]--> Storage (jobs.go, db.go)
                                                    |
                              --[broadcast]--> SSE stream → TUI (tui/)
                                                    |
                              --[fire]--> Hooks + CI poller

Skills (internal/skills/claude/**) --[Go embed]--> skills.go --[install]--> ~/.claude/skills/
Skills --[trigger]--> Agent (Claude Code) --[invokes roborev CLI commands]

Config hierarchy: CLI flags → repo .roborev.toml → global config.toml → defaults
  lookupFieldByTag() resolves {Workflow}{Setting}{Level} patterns via reflection

Job state machine: queued → running → done | failed | canceled | applied | rebased
  Retry: up to 3 × db.RetryJob → db.FailoverJob (backup agent)
  Cooldown: quota errors trigger per-agent cooldown (default 30 min)

Worktree: worker.go --[create]--> worktree.Create() → patch captured → stored in DB
         TUI user confirm --[apply]--> worktree.ApplyPatch() → working tree
```

**What breaks if a contract changes:**
- If `Agent.Review()` signature changes → all 10 agent adapters break
- If job JSON shape changes (`job.verdict`, `closed`, `comments`) → all skills misparse output
- If `roborev show --job <id> --json` output shape changes → roborev-fix/refine steps 1-2 misparse
- If `roborev fix --open --list` line format changes → step 1 discovery breaks

---

## Dimensional Extraction

### Dimension 1 — Behavior (operational detail)

**Worker lifecycle (10 steps, exact):**
1. `db.ClaimJob(workerID)` — atomic status=running set
2. Register for cancellation tracking
3. Check agent cooldown (quota exhaustion)
4. Build prompt via `prompt.Builder` or use stored prompt (task/compact/fix)
5. Get agent via `agent.GetAvailableWithConfig()`, apply reasoning/model/agentic settings
6. For fix jobs: create isolated worktree via `worktree.Create()`
7. Invoke `Agent.Review()` with streaming output capture
8. For fix jobs: capture patch via `worktree.CapturePatch()`
9. Store result via `db.CompleteJob()` or `db.CompleteFixJob()`
10. Broadcast `review.completed` event, fire hooks

**Retry/failover thresholds:**
- Up to **3 retries** (`db.RetryJob`) for transient failures
- After retries exhausted OR on quota errors: `db.FailoverJob` → backup agent
- Cooldown default: **30 min** (parsed from error message)
- `LimitKindQuota` triggers cooldown; `LimitKindSession` same path but no production rule emits it yet

**Agent fallback cascade (priority order):**
codex → claude-code → gemini → copilot → opencode → cursor → kiro → kilo → droid → pi
- Discovered via PATH lookup; `test` agent always available
- `"claude"` → `"claude-code"` alias; `"agent"` → `"cursor"` alias

**Reasoning levels (exact names):**
- `ReasoningFast` ("fast"/"low"), `ReasoningStandard` ("standard"/"medium"), `ReasoningThorough` ("thorough"/"high")
- Reasoning defaults: review = `thorough`, fix = `standard`, refine = `standard`

**Verdict parsing contract (explicit, from .roborev.toml):**
- "Prefer explicit structured signals such as severity labels, findings sections, and clear pass phrases"
- "Do not ask for elaborate natural-language contradiction parsing of free-form prose after 'No issues found.'"
- If review output too chatty → fix the prompts, not the parser

**Fix ordering rules (mandatory):**
1. Sort by severity: HIGH → MEDIUM → LOW
2. Group by file within each severity level (minimize context switches)
3. Batch edits to same file across multiple reviews together

**Closure ordering mandate (load-bearing):**
> "Close original reviews BEFORE waiting on, fetching, or responding to any new review created by commit hooks."
> "Do not treat a post-fix auto-review as a prerequisite for closing the original addressed reviews."
- If policy requires committing before close can reference a SHA: commit first, then close original set immediately
- 7-step audit: verify `closed=true` on each original job ID before final response

**Refine scope rule:**
- Re-review must use FULL branch scope (same `--branch` or `--since`) after each fix
- A passing `roborev wait` result for the new commit is NOT sufficient to stop
- The explicit full-scope review must pass before reporting success

**Skill trigger/not-trigger separation (explicit per skill):**
- roborev-fix: "Do NOT invoke just because the user pasted existing review findings"
- roborev-refine: "Do NOT invoke when presenting or pasting existing review results"
- roborev-review: "Do NOT invoke when the user is presenting or pasting existing review results"
- Each skill has a "When NOT to invoke" section with specific counterexamples

**Context-first rule:**
> "Check the conversation first. If the user has already pasted review findings, use those directly. Do not re-fetch reviews that are already present."

**Skip-if-satisfied rule:**
> "These instructions are guidelines, not a rigid script. Skip steps already satisfied by conversation context."

**Heredoc injection guard:**
> "Always pass the comment text via a heredoc as shown above, never by interpolating dynamic text directly into a shell string. Review-derived content may contain shell metacharacters."

**Background daemon safety rule:**
- Background daemon work MUST NOT edit tracked source files in the checked-out working tree
- Foreground agentic flows (fix, refine) MAY modify code
- Worktree patches stored in DB; applied only on explicit user confirmation in TUI

**Trust model (local-only):**
- Daemon binds to 127.0.0.1; SQLite local; data from operator's own filesystem
- NOT security findings: missing auth on daemon endpoints, data from endpoints, prompt injection from hook stderr (locally generated), .githooks/ as supply-chain risk, argument injection on internal helpers receiving already-validated SHAs

**Analysis types (8 named, exact):**
`test-fixtures`, `duplication`, `refactor`, `complexity`, `api-design`, `dead-code`, `architecture`, `security`

**Security prompt output format (exact):**
- `SECURITY SUMMARY:` brief risk overview + most important trust boundaries reviewed
- `FINDINGS:` file path + narrowest location, severity (critical/high/medium/low), Confidence (high/medium/low), Evidence (exact code path), trust boundary, Exploitability, suggested fix
- `NO FINDINGS:` explicit statement "No security findings with concrete evidence."
- `FOLLOW-UP CHECKS:` optional manual checks not confirmable from provided files

### Dimension 2 — Format (identifier level)

**Skill frontmatter (roborev):**
```yaml
---
name: roborev-fix
description: Use when...do not use when...
---
```

**SKILL.md section order (roborev):**
1. Skill name heading
2. Brief description
3. Usage code block
4. "When NOT to invoke this skill" section (explicit)
5. IMPORTANT block (execution mode declaration)
6. Instructions (numbered steps, lettered sub-steps)
7. Examples (with exact command sequences)
8. "See also" cross-references

**Job JSON schema (exact fields):**
```
job_id, output (review text), job.verdict ("P"/"F"/""), job.git_ref,
closed (bool), comments[].responder, comments[].response
```

**Finding format (roborev):** `SEVERITY: description [file:line]`
- 3-tier severity: HIGH, MEDIUM, LOW (not 4 or 5 tier)
- Grouped by severity in presentation, then by file within severity

**Config field naming convention:**
- Pattern: `{Workflow}{Setting}{Level}`
- Workflows: Review, Refine, Fix, Security, Design
- Settings: Agent, Model, BackupAgent, BackupModel
- Levels (agent/model only): Fast, Standard, Thorough
- TOML tags: `review_agent_fast`, `fix_model_thorough`, `security_backup_agent`

**Commenter field in close commands:**
`roborev comment --commenter roborev-fix --job <id> "..."`
`roborev comment --commenter roborev-refine --job <id> -m "$(cat <<'HEREDOC'...HEREDOC)"`

### Dimension 3 — Interactions (contract level)

**Agent.Review() contract:**
- Producer: worker.go
- Consumer: any agent adapter (claude.go, codex.go, etc.)
- Shape: `(ctx context.Context, repoPath, commitSHA, prompt string, output io.Writer) (string, error)`
- Break condition: any adapter not implementing all 4 interface methods

**Skills → Agent contract:**
- Skills embedded in binary via `//go:embed` in `skills.go`
- Install path: `~/.claude/skills/<name>/SKILL.md` for Claude Code
- Skills trigger via Claude Code's skill loader on slash command
- Skills call roborev CLI; they do not call the HTTP API directly

**Skill → daemon contract:**
- Skills invoke `roborev show --job <id> --json`; expect `job_id, output, job.verdict, closed, comments` at top level
- Skills invoke `roborev fix --open --list`; expect one line per job with ID, SHA, agent, summary
- If daemon not running: these commands fail; skill must report error + suggest `roborev status`

**Config resolution sequencing:**
- `lookupFieldByTag()` resolves fields via TOML struct reflection
- Resolution order is enforced per-call, not cached globally
- CLI flags always win: skills cannot override what the user passes at CLI

**Worktree isolation contract:**
- Worker creates worktree in temp dir; daemon writes patch to DB
- Working tree untouched until `job/applied` POST from TUI
- `worktree.CheckPatch()` dry-run before apply; returns `PatchConflictError` on conflicts

---

## Section 1 — Reference Summary

**Type:** Production Go CLI tool / daemon — real usage, CI, tests, versioned releases, MIT license.

**Problem it solves:** Continuous AI code review integrated into the git commit workflow. Every commit triggers background parallel reviews by AI agents. Results surface in a TUI; findings can be auto-fixed by an iterative review-fix loop.

**Behavioral content:**
- 10-step worker lifecycle with retry, failover, and cooldown
- 7-step fix protocol with closure ordering mandate and audit verification
- Iterative refine loop with full-scope re-review (not commit-level)
- Explicit skill trigger/not-trigger separation
- Context-first, skip-if-satisfied execution model
- Heredoc injection prevention for shell-derived content
- 8 named analysis types with structured output contracts

**Structural content:**
- Skill SKILL.md format with mandatory "When NOT to invoke" section
- Config naming: `{Workflow}{Setting}{Level}` pattern
- Job JSON schema: `job_id`, `output`, `job.verdict`, `job.git_ref`, `closed`, `comments[]`
- Finding format: 3-tier severity (HIGH/MEDIUM/LOW), grouped by severity then by file

**Interaction content:**
- Thin CLI → HTTP API → Daemon architecture
- Skills embedded in binary, installed to agent's skill directory
- Worker → Agent.Review() interface with well-defined contract
- Worktree isolation: patches in DB, applied only on user confirmation

**Maturity:** Active production tool. CI present. Tests extensive (unit + integration + postgres tags). Real user base. Versioned releases on GitHub.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `roborev-fix/SKILL.md:17-29` | "When NOT to invoke" negative trigger clauses per skill | WabbleSpec skills fire on pasted findings, triggering unnecessary re-runs; explicit negative triggers prevent misfire | Add `## When NOT to use` section to each WabbleSpec SKILL.md with at least one negative example | HIGH |
| `roborev-fix/SKILL.md:113-119` | Severity sort + file-group ordering for findings | Executor currently has no mandated ordering for multi-finding fixes; grouping by file reduces context switches | Add severity-sort + file-group rule to Reviewer/Verifier finding output contract and Executor fix guidance | HIGH |
| `roborev-fix/SKILL.md:133-150` | Closure ordering mandate (close original set before new reviews) | WabbleSpec receipt chain can drift when wave N+1 starts before wave N receipts fully close; the ordering rule prevents this | Add explicit closure-ordering rule to Verifier pre-archive sweep and Executor inter-wave contract | HIGH |
| `roborev-fix/SKILL.md:36-51` | Context-first rule + skip-if-satisfied pattern | WabbleSpec skills re-derive state they already have; explicit "check conversation first" reduces redundant tool calls | Add "Check prior context before re-deriving" guidance to Executor wave protocol | MEDIUM |
| `roborev-refine/SKILL.md:154-170` | Full-scope re-review mandate after each fix (not commit-level) | WabbleSpec REVISE loop re-runs only the failing criterion; full-wave re-verification would catch regressions introduced during the fix | Add full-artifact re-check to step 1 of each REVISE cycle in Verifier | MEDIUM |
| `roborev-refine/SKILL.md:132-147` | Heredoc shell injection guard for externally-derived content | WabbleSpec's Executor and skills interpolate user/spec content into shell commands without escaping | Add heredoc rule to any WabbleSpec script delegation that embeds spec prose or review content | MEDIUM |
| `internal/prompt/analyze/security.txt` | Security analysis rubric (6 focus areas, FINDINGS/NO FINDINGS output contract) | WabbleSpec gateway-security has no structured rubric for what to report and what confidence threshold to require | Port the 6-focus-area rubric + FINDINGS/NO FINDINGS/FOLLOW-UP CHECKS contract to gateway-security reference | MEDIUM |
| `CLAUDE.md:179-185` | Workflow-specific config pattern `{Workflow}{Setting}{Level}` | WabbleSpec's config/recipe fields have no systematic naming; the pattern makes field lookup predictable via reflection/grep | Apply `{Workflow}{Setting}` naming to WabbleSpec recipe.json fields that vary by phase or module type | LOW |
| `CLAUDE.md:195-226` | Cancellation 3-phase race-safe check (running map → DB → pending set) | WabbleSpec Executor has no defined cancellation protocol; if a wave is interrupted mid-run, state is undefined | Document a 3-state check (active → receipt → pending cancel) in Executor's interruption protocol | LOW |
| `.roborev.toml:1-93` | Review guidelines as `.toml` block that agents read per-repo | WabbleSpec's session scope.md is consumed by framework; a per-project review guideline block would give domain-specific review instructions to any review agent | Add `review_guidelines` field to WabbleSpec's `.wabblespec/wabblespec.yaml` or a dedicated `review-config.toml` | LOW |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `CLAUDE.md:100-110` | Agent fallback cascade names vendors (codex, claude-code, gemini, etc.) | Direct copy violates I6 (no model names in framework files) | Replace with capability descriptors (`~~code-generation-primary`, `~~code-generation-backup`) | HIGH |
| `CLAUDE.md:213-232` | "Landing the plane" mandatory push mandate conflicts with WabbleSpec's no-push-unless-asked convention | WabbleSpec prohibits destructive/shared-state actions without user confirm | Do not copy; this is roborev's project-specific CLAUDE.md, not a universal rule | HIGH |
| `CLAUDE.md:5-21` | Session completion pattern ("complete ALL steps without stopping") conflicts with WabbleSpec's phase-gated I1 execution | WabbleSpec requires locked spec before execution; roborev assumes no phase gates | Do not copy session completion rules from roborev CLAUDE.md into WabbleSpec framework files | HIGH |
| `internal/skills/claude/` | Skills reference roborev CLI commands specifically (`roborev show`, `roborev fix`) | Adopted skills would hardcode roborev as a dependency | Adapt behavioral patterns only; use `~~review-daemon` capability placeholder for any roborev command | MEDIUM |
| `internal/skills/claude/roborev-review/SKILL.md:58-64` | Task tool invocation with `subagent_type: "Bash"` and `run_in_background: true` | WabbleSpec's Agent/Task tool use is governed by Autopilot; parallel subagent spawning without Guard approval violates I1 | Adapt the background launch pattern only where Autopilot/Guard has approved parallel execution | MEDIUM |
| Go implementation (SQLite, goroutines, HTTP) | Architecture is Go-specific; none of it ports to WabbleSpec's Python/JSON recipe layer | Risk of over-specifying Go patterns in behavioral rules | Take behavioral patterns only; explicitly exclude all implementation-level Go details | LOW |
| `internal/skills/skills.go` | Binary embedding of skills via `//go:embed` is Go-specific | WabbleSpec uses file-system skill sync (`wabblespec-sync-skills.py`); embedding is irrelevant | No adoption needed; WabbleSpec's sync approach is already superior | LOW |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Negative trigger clauses per skill | **Adapt** | Prevents misfire, directly adoptable | All WabbleSpec SKILL.md files | P1 |
| Severity sort + file-group ordering | **Adapt** | Improves fix quality, no conflict | Reviewer/Verifier output contract | P1 |
| Closure ordering mandate | **Adapt** | Prevents receipt drift | Verifier + Executor inter-wave | P1 |
| Context-first + skip-if-satisfied | **Adapt** | Reduces redundant tool calls | Executor wave protocol | P2 |
| Full-scope re-review after fix | **Adapt** | Catches regressions in REVISE | Verifier REVISE step 1 | P2 |
| Heredoc injection guard | **Adapt** | Shell safety for spec-derived content | Any skill writing to shell | P2 |
| Security analysis rubric (6 areas) | **Adapt** | Structure for gateway-security | gateway-security reference | P2 |
| Workflow config naming pattern | **Adapt** | Naming discipline for recipe fields | recipe.json schema | P3 |
| 3-phase cancellation check | **Study Only** | Useful if Executor gets interruption protocol | Future Executor extension | P4 |
| Review guidelines TOML block | **Study Only** | Pattern only; WabbleSpec uses scope.md | — | P4 |
| Agent fallback cascade (vendor names) | **Avoid** | I6 violation | — | — |
| Mandatory push mandate | **Avoid** | Conflicts with WabbleSpec convention | — | — |
| Phase-free session completion | **Avoid** | Conflicts with I1 spec-gating | — | — |
| roborev CLI commands in skills | **Avoid** | Hardcodes roborev dependency | — | — |
| Go implementation patterns | **Avoid** | Not portable | — | — |
| Binary skill embedding | **Avoid** | WabbleSpec sync approach is better | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 9 | roborev's review-fix-verify loop is a production implementation of the same lifecycle WabbleSpec orchestrates abstractly; the behavioral vocabulary maps almost 1:1 |
| Architecture fit | 6 | roborev is Go daemon + SQLite; WabbleSpec is Python scripts + JSON receipts; the patterns port but the implementation does not |
| Implementation fit | 5 | Skill SKILL.md format is similar but not identical; roborev's frontmatter and section order differ from WabbleSpec's conventions |
| Maintenance fit | 8 | roborev is actively maintained, MIT license, real users — staying current is plausible; patterns are stable enough to adopt without drift risk |
| Risk level | 3 | Primary risks are I6 (vendor names) and CLAUDE.md conflicts; both are avoidable by copying behavioral patterns only, not prose blocks |
| Overall usefulness | 9 | Highest behavioral pattern density of any reference reviewed so far; multiple P1 adoptions available immediately |

**Overall verdict: critical reference** — overall usefulness 9/10.

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — additive to existing files, no new files):**
1. Negative trigger clauses → `description:` fields in all 6+ review/verifier/adversary/grader SKILL.md files (roborev-fix:17-29)
2. Severity sort + file-group ordering → Reviewer SKILL.md finding output contract (roborev-fix:113-119)
3. Closure ordering mandate → Verifier SKILL.md inter-wave contract (roborev-fix:133-150)

**Phase 2 (Low-Risk Adaptation — extensions to existing sections):**
4. Context-first + skip-if-satisfied → Executor SKILL.md wave protocol (refine:44-46)
5. Full-scope re-review after REVISE → Verifier SKILL.md step 4 REVISE loop (refine:154-170)
6. Heredoc injection guard → Executor + any skill writing spec-derived content to shell (refine:132-147)
7. Security rubric (6 areas + output contract) → gateway-security reference document (security.txt)

**Phase 3 (Deeper Integration — new files or module-level changes):**
8. Workflow config naming pattern → recipe.json schema documentation
9. Review daemon integration concept → new `daemon` Verifier mode (Tier 6 synthesis)

**Phase 4 (Do Not Cross):**
- Agent vendor names from fallback cascade
- Mandatory push mandate
- roborev CLI dependency in WabbleSpec skills
- Go implementation code

---

## Section 7 — Final Verdict

**Best 3 to steal:**
1. **Negative trigger clauses** (roborev-fix/SKILL.md:17-29) — WabbleSpec skills have `description:` trigger guidance but no dedicated negative-trigger section; adding "When NOT to use" with concrete counterexamples would directly reduce misfire across all 10+ invokable review-type skills.
2. **Closure ordering mandate** (roborev-fix/SKILL.md:133-136) — the rule "close original set before fetching post-fix reviews" directly addresses WabbleSpec's receipt chain drift risk; this is a load-bearing behavioral rule, not a style preference.
3. **Full-scope re-review after REVISE** (roborev-refine/SKILL.md:154-170) — WabbleSpec's REVISE loop re-runs only the failing criterion; roborev proved that commit-level re-review is insufficient and the full branch scope must re-pass; this is the exact same risk profile as WabbleSpec verifying only the failing criterion instead of re-running all wave checks.

**Worst 3 to avoid:**
1. **Agent fallback cascade with vendor names** (CLAUDE.md:100-110) — copying this list would embed 10 vendor names into WabbleSpec framework files, a hard I6 violation.
2. **Mandatory push mandate** (CLAUDE.md:213-232) — this entire "Landing the Plane" section contradicts WabbleSpec's explicit no-push-unless-asked invariant; block-copying it would override user trust.
3. **Phase-free session completion** (CLAUDE.md:5-21) — roborev's "complete ALL steps without stopping" assumes no phase gates; WabbleSpec's I1 requires explicit spec lock before execution.

**Classification: critical**

**Next action:** Proceed to Phase 2 (ref-plan) immediately. No gate A stop.

---

## Section 8 — Project Synthesis

Ideas that require both roborev's behavioral patterns AND WabbleSpec's specific infrastructure:

| Idea | Reference contribution | Project contribution | Target (exact file) | Gap closed |
|---|---|---|---|---|
| **Daemon-backed Verifier mode** | roborev daemon's continuous background review of every commit; `roborev wait` discovers the latest review for HEAD; the refine loop waits on review completion before proceeding | WabbleSpec Verifier's pluggable `verification_mode` table; the `Demonstration` mode already proves live-condition verification is a valid mode | `.claude/skills/verifier/SKILL.md` (add `Daemon` mode row to Step 2 mode table) | No current WabbleSpec mode triggers a live external review process; Executor commits wave output but nothing reviews that commit before the next wave begins |
| **Negative-trigger library for all skills** | roborev's skill-by-skill "When NOT to invoke" sections with specific pasted-findings counterexamples — a standard pattern applied to every skill | WabbleSpec's `description:` field in skill frontmatter — already loaded by the skill router for trigger matching | All 6+ review-type `.claude/skills/*/SKILL.md` files + the skill-authoring section of `CLAUDE.md` | WabbleSpec's skill router matches on positive triggers only; negative examples in `description:` would let the router (and Claude) suppress on misfire conditions |
| **Severity-keyed finding schema in Reviewer** | roborev's 3-tier (HIGH/MEDIUM/LOW) + file-group ordering as an explicit output contract; the `finding_summary.by_severity` count field in gate receipts | WabbleSpec Reviewer's `findings` array in gate receipts (`finding.schema.json`) — already has severity field | `.claude/skills/reviewer/SKILL.md` (Step 3 output section) + `engine/modules/l2/reviewer/schemas/finding.schema.json` | WabbleSpec Reviewer produces findings but has no mandated presentation ordering; adopting roborev's sort rule would make Executor's fix order deterministic |
| **Scope-preserving REVISE** | roborev refine's rule that the explicit full-scope review must pass, not just the post-commit hook review — the scope of re-verification must match the scope of the original review | WabbleSpec Verifier's REVISE loop (Step 4) which currently re-runs the failing criterion only, not the full wave spec-compliance + mode check | `.claude/skills/verifier/SKILL.md` (Step 4 REVISE loop) | WabbleSpec REVISE can pass the criterion that failed while introducing a regression in another criterion; scope-preserving REVISE would catch this |
| **Heredoc injection guard as a framework invariant** | roborev's explicit mandate: "Never interpolate review-derived content directly into a shell string — always use heredoc" — a codified injection prevention rule | WabbleSpec's I11 (framework/product boundary) and the `guard-check.py` COMMAND_RISK taxonomy — both govern what scripts are safe to run | `.wabblespec/engine/shared/references/invariants.md` (new I12 candidate) + `guard-check.py` COMMAND_RISK taxonomy (new category: CONTENT_INJECTION) | WabbleSpec framework scripts embed spec prose and receipt content into shell commands; no current invariant or guard check covers shell injection from trusted-but-unescaped content |

All 5 synthesis ideas appear in the ref-plan as Tier 6 items.
