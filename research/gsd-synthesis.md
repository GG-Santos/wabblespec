# GSD Redux → WabbleSpec Synthesis

**Source reference:** `C:\Users\Kirsten\Downloads\Orchestrator\get-shit-done-redux`
**Ref-eval report:** `research/ref-eval/get-shit-done-redux.md`
**Ref-plan:** `research/ref-plan/get-shit-done-redux.md`
**Date:** 2026-05-29

Full breakdown of learnings from the GSD Redux study and how each applies to WabbleSpec. Organized by impact tier. Every item names an exact target file.

---

## Tier 1 — Immediate, additive, low-risk

Behavioral rules added to existing skills without restructuring anything.

### Executor: 4-rule deviation framework

GSD Executor has explicit rules for everything discovered during implementation that was not in the plan. WabbleSpec Executor has no structured deviation handling — the agent improvises.

**Proposed rules for WabbleSpec Executor:**

| Rule | Trigger | Action |
|---|---|---|
| 1 — Auto-fix bugs | Code does not work as intended | Fix inline, track as deviation in wave receipt |
| 2 — Auto-add critical missing functionality | Missing error handling, null checks, missing auth on protected outputs | Fix inline, track |
| 3 — Auto-fix blocking issues | Broken import, missing env var, wrong type — **exclude package installs** | Fix inline |
| 4 — Escalate architectural changes | New table, changed schema, switched library | Stop → return CHECKPOINT to Executor orchestrator |

Package install failures in Rule 3 must gate to a human checkpoint (`checkpoint:human-verify`) with the package name for legitimacy review. This is supply-chain defense.

Priority order: Rule 4 wins if triggered (architectural change). Rules 1–3 apply next. If genuinely unsure → Rule 4.

**Target:** `executor/SKILL.md` — add a `## Deviation Rules` section.

---

### Executor: Analysis paralysis guard

If the Executor makes 5+ consecutive Read/Grep/Glob calls with no Write/Edit/Bash action, it is stuck. Force a decision: act on sufficient context or report blocked with the specific missing information. Do not continue reading.

**Target:** `executor/SKILL.md` — one paragraph in execution flow.

---

### Executor: Self-check before receipt write

After producing wave output, before writing the wave receipt, verify:
- Declared artifacts exist at their paths
- If commits were required, the commit hash resolves in git log

If self-check fails, mark wave PARTIAL in the receipt, not PASS.

**Target:** `executor/SKILL.md` — adds to existing final-step sequence.

---

### Verifier: Stall detection in REVISE loop

WabbleSpec Verifier allows up to 3 REVISE cycles but does not detect stalls. GSD escalates early when the issue count does not decrease between consecutive iterations.

**Add:** after each REVISE cycle, compare the issue count to the previous cycle. If count did not decrease, escalate to BLOCKED immediately without waiting for the iteration cap.

**Target:** `verifier/SKILL.md` — REVISE loop section.

---

### Verifier: Deferred item filtering

Not every gap is a real gap. If a "Then" clause artifact is declared in a later wave's `outputs`, it is deferred, not failed. Extend the existing `deferred_then_clauses` logic to also filter spec compliance failures that correspond to outputs declared in future waves.

**Target:** `verifier/SKILL.md` — Step 1 spec compliance check.

---

### Specify + Executor: Scope reduction prohibition

GSD bans this language from task action descriptions. These phrases indicate silent scope reduction — delivering less than the spec requires without surfacing it as a deviation.

**Banned language list:**
- `v1`, `v2`, `simplified version`
- `static for now`, `hardcoded for now`
- `future enhancement`, `placeholder`
- `basic version`, `minimal implementation`
- `will be wired later`, `dynamic in future phase`
- `skip for now`, `not wired to`, `stub`
- `too complex`, `too difficult`, `challenging` (when used to justify omission)

If the spec says "calculate cost from billing table," the wave plan must deliver that. If scope is genuinely too large, Decompose must propose a wave split — not silently reduce scope.

**Target:** `decompose/SKILL.md` (planner checks its own task descriptions) + `executor/SKILL.md` (flags scope reduction language encountered during implementation).

---

### Specify + Decompose: Specificity test

Before finalizing any task in the wave plan, apply one rule: "Could a different agent instance execute this task without asking a clarifying question?" If not, the task description is not specific enough. File paths, identifiers, API contracts, config keys, function signatures must be named explicitly.

