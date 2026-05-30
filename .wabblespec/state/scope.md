# Session Scope

**target:** Framework
**complexity:** High
**locked_at:** 2026-05-30T14:05:00Z
**session_id:** tier7-expansions-20260530

## In Scope

1. Skill Bundle Presets -- `.claude/bundles/*.yaml` + `recipe-writer.py --bundle` flag
2. Epistemic Reminder Hook -- PostToolUse/Grep hook in `settings.json`
3. Reference Staleness Watcher -- `wabblespec-watch-refs.py` + watermark file
4. Session Handoff Scanner -- `watzup-scan.py` + `/watzup` skill
5. Spec Shape Artifact -- `shape-writer.py` + Specify SKILL.md integration
6. Internal Reference Capture -- `research-artifact-writer.py` + Executor SKILL.md integration
7. Parallel Session Conflict Detection -- `session-conflict-check.py` + Archive pre-condition note
8. Compaction-Resistant Session Memo -- `memo-writer.py` + PreCompact hook + SessionStart injection
9. Post-Wave Background Reviewer -- Executor subagent spawn between wave receipt and Verifier
10. Skill TDD Harness -- `/skill-tdd` skill with pressure-test subagent
11. Autonomous Benchmark Loop -- `/benchmark-loop` skill with git-backed iteration and stuck detection
12. Parallel Topology Planner -- Decompose Step 3b + wave-plan schema `execution_mode` field
13. Transcript Auto-Handoff -- PreCompact handler + SessionStart handoff injection
14. Pattern Inference Module -- `pattern-inference.py` + Autopilot SKILL.md Phase 0 integration
15. Per-Plan Knowledge Notebooks -- `notebook-writer.py` + session-registry + Executor per-wave step
16. Visual Companion for Brainstorming -- Node.js localhost server + Brainstorm SKILL.md opt-in step
17. CRDT-Based Parallel Wave Merge -- Python CRDT module + queue-orchestrator merge phase
18. Schema-Defined Custom Workflow -- YAML schema design + format validator (Phase 1 only; Executor integration deferred)

## Out of Scope

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
- PostToolUse hook with tool matcher is supported in `settings.json`
- Node.js available for visual companion server
- User's goal statement constitutes scope confirmation (18 items enumerated in prior table discussion)
- No file-based project-standard drawers found; ChromaDB not queried in this phase

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
| 2026-05-30T14:05:00Z | Initial scope locked (18 Tier 7 expansions, excl. multi-tool adapters) | user-confirmed via goal statement |
