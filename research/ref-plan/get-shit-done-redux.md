# Integration Plan: get-shit-done-redux

**generated_at:** 2026-05-30T00:00:00Z
**ref_eval_report:** research/ref-eval/get-shit-done-redux.md
**risk_appetite:** balanced
**integration_goal:** Adopt GSD Redux's proven behavioral patterns — deviation handling, scope reduction enforcement, 4-level verification, context awareness, debug module — into WabbleSpec's skill layer, reference infrastructure, and hook layer. Each item must be specific enough to implement without re-reading the ref-eval.

---

## Signal Summary

GSD Redux evaluated as critical-reference (overall usefulness 9/10). 20 items identified for integration across 6 tiers. 7 items excluded (I6 model names, I11 path violations, domain-coupled patterns, wrong language stack). 4 synthesis items generated. The reference provides the most production-validated source of AI-agent SDLC behavioral patterns available and maps directly to WabbleSpec's existing module structure.

---

## Do-Not-Copy List

| Item | Source in ref-eval | Reason | Invariant |
|---|---|---|---|
| Model profile tables (Opus/Sonnet/Haiku names) | Section 3 / R1 | Model names in framework files | I6 |
| `.planning/` directory path structure | Section 3 / R3 | Incompatible with `.wabblespec/state/` | I11 |
| `gsd-tools.cjs` Node.js CLI implementation | Section 3 / R2 | Wrong language stack (Python) | None (stack mismatch) |
| React/Next.js-specific grep patterns in verifier | Section 3 / R4 | Domain-coupled, not language-agnostic | None (domain mismatch) |
| `commit-to-subrepo` multi-repo commit routing | Section 3 / R5 | Wrong execution model | None (model mismatch) |
| Worktree cwd-drift and per-agent branch guards | Section 3 / R6 | Wrong execution model | None (model mismatch) |
| Full 8-dimension user profiler machinery | Section 3 / R7 | Over-engineered; adopt 2 dimensions only | None (scope) |

---

## Integration Backlog (ranked)

| Rank | ID | Item | Tier | Impact | Risk | Score |
|---|---|---|---|---|---|---|
| 1 | T1a | Verifier stall detection | 1 | High | Low | 8 |
| 2 | T3a | Gate taxonomy reference | 3 | Medium | Low | 5 |
| 3 | T3b | Verification patterns reference | 3 | High | Low | 7 |
| 4 | T1b | Context degradation tiers (exact %) | 1 | High | Low | 8 |
| 5 | T1c | Executor deviation rules (4-rule framework) | 1 | High | Low | 8 |
| 6 | T1d | Executor analysis paralysis guard | 1 | High | Low | 8 |
| 7 | T1e | Executor fix attempt limit | 1 | High | Low | 8 |
| 8 | T1f | Executor self-check before receipt | 1 | High | Low | 8 |
| 9 | T1g | Scope reduction prohibition (banned list) | 1 | High | Low | 8 |
| 10 | T1h | Specificity test in decompose | 1 | High | Low | 8 |
| 11 | T2a | Verifier 4-level artifact upgrade | 2 | High | Medium | 6 |
| 12 | T1i | Verifier deferred item filtering | 1 | Medium | Low | 5 |
| 13 | T1j | Override mechanism (YAML schema) | 1 | Medium | Low | 5 |
| 14 | T2b | Multi-source coverage audit | 2 | High | Low | 7 |
| 15 | T1k | Guard scope reduction detection layer | 1 | High | Low | 8 |
| 16 | T4a | Debug module (new skill) | 4 | High | Medium | 6 |
| 17 | T4b | Context monitor hook (new hook) | 4 | High | Medium | 6 |
| 18 | T5a | Namespace routing layer | 5 | Medium | Medium | 4 |
| 19 | T2c | Skill size budget enforcement | 2 | Medium | Low | 5 |
| 20 | T2d | Context cost signals in Decompose | 2 | Medium | Low | 5 |

---

## Tier 1 — Behavioral Additions

### T1a — Verifier stall detection

- **What:** Add stall detection to the REVISE loop — if issue count does not decrease between consecutive iterations, escalate immediately without waiting for the 3-iteration cap.
- **Target:** `skills/verifier/SKILL.md` — REVISE loop section (wherever the iteration cap is tracked)
- **How:** After each REVISE cycle, compare issue count to prior cycle. If count did not decrease: escalate to BLOCKED immediately, bypassing remaining iterations. Add a single paragraph to the existing REVISE loop protocol.
- **Literal values:** "The loop also escalates early if issue count does not decrease between consecutive iterations (stall detection). After max iterations, escalates unconditionally." Gate type: Revision Gate.
- **Gate:** Verifier REVISE loop no longer completes 3 iterations when stalled — it escalates on the first non-decreasing cycle.
- **Reference location:** `get-shit-done/references/gates.md` → Revision Gate definition; `agents/gsd-verifier.md` → Step 9 status determination.