Examples:
- Too vague: "Add authentication"
- Just right: "Add JWT auth with refresh rotation using jose library, store in httpOnly cookie, 15-min access / 7-day refresh"

**Target:** `decompose/SKILL.md`.

---

## Tier 2 — Module-level augmentation

### Verifier: 4-level artifact verification

WabbleSpec Verifier currently checks declared artifact existence. GSD adds three more levels, each catching a distinct failure class.

| Level | Question | What it catches |
|---|---|---|
| 1 — Exists | File at declared path? | Missing file |
| 2 — Substantive | Real implementation, not stub? | Placeholder code |
| 3 — Wired | Connected to rest of system? | Orphaned artifact |
| 4 — Functional / Data-flows | Actually produces real output when invoked? | Hollow wiring |

**Universal stub patterns (language-agnostic) to detect:**
- Comment-based: `TODO`, `FIXME`, `PLACEHOLDER`, `not implemented`, `coming soon`
- Empty returns: `return null`, `return {}`, `return []`, `pass`, `...`
- Log-only: functions whose body is only `console.log` or `print`
- Hardcoded values where dynamic content expected

**Wiring patterns to verify:**
- Component → API: fetch/axios call exists and uses the response
- API → Database: query exists and result is returned (not a static return)
- Form → Handler: onSubmit calls the API/mutation (not just `preventDefault`)
- State → Render: state variables appear in the output

Level 4 (data-flow trace): for artifacts that pass Levels 1–3 and render dynamic data, verify the data source actually produces real output (not empty array, not hardcoded value, not disconnected prop).

**Target:** New `engine/shared/references/verification-patterns.md` routed from `verifier/SKILL.md`.

---

### Verifier: Override mechanism

Allow intentional deviations to be documented without failing verification. When a "Then" clause cannot be satisfied for a legitimate reason (external dependency unavailable, explicitly deferred by the team), an override entry in the wave plan or task card marks it `PASSED (override)` with `reason`, `accepted_by`, and `timestamp`. This makes deliberate technical debt auditable rather than hidden.

Override format (YAML in wave plan or task card):

```yaml
overrides:
  - must_have: "text of the Then clause or artifact"
    reason: "why this deviation is acceptable"
    accepted_by: "name"
    accepted_at: "2026-05-29T00:00:00Z"
```

**Target:** `verifier/SKILL.md` — add `## Override Protocol` section.

---

### Guard: Scope reduction detection (new layer)

GSD's plan-checker scans task descriptions for banned language before execution. WabbleSpec Guard already runs 5 layers pre-wave. Add a new layer that scans wave task descriptions for the scope reduction language list (see Tier 1 above). If found, HARD block — Decompose must revise before Guard will pass.

**Target:** `guard/SKILL.md` and `guard/skill-rules.json`.

---

### Guard: Cross-wave data contract check

GSD's dimension 9 catches incompatible data transformations between plans running in the same phase. WabbleSpec's Guard runs before each wave but does not check whether this wave's transformations conflict with a future wave's expected inputs.

Add: when Guard runs for Wave N, scan Wave N+1's declared inputs against Wave N's declared outputs. If Wave N strips/sanitizes data that Wave N+1 expects in original form (e.g., Wave N normalizes a field that Wave N+1 needs raw), flag as SOFT warning.

**Target:** `guard/SKILL.md` — extend Layer 3 invariant check or add new Layer 6.

---

### Decompose: Multi-source coverage audit

GSD Planner audits 4 source types before finalizing plans. WabbleSpec Decompose breaks tasks into waves but does not formally audit that every source item has been covered. Add a mandatory coverage audit step before finalizing the wave plan.

**Four sources to audit:**

| Source | Content |
|---|---|
| GOAL | Task card goal and acceptance criteria "Then" clauses |
| REQUIREMENTS | All requirement IDs in scope.md mapped to at least one wave |
| RESEARCH | All research findings flagged as must-implement |
| CONTEXT | All locked decisions from task card `Decisions` section |

Every item must be COVERED by at least one wave. Uncovered items trigger one of:
- Add a wave to cover the item
- Return `## SPLIT RECOMMENDED` to the orchestrator
- Document as explicitly deferred with justification

Never finalize the wave plan silently with gaps.

