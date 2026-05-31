# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## What This Repository Is

WabbleSpec v6.1: spec-driven, receipt-gated, hook-enforced SDLC framework for single agent runtime. Framework is the product — 116 skill modules across layers L0–L8, `.wabblespec/wabblespec.yaml` as canonical module registry.

Current version: **0.50.0** (see `.wabblespec/VERSION`)

## Key Scripts

Pipeline/automation scripts live in `.wabblespec/engine/shared/scripts/` unless noted otherwise; run any with `--help`. The L5 memory daemons (dream, memory-mine, entity-graph) live in `.wabblespec/engine/modules/l5/<module>/scripts/`, not shared/scripts/. Required deps: `pip install pyyaml duckdb` (duckdb for receipt-db.py).

**Pipeline automation (all sessions):**
- `archive.py` — CHANGELOG + VERSION + delivery receipt + receipt-index (replaces manual Archive steps)
- `receipt-writer.py` — 17 receipt types; auto-upserts into DuckDB if DB exists; use `--no-db` to skip
- `guard-check.py` — Layers 4+5 (authority + command risk + receipt chain via `chain` subcommand)

**Session lifecycle:**
- `session-state.py` — init/show/set/complete/clear session state.json
- `session-registry.py` — create/list/close/purge namespaced session directories
- `recipe-writer.py` — write recipe.json
- `task-card-writer.py` — write task-card.md from CLI args
- `wave-plan-writer.py` — write current-wave-plan.md from wave JSON
- `scope-writer.py` — write scope.md from CLI args

**Receipt store:**
- `receipt-db.py` — DuckDB store; `init`, `import`, `query`, `stats`, `export` subcommands
- `wave-queue.py` — file-locked parallel wave task queue
- `queue-orchestrator.py` — parallel wave coordinator; `populate` loads queue from wave plan, `ready` outputs JSON of tasks for parallel Agent dispatch, `advance` checks progress (exit 0=done, 1=pending, 2=fail), `run` for sequential fallback

**Analysis and validation:**
- `quality-floor-check.py` — Gate 1 + Gate 2 for all 108 modules; `--verbose` for full detail
- `validate-graph.py` — module registry integrity
- `agent-output-validator.py` — validate JSON output from skill subagents
- `wabblespec-doctor.py` — read-only drift detector; 30 checks (C/H/M/L) covering the foundation-audit finding classes. `--all`, `--severity {critical,high,medium,low}`, `--format json`, `--self-test`. Run after a batch of changes (e.g. reference integrations) to catch regressions. Reports only — no edits, no hook wiring.

**Memory layer:**
- `drawer-writer.py` — write file-based drawer JSON
- `provenance-append.py` — append to provenance ledger

**Background scripts (fired by stop-hook via daemon-config.json):**
- `dream.py` — EMA decay + gap-map + staleness-map (on_stop) — `l5/dream/scripts/`
- `quality-floor-check.py` — regression check (on_archive) — `shared/scripts/`
- `index-update.py` — regenerate INDEX.md managed sections (on_archive) — `shared/scripts/`
- `receipt-db.py import` — sync JSON receipts to DuckDB (on_archive) — `shared/scripts/`
- `memory-mine.py` — closet indexing (on_stop, enabled at 50+ drawers) — `l5/memory-mine/scripts/`
- `entity-graph.py` — graph update (on_stop) — `l5/entity-graph/scripts/`

**Engine scripts (not in shared/scripts/):**
- `.wabblespec/engine/scripts/wabblespec-sync-skills.py` — sync engine/modules/ → .claude/skills/; use `--filter-recipe .wabblespec/state/recipe.json` to sync only the skills declared in `active_skills:` (run without flag to restore all)
- `.wabblespec/engine/scripts/stop-hook.py` — Stop hook orchestrator

**Selective skill preloading:**
Add `--skills <name>` (repeatable) to `recipe-writer.py` to declare which skills are active for the session. This writes `active_skills: [...]` to recipe.json. Then run sync with `--filter-recipe` to limit `.claude/skills/` to only those skills. Run sync without `--filter-recipe` at session end to restore all 100 skills. Sessions that omit `--skills` default to all skills.

## The 12 Invariants

Full table: `.wabblespec/engine/shared/references/invariants.md`. Key session rules:

- **I1 SPEC IS SINGLE SOURCE OF TRUTH** — Every execution is grounded in spec. P2 blocked until P1 locked; P3 blocked until P2 locked.
- **I4 VERIFICATION IS EXPLICIT** — Every output passes a declared verification gate. Max 3 REVISE cycles; at 3 failures, Attestation required.
- **I6 RUNTIME IS VENDOR-NEUTRAL** — No model names anywhere in framework files. Use capability descriptors only (`code-generation`, `analysis`, `synthesis`, `long-context`).
- **I10 RECEIPTS ARE OPERATIONAL ARTIFACTS** — Every non-trivial execution writes a receipt. Implied completion is prohibited.
- **I11 FRAMEWORK AND PRODUCT NEVER MIX** — `.wabblespec/` is framework space. Project root (excluding `.wabblespec/`, `.claude/`, `.git/`) is product space. Never cross the boundary. Apply writes only to product space.
- **I8 SELF-IMPROVEMENT THROUGH EVIDENCE** — Evolution chain is Execution → Receipt → Instinct → Synth → Blueprint → Augment → Benchmark → Forge. No stage skips. Self-promotion requires Attestation.

## Quality Floor Gates

Both gates enforced by `quality-floor-check.py`. Details in that script's output (`--verbose` for full check list).

## Framework State (`.wabblespec/`)

**Do not write to `.wabblespec/` from product-space tasks (I11).** Framework modules own all writes here.

Key paths:
- `.wabblespec/wabblespec.yaml` — canonical module registry; source of truth for all 108 modules
- `.wabblespec/state/receipts/` — individual seed run receipts (100 accumulated)
- `.wabblespec/state/archive/receipt-index.json` — completed task receipt index
- `.wabblespec/state/memory/` — drawers, entity graph, gap-map, instinct observations
- `.wabblespec/state/experiments/` — L8 evolution cycle artifacts (candidates, blueprints, augments, fixtures, tracker.json)
- `.wabblespec/state/plans/` — active task card and wave plan
- `.wabblespec/state/session/state.json` — session enforcement state (active only during open task)

**Canonical session state paths** (do not use root-level copies):
- `.wabblespec/state/scope.md` — active session scope (not `.wabblespec/scope.md`)
- `.wabblespec/state/recipe.json` — active session recipe (not `.wabblespec/recipe.json`)

The Phase 2 path migration is **complete**: all modules, skill-rules, and scripts read and write the `state/` paths exclusively. Root-level `scope.md`/`recipe.json` are no longer written or referenced (the legacy root copies have been removed).

## Receipt Chain

Every non-trivial task: Research receipt → Plan receipt → Execution receipt → Verifier receipt → Archive receipt. Each phase reads the prior phase's receipt. Skip requires `collapse_eligible: true` in recipe.json plus complexity below threshold.

## Staleness States

Drawer evidence states and decay rules: `.wabblespec/engine/shared/references/staleness-states.md`. `EXPIRED` evidence emits `STALENESS_VIOLATION` (I9) — Guard pre-tool-use hook enforces.

## L8 Evolution Gate

Gate: **MET** (as of 0.23.0). Gate conditions and current status: `.wabblespec/engine/shared/references/l8-corpus-gate.md`.

## Hook Architecture

Hook files live in `.wabblespec/engine/hooks/`. All four JS files are CommonJS modules. `hooks/package.json` sets `{"type": "commonjs"}` to prevent ESM/CJS conflict when an ancestor `package.json` declares `"type": "module"`.

**SessionStart** (`wabblespec-session-start.js`): Runs once per session open. Writes a session flag to `~/.claude/.wabblespec-session`. Emits invariant context and active task state as stdout — Claude Code injects this as a system prompt addendum, so invariants don't need re-stating per turn.

**UserPromptSubmit** (`wabblespec-prompt-guard.js`): Runs before every user prompt. Two informational nudges only — never blocks:
- If active session with completed waves: emits wave progress to prevent Executor drift.
- If no active session and prompt looks like a task-start phrase: reminds to run Recipe first.

**Statusline** (`wabblespec-statusline.ps1`): Reads the flag file and outputs a badge (`[WS idle]` or `[WS task-id w:N/M]`).

**Flag file channel** (`~/.claude/.wabblespec-session`): Shared state between SessionStart hook and statusline. Written by SessionStart via `safeWriteFlag()` (atomic temp+rename, mode 0600, refuses symlinks). Never written by prompt-guard.