---

### T1b — Context degradation tiers (exact thresholds)

- **What:** Add 4 named tiers with exact percentage thresholds to Economy's cold-start rules. Replace vague "context getting heavy" guidance with actionable behavioral tiers.
- **Target:** `skills/economy/rules/cold-start.md` — append two new sections
- **How:** Append a context degradation tier table and a context cost signals table. Both are already extracted verbatim below.
- **Literal values:**
  - PEAK: 0–30% used. Full reads, spawn subagents freely, inline results.
  - GOOD: 30–50%. Normal ops, prefer frontmatter reads, delegate aggressively.
  - DEGRADING: 50–70%. Frontmatter-only reads, minimal inlining, warn user about budget.
  - POOR: 70%+. Emergency: checkpoint immediately, no new reads unless critical.
  - "Plans should complete within ~50% context (not 80%). No context anxiety, quality maintained start to finish, room for unexpected complexity."
  - Context cost signals: 0–3 files = ~10–15%; 4–6 files = ~20–30%; 7+ files = ~40%+; New subsystem = ~25–35%; Migration + data transform = ~30–40%; Pure config/wiring = ~5–10%.
- **Gate:** Economy guidance references specific tier names rather than narrative descriptions.
- **Reference location:** `agents/gsd-planner.md` → `<philosophy>` → Quality Degradation Curve table; `<task_breakdown>` → Task Sizing → Context Cost signals.

---

### T1c — Executor: 4-rule deviation framework

- **What:** Add a `## Deviation Rules` section to Executor with 4 explicitly numbered rules, priority ordering, supply-chain gate, and scope boundary.
- **Target:** `skills/executor/SKILL.md` — add after the execution flow section
- **How:** Add the section verbatim with WabbleSpec path adaptations. Replace `.planning/` references with `.wabblespec/state/`. Replace SUMMARY.md with wave receipt.
- **Literal values:**
  - Rule 1: Auto-fix bugs (broken behavior, errors, incorrect output)
  - Rule 2: Auto-add missing critical functionality (missing error handling, null checks, missing auth on protected outputs)
  - Rule 3: Auto-fix blocking issues (broken imports, missing env var, wrong type) — EXCLUDED: package manager installs (pip install, any equivalent)
  - Rule 4: STOP on architectural changes (new DB table, major schema changes, switching libraries, breaking API changes)
  - Priority: "Rule 4 applies → STOP. Rules 1–3 apply → Fix automatically. Genuinely unsure → Rule 4."
  - Package install failure gate: `checkpoint:human-verify` with `gate="blocking-human"`. Do NOT auto-substitute alternative package names.
  - "No user permission needed for Rules 1–3. Track all deviations for wave receipt."
  - Scope boundary: "Only auto-fix issues DIRECTLY caused by the current task's changes. Pre-existing warnings or failures in unrelated files are out of scope."
- **Gate:** Executor receipts contain a `deviations` array listing every Rule 1–3 auto-fix applied.
- **Reference location:** `agents/gsd-executor.md` → `<deviation_rules>` block (lines 143–243)

---

### T1d — Executor: Analysis paralysis guard

- **What:** Add one paragraph to execution flow: 5+ consecutive Read/Grep/Glob calls with no Write/Edit/Bash = stuck.
- **Target:** `skills/executor/SKILL.md` — within execution flow, after task start
- **How:** Add exactly this paragraph, no adaptation needed:
- **Literal values:** "During task execution, if you make 5+ consecutive Read/Grep/Glob calls without any Edit/Write/Bash action: STOP. State in one sentence why you haven't written anything yet. Then either: 1. Write code (you have enough context), or 2. Report 'blocked' with the specific missing information. Do NOT continue reading. Analysis without action is a stuck signal."
- **Gate:** Executor execution flow now has an explicit stuck-detection mechanism.
- **Reference location:** `agents/gsd-executor.md` → `<analysis_paralysis_guard>` block (lines 245–253)

---

### T1e — Executor: Fix attempt limit

- **What:** Add a hard cap of 3 auto-fix attempts per task to the deviation rules section.
- **Target:** `skills/executor/SKILL.md` — within `## Deviation Rules` (added in T1c)
- **How:** Add as a named subsection at the end of the deviation rules block.
- **Literal values:** "Track auto-fix attempts per task. After 3 auto-fix attempts on a single task: STOP fixing — document remaining issues in the wave receipt under 'Deferred Issues'. Continue to the next task (or return checkpoint if blocked). Do NOT restart the build to find more issues."
- **Gate:** Wave receipts contain a `deferred_issues` field populated when the 3-attempt limit fires.
- **Reference location:** `agents/gsd-executor.md` → `<deviation_rules>` → FIX ATTEMPT LIMIT block (lines 235–239)

