# Ref-Eval: get-shit-done-redux

**generated_at:** 2026-05-30T00:00:00Z
**reference_path:** C:\Users\Kirsten\Downloads\Orchestrator\get-shit-done-redux
**reference_slug:** get-shit-done-redux
**reference_type:** skill/behavioral spec + CLI tooling framework
**trust_level:** MEDIUM
**verdict:** critical-reference
**depth:** deep

---

## Section 1 — Reference Summary

**Type:** Production behavioral spec framework + CLI orchestration tooling. GSD Redux is a full SDLC system for solo developers using AI agents. It encodes runtime behavior for planning, execution, verification, debugging, and context management as agent instruction files — not boilerplate.

**Maturity signals:** Active CI, versioned releases (v1.42.x+), 400+ changesets, comprehensive test suite, real usage evidence across multiple runtimes (Claude Code, OpenCode, Gemini CLI, Codex, Kilo), Japanese/Korean/Portuguese/Chinese documentation.

**Red flags:** `model-profiles.md` embeds model names (Opus, Sonnet, Haiku) directly — I6 violation if copied.

---

## File Inventory (Step 1b)

| File | Purpose | Size | Key contents | Read |
|---|---|---|---|---|
| `agents/gsd-executor.md` | Wave execution agent | Large | 4-rule deviation framework, analysis paralysis guard, fix attempt limit, self-check, commit protocol | Yes |
| `agents/gsd-planner.md` | Wave planning agent | Large | Multi-source coverage audit, scope reduction prohibition, specificity test, context cost signals, goal-backward methodology | Yes |
| `agents/gsd-verifier.md` | Post-execution verifier | Large | 4-level artifact verification, wiring patterns, stall detection, deferred item filtering, override mechanism | Yes |
| `agents/gsd-plan-checker.md` | Pre-execution plan checker | Large | Scope reduction detection (Dim 7b), 11 verification dimensions, gates pattern | Yes |
| `agents/gsd-debugger.md` | Debug session manager | Large | 5-section debug file, structured reasoning checkpoint, knowledge base, 8 investigation techniques | Yes |
| `agents/gsd-user-profiler.md` | User behavioral profiler | Medium | 8 dimensions, confidence thresholds, claude_instruction format | Yes |
| `hooks/gsd-context-monitor.js` | PostToolUse context warning hook | Medium | Exact thresholds (35%/25%), debounce (5 calls), stale check (60s), severity escalation, CRITICAL breadcrumb | Yes |
| `hooks/gsd-statusline.js` | Statusline + bridge file writer | Medium | Writes `/tmp/claude-ctx-{session_id}.json` with context metrics | Summary |
| `hooks/gsd-read-guard.js` | PreToolUse read-before-edit advisory | Small | Advisory only, skips Claude Code, non-Claude model guard | Yes |
| `hooks/gsd-prompt-guard.js` | UserPromptSubmit informational nudge | Small | Informational only, never blocks | Summary |
| `commands/gsd/ns-workflow.md` | Namespace router example | Small | Routing table format, requires: field, pipe-separated keyword description | Yes |
| `docs/adr/0010-skill-surface-budget-module.md` | Skill surface budget ADR | Medium | 100-char description ceiling, profile tiers (core/standard/full), requires: dependency manifest, lint enforcement | Yes |
| `docs/context-monitor.md` | Context monitor documentation | Small | Architecture diagram, bridge file schema, threshold table, debounce rules | Yes |
| `get-shit-done/references/gates.md` | Gates taxonomy reference | Small | 4 gate types with exact selection heuristic | Yes |
| `get-shit-done/references/model-profiles.md` | Model profile table | Medium | Opus/Sonnet/Haiku per agent — DO NOT COPY (I6) | Yes |
| `docs/zh-CN/references/verification-patterns.md` | Verification patterns (Chinese) | Medium | 4-level framework, wiring patterns per type, stub detection grep commands | Yes |
| `get-shit-done/references/user-profiling.md` | User profiling rubric | Not read — adapt only 2 dimensions |
| `get-shit-done/references/planner-antipatterns.md` | Planner antipatterns | Not read — covered by gsd-planner.md |
| 34 other agent files | Domain-specific agents | Various | Not read — out of scope for this integration |
| 48 command files | Skill/command definitions | Various | Pattern captured from ns-workflow.md sample | Summary |

---

## Connection Map (Step 1c)