**Silent-fail contract**: All hooks catch errors and emit `{}` rather than non-zero exit. Hook failures must not interrupt the session.

## Tool Call Batching

Claude Code executes independent tool calls in parallel. Real effect on seed run speed — use it.

**Rules:**
- All file reads that do not depend on each other go in one response turn.
- All file writes/edits that do not conflict go in one response turn.
- Script executions that are independent (validate-graph + quality-floor-check + complexity-scorer) can be issued as parallel Bash calls.
- Do not chain `Read → Edit → Read` when the second Read is only to confirm — `Edit` succeeds or errors; a re-read is wasted.

**What cannot be parallel:**
- A write that depends on the content of a prior read in the same turn.
- A script whose input is the output of another script in the same turn.
- Receipt writes: each phase's receipt depends on the prior phase's receipt content.

Applies to framework authoring (seed runs, module builds) and product-space tasks equally.

## Skill Authoring Conventions

**Tool references in SKILL.md files use capability placeholders, not provider names (extends I6).**

When a SKILL.md references an external tool by capability — an MCP server, external API, CLI tool, or data connector — use the `~~capability-name` placeholder form rather than hardcoding a provider name or tool prefix. Examples:

- `~~search-console` (not `mcp__google__searchConsole` or `gcloud`)
- `~~vector-store` (not `mcp__chroma__*` or a hardcoded ChromaDB path)
- `~~code-runner` (not `bash` or a specific interpreter name)

The shared skill preamble or Guard resolves `~~capability-name` to the active provider at runtime. Skills written this way work with any conforming provider and never require edits when a backend changes.

**Reference routing over inline documentation.** When a SKILL.md section has a dedicated reference document, add a `## Reference Routing` table and route the situation to that file rather than duplicating the content inline. Each routing entry replaces (not supplements) the corresponding inline block — SKILL.md line counts must go down when routing tables are added.

**Negative triggers are mandatory.** Every SKILL.md must include a `## When NOT to use` section with at least two specific counterexamples. Positive trigger guidance in `description:` is not sufficient — the skill router and the runtime agent both benefit from knowing what inputs look like a trigger but are not one. Minimum counterexample types to cover: (1) an artifact or message that contains output-shaped content but is not a request to re-run the skill, and (2) a state condition under which the skill's gate is not met. Skills that omit this section fail the quality floor Gate 1 check.

**Skill intro must state both dimensions.** The 2–3 sentence intro at the top of a SKILL.md body should declare what the skill does AND what it explicitly does not do. The "doesn't do" boundary prevents the skill from being activated for adjacent tasks that look similar but fall outside its scope.

**Recommendation-only skills must declare a "Not guaranteed" line.** Any skill that produces a recommendation, signal, verdict, or flag — but does not take the resulting action itself — must include a "Not guaranteed:" statement in its intro or `## What this skill does` section. The statement names exactly what human operator or downstream module holds the actual decision authority. Examples: "Not guaranteed: Verifier issues PASS/FAIL; the operator decides whether to archive, extend, or re-plan." "Not guaranteed: Guard emits risk signals; Executor decides whether to proceed, hold, or escalate." This prevents a calling agent from treating the skill's output as an authorization to act, when human judgment or another module's gate is still required.

**`## Pitfalls` is a recognized optional section.** Skills may include a `## Pitfalls` section for operational gotchas that would surprise an agent during execution — edge cases, ordering constraints, known failure modes. This is distinct from `## When NOT to use` (trigger boundaries) and `## When to use` (activation conditions). Target: 3–6 bullet points covering the most common execution surprises. Each entry should follow the Problem / Why / Fix structure: what the agent does wrong, why that failure mode occurs, and the corrective action. This mirrors the WHY-over-directives convention — a pitfall that only names the mistake without explaining causality will not help an agent recognize the failure mode before it occurs.

**Skill eval fixtures must include negative routing cases.** For every skill that has an eval fixture, at least 2 entries must declare `should_trigger: false` with a specific prompt that looks like the skill's trigger but must not activate it. Entry schema: `{ "id": "negative-001", "prompt": "<natural language>", "expected_skill": "<skill that SHOULD handle it>", "should_trigger": false, "notes": "<why this must NOT trigger the candidate skill>" }`. Negative cases catch mis-routing regressions when `description:` fields are edited. This is enforced by quality-floor-check.py Gate 1.