---

### T1f — Executor: Self-check before receipt write

- **What:** Add a self-check step after wave output, before `receipt-writer.py` is called. Check declared artifacts exist and commits resolve.
- **Target:** `skills/executor/SKILL.md` — final step in execution flow
- **How:** Add a named step "Self-Check" that runs two shell checks before the receipt-writer call. On failure: receipt status is PARTIAL, not PASS.
- **Literal values:** "Check created files exist: `[ -f 'path/to/file' ] && echo 'FOUND' || echo 'MISSING'`. Check commits exist: `git log --oneline --all | grep -q '{hash}'`. If self-check fails: mark wave PARTIAL in receipt, not PASS."
- **Gate:** A wave receipt marked PASS has passed the self-check. A wave with missing artifacts or unresolvable commits produces a PARTIAL receipt, not a false PASS.
- **Reference location:** `agents/gsd-executor.md` → `<self_check>` block (lines 641–657)

---

### T1g — Scope reduction prohibition (banned language list)

- **What:** Add `## Scope Reduction Prohibition` section to Decompose with the exact 14-phrase banned list. Flag the same language in Executor during implementation.
- **Target:** `skills/decompose/SKILL.md` — add section before wave plan finalization. `skills/executor/SKILL.md` — add note in deviation rules.
- **How:** Decompose checks its own task descriptions against the list before finalizing the wave plan. Executor flags any scope reduction language encountered during implementation and escalates to Rule 4.
- **Literal values:** Banned phrases: "v1", "v2", "simplified version", "static for now", "hardcoded for now", "future enhancement", "placeholder", "basic version", "minimal implementation", "will be wired later", "dynamic in future phase", "skip for now", "not wired to", "stub". Also: "too complex", "too difficult", "challenging" when used to justify omission. Time-estimates as scope justification: "would take", "hours", "days", "minutes" in sizing context. / If the spec says "calculate cost from billing table," the wave plan must deliver that. If scope is genuinely too large, Decompose must propose a wave split — not silently reduce scope.
- **Gate:** Guard scope reduction layer (T1k) enforces this at execution time. Decompose enforces at planning time.
- **Reference location:** `agents/gsd-planner.md` → `<scope_reduction_prohibition>` block (lines 76–107); `agents/gsd-plan-checker.md` → Dimension 7b (lines 346–388)

---

### T1h — Specificity test in Decompose

- **What:** Add a mandatory specificity check before finalizing any task in the wave plan.
- **Target:** `skills/decompose/SKILL.md` — add as a finalization gate after drafting each task
- **How:** Add the test as a named step. If the answer to the test question is "no," the task description must be revised before the wave plan is written.
- **Literal values:** "Test: Could a different agent instance execute this task without asking a clarifying question? If not, the task description is not specific enough. File paths, identifiers, API contracts, config keys, function signatures must be named explicitly. Too vague: 'Add authentication'. Just right: 'Add JWT auth with refresh rotation using jose library, store in httpOnly cookie, 15-min access / 7-day refresh'."
- **Gate:** Every task in the wave plan has been checked against the specificity test before the plan is written.
- **Reference location:** `agents/gsd-planner.md` → `<task_breakdown>` → Specificity section (lines 269–271)

---

### T1i — Verifier deferred item filtering

- **What:** Before reporting gaps, check if any identified gap is explicitly addressed in a later wave's declared outputs. Move it to a `deferred` list if so.
- **Target:** `skills/verifier/SKILL.md` — Step 1 spec compliance check, before gap list is finalized
- **How:** For each potential gap, check if the failed criterion corresponds to an output declared in a future wave. If clear specific evidence: move to deferred list. If vague: keep as real gap.
- **Literal values:** "Be conservative when matching. Only defer a gap when there is clear, specific evidence in a later wave's declared outputs. Vague or tangential matches should NOT cause a gap to be deferred — when in doubt, keep it as a real gap." Deferred items do NOT affect the status determination.
- **Gate:** Verifier VERIFICATION receipt distinguishes `gaps` from `deferred` items. Deferred items appear in a separate section and do not affect the PASS/FAIL verdict.
- **Reference location:** `agents/gsd-verifier.md` → Step 9b (lines 579–637)

---

### T1j — Override mechanism (YAML schema)

