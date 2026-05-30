# Task Card

**goal:** All 18 Tier 7 expansion capabilities from the ref-adopt drawer library are implemented as verified, additive framework artifacts -- scripts, hooks, skills, and SKILL.md extensions -- each satisfying its drawer-defined session seed acceptance condition.
**target:** Framework
**complexity:** High
**change_class:** ADDITIVE
**locked_at:** 2026-05-30T14:10:00Z
**session_id:** tier7-expansions-20260530

## Non-Goals

- Multi-Tool Skill Adapters (Cursor/Windsurf/Copilot): excluded by user directive
- Product-space writes (I11): all work is framework-space only
- External binary dependencies beyond Python and Node.js
- Breaking changes to existing receipt schema or SKILL.md APIs (additive only)
- Live browser runtime verification of visual companion
- Full Executor integration for Schema-Defined Workflow (months-scope; Phase 1 design only)

## Assumptions

- All 18 expansion drawer files are FRESH and verified in this session
- `queue-orchestrator.py`, `session-registry.py`, `receipt-writer.py`, `stop-hook.py`, `recipe-writer.py` exist as declared
- PreCompact hook event is supported by Claude Code harness
- PostToolUse hook with tool matcher is supported in settings.json
- Node.js available for visual companion server
- User's goal statement constitutes scope confirmation (18 items enumerated in prior table discussion)
- No file-based project-standard drawers found; ChromaDB not queried in this phase

## Acceptance Criteria

### Criterion 1: Skill Bundle Presets

Given `.claude/bundles/ref-adopt.yaml` exists declaring `name`, `description`, and `skills` fields
When `python .wabblespec/engine/shared/scripts/recipe-writer.py --bundle ref-adopt` is run
Then `recipe.json` contains `active_skills` populated from the bundle YAML's skills list, and `--bundle unknown-name` exits non-zero with a legible error

### Criterion 2: Epistemic Reminder Hook wired

Given a PostToolUse hook file exists at its declared path
When `settings.json` contains a PostToolUse entry matching the Grep tool
Then executing the hook with a mock Grep result emits valid JSON containing a `systemMessage` key (non-empty) and does not block (no non-zero exit)

### Criterion 3: Reference Staleness Watcher

Given reference drawers with `source` fields exist in `.wabblespec/state/memory/wings/references/`
When `python .wabblespec/engine/shared/scripts/wabblespec-watch-refs.py` is run
Then `.wabblespec/state/memory/wings/references/watch-watermarks.json` is written or updated, and any drawer whose upstream SHA differs from the stored watermark has its `staleness_state` field set to `NEEDS_REVERIFICATION`

### Criterion 4: Session Handoff Scanner

Given an existing WabbleSpec session state (session-state.py show returns data)
When `python .wabblespec/engine/shared/scripts/watzup-scan.py` is run
Then stdout contains labelled sections for Current Session, Active Wave, Pending Receipts, and Recent Commits, with no uncaught exceptions

### Criterion 5: Spec Shape Artifact

Given `state/scope.md` is locked and a session ID is active
When `python .wabblespec/engine/shared/scripts/shape-writer.py` is run
Then `state/plans/shape.md` is created containing a Scope summary section, a Decisions section (bulleted rationale), and a Standards Applied section

### Criterion 6: Compaction-Resistant Memo

Given `settings.json` contains a PreCompact hook entry pointing to the memo hook handler
When the PreCompact event fires (simulated by running the hook directly with `trigger: manual`)
Then `state/session/memo.md` is written with at least a timestamp header, and `wabblespec-session-start.js` reads and injects `memo.md` content when the file exists

### Criterion 7: Post-Wave Background Reviewer

Given Executor has written a wave receipt and the post-wave review step is present in Executor SKILL.md
When the review subagent is dispatched (Read+Write tools only)
Then the subagent applies the four Dream anti-pattern filters and either writes exactly one drawer to wing `instinct` / room `wave-review-candidates` or writes nothing; it MUST NOT write more than one drawer per wave

### Criterion 8: Skill TDD Harness

Given a candidate SKILL.md path and a pressure scenario description are provided
When `/skill-tdd` is invoked
Then the skill dispatches a subagent WITHOUT the candidate skill (recording baseline rationalizations) and then WITH the skill (recording compliance delta); the final report declares READY if delta >= 80% compliance improvement, BLOCKED otherwise

### Criterion 9: Autonomous Benchmark Loop (happy path + stuck detection)

Given `quality-floor-check.py --format json` returns a parseable score and the working tree is clean
When `/benchmark-loop` is invoked
Then each iteration makes exactly one atomic commit before verify; a regression reverts the commit; after 5 consecutive discards execution shifts strategy; after 10 consecutive discards execution halts and surfaces findings to the user; a TSV log of `iteration/commit/metric/delta/status` is written

### Criterion 10: Parallel Topology Planner

Given a task with at least one wave group having `parallelizability: high` and no declared cross-wave file conflicts
When Decompose runs Step 3b on that task
Then each wave group entry in `current-wave-plan.md` contains an `execution_mode` field with value `sequential`, `parallel`, or `mixed`

### Criterion 11: Pattern Inference Module

Given a task card goal text and a complexity score
When `python .wabblespec/engine/shared/scripts/pattern-inference.py --goal "<text>" --complexity <score>` is run
Then stdout is valid JSON containing `pattern` (one of: hierarchical/pipeline/swarm/generator-critic/adversarial/jury), `confidence` (0.0-1.0 float), `signals` (non-empty list), `needs_clarification` (boolean), and `work_breakdown` (string)

### Criterion 12: CRDT Wave Merge (Phase 1 -- Python module)

Given two Python dicts representing parallel wave edits to overlapping keys
When `crdt_merge.merge(wave_a, wave_b)` is called
Then the result is deterministic (same output regardless of argument order for LWW-Register resolution), all non-conflicting keys from both inputs are present, and conflicting keys resolve to the higher-timestamp value with no KeyError or exception