```
gsd-statusline.js --[writes bridge file]--> /tmp/claude-ctx-{session_id}.json
  shape: {session_id, remaining_percentage, used_pct, timestamp}
  /tmp/claude-ctx-{session_id}.json --[read on PostToolUse]--> gsd-context-monitor.js
  gsd-context-monitor.js --[additionalContext injection]--> Agent conversation
  [if CRITICAL + GSD active]: gsd-context-monitor.js --[fire-and-forget subprocess]--> gsd-tools state record-session

commands/gsd/execute-phase.md --[spawns]--> agents/gsd-executor.md
commands/gsd/plan-phase.md --[spawns]--> agents/gsd-planner.md + agents/gsd-plan-checker.md
commands/gsd/verify-work.md --[spawns]--> agents/gsd-verifier.md
commands/gsd/debug.md --[spawns]--> agents/gsd-debugger.md

gsd-planner.md --[queries]--> gsd-tools query init.plan-phase {phase}
  returns: {planner_model, researcher_model, checker_model, commit_docs, research_enabled,
            phase_dir, phase_number, has_research, has_context}
gsd-executor.md --[queries]--> gsd-tools query init.execute-phase {phase}
  returns: {executor_model, commit_docs, sub_repos, phase_dir, plans, incomplete_plans}
gsd-executor.md --[queries]--> gsd-tools query commit "{msg}" --files ...
  returns: {committed: bool, hash?, reason: 'committed'|'skipped_commit_docs_false'|
            'skipped_gitignored'|'nothing_to_commit'|'commit_failed', skipped?: bool}
  CONTRACT: skipped=true is intentional success — do NOT fall back to raw git add

gsd-verifier.md --[queries]--> gsd-tools query verify.artifacts "$PLAN_PATH"
  returns: {all_passed, passed, total, artifacts: [{path, exists, issues, passed}]}
gsd-verifier.md --[queries]--> gsd-tools query verify.key-links "$PLAN_PATH"
  returns: {all_verified, verified, total, links: [{from, to, via, verified, detail}]}

gsd-planner.md --[queries]--> gsd-tools graphify query "<keyword>" --budget 2000
  returns: graph nodes+edges for dependency context
  if stale: true in status → annotate "treat as approximate"

orchestrator --[passes completion context]--> gsd-executor.md continuation
  shape: <completed_tasks> block in prompt
  executor MUST: verify prior commits exist via git log before resuming

gsd-debugger.md --[writes]--> .planning/debug/{slug}.md (debug session file)
gsd-debugger.md --[archives]--> .planning/debug/resolved/{slug}.md
gsd-debugger.md --[appends]--> .planning/debug/knowledge-base.md
  future gsd-debugger.md --[reads Phase 0]--> knowledge-base.md
  matching: 2+ keyword overlap (case-insensitive) = hypothesis candidate
```

---

## Dimension Extraction (Step 2)

### Dimension 1 — Behavior (operational detail)

**Executor deviation rules — exact priority and rules:**
1. Rule 1: Auto-fix bugs (broken behavior, errors, incorrect output)
2. Rule 2: Auto-add missing critical functionality (missing error handling, null checks, missing auth on protected outputs)
3. Rule 3: Auto-fix blocking issues (wrong types, broken imports, missing env var) — EXCLUDED: package manager installs
4. Rule 4: Ask about architectural changes (new DB table, major schema changes, switching libraries, breaking API changes) → STOP
- Priority: Rule 4 wins if triggered. Rules 1–3 apply next. Genuinely unsure → Rule 4.
- Package install failure → `checkpoint:human-verify` with `gate="blocking-human"`. Do NOT auto-substitute alternative package names.
- Fix attempt limit: after 3 auto-fix attempts per task → STOP, document remaining issues, continue to next task.

**Analysis paralysis guard:** 5+ consecutive Read/Grep/Glob calls with no Write/Edit/Bash action = stuck. STOP. State why in one sentence. Then act or report blocked.

**Scope reduction prohibition — exact 14-phrase banned list:**
"v1", "v2", "simplified version", "static for now", "hardcoded for now", "future enhancement", "placeholder", "basic version", "minimal implementation", "will be wired later", "dynamic in future phase", "skip for now", "not wired to", "stub". Plus time-estimate-as-justification: "would take", "hours", "days", "minutes" in sizing context. Also: "too complex", "too difficult", "challenging" when used to justify omission.

**Context degradation tiers — exact thresholds:**
- PEAK: 0–30% context used
- GOOD: 30–50%
- DEGRADING: 50–70%
- POOR: 70%+
- Plans should complete within ~50% context (not 80%). "No context anxiety, quality maintained start to finish, room for unexpected complexity."

**Context monitor hook — exact operational values:**
- WARNING: remaining ≤ 35%
- CRITICAL: remaining ≤ 25%
- Debounce: 5 tool calls between warnings
- Stale metrics: ignored if timestamp > 60 seconds old
- Severity escalation (WARNING→CRITICAL) bypasses debounce
- CRITICAL + active session: fire subprocess `gsd-tools state record-session --stopped-at "<context_exhaustion_pct>% (date)"` as breadcrumb