- **What:** Allow intentional deviations to be documented without failing verification. Add `## Override Protocol` to Verifier with exact YAML schema.
- **Target:** `skills/verifier/SKILL.md` — add `## Override Protocol` section
- **How:** Before marking any must-have as FAILED, check the wave plan or task card for a matching override entry. If found: mark `PASSED (override)` with the override reason included in evidence.
- **Literal values:** Override schema:
  ```yaml
  overrides:
    - must_have: "text of the Then clause or artifact"
      reason: "why this deviation is acceptable"
      accepted_by: "name"
      accepted_at: "2026-05-30T00:00:00Z"
  ```
  Matching: "normalize both strings to lowercase, strip punctuation, collapse whitespace; split into tokens; compute intersection — match if 80% token overlap in either direction." Technical terms (file paths, component names, API endpoints) have higher weight. Status on match: `PASSED (override)`.
- **Gate:** Override entries are auditable. Archive can compute: how many overrides exist across the task history.
- **Reference location:** `agents/gsd-verifier.md` → Step 3b (lines 183–215)

---

### T1k — Guard: Scope reduction detection layer

- **What:** Add a new Guard layer that scans wave task descriptions for the banned language list (see T1g) before execution. HARD block if found.
- **Target:** `skills/guard/SKILL.md` — add as a new pre-wave layer. `skills/guard/skill-rules.json` — register the new layer.
- **How:** Guard already runs multiple layers pre-wave. Add a new layer that reads each task description in the wave plan and scans against the banned phrase list. If found: return HARD block with the specific phrase and task ID. Decompose must revise before Guard will pass.
- **Literal values:** "ALWAYS BLOCKER. Scope reduction is never a warning." Fix path returned to Decompose: "Plans reduce N wave items. Options: 1. Revise to deliver fully (may increase wave count). 2. Split phase: [suggested grouping]."
- **Gate:** Guard PASS means wave task descriptions have been scanned for scope reduction language.
- **Reference location:** `agents/gsd-plan-checker.md` → Dimension 7b (lines 346–388)

---

## Tier 2 — Module-Level Augmentation

### T2a — Verifier: 4-level artifact verification

- **What:** Extend `skills/verifier/SKILL.md` Step 2 to add Levels 2–4 (Substantive, Wired, Data-flows) using the verification-patterns reference (T3b).
- **Target:** `skills/verifier/SKILL.md` — Step 2 artifact verification
- **How:** After verifying existence (Level 1), proceed to: Level 2 — check for stub patterns (universal list from verification-patterns.md); Level 3 — check if artifact is imported AND used (not orphaned); Level 4 — for wired artifacts that render dynamic data, trace the data source. Route all pattern detail to `engine/shared/references/verification-patterns.md`.
- **Literal values:** Final status table: Exists+Substantive+Wired+DataFlows=VERIFIED; Exists+Substantive+Wired-DataFlows=HOLLOW; Exists+Substantive-Wired=ORPHANED; Exists-Substantive=STUB; -Exists=MISSING. Level 4 only runs when: artifact passes Levels 1–3 AND renders dynamic data (components, pages, dashboards — not utilities or configs).
- **Consumers:** Routes pattern detail to `engine/shared/references/verification-patterns.md`.
- **Gate:** Verifier receipts include artifact status from the extended 5-status taxonomy. HOLLOW and ORPHANED are now distinct from STUB and MISSING.
- **Reference location:** `agents/gsd-verifier.md` → Steps 4+4b (lines 217–320)

---

### T2b — Decompose: Multi-source coverage audit

- **What:** Add a mandatory `## Coverage Audit` step before wave plan finalization. 4 source types must all be covered.
- **Target:** `skills/decompose/SKILL.md` — add as a named step before writing the wave plan
- **How:** Before writing the wave plan, audit each source type: GOAL (task card goal + acceptance criteria Then clauses), REQ (all requirement IDs in scope.md), RESEARCH (all research findings flagged as must-implement), CONTEXT (all locked decisions from task card Decisions section). Every item must be COVERED by at least one wave. Uncovered → add wave, return SPLIT RECOMMENDED, or document as explicitly deferred with justification.
- **Literal values:** "Every item must be COVERED by at least one wave. Uncovered items trigger one of: Add a wave to cover the item / Return `## SPLIT RECOMMENDED` to the orchestrator / Document as explicitly deferred with justification. Never finalize the wave plan silently with gaps."
- **Gate:** Wave plan output includes a coverage audit table. Uncovered items appear as a named section before finalization.
- **Reference location:** `agents/gsd-planner.md` → `<scope_reduction_prohibition>` → Multi-Source Coverage Audit block (lines 98–107)

---

### T2c — Skill size budget enforcement