**Target:** `decompose/SKILL.md` — add a `## Coverage Audit` step before the wave plan is finalized.

---

### Decompose: Architectural Responsibility Map

Before designing the wave breakdown, map each capability the task delivers to its architectural tier. This prevents misassignment — auth logic placed in the wrong layer, data persistence in the wrong module.

For WabbleSpec's framework context, the tiers are:

| Tier | Examples |
|---|---|
| Skill layer | SKILL.md files, skill-rules.json |
| Script layer | Python scripts in `engine/shared/scripts/` |
| Hook layer | JS hooks in `engine/hooks/` |
| State layer | `.wabblespec/state/` files and schemas |
| Schema layer | JSON schemas in `engine/shared/schemas/` |

Produce an `## Architectural Responsibility Map` table in the wave plan. This is consumed by Guard for tier-compliance checking and by Verifier for wiring verification.

**Target:** `decompose/SKILL.md` — add as Step 1 of the planning protocol.

---

### Economy: Context degradation tiers

Add named tiers with specific read-depth rules. The 4 tiers replace vague "context getting heavy" warnings with actionable behavioral changes.

| Tier | Context Used | Behavior |
|---|---|---|
| PEAK | 0–30% | Full reads, spawn subagents freely, inline results |
| GOOD | 30–50% | Normal ops, prefer frontmatter reads, delegate aggressively |
| DEGRADING | 50–70% | Frontmatter-only reads, minimal inlining, warn user about budget |
| POOR | 70%+ | Emergency: checkpoint immediately, no new reads unless critical |

**Read depth by context window:**

| Context Window | Subagent output reading | Receipt bodies | Prior wave receipts |
|---|---|---|---|
| < 500k tokens (default) | Frontmatter only | Frontmatter only | Current wave only |
| ≥ 500k tokens (1M models) | Full body permitted | Full body permitted | Current wave only |

**Three named early warning signs** (appear before panic threshold fires):
- **Silent partial completion** — agent claims PASS but artifacts are incomplete; self-check catches this
- **Increasing vagueness** — agent uses "appropriate handling" or "standard patterns" instead of specific code
- **Skipped steps** — reports 5 of 8 declared checks from the wave plan

**Pre-wave MCP audit checklist:**
- Browser/playwright tools enabled? Disable if no UI work in this wave.
- Platform-specific tools enabled? Disable if not needed.
- Stale cross-project MCPs? Remove leftover servers from other projects.
- Duplicate servers providing similar tools? Keep one.

Each disabled MCP removes its schema from every subsequent turn for the rest of the session. MCP schemas can cost 20k+ tokens per turn each.

**Target:** `economy/rules/cold-start.md` — append two sections.

---

## Tier 3 — New reference infrastructure

Shared reference files that multiple modules route to. These reduce duplication and enforce consistent vocabulary.

### `engine/shared/references/gate-taxonomy.md`

The 4-type gate vocabulary adapted to WabbleSpec modules.

| Gate type | Selection rule | WabbleSpec examples |
|---|---|---|
| Pre-flight | Before any work starts; cheap and deterministic | Guard Layers 1–5, I1 locked-spec check |
| Revision | After a producer step where quality varies; bounded by iteration cap | Verifier REVISE loop (max 3 cycles) |
| Escalation | When automated resolution is impossible; pause and wait for human input | Attestation, BLOCKED verdict, stall detected |
| Abort | When continuing would cause damage or produce meaningless output | CONTEXT_EXHAUSTION, STALENESS_VIOLATION, I4 violation |

**Selection heuristic:** Start with Pre-flight. If the check happens after work is produced, it is Revision. If the Revision loop cannot resolve it, Escalate. If continuing is dangerous, Abort.

**Target:** New file. Route `guard/SKILL.md` and `verifier/SKILL.md` to it.

---

### `engine/shared/references/verification-patterns.md`

Already queued in ref-plan Phase 1. Contains:
- 4-level framework (Exists → Substantive → Wired → Functional)
- Universal stub detection patterns
- Wiring verification patterns (component→API, API→database, form→handler, state→render)
- When to require human verification (visual, real-time behavior, external service integration)

**Target:** New file. Route `verifier/SKILL.md` to it.

---

### `engine/shared/references/context-degradation.md`

Already queued in ref-plan Phase 1 (currently targeting `economy/rules/cold-start.md` directly). If it grows, extract to a dedicated reference.