**`description:` must end with a period.** The description field in SKILL.md frontmatter must be a single sentence ending with a period. No marketing words ("powerful", "comprehensive", "seamless"). State the capability, not the implementation.

**Skill descriptions must not contain time-sensitive information.** Version numbers, current counts, and dates embedded in a description field are stale at the next session. A description saying "supports 108 modules as of v0.50.0" is wrong the moment a module is added or the version bumps. State what the skill does and when to trigger it — not facts about the current state of the world.

**Description must describe complex multi-step use cases, not simple single-step queries.** The triggering mechanism only activates when the model judges it would benefit from consulting the skill. A description calibrated for a simple one-step query will undertrigger — the model handles simple requests directly without loading skills. Describe the complex or specialized scenario where the skill is genuinely necessary.

**Skill content has three loading tiers with distinct budget rules.** Tier 1 — frontmatter metadata (name + description): always in context, ~100 words; routing decisions read only this. Tier 2 — SKILL.md body: loaded when skill activates, budget <500 lines; put operational instructions here. Tier 3 — bundled resources (scripts/, references/, assets/): loaded on demand, unlimited; offload large schemas, reference material, and scripts here. When the body approaches 500 lines, promote content to Tier 3 with an explicit routing pointer — do not truncate. The sweet spot for SKILL.md body length is 200–600 lines. Below 200 lines is usually underpowered. Above 800 lines without a Tier 3 references/ directory is BLOATED_SKILL — promote content to Tier 3 rather than extending the body further.

**Prefer explaining reasoning over capitalized directives.** When writing SKILL.md instructions, explain *why* a rule matters rather than issuing MUST/ALWAYS/NEVER/CRITICAL commands. Models given the WHY handle edge cases that flat directives miss. Writing ALWAYS or NEVER in all caps is a yellow flag that the rule needs better motivation, not stronger emphasis.

**When evaluating description effectiveness against an eval set, split 60% train / 40% held-out test; select the best description by test score, not train score.** Selection by train score overfits the description to the eval set and produces a description that triggers on test queries but not on real user queries.

**`description:` must not summarize the skill's workflow.** State only the triggering condition — what the agent is doing that warrants loading this skill. Do not list the steps the skill will perform. Empirical evidence from agent testing shows that when a description contains workflow steps, agents follow the description as a shortcut and skip reading the skill body. A description saying "dispatches subagent per task with two-stage review" caused agents to run ONE review instead of TWO because the description summary was used instead of the flowchart in the skill body. Triggering conditions only; no workflow content.

**`<HARD-GATE>` is a recognized optional inline marker.** Use `<HARD-GATE>...</HARD-GATE>` within a skill body to wrap a verification requirement that is non-negotiable before the agent may proceed past that point in the skill flow. Unlike a general rule, a HARD-GATE is position-sensitive: it fires at the exact step where skipping it would guarantee a defect. Do not use for general guidance — reserve for checkpoints where the agent has no valid path forward without completing the check.

**Avoid generic visual defaults in platform-web and gateway-aesthetic output.** Never default to: Inter, Roboto, Arial, or system fonts as the primary typeface; purple-to-blue gradients or purple/white backgrounds as the primary palette; or identical same-size card grids as the primary layout. These are the most common AI-generation convergence patterns. Each project's visual identity must be distinct — never converge on the same choices across different project outputs. Commit to a named aesthetic direction and document what is NOT being used.

**Avoid dangerous inline backtick patterns.** Do not write inline code spans (single backticks) in SKILL.md prose that contain `!` or `>` followed by a word character. Claude Code's bash permission scanner interprets these as history expansion or output redirection, which can prevent the skill from loading. Both patterns are safe inside fenced code blocks (triple backticks). The quality floor `INLINE_DANGER` check enforces this automatically.

**Task card briefs must quote, not paraphrase.** When authoring a task card or writing an agent brief that references a canonical rule (invariant, SKILL.md gate, reference doc), quote the exact line from the source document. Paraphrasing corrupts the rule — it produces a version that sounds similar but changes thresholds, omits conditions, or inverts the polarity. Empirical evidence: paraphrasing a single changelog rule caused 5 of 8 parallel agents to violate CONTRIBUTING.md in the same direction. Quote verbatim; adapt only when quoting would violate I6 (model names, vendor names).