- **What:** Extend `quality-floor-check.py` with a new gate checking SKILL.md line counts against size tiers.
- **Target:** `engine/shared/scripts/quality-floor-check.py` — add new gate in the existing gate checking loop
- **How:** For each SKILL.md, count lines. Compare against tier: XL (1700 lines) for top-level orchestrators (Executor, Autopilot), LARGE (1500) for multi-step planners (Decompose, Verifier), DEFAULT (1000) for focused single-purpose skills. If a skill exceeds its tier without a `## Reference Routing` table that offloads the excess: flag as FAIL.
- **Literal values:** Tiers: XL=1700, LARGE=1500, DEFAULT=1000. "When a skill exceeds its tier, the excess must be extracted to `rules/` reference files and routed via a `## Reference Routing` table. A SKILL.md over 1000 lines without a routing table that offloads the excess is flagged."
- **Gate:** `quality-floor-check.py` includes skill size in its gate outputs.
- **Reference location:** `docs/adr/0010-skill-surface-budget-module.md` + manual synthesis for WabbleSpec tier mapping

---

### T2d — Decompose: Context cost signals

- **What:** Add context cost estimation heuristics to Decompose's wave sizing guidance.
- **Target:** `skills/decompose/SKILL.md` — add after the wave sizing section
- **How:** When sizing waves, apply the file-count-to-context-percentage heuristics. Large waves (7+ files or new subsystem) trigger a split recommendation. This data also feeds the Synthesis S4 context-aware wave sizing item.
- **Literal values:** 0–3 files = ~10–15%; 4–6 files = ~20–30%; 7+ files = ~40%+ (split recommended); New subsystem = ~25–35%; Migration + data transform = ~30–40%; Pure config/wiring = ~5–10%.
- **Gate:** Wave plan entries include a `estimated_context_budget` field with the estimated percentage.
- **Reference location:** `agents/gsd-planner.md` → `<task_breakdown>` → Task Sizing → Context Cost signals table (lines 248–254)

---

## Tier 3 — New Shared Infrastructure

### T3a — Gate taxonomy reference

- **What:** New `engine/shared/references/gate-taxonomy.md` with 4 gate types, gate matrix, and exact selection heuristic.
- **Target:** new `engine/shared/references/gate-taxonomy.md`
- **Consumers:** `skills/guard/SKILL.md` and `skills/verifier/SKILL.md` via `## Reference Routing` tables
- **How:** Create the file with the 4 gate types (Pre-flight, Revision, Escalation, Abort), a gate matrix table mapping workflow steps to gate types, and the selection heuristic verbatim. Route `guard/SKILL.md` and `verifier/SKILL.md` to it.
- **Literal values:** Selection heuristic: "Start with Pre-flight. If the check happens after work is produced, it is Revision. If the Revision loop cannot resolve it, Escalate. If continuing is dangerous, Abort." Revision gate note: bounded by iteration cap + stall detection fires early (before cap).
- **Gate:** Guard and Verifier reference a shared gate vocabulary rather than each defining their own.
- **Reference location:** `get-shit-done/references/gates.md` (entire file)

---

### T3b — Verification patterns reference

- **What:** New `engine/shared/references/verification-patterns.md` with 4-level framework, 4 wiring patterns, and language-agnostic stub detection patterns.
- **Target:** new `engine/shared/references/verification-patterns.md`
- **Consumers:** `skills/verifier/SKILL.md` (primary), `skills/executor/SKILL.md` (self-check), `skills/guard/SKILL.md` (pre-wave artifact check)
- **How:** Create the file. Extract language-agnostic content only — strip all React/Next.js-specific grep patterns. Include: 4-level framework with final status table; 4 wiring patterns with positive and negative examples; universal stub detection patterns (TODO/FIXME/PLACEHOLDER comments, empty returns, hardcoded values where dynamic expected, log-only functions); when to require human verification (visual, real-time behavior, external service integration).
- **Literal values:** Universal stub patterns (language-agnostic): comment-based (`TODO`, `FIXME`, `PLACEHOLDER`, `not implemented`, `coming soon`); empty returns (`return null`, `return {}`, `return []`, `pass`, `...`); log-only (functions whose body is only `console.log` or `print`); hardcoded values where dynamic content expected. / 4 wiring patterns: Component→API: fetch/axios call exists AND response is used. API→Database: query exists AND result is returned (not static). Form→Handler: onSubmit calls API/mutation (not just preventDefault). State→Render: state variables appear in the output.
- **Gate:** Verifier routes wiring verification guidance to this file rather than inlining it. File must not contain any React/Next.js-specific patterns.
- **Reference location:** `agents/gsd-verifier.md` → Steps 4+4b + stub_detection_patterns; `docs/zh-CN/references/verification-patterns.md`

---

## Tier 4 — New Module Candidates

### T4a — Debug module