**Verification 4-level framework:**
- Level 1: Exists (file at declared path)
- Level 2: Substantive (real implementation, not stub)
- Level 3: Wired (connected to system — imported AND used)
- Level 4: Data-flows (actually produces real output when invoked)
- Level 4 only runs on artifacts that pass Levels 1–3 AND render dynamic data.
- Final status: Exists+Substantive+Wired+DataFlows=VERIFIED; -DataFlows=HOLLOW; -Wired=ORPHANED; -Substantive=STUB; -Exists=MISSING

**Wiring verification patterns — 4 exact types:**
- Component→API: fetch/axios call exists AND response is used (not just preventDefault)
- API→Database: query exists AND result is returned (not `return Response.json([])`)
- Form→Handler: onSubmit calls API/mutation (not just e.preventDefault())
- State→Render: state variables appear in JSX output

**Verifier stall detection:** If issue count does not decrease between consecutive REVISE iterations → escalate immediately, not at cap.

**Override schema (exact YAML):**
```yaml
overrides:
  - must_have: "text of the Then clause or artifact"
    reason: "why this deviation is acceptable"
    accepted_by: "name"
    accepted_at: "2026-05-30T00:00:00Z"
```
Matching algorithm: normalize both strings (lowercase, strip punctuation, collapse whitespace), split into tokens, compute intersection. Match if 80% token overlap in either direction.

**Debug file update rules (exact):**
- Current Focus: OVERWRITE on each update — reflects NOW
- Symptoms: IMMUTABLE after gathering complete
- Eliminated: APPEND only — prevents re-investigating
- Evidence: APPEND only — facts discovered
- Resolution: OVERWRITE as understanding evolves
- UPDATE FILE BEFORE TAKING ACTION, not after. If context resets mid-action, the file shows what was about to happen.

**Structured reasoning checkpoint (exact 5-field schema, MANDATORY before any fix):**
```yaml
reasoning_checkpoint:
  hypothesis: "[exact statement — X causes Y because Z]"
  confirming_evidence:
    - "[specific evidence item]"
  falsification_test: "[what specific observation would prove this wrong]"
  fix_rationale: "[why the proposed fix addresses the root cause, not the symptom]"
  blind_spots: "[what has not been tested that could invalidate this hypothesis]"
```
All 5 fields must have specific, concrete answers. If any is vague: root cause is not confirmed — return to investigation loop.

**Knowledge base matching:** 2+ keyword overlap (case-insensitive) = hypothesis candidate, not certainty.

**Gates taxonomy (selection heuristic — exact wording):** "Start with Pre-flight. If the check happens after work is produced, it is Revision. If the Revision loop cannot resolve it, Escalate. If continuing is dangerous, Abort."

**Multi-source coverage audit — 4 source types:**
- GOAL: phase goal and acceptance criteria
- REQ: requirement IDs mapped to at least one wave
- RESEARCH: all research findings flagged as must-implement
- CONTEXT: all locked decisions from task card Decisions section
- "Never finalize the wave plan silently with gaps."

**Specificity test:** "Could a different Claude instance execute this task without asking a clarifying question? If not, the task description is not specific enough."

**Context cost signals (exact heuristics):**
- 0–3 files modified: ~10–15%
- 4–6 files modified: ~20–30%
- 7+ files modified: ~40%+ (split recommended)
- New subsystem: ~25–35%
- Migration + data transform: ~30–40%
- Pure config/wiring: ~5–10%

**Skill surface budget:** Description ceiling = 100 characters (enforced by lint). Profile tiers: `core` (~7 skills), `standard` (~13 skills), `full` (66 skills). `requires:` frontmatter lists other skills the body references — used for transitive closure in profile resolution.

### Dimension 2 — Format (identifier level)

- Agent file frontmatter: `name`, `description`, `tools` (list), `color`
- Skill file frontmatter: `name`, `description`, `argument-hint`, `allowed-tools`, `requires`
- Namespace router frontmatter: `name`, `description` (pipe-separated keyword tags ≤60 chars), `argument-hint`, `allowed-tools`, `requires` (list of constituent skills)
- Agent instruction structure: XML tags — `<role>`, `<step name="">`, `<execution_flow>`, `<deviation_rules>`, `<success_criteria>`, `<checkpoint_protocol>`, `<analysis_paralysis_guard>`
- Routing table format in commands: `| User wants | Invoke |` with two columns
- Debug file YAML frontmatter: `status` (gathering/investigating/fixing/verifying/awaiting_human_verify/resolved), `trigger`, `created`, `updated`
- Override YAML in verification frontmatter: `overrides:` array with `must_have`, `reason`, `accepted_by`, `accepted_at`
- PLAN.md frontmatter required fields: `phase`, `plan`, `type`, `wave`, `depends_on`, `files_modified`, `autonomous`, `requirements`, `must_haves` (truths/artifacts/key_links). Plans with empty `requirements` are invalid.
- Knowledge base entry format: `## {slug} — {description}`, then `Date`, `Error patterns`, `Root cause`, `Fix`, `Files changed`, `---`