**Boundary coverage requirement.** Any script, check, or quality gate that enforces a threshold or budget must have test coverage at exactly N-1, N, and N+1 where N is the threshold. Tests covering only "trivially fits" (N far below) and "trivially overflows" (N far above) do not constitute edge-case coverage and routinely miss off-by-one and reservation-accounting bugs. Apply to quality-floor-check.py, receipt-writer.py, and any new guard script with numeric limits.

**Before deleting any file or module, grep all consumers.** Check: workflow .md files, docs/, manifests (wabblespec.yaml), npm/pip scripts, CLAUDE.md references. If any reference exists, the removal is incomplete — update every consumer in the same commit or do not delete. "Already removed from source" does not mean removed from every consumer. Empirical evidence: removing a file that was declared in a workflow as `@file:` ref caused a silent downstream failure that only surfaced at CI run time.

**Tool descriptions must answer four questions.** When writing a tool description (for MCP tools, skills referenced as tools, or any externally-callable interface): (1) What does it do? (2) When should it be used? (3) What inputs does it accept? (4) What does it return? A description that omits any of these — especially "when to use" vs "when not to use" — produces mis-invocation. "Search for things" is not a description. "Retrieve customer profile by ID. Use for order processing and support lookup. Returns 404 if not found." is a description.

**Create a new skill when a behavior repeats without guidance in 3+ distinct execution contexts.** If an agent performs the same behavioral pattern three or more times across unrelated tasks without being prompted by a skill, that is the signal to formalize the behavior as a skill. Repeating in fewer contexts indicates an ad-hoc pattern, not a generalizable workflow.

**Before publishing a new skill, verify six readiness criteria.** Actionable (provides clear implementable guidance, not vague recommendations), Specific (names exact files, thresholds, or conditions), Tested (examples drawn from actual project code, not invented), Complete (covers common edge cases including failure modes), Current (no version numbers, dates, or counts in description), Linked (cross-references at least one related skill by name). A skill that fails any criterion should be revised rather than published.

**Skill examples must reference actual project artifacts, not theoretical constructs.** When a SKILL.md includes an example command, file path, code snippet, or workflow, the example must be drawn from something that exists in the codebase — a real script path, a real SKILL.md section, a real receipt type. Invented example paths and fake filenames teach incorrect mental models and diverge from the project as it evolves.

**Cross-reference related skills by name rather than duplicating their content.** When a SKILL.md section would repeat content already covered by another skill, add a reference pointer instead of copying the block. Duplicated content creates two maintenance targets and diverges over time. The `## Reference Routing` table is the correct location for these pointers.

**Never inject dynamic metadata into the stable prompt prefix.** Timestamps, session IDs, version numbers, or request counters in the system prompt prefix invalidate the entire KV-cache block downstream of that change — causing a full cache miss on every request. Move all dynamic metadata into a separate user message or tool result appended after the stable prefix. Stable ordering: system instructions first, tool definitions second, reusable templates third, dynamic content last. Even one character change in the prefix destroys all cached blocks that follow it.

**Match instruction specificity to task fragility.** Three freedom levels: High freedom (text instructions only) — use when multiple valid approaches exist and decisions depend on context. Medium freedom (pseudocode or scripts with configurable parameters) — use when a preferred pattern exists but reasonable variation is acceptable. Low freedom (exact script, no modification) — use when the operation is fragile, order-sensitive, or invariant-critical (e.g., receipt writes, database migrations, wave plan execution). Default to medium freedom and escalate to low only when tested failure modes confirm it.

**Skill reference chains must be at most 1 level deep from SKILL.md.** When a SKILL.md references a file in references/, that file must not reference a third file. Nested reference chains (SKILL.md → ref-A.md → ref-B.md) cause agents to read ref-B using partial reads rather than full reads, producing incomplete information. All Tier 3 reference files must link directly from SKILL.md or from a dedicated Reference Routing section, not from within other reference files.

**Use Incorrect/Correct as the preferred label pair in code example blocks.** When SKILL.md files or rule documents include code comparisons showing what to do vs. what not to do, use `**Incorrect:**` and `**Correct:**` as the headings. This is more precise than Before/After (which implies temporal change, not correctness) and clearer than Bad/Good (which is evaluative). Exact format: `**Incorrect:**` on its own line before the wrong example, `**Correct:**` before the right example. Match case exactly.