- **What:** New `skills/debug/SKILL.md` — a systematic debugging module with persistent debug file, structured reasoning checkpoint, knowledge base, and investigation technique library.
- **Target:** new `skills/debug/SKILL.md` + new `engine/shared/references/debug-file-protocol.md` + new `engine/shared/references/debug-investigation-techniques.md`
- **New artifacts:**
  - `skills/debug/SKILL.md` — skill entry point
  - `engine/shared/references/debug-file-protocol.md` — 5-section file structure, update rules
  - `engine/shared/references/debug-investigation-techniques.md` — 8 techniques (binary search, rubber duck, delta debugging, minimal reproduction, working backwards, differential debugging, observability first, follow the indirection)
  - Debug state path: `.wabblespec/state/debug/{slug}.md`
  - Knowledge base path: `.wabblespec/state/debug/knowledge-base.md`
- **How:** Adapt `agents/gsd-debugger.md` to WabbleSpec's skill format and path conventions. Replace `.planning/debug/` with `.wabblespec/state/debug/`. Replace `gsd-tools query commit` with `receipt-writer.py`. Replace `gsd-tools query state.load` with session-state.py. Preserve all behavioral logic exactly.
- **Literal values:**
  - 5-section structure: Current Focus (OVERWRITE), Symptoms (IMMUTABLE after gathering), Eliminated (APPEND), Evidence (APPEND), Resolution (OVERWRITE).
  - UPDATE FILE BEFORE ACTION, not after.
  - `next_action` must be concrete — "Add logging at line 47 of auth.py to observe token value before validation()" not "continue investigating".
  - Reasoning checkpoint 5 fields: `hypothesis`, `confirming_evidence`, `falsification_test`, `fix_rationale`, `blind_spots`. All 5 must have specific, concrete answers. If any is vague: return to investigation loop.
  - Knowledge base matching: 2+ keyword overlap (case-insensitive) = hypothesis candidate, not certainty.
  - Knowledge base append: happens only after human confirmation of fix, not earlier.
- **Gate:** `wabblespec.yaml` registers `debug` as a new module. Debug state path exists at `.wabblespec/state/debug/`.
- **Reference location:** `agents/gsd-debugger.md` (entire file)

---

### T4b — Context monitor hook

- **What:** New `engine/hooks/wabblespec-context-monitor.js` — PostToolUse hook that injects context warnings into agent conversation based on remaining context percentage.
- **Target:** new `engine/hooks/wabblespec-context-monitor.js` + `settings.local.json` registration
- **New artifacts:**
  - `engine/hooks/wabblespec-context-monitor.js`
  - Entry in `settings.local.json` under `hooks.PostToolUse`