Contains: tier table, read-depth table, 3 named warning signs, MCP audit checklist.

**Target:** New file or section in `economy/rules/cold-start.md`. Route `economy/SKILL.md`, `executor/SKILL.md`, `autopilot/SKILL.md`.

---

## Tier 4 — New module candidates

### Debug module (new)

GSD has a complete debugging system with persistent state, hypothesis testing, and a knowledge base. WabbleSpec has no Debug skill. This gap matters for framework-development sessions where diagnosing failures in hooks, scripts, or skill logic requires systematic investigation.

**Core design (WabbleSpec-native):**

**Persistent debug file** at `.wabblespec/state/debug/{slug}.md`:

```
## Current Focus     ← OVERWRITE on each update — reflects NOW
## Symptoms          ← Written during gathering, then IMMUTABLE
## Eliminated        ← APPEND only — prevents re-investigating
## Evidence          ← APPEND only — facts discovered
## Resolution        ← OVERWRITE as understanding evolves
```

Critical rule: update the file BEFORE taking action, not after. If context resets mid-action, the file shows what was about to happen.

**Knowledge base** at `.wabblespec/state/debug/knowledge-base.md` — keyword-matched at session start, appended on resolve. One entry per resolved session with: error patterns, root cause, fix, files changed.

**Investigation protocol:**
- Phase 0: knowledge base keyword match (2+ word overlap → hypothesis candidate, not certainty)
- Phase 1: evidence gathering (read files, run scripts, observe behavior)
- Phase 2: form ONE specific, falsifiable hypothesis
- Phase 3: test ONE hypothesis at a time
- Phase 4: CONFIRMED → structured reasoning checkpoint before fix / ELIMINATED → new hypothesis

**Structured reasoning checkpoint** (mandatory before any fix):
```yaml
reasoning_checkpoint:
  hypothesis: "[exact statement — X causes Y because Z]"
  confirming_evidence:
    - "[specific evidence item]"
  falsification_test: "[what specific observation would prove this wrong]"
  fix_rationale: "[why the proposed fix addresses the root cause, not the symptom]"
  blind_spots: "[what has not been tested that could invalidate this hypothesis]"
```

All 5 fields must be filled with specific, concrete answers. If any is vague: root cause is not confirmed — return to Phase 2.

**Modes:**
- `find_root_cause_only` — diagnose without fixing (useful for Guard/Verifier triage)
- `find_and_fix` (default) — full cycle through human verification