### Dimension 3 — Interactions (contract level)

Bridge file contract: `gsd-statusline.js` produces `{session_id, remaining_percentage, used_pct, timestamp}`. `gsd-context-monitor.js` expects this exact shape. Missing `timestamp` → stale check skipped (not an error). `session_id` containing `/\` or `..` → exit 0 (path traversal guard). If `hooks.context_warnings === false` in `.planning/config.json` → exit 0 (disable override).

`gsd-tools query commit` contract: returns 4 distinct shapes. `skipped=true` is intentional success. Do NOT fall back to raw `git add` when `skipped=true` — this was the exact regression in #3678.

`gsd-tools query verify.artifacts` and `verify.key-links`: consume `$PLAN_PATH`. The `issues` array presence on any artifact = STUB. `verified=false` with "not found" in `detail` = NOT_WIRED.

Planner → graphify: query uses `gsd-tools.cjs graphify query` (NOT `gsd-tools query`) — this is a known discrepancy documented inline. The graphify command is not exposed on the `gsd-tools query` interface yet.

Orchestrator → continuation executor: passes `<completed_tasks>` with prior commit hashes. Continuation executor MUST verify: `git log --oneline -5` before resuming. If hashes not found → do NOT redo completed tasks; instead surface as blocker.

Debug session chain: slug is generated from user input (lowercase, hyphens, max 30 chars). File MUST be created immediately — even before symptom gathering. Knowledge base append happens only after human confirmation of fix (in `archive_session`), not earlier.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Literal extract | Impact |
|---|---|---|---|---|---|
| `agents/gsd-executor.md` → `<deviation_rules>` | 4-rule deviation framework with exact priority and supply-chain gate | WabbleSpec Executor improvises on deviations — no structured handling, no audit trail | Add `## Deviation Rules` to `skills/executor/SKILL.md` | Priority: "Rule 4 applies → STOP. Rules 1–3 → fix automatically. Unsure → Rule 4." Package install failure → `checkpoint:human-verify` gate="blocking-human". Rule 3 exclusion: "npm install, pip install, cargo add" | High |
| `agents/gsd-executor.md` → `<analysis_paralysis_guard>` | 5-read threshold for stuck detection | WabbleSpec Executor can read-loop indefinitely | Add one paragraph to execution flow in `skills/executor/SKILL.md` | "5+ consecutive Read/Grep/Glob calls without any Edit/Write/Bash action: STOP." | High |
| `agents/gsd-executor.md` → `<deviation_rules>` → FIX ATTEMPT LIMIT | 3-attempt cap per task | No limit → infinite loops | Add to deviation rules section | "After 3 auto-fix attempts on a single task: STOP fixing — document remaining issues... Continue to the next task." | High |
| `agents/gsd-executor.md` → `<self_check>` | Verify artifacts exist + commits resolve before receipt | Phantom PASS receipts accumulate | Add self-check step before `receipt-writer.py` call | "Check created files exist: `[ -f 'path' ]`. Check commits exist: `git log --all | grep -q '{hash}'`. If fails: mark wave PARTIAL, not PASS." | High |
| `agents/gsd-planner.md` → `<scope_reduction_prohibition>` + `agents/gsd-plan-checker.md` → Dim 7b | 14-phrase banned language list | Silent scope cuts pass undetected through the pipeline | Add banned list to `skills/decompose/SKILL.md` + `skills/executor/SKILL.md` | Full 14-phrase list: v1, v2, simplified version, static for now, hardcoded for now, future enhancement, placeholder, basic version, minimal implementation, will be wired later, dynamic in future phase, skip for now, not wired to, stub. Plus time-estimates and complexity-as-justification. | High |
| `agents/gsd-planner.md` → `<task_breakdown>` → Specificity | Specificity test before finalizing wave plan | WabbleSpec wave items are often vague, non-executable | Add as finalization gate in `skills/decompose/SKILL.md` | "Could a different Claude instance execute this task without asking a clarifying question? If not, the task description is not specific enough." | High |
| `agents/gsd-planner.md` → `<scope_reduction_prohibition>` → Multi-Source Coverage Audit | 4-source mandatory audit: GOAL/REQ/RESEARCH/CONTEXT | WabbleSpec Decompose doesn't audit requirement coverage | Add `## Coverage Audit` step to `skills/decompose/SKILL.md` | "Never finalize the wave plan silently with gaps." 4 sources, every item must be COVERED. | High |
| `agents/gsd-verifier.md` → Steps 4+4b | 4-level verification framework | WabbleSpec Verifier stops at Level 1 (existence) | Extend `skills/verifier/SKILL.md`; route wiring patterns to new reference file | Level 4 only runs on artifacts passing Levels 1–3 that render dynamic data. Final status table (VERIFIED/HOLLOW/ORPHANED/STUB/MISSING). | High |
| `docs/zh-CN/references/verification-patterns.md` | Language-agnostic wiring patterns (4 types) with grep commands | Stub code in wiring connections is WabbleSpec's most common verification miss | New `engine/shared/references/verification-patterns.md` (strip React-specific patterns) | 4 patterns: Component→API, API→Database, Form→Handler, State→Render. Each with positive and negative examples. | High |
| `get-shit-done/references/gates.md` | 4-type gate taxonomy with exact selection heuristic | WabbleSpec uses gate concepts inconsistently across Guard/Verifier/Executor | New `engine/shared/references/gate-taxonomy.md` routed from `guard/SKILL.md` and `verifier/SKILL.md` | Selection heuristic verbatim. Revision gate: bounded by iteration cap + stall detection fires early. | Medium |
| `agents/gsd-verifier.md` → Step 9b | Deferred item filtering (check later waves before declaring gap) | WabbleSpec Verifier flags intentionally deferred items as failures | Add Step 9b logic to `skills/verifier/SKILL.md` spec compliance check | "Be conservative. Only defer when there is clear, specific evidence in a later phase. Vague matches: keep as real gap." | Medium |
| `agents/gsd-verifier.md` → Step 3b | Override mechanism with exact YAML schema | WabbleSpec has no auditable technical debt mechanism | Add `## Override Protocol` to `skills/verifier/SKILL.md` | Override schema: `must_have`, `reason`, `accepted_by`, `accepted_at`. Matching: 80% token overlap after normalization. Status: `PASSED (override)`. | Medium |
| `agents/gsd-plan-checker.md` → Dim 7b | Scope reduction detection before execution (ALWAYS BLOCKER) | WabbleSpec Guard doesn't scan for scope reduction language | Add layer to `skills/guard/SKILL.md` scanning wave task descriptions | "ALWAYS BLOCKER. Scope reduction is never a warning." | High |
| `agents/gsd-planner.md` → `<philosophy>` → Quality Degradation Curve | Exact 4-tier context degradation with percentages | WabbleSpec Economy has vague context guidance | Extend `skills/economy/rules/cold-start.md` with tier table + MCP audit | PEAK 0–30%, GOOD 30–50%, DEGRADING 50–70%, POOR 70%+. Plans target ~50%, not 80%. | High |
| `hooks/gsd-context-monitor.js` + `docs/context-monitor.md` | PostToolUse hook injecting context warnings into agent conversation | WabbleSpec agent is context-blind | New `engine/hooks/wabblespec-context-monitor.js` + `settings.local.json` registration | WARNING ≤35%, CRITICAL ≤25%, debounce 5 calls, stale >60s, escalation bypasses debounce, CRITICAL breadcrumb via subprocess. | High |
| `agents/gsd-debugger.md` | Persistent debug module with 5-section file, structured reasoning checkpoint, knowledge base, 8 investigation techniques | WabbleSpec has no Debug skill | New `skills/debug/SKILL.md` + reference files | 5 sections: Current Focus (OVERWRITE), Symptoms (IMMUTABLE), Eliminated (APPEND), Evidence (APPEND), Resolution (OVERWRITE). 5-field reasoning checkpoint (all fields must be concrete). Knowledge base: 2+ keyword overlap = candidate. | High |
| `commands/gsd/ns-*.md` | Namespace router pattern | 103 skills loaded eagerly every turn — token cost compounds | New `commands/ns-*.md` files adapted to Skill-tool invocation model | Description format: pipe-separated keyword tags ≤60 chars. `requires:` frontmatter. Routing table: user intent → invoke. | Medium |
| `docs/adr/0010-skill-surface-budget-module.md` | Skill size budget enforcement via quality-floor check | SKILL.md files grow without constraint | Extend `quality-floor-check.py` with line count gate per tier | 100-char description ceiling enforced by lint. XL=1700, LARGE=1500, DEFAULT=1000 lines. Skills over limit without routing table → flagged. | Medium |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `get-shit-done/references/model-profiles.md` | Model names (Opus/Sonnet/Haiku) in profile tables | I6 violation — framework files must use capability descriptors | Adapt tier logic using capability descriptors; do not copy model names | High |
| All agent files referencing `.planning/` | Path structure incompatible with WabbleSpec | I11 — WabbleSpec canonical paths are `.wabblespec/state/` | Adapt all path references during integration | High |
| `get-shit-done/bin/gsd-tools.cjs` | Node.js CLI tooling | Wrong language stack; WabbleSpec engine is Python | Adapt behavioral patterns to existing Python scripts | Medium |
| `agents/gsd-verifier.md` → stub detection | React/Next.js-specific grep patterns | Domain-coupled; WabbleSpec verifies skills/scripts, not React components | Extract language-agnostic patterns only (TODO/FIXME/empty returns/hardcoded values) | Medium |
| `agents/gsd-executor.md` → commit protocol | Multi-repo `commit-to-subrepo` logic | Wrong execution model; WabbleSpec is single-repo | Adapt single-repo commit protocol only | Low |
| `agents/gsd-executor.md` → worktree guards | cwd-drift assertion, per-agent branch namespace | Wrong execution model; WabbleSpec doesn't use parallel worktrees | Adapt general principle (verify commit target) without worktree-specific code | Low |
| `agents/gsd-user-profiler.md` | Full 8-dimension profiling system | Over-engineered for WabbleSpec session length; requires 100+ messages | Adopt 2 dimensions only (communication_style, technical_depth) as memory drawer schema | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| 4-rule deviation framework | Adapt | Closes biggest behavioral gap | `skills/executor/SKILL.md` | High |
| Analysis paralysis guard (5 reads) | Adapt | Simple, high-impact, exact threshold | `skills/executor/SKILL.md` | High |
| Fix attempt limit (3 per task) | Adapt | Prevents infinite loops | `skills/executor/SKILL.md` | High |
| Self-check before receipt write | Adapt | Closes phantom PASS receipt problem | `skills/executor/SKILL.md` | High |
| Scope reduction prohibition (14-phrase list) | Adapt | Prevents silent scope cuts | `skills/decompose/SKILL.md`, `skills/executor/SKILL.md` | High |
| Specificity test | Adapt | Forces actionable wave items | `skills/decompose/SKILL.md` | High |
| Multi-source coverage audit (4 sources) | Adapt | Closes "silently missing requirement" failure class | `skills/decompose/SKILL.md` | High |
| Verification 4-level framework | Adapt | Elevates verifier from existence to behavioral check | `skills/verifier/SKILL.md`, new `verification-patterns.md` | High |
| Wiring verification patterns (4 types) | Adapt | Stub detection where most stubs hide | new `engine/shared/references/verification-patterns.md` | High |
| Verifier stall detection | Adapt | Closes infinite REVISE loops | `skills/verifier/SKILL.md` | High |
| Deferred item filtering | Adapt | Prevents false-positive gap reports | `skills/verifier/SKILL.md` | Medium |
| Override mechanism (YAML schema) | Adapt | Makes intentional debt auditable | `skills/verifier/SKILL.md` | Medium |
| Gates taxonomy | Adapt | Shared vocabulary across Guard/Verifier/Executor | new `engine/shared/references/gate-taxonomy.md` | Medium |
| Guard scope reduction detection layer | Adapt | Pre-execution enforcement | `skills/guard/SKILL.md` | High |
| Context degradation tiers (exact %) | Adapt | Replaces vague guidance | `skills/economy/rules/cold-start.md` | High |
| Context monitor hook | Adapt | Agent-facing context awareness | new `engine/hooks/wabblespec-context-monitor.js` | High |
| Debug module | Adapt | New capability, no WabbleSpec equivalent | new `skills/debug/SKILL.md` | High |
| Namespace routing layer | Adapt | Token efficiency at 103-skill scale | new `commands/ns-*.md` | Medium |
| Skill size budget enforcement | Adapt | Prevents SKILL.md bloat | `quality-floor-check.py` | Medium |
| Context cost signals (file count heuristics) | Adapt | Enables context-aware wave sizing (Synthesis S4) | `skills/decompose/SKILL.md` | Medium |
| Model profile tables (model names) | Avoid | I6 violation | — | — |
| `.planning/` path structure | Avoid | I11 violation | — | — |
| gsd-tools.cjs Node.js CLI | Avoid | Wrong language stack | — | — |
| React/Next.js grep patterns | Avoid | Domain-coupled | — | — |
| commit-to-subrepo multi-repo | Avoid | Wrong execution model | — | — |
| Worktree git safety guards | Avoid | Wrong execution model | — | — |
| Full 8-dimension user profiling | Study only | Over-engineered; adopt 2 dimensions only | — | Low |