- **How:** Adapt `hooks/gsd-context-monitor.js` to WabbleSpec. Replace `.planning/STATE.md` active-session detection with `.wabblespec/state/session/state.json` existence check. Replace `gsd-tools state record-session` with `session-state.py set context_exhaustion_pct <value>`. Keep all threshold values, debounce logic, and severity escalation exactly as in the reference.
- **Literal values:**
  - WARNING threshold: `remaining_percentage <= 35`
  - CRITICAL threshold: `remaining_percentage <= 25`
  - Debounce: 5 tool calls (`DEBOUNCE_CALLS = 5`)
  - Stale: ignore metrics older than 60 seconds (`STALE_SECONDS = 60`)
  - Severity escalation bypasses debounce: `severityEscalated = (currentLevel === 'critical' && warnData.lastLevel === 'warning')`
  - CRITICAL + active session: fire subprocess `session-state.py set context_exhaustion_pct <pct>` as breadcrumb
  - Path traversal guard: reject session_id containing `/\` or `..`
  - Bridge file shape: `{session_id, remaining_percentage, used_pct, timestamp}` at `${os.tmpdir()}/claude-ctx-${sessionId}.json`
  - Config disable: if `hooks.context_warnings === false` in state.json → exit 0
- **Gate:** Hook registered in `settings.local.json`. Session state includes `context_exhaustion_pct` field after any CRITICAL event.
- **Reference location:** `hooks/gsd-context-monitor.js` (entire file); `docs/context-monitor.md`

---

## Tier 5 — Architecture-Level

### T5a — Namespace routing layer

- **What:** Create 8–10 namespace router files that group WabbleSpec's 105 modules into topic clusters. Load namespace routers instead of all skills at session start.
- **Target:** New `commands/ns-*.md` files (8–10 files). `wabblespec.yaml` registration of namespace tier.
- **Adversarial review required:** Yes — architecture-level change affecting skill discovery.
- **Breaking change risk:** Possible — if users invoke skills directly by name, namespace routing must preserve that behavior.
- **Promotion condition:** A prototype must demonstrate that namespace routing does not break any existing skill invocation before this moves to execution.
- **Literal values:** Description format: pipe-separated keyword tags ≤60 characters. `requires:` frontmatter lists constituent skills. Routing table: `| User wants | Invoke |`. Proposed groupings:
  - `ns-l0-entry`: Recipe, Scope-Frame, Guard
  - `ns-l1-spec`: Specify, Propose, Brainstorm
  - `ns-l2-plan`: Decompose, Executor
  - `ns-l3-verify`: Verifier, Reviewer, Grader, Adversary, Inference-Guard
  - `ns-l4-memory`: Memory, Memory-Search, Memory-Mine, Dream, Entity-Graph, Provenance
  - `ns-l5-evolution`: Instinct, Synth, Blueprint, Augment, Benchmark, Forge
  - `ns-l6-platform`: All platform-* skills
  - `ns-l7-content`: Writer, Markdown, Copy, Translate, Proofread, Legal, Document, Changelog
  - `ns-l8-utility`: Analyze, Explore, Research-Log, Ref-Eval, Ref-Plan, Ref-Comp, Ref-Adopt, Audit, Clean
  - `ns-meta`: Archive, Sync, Recipe, Autopilot
- **Gate:** All 105 modules remain invocable by direct name. Namespace routers load correctly in session context.
- **Reference location:** `commands/gsd/ns-workflow.md` and other `ns-*.md` files; `docs/adr/0010-skill-surface-budget-module.md`

---

## Tier 6 — Synthesis

### S1 — Receipt-gated hypothesis testing

- **What:** Before writing the wave receipt, Executor includes a `reasoning_checkpoint` field documenting the hypothesis, evidence, and falsification test for the wave's approach.
- **Target:** `skills/executor/SKILL.md` (add reasoning_checkpoint to execution receipt), `engine/shared/scripts/receipt-writer.py` (add field to execution receipt type)
- **Reference contribution:** GSD's structured reasoning checkpoint (`agents/gsd-debugger.md` → 5-field YAML schema)
- **Project contribution:** WabbleSpec's receipt chain makes the checkpoint a queryable artifact; Archive can compute reasoning checkpoint coverage as a plan quality metric
- **Literal values:** 5-field schema: `hypothesis`, `confirming_evidence`, `falsification_test`, `fix_rationale`, `blind_spots`. All 5 must have concrete answers.
- **Feasibility gate:** Confirm `receipt-writer.py` accepts arbitrary JSON extension fields without schema rejection before implementing.

---

### S2 — Deviation receipt as Instinct signal

- **What:** Auto-fixed deviations (Rules 1–3) write deviation receipts linked to wave receipts. Instinct reads deviation aggregates to identify which planning templates consistently under-specify work.
- **Target:** `engine/shared/scripts/receipt-writer.py` (new `--type deviation`), `skills/executor/SKILL.md` (deviation receipt write step), `skills/instinct/SKILL.md` (add deviation aggregate as Instinct input)
- **Reference contribution:** GSD Executor's SUMMARY.md deviation documentation with Rule N tagging
- **Project contribution:** WabbleSpec's Instinct → Synth → Blueprint evolution chain converts per-task observations into planning improvements
- **Literal values:** Deviation receipt fields: `rule` (1/2/3), `task_id`, `wave_id`, `trigger_description`, `fix_applied`, `files_modified`. Linked to wave receipt via `wave_receipt_id`.
- **Feasibility gate:** Instinct currently ingests seed run receipts. Confirm it can ingest a new receipt type without impacting existing signal sources.

---

### S3 — Entity-graph as wave dependency input

- **What:** When Decompose is designing waves, query the entity-graph for cross-module dependency context. Force co-location of entities that reference each other and are being modified in different waves.
- **Target:** `skills/decompose/SKILL.md` — add entity-graph query step alongside memory drawer loading step
- **Reference contribution:** GSD planner's graphify integration (`agents/gsd-planner.md` → `<step name="load_graph_context">`)
- **Project contribution:** WabbleSpec's entity-graph (`.wabblespec/state/memory/entity-graph.json`) already tracks module relationships
- **Literal values:** Query command: `python .wabblespec/entity-graph.py query <keyword> --format json`. If graph stale: annotate "treat semantic relationships as approximate" inline. Budget: `--budget 2000` equivalent (limit output tokens).
- **Feasibility gate:** Confirm entity-graph.py supports a `query` subcommand with `--format json` output before implementing.

---

### S4 — Context-aware wave sizing

- **What:** Decompose adds a `recommended_wave_context_budget` field to each wave plan entry. Guard checks this field before spawning the wave. If exceeded: SOFT warning recommending Economy mode.
- **Target:** `skills/decompose/SKILL.md` (add budget estimation to wave plan output), `skills/guard/SKILL.md` (add budget check as new Guard layer), `skills/economy/rules/cold-start.md` (route heuristics table here — see T1b which adds this already)
- **Reference contribution:** GSD planner's context cost heuristics (file count → context percentage table)
- **Project contribution:** WabbleSpec's Guard (pre-wave) + Economy module create infrastructure to enforce budget before execution starts
- **Literal values:** Budget field name: `recommended_wave_context_budget`. Guard check: if field value > 50% → SOFT warning "This wave is estimated at X% context. Executor should operate in Economy mode (DEGRADING tier)."
- **Feasibility gate:** T1b (context degradation tiers) and T2d (context cost signals in Decompose) must be implemented first. T4b (context monitor) provides the runtime data that validates the estimates.

---

## Watch Only

- **Phase-lifecycle fields in session state** (active_wave, next_wave, wave_progress.percent in state.json + statusline update): Depends on T4b context monitor implementation validating the state.json extension pattern. Promote when T4b is complete and working.
- **Behavioral profiling → skill adaptive language** (2 dimensions as drawer schema, profiler reads in Specify/Decompose/Reviewer): Depends on establishing 50+ curated drawers (existing Phase 5 gate). Promote when drawer gate is cleared.

---

## Priority Implementation Order

Ordered list of Tier 1–4 items ready to implement now, in recommended sequence.

| Priority | Item | Tier | Target | Why first |
|---|---|---|---|---|
| 1 | T1a — Verifier stall detection | 1 | `skills/verifier/SKILL.md` | One paragraph; already queued; no dependencies |
| 2 | T3a — Gate taxonomy reference | 3 | new `engine/shared/references/gate-taxonomy.md` | New file; unblocks gate vocabulary for all items below |
| 3 | T3b — Verification patterns reference | 3 | new `engine/shared/references/verification-patterns.md` | New file; unblocks T2a (4-level verifier upgrade) |
| 4 | T1b — Context degradation tiers | 1 | `skills/economy/rules/cold-start.md` | Append-only to existing file; closes most-referenced guidance gap; also needed by T2d and S4 |
| 5 | T1c — Executor deviation rules | 1 | `skills/executor/SKILL.md` | Same file as T1d/T1e/T1f; write all four together |
| 6 | T1d — Executor analysis paralysis guard | 1 | `skills/executor/SKILL.md` | Same file as T1c; write together |
| 7 | T1e — Executor fix attempt limit | 1 | `skills/executor/SKILL.md` | Same file as T1c; write together |
| 8 | T1f — Executor self-check | 1 | `skills/executor/SKILL.md` | Same file as T1c; write together |
| 9 | T1g — Scope reduction prohibition | 1 | `skills/decompose/SKILL.md`, `skills/executor/SKILL.md` | Closes the most insidious planner failure class |
| 10 | T1h — Specificity test | 1 | `skills/decompose/SKILL.md` | Same file as T1g; write together |
| 11 | T2a — Verifier 4-level upgrade | 2 | `skills/verifier/SKILL.md` | Requires T3b (verification patterns reference) |
| 12 | T1i — Verifier deferred item filtering | 1 | `skills/verifier/SKILL.md` | Same file as T2a; write together |
| 13 | T1j — Override mechanism | 1 | `skills/verifier/SKILL.md` | Same file as T2a and T1i; write together |
| 14 | T2b — Multi-source coverage audit | 2 | `skills/decompose/SKILL.md` | Same file as T1g/T1h; add after those |
| 15 | T2d — Context cost signals | 2 | `skills/decompose/SKILL.md` | Same file; add after T2b |
| 16 | T1k — Guard scope reduction detection | 1 | `skills/guard/SKILL.md` | Adds enforcement to complement T1g |
| 17 | T2c — Skill size budget enforcement | 2 | `quality-floor-check.py` | Standalone script edit; no dependencies |
| 18 | T4a — Debug module | 4 | new `skills/debug/SKILL.md` + references | New capability; no implementation dependencies |
| 19 | T4b — Context monitor hook | 4 | new `engine/hooks/wabblespec-context-monitor.js` | New hook; depends on understanding bridge file architecture |

---

## Execution Notes

**Sequencing constraints:**
- T3a and T3b (new reference files) must be created before T2a (4-level verifier upgrade) — T2a routes to them.
- T1b (context degradation tiers) should be created before T2d (context cost signals in Decompose) — T2d routes its heuristics table to economy/rules/cold-start.md.
- T1c/T1d/T1e/T1f are all in `skills/executor/SKILL.md` — write in one wave to avoid repeated file edits.
- T1g/T1h/T2b/T2d are all in `skills/decompose/SKILL.md` — write in one wave.
- T2a/T1i/T1j are all in `skills/verifier/SKILL.md` — write in one wave.

**Items that must NOT run in parallel:**
- Do not implement T2a before T3b is complete (routing target must exist).
- Do not implement T4b before T4a (context monitor references session-state.py patterns established in the debug module integration).

**Synthesis gates:** S3 depends on entity-graph.py query capability being confirmed. S4 depends on T1b + T2d being complete. S1 and S2 depend on the receipt-writer.py extension pattern being validated.

After implementation, run `/ref-comp get-shit-done-redux` to audit execution fidelity.