**Investigation techniques reference:**
- Binary search (large codebase, many files)
- Delta debugging (binary search over commit/config/input space)
- Minimal reproduction (strip away everything until smallest code reproduces bug)
- Working backwards (from correct output, trace what must be true)
- Differential debugging (worked before, doesn't now — what changed?)
- Observability first (add logging before changing behavior)
- Follow the indirection (paths/URLs/keys constructed from variables — trace both producer and consumer)
- Rubber duck (explain the problem aloud — spot assumption errors mid-explanation)
- Git bisect (`git bisect start`, `git bisect bad`, `git bisect good <hash>`)

**Target:** New `debug/SKILL.md` + `debug/skill-rules.json` + `engine/shared/references/debug-investigation-techniques.md` + `engine/shared/references/debug-file-protocol.md`.

---

### Context monitor hook (new)

GSD has a two-part bridge: the statusline writes a metrics file per session to `/tmp/claude-ctx-{session}.json` on every statusLine event; a PostToolUse hook reads it after each tool call and injects `additionalContext` warnings when context is running low.

WabbleSpec has a statusline badge (`[WS task-id w:N/M]`) but no agent-facing context injection. The agent does not know its own context level unless it explicitly asks.

**Proposed behavior:**

Thresholds:
- WARNING (remaining ≤ 35%): "Context getting limited. Avoid starting new complex work."
- CRITICAL (remaining ≤ 25%): "Context nearly exhausted. Checkpoint progress immediately."

On CRITICAL with an active WabbleSpec task: fire-and-forget subprocess writes the context percentage to `.wabblespec/state/session/state.json` under `context_exhaustion_pct`. This creates a breadcrumb for `/resume`.

Debounce: 5 tool calls between repeated same-level warnings. Severity escalation (WARNING → CRITICAL) bypasses debounce. Always advisory — never imperative.

**Target:** New hook in `.wabblespec/engine/hooks/wabblespec-context-monitor.js` + registration in `settings.local.json`.

---

### Supply-chain Guard layer (thin, new)

For WabbleSpec tasks that install Python packages (e.g., `pip install` in skill scripts or daemon scripts), add a Guard check: before any wave that declares a package install task, require a legitimacy check. Protocol:

1. Run `slopcheck install <pkgs> --json` if slopcheck is available
2. `[SLOP]` → remove from recommendation, block wave
3. `[SUS]` → flag, require human checkpoint before install
4. `[OK]` → proceed
5. Slopcheck unavailable → mark all packages `[ASSUMED]`, gate each behind human checkpoint

Cross-ecosystem verification: use the correct registry command for the language (npm/pip/cargo). A Python package that passes `npm view` is not verified on PyPI.

**Target:** Guard Layer 6, or a new pre-execution check in the daemon orchestrator config.

---

## Tier 5 — Architecture-level opportunities

### Namespace meta-skill routing for 103 skills

GSD reduced a 65-skill flat listing to 6 namespace routers at approximately 40% the token cost. WabbleSpec has 103 skills loaded eagerly each turn. The cost compounds: every turn every skill description contributes to the context load.

**Proposed namespace grouping (8–10 routers):**

| Namespace | Skills |
|---|---|
| `ns-l0-entry` | Recipe, Scope-Frame, Guard |
| `ns-l1-spec` | Specify, Propose, Brainstorm |
| `ns-l2-plan` | Decompose, Executor |
| `ns-l3-verify` | Verifier, Reviewer, Grader, Adversary, Inference-Guard |
| `ns-l4-memory` | Memory, Memory-Search, Memory-Mine, Dream, Entity-Graph, Provenance |
| `ns-l5-evolution` | Instinct, Synth, Blueprint, Augment, Benchmark, Forge |
| `ns-l6-platform` | All platform-* skills (cli, web, api-service, mobile, desktop, etc.) |
| `ns-l7-content` | Writer, Markdown, Copy, Translate, Proofread, Legal, Document, Changelog |
| `ns-l8-utility` | Analyze, Explore, Research-Log, Ref-Eval, Ref-Plan, Ref-Comp, Ref-Adopt, Audit, Clean |
| `ns-meta` | Archive, Sync, Recipe, Autopilot (orchestration layer) |

Each namespace router is ~8 lines: a description (pipe-separated keyword tags ≤60 chars for token efficiency) and a routing table. The model sees ~10 routers at session load instead of 103 skill listings. Every concrete skill remains directly invocable via `/skill-name`.

**Target:** New `commands/ns-*.md` files adapted to WabbleSpec's Skill-tool invocation model. Add to `wabblespec.yaml` as a new module tier.

---

### Phase-lifecycle fields in session state

GSD's STATE.md carries `active_phase`, `next_action`, `next_phases`, and `progress.percent` in YAML frontmatter. The statusline reads these in real time and displays "Phase 4.5 executing" or "next execute-phase 4.5" without querying the full file.

WabbleSpec's `state.json` has `active_module` and basic wave info but the statusline only shows `[WS task-id w:N/M]`. Extending state.json to carry richer lifecycle fields enables a more informative statusline and allows the prompt-guard hook to emit more precise wave-progress nudges.

**Proposed state.json additions:**

```json
{
  "active_wave": "wave-2",
  "active_module": "executor",
  "next_action": "verifier",
  "next_wave": "wave-3",
  "wave_progress": {
    "completed": 2,
    "total": 5,
    "percent": 40
  }
}
```

**Target:** `session-state.py` schema extension + `wabblespec-statusline.ps1` update to read and display `wave_progress.percent` as a bar and `next_action` when idle.

---

### Skill size budget enforcement

GSD enforces workflow file size via an automated test (`tests/workflow-size-budget.test.cjs`). WabbleSpec SKILL.md files grow without constraint, and large skills degrade performance and increase context load.

**Proposed size tiers:**

| Tier | Line limit | Used for |
|---|---|---|
| XL | 1700 | Top-level orchestrators (Executor, Autopilot) |
| LARGE | 1500 | Multi-step planners (Decompose, Verifier) |
| DEFAULT | 1000 | Focused single-purpose skills |

When a skill exceeds its tier, the excess must be extracted to `rules/` reference files and routed via a `## Reference Routing` table. A SKILL.md over 1000 lines without a routing table that offloads the excess is flagged by quality-floor-check.

**Target:** `quality-floor-check.py` — add new gate checking SKILL.md line counts against tier. `skill-creator/SKILL.md` (skill-creator:skill-creator) — add size budget guidance section.

---

### Thinking-model integration references

GSD has 5 reference files specifying when and how to invoke extended thinking at decision points across workflow contexts (debug, planning, execution, research, verification). WabbleSpec uses capability descriptors (I6) but has no guidance on when higher-reasoning invocation is warranted within a skill.

**Proposed:** Single `engine/shared/references/thinking-model-integration.md` with 5 sections.

| Section | Decision triggers for extended reasoning |
|---|---|
| Research | Choosing between competing approaches, evaluating architectural tradeoffs |
| Planning (Decompose) | Wave dependency graph with circular dependencies, ambiguous scope boundaries |
| Execution | Encountering Rule 4 deviation (architectural change), checkpoint type classification |
| Verification | Ambiguous stub/wiring verdict where evidence is incomplete |
| Debug | Forming hypotheses when multiple plausible causes remain after evidence gathering |

**Target:** New reference file. Route `decompose/SKILL.md`, `verifier/SKILL.md`, `executor/SKILL.md` to it.

---

## Tier 6 — Synthesis: Ideas unique to the WabbleSpec × GSD combination

These are not direct GSD extractions but new patterns made possible by combining GSD's behavioral designs with WabbleSpec's receipt-gated architecture.

---

### Receipt-gated hypothesis testing

WabbleSpec's receipt chain (Research → Plan → Execution → Verify → Archive) combined with GSD's Structured Reasoning Checkpoint creates a new pattern: before writing the execution receipt, the Executor must include a `reasoning_checkpoint` field in the receipt JSON documenting:

- What the wave was supposed to do (from wave plan)
- What evidence confirms it was done (artifact existence + substantive check)
- What would have falsified the approach (from task card acceptance criteria)

This makes the receipt chain not just a completion gate but an evidence chain. Archive can then compute coverage: what fraction of execution receipts have well-documented reasoning checkpoints vs. bare PASS verdicts.

---

### Claim provenance in plan receipts

GSD tags research claims `[VERIFIED]`, `[CITED]`, or `[ASSUMED]`. WabbleSpec has receipts with `confidence` scores. These could be merged: every assertion in a plan receipt carries a provenance tag. The Verifier checks that HIGH-confidence assertions in the plan receipt are substantiated by wave output artifacts. Unsubstantiated HIGH-confidence claims in the plan receipt become a FAIL signal — the confidence was not earned.

---

### Deviation receipt (autonomous record-keeping)

GSD Executor tracks all deviations from the plan in SUMMARY.md. WabbleSpec could introduce a `deviation-receipt.py` (via `receipt-writer.py --type deviation`) that records auto-fixed deviations (Rule 1–3) as standard JSON linked to the wave receipt. The Verifier and Archive aggregate deviation receipts to compute drift-from-spec metrics across the project lifecycle. Over many tasks, this produces an Instinct signal: which task types consistently require auto-fixes → which planning templates are underspecified.

---

### Context-aware wave sizing

GSD Planner sizes tasks to fit within 50% of a single agent's context window. WabbleSpec's Decompose does not consider context window when sizing waves. Combine GSD's context-cost estimation heuristics (file count, subsystem count, new code vs modification) with WabbleSpec's wave complexity scoring to produce a `recommended_wave_context_budget` field in each wave plan entry. Guard checks this budget field is not exceeded before spawning the wave. If it is, Guard returns SOFT warning recommending the Executor operate in economy mode for this wave.

Heuristics to expose in `decompose/SKILL.md`:

| Signal | Estimated context cost |
|---|---|
| 0–3 files modified | ~10–15% |
| 4–6 files modified | ~20–30% |
| 7+ files modified | ~40%+ (split recommended) |
| New subsystem | ~25–35% |
| Migration + data transform | ~30–40% |
| Pure config/wiring | ~5–10% |

---

### Knowledge graph × memory layer

GSD's graphify builds a semantic knowledge graph of the project for dependency-aware planning. WabbleSpec has an entity-graph + memory drawers. These serve partially overlapping purposes. The synthesis: use WabbleSpec's entity-graph as a planning input.

When Decompose is designing waves, query the entity-graph for cross-module dependency context before assigning wave boundaries. If entity A is referenced by entity B and both are being modified in different waves, force them into the same wave or add an explicit dependency edge to the wave plan. This uses an existing WabbleSpec artifact (entity-graph) to provide the same dependency-context benefit GSD gets from graphify, without requiring a new tool.

Command: `python .wabblespec/entity-graph.py query <keyword> --format json`

**Target:** `decompose/SKILL.md` — add entity-graph query step alongside the existing memory drawer loading step.

---

### Behavioral profiling → skill adaptive language

GSD profiles users across 8 behavioral dimensions (communication style, decision patterns, debugging approach, UX preferences, vendor/technology choices, frustration triggers, learning style, explanation depth) and adapts discuss-phase language accordingly. WabbleSpec has user preferences in memory drawers but does not adapt skill output language.

Memory module already maintains user drawers. Extension: add a `user-profile` drawer schema capturing two dimensions: `communication_style` (terse vs verbose) and `technical_depth` (implementation-level vs high-level). Skills that produce human-facing output — Specify, Decompose (when presenting wave plan for approval), Reviewer — read the profile drawer and adapt their output level.

**Target:** New drawer schema in `engine/shared/schemas/`. Add profile-read step to `specify/SKILL.md`, `decompose/SKILL.md`, and `reviewer/SKILL.md`.

---

## Implementation priority order

Based on impact-to-effort ratio and dependency structure:

| Priority | Item | Target | Why |
|---|---|---|---|
| 1 | Stall detection | `verifier/SKILL.md` | Already queued in ref-plan; one-line edit |
| 2 | Gate taxonomy reference | `engine/shared/references/gate-taxonomy.md` | Already queued; unblocks vocabulary for items below |
| 3 | Verification patterns reference | `engine/shared/references/verification-patterns.md` | Already queued; unblocks Verifier 4-level upgrade |
| 4 | Context degradation tiers + MCP audit | `economy/rules/cold-start.md` | Already queued; closes context-management gap |
| 5 | Executor deviation rules | `executor/SKILL.md` | Closes biggest behavioral gap in execution |
| 6 | Executor analysis paralysis guard | `executor/SKILL.md` | Same file; write together with #5 |
| 7 | Executor self-check | `executor/SKILL.md` | Same file; write together with #5 and #6 |
| 8 | Scope reduction prohibition | `decompose/SKILL.md`, `executor/SKILL.md` | Prevents the most insidious planner failure class |
| 9 | Specificity test | `decompose/SKILL.md` | Same file as #8; write together |
| 10 | Verifier 4-level artifact verification | `verifier/SKILL.md` | Requires verification-patterns.md (item #3) |
| 11 | Multi-source coverage audit | `decompose/SKILL.md` | Closes "silently missing requirement" failure class |
| 12 | Guard scope reduction detection | `guard/SKILL.md` | Adds enforcement to complement #8 |
| 13 | Debug module | New skill | Entirely new capability; no dependencies |
| 14 | Context monitor hook | New hook | Closes agent context-blindness gap |
| 15 | Namespace routing layer | New `ns-*.md` files | Pure token efficiency; no behavior changes |
| 16 | Skill size budget enforcement | `quality-floor-check.py`, `skill-creator/SKILL.md` | Keeps framework maintainable as it grows |
| 17 | Entity-graph as planning input | `decompose/SKILL.md` | Leverages existing artifact for dependency awareness |

---

## Do-not-copy list

Items studied from GSD that must not be adopted (I6 or I11 violations, or wrong stack):

| GSD item | Reason to avoid |
|---|---|
| Model profile tables with Opus/Sonnet/Haiku names | I6 violation — model names in framework files |
| Runtime abstraction / installer architecture | Competes with WabbleSpec; out of scope |
| Node.js/npm tooling (gsd-tools.cjs, slopcheck CLI) | Wrong language stack; WabbleSpec is Python |
| `.planning/` directory structure | Incompatible with `.wabblespec/state/` canonical paths |
| React/Next.js-specific verification grep patterns | Domain-coupled; inappropriate for general verifier |
| Full SDLC pipeline replication | WabbleSpec has its own pipeline; duplication not value |