---

## Section 5 — Integration Fit

| Dimension | Score | Explanation |
|---|---|---|
| Concept fit | 9 | Same problem class — spec-driven SDLC execution; near-identical module decomposition (plan, execute, verify, guard) |
| Architecture fit | 7 | Both use skill/agent instruction files as the behavioral layer; GSD's Node.js CLI tooling doesn't map but instruction patterns do |
| Implementation fit | 7 | WabbleSpec is Python/PowerShell/JS; GSD is Node.js; hook architecture is directly compatible; instruction file format is compatible |
| Maintenance fit | 8 | GSD's reference routing pattern (route to reference files rather than inline documentation) is already used in WabbleSpec |
| Risk level | 3 | Low — all adaptations are additive or new files; no breaking changes required |
| Overall usefulness | 9 | Deepest available source of behavioral patterns for AI-driven SDLC execution; directly applicable across 8+ WabbleSpec modules |

---

## Section 6 — Recommended Extraction Plan

Each item below names exact target file and exact change. Implementer should not need to re-read this eval to act.

**Phase 1 — Safe Learning (complete)**
Study: `gsd-synthesis.md` at `research/gsd-synthesis.md`. Literal values: extracted in Section 2 above.

**Phase 2 — Low-Risk Adaptation**

1. **Verifier stall detection** → `skills/verifier/SKILL.md` REVISE loop section: add "if issue count does not decrease between consecutive iterations, escalate immediately" — one paragraph.
2. **Gate taxonomy reference** → new `engine/shared/references/gate-taxonomy.md`: 4 gate types table + selection heuristic verbatim. Route `guard/SKILL.md` and `verifier/SKILL.md` to it.
3. **Verification patterns reference** → new `engine/shared/references/verification-patterns.md`: 4-level framework + 4 wiring patterns + language-agnostic stub detection. Route `verifier/SKILL.md` to it.
4. **Context degradation tiers** → `skills/economy/rules/cold-start.md`: append PEAK/GOOD/DEGRADING/POOR table with exact percentages. Add MCP audit checklist. Add context cost signals table.
5. **Executor deviation rules** → `skills/executor/SKILL.md`: add `## Deviation Rules` section with all 4 rules including priority ordering, supply-chain gate, fix attempt limit, and self-check before receipt write.
6. **Analysis paralysis guard** → `skills/executor/SKILL.md` (same file as #5): one paragraph.
7. **Scope reduction prohibition** → `skills/decompose/SKILL.md`: add `## Scope Reduction Prohibition` with full 14-phrase banned list. `skills/executor/SKILL.md`: add flag during implementation.
8. **Specificity test** → `skills/decompose/SKILL.md`: add finalization gate with exact question wording.
9. **Verifier deferred item filtering** → `skills/verifier/SKILL.md` Step 1 spec compliance check.
10. **Override mechanism** → `skills/verifier/SKILL.md`: add `## Override Protocol` with exact YAML schema and 80% token overlap matching rule.
11. **Multi-source coverage audit** → `skills/decompose/SKILL.md`: add `## Coverage Audit` step before wave plan finalization. 4 sources. "Never finalize silently with gaps."
12. **Guard scope reduction detection** → `skills/guard/SKILL.md`: new layer scanning wave task descriptions for banned list. HARD block on detection.

**Phase 3 — Deeper Integration**

13. **Verifier 4-level upgrade** → `skills/verifier/SKILL.md`: extend Step 2 to add Levels 2–4 using `verification-patterns.md` (from Phase 2 item 3).
14. **Context monitor hook** → new `engine/hooks/wabblespec-context-monitor.js` + `settings.local.json` registration. GSD-active detection reads `state.json`. Breadcrumb writes to `state.json.context_exhaustion_pct`.
15. **Debug module** → new `skills/debug/SKILL.md` + `engine/shared/references/debug-file-protocol.md` + `engine/shared/references/debug-investigation-techniques.md`. State at `.wabblespec/state/debug/`.
16. **Namespace routing layer** → new `commands/ns-*.md` files (8–10 routers). Requires `wabblespec.yaml` registration.
17. **Skill size budget gate** → `engine/shared/scripts/quality-floor-check.py`: add gate for SKILL.md line counts (XL=1700, LARGE=1500, DEFAULT=1000).

**Phase 4 — Do Not Cross**

- `model-profiles.md` model name tables → I6
- `.planning/` path references → I11
- React/Next.js grep patterns → domain-coupled
- Full 8-dimension user profiler → over-engineered for use case
- `gsd-tools.cjs` Node.js CLI → wrong stack

---

## Section 7 — Final Verdict

Worth using: yes, immediately. GSD Redux and WabbleSpec solve the same problem class. GSD's behavioral specs are the most production-validated source of AI-agent SDLC patterns available.

**Best 3 to steal:**
1. `agents/gsd-executor.md` → `<deviation_rules>`: 4-rule deviation framework with exact priority ordering and supply-chain gate. WabbleSpec Executor has nothing comparable.
2. `agents/gsd-planner.md` → `<scope_reduction_prohibition>`: 14-phrase banned list + specificity test. Closes the silent scope reduction failure class end-to-end.
3. `agents/gsd-verifier.md` → Steps 4+4b: 4-level verification (Exists/Substantive/Wired/Data-flows) with wiring patterns. WabbleSpec currently stops at Level 1.

**Worst 3 to avoid:**
1. `get-shit-done/references/model-profiles.md`: embeds Opus/Sonnet/Haiku model names → I6 violation.
2. `.planning/` path structure throughout all agent files: incompatible with `.wabblespec/state/` → I11 violation.
3. React/Next.js stub detection patterns: domain-coupled noise for WabbleSpec's language-agnostic verifier.

**Classification: critical-reference** — actively drives current design decisions.

**Recommended next action:** Run ref-plan against this eval to produce the phased integration plan.

---

## Section 8 — Project Synthesis

Novel patterns that require both GSD's behavioral designs AND WabbleSpec's existing infrastructure.

### S1 — Receipt-gated hypothesis testing

**Reference contribution:** GSD's structured reasoning checkpoint (`agents/gsd-debugger.md` → `<investigation_techniques>` → Structured Reasoning Checkpoint) — 5-field YAML schema that forces articulation of hypothesis, evidence, and falsification test before any fix.

**Project contribution:** WabbleSpec's receipt chain (`receipt-writer.py`, Research → Plan → Execution → Verify → Archive). Each receipt is queryable.

**What:** Before writing the wave receipt, Executor includes a `reasoning_checkpoint` field documenting: what the wave was supposed to do, what evidence confirms it was done, what would have falsified the approach.

**Target:** `skills/executor/SKILL.md` — add `reasoning_checkpoint` to execution receipt JSON schema; `engine/shared/scripts/receipt-writer.py` — add field to execution receipt type.

**Gap closed:** Execution receipts contain bare PASS verdicts with no reasoning. Archive could compute coverage: what fraction of receipts have documented reasoning vs. bare PASS.

---

### S2 — Deviation receipt as Instinct signal

**Reference contribution:** GSD Executor tracks all deviations from the plan in SUMMARY.md (`agents/gsd-executor.md` → `<summary_creation>` → Deviation documentation section with Rule N tagging).

**Project contribution:** WabbleSpec's `receipt-writer.py`, the Instinct → Synth → Blueprint evolution chain, and memory drawer infrastructure create a multi-session learning loop.

**What:** Auto-fixed deviations (Rules 1–3) write deviation receipts linked to the wave receipt. Archive aggregates them to compute drift-from-spec metrics. Instinct reads: which task types consistently require auto-fixes → which planning templates are underspecified.

**Target:** `engine/shared/scripts/receipt-writer.py` (new `--type deviation`), `skills/executor/SKILL.md` (deviation receipt write step after each Rule 1–3 auto-fix), `skills/instinct/SKILL.md` (add deviation receipt aggregate as Instinct input signal).

**Gap closed:** WabbleSpec currently has no systematic way to identify which planning patterns consistently under-specify work.

---

### S3 — Entity-graph as wave dependency input

**Reference contribution:** GSD planner queries graphify for dependency context before designing waves (`agents/gsd-planner.md` → `<step name="load_graph_context">`). Stale graph annotated as approximate.

**Project contribution:** WabbleSpec's entity-graph (`.wabblespec/state/memory/entity-graph.json`) already tracks module relationships.

**What:** When Decompose is designing waves, query the entity-graph for cross-module dependency context. If entity A references entity B and both are being modified in different waves, force them into the same wave or add an explicit dependency edge.

**Target:** `skills/decompose/SKILL.md` — add entity-graph query step alongside memory drawer loading step: `python .wabblespec/entity-graph.py query <keyword> --format json`. If graph stale: treat relationships as approximate.

**Gap closed:** WabbleSpec waves are designed without dependency-context from the entity graph. Cross-module modifications that should be co-located are silently split.

---

### S4 — Context-aware wave sizing

**Reference contribution:** GSD planner's context cost signals from `agents/gsd-planner.md` → `<task_breakdown>` → Task Sizing (file count → context % heuristics). Plans target ~50%.

**Project contribution:** WabbleSpec's Guard (runs before each wave) + wave plan structure + Economy module create infrastructure to enforce a context budget constraint before execution starts.

**What:** Decompose adds a `recommended_wave_context_budget` field to each wave plan entry based on the context cost heuristics. Guard checks this field before spawning the wave. If budget exceeded: SOFT warning recommending Executor operate in Economy mode.

**Target:** `skills/decompose/SKILL.md` (add budget estimation to wave plan output using heuristics table), `skills/guard/SKILL.md` (add budget check as new Guard layer), `skills/economy/rules/cold-start.md` (route heuristics table here as the canonical reference).

**Gap closed:** WabbleSpec has no mechanism to predict or limit context consumption per wave before execution begins. Context exhaustion mid-wave is currently discovered rather than anticipated.
