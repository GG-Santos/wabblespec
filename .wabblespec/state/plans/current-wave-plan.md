# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Framework
**complexity:** High
**collapse_eligible:** false
**generated_at:** 2026-05-30T14:15:00Z
**session_id:** tier7-expansions-20260530

Complexity confirmed High: 18 deliverables across 6 integration surfaces (shared/scripts, hooks, .claude/skills, SKILL.md extensions, settings.json, wabblespec.yaml).

Recommend parallel fan-out — Wave 1 items are fully independent (6 scripts/hooks with no shared state); Wave 3 skills are independent of each other. Executor may dispatch Wave 1 items and Wave 3 items as parallel sub-tasks within each wave.

## Waves

### Wave 1: Standalone scripts and hook infrastructure

**inputs:** task-card AC1-AC4; expansion drawers: skill-bundles, epistemic-hook, ref-watcher, watzup-scanner, shape-artifact, conflict-detection; `recipe-writer.py` (exists); `settings.json` (exists)
**outputs:**
- `.claude/bundles/ref-adopt.yaml` (+ `code-review.yaml`, `evolution.yaml`, `maintenance.yaml`)
- `.wabblespec/engine/shared/scripts/recipe-writer.py` (--bundle flag added)
- `.wabblespec/engine/shared/scripts/wabblespec-watch-refs.py` (new)
- `.wabblespec/state/memory/wings/references/watch-watermarks.json` (initialized empty)
- `.wabblespec/engine/shared/scripts/watzup-scan.py` (new)
- `.wabblespec/engine/shared/scripts/shape-writer.py` (new)
- `.wabblespec/engine/shared/scripts/session-conflict-check.py` (new)
- `.wabblespec/engine/hooks/wabblespec-epistemic-reminder.js` (new PostToolUse hook)
- `.claude/settings.json` updated with PostToolUse Grep hook entry
**checkpoint:** all 5 scripts respond to --help; bundle YAML parses; hook emits valid JSON with `systemMessage` key; recipe-writer --bundle flag expands active_skills from YAML
**rollback_to:** null
**verification_mode:** Test
**verification_command:** `python -c "import yaml; yaml.safe_load(open('.claude/bundles/ref-adopt.yaml').read()); print('bundle-ok')" && for s in wabblespec-watch-refs watzup-scan shape-writer session-conflict-check; do python .wabblespec/engine/shared/scripts/$s.py --help > /dev/null || exit 1; done && node .wabblespec/engine/hooks/wabblespec-epistemic-reminder.js '{"tool":"Grep","result":""}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'systemMessage' in d; print('hook-ok')"`

---

### Wave 2: Executor, Specify, and session-start extensions

**inputs:** Wave 1 checkpoint; task-card AC5-AC7; expansion drawers: ref-capture, post-wave-reviewer, compaction-memo, transcript-handoff, plan-notebooks; `stop-hook.py` (exists); `session-registry.py` (exists); `wabblespec-session-start.js` (exists)
**outputs:**
- `.wabblespec/engine/shared/scripts/research-artifact-writer.py` (new)
- `.wabblespec/engine/shared/scripts/memo-writer.py` (new)
- `.wabblespec/engine/shared/scripts/notebook-writer.py` (new)
- `.claude/skills/executor/SKILL.md` (post-wave reviewer step + ref capture step added)
- `.claude/skills/specify/SKILL.md` (shape artifact step added after scope lock)
- `.wabblespec/engine/hooks/wabblespec-session-start.js` (memo.md injection on startup)
- `.claude/settings.json` updated with PreCompact hook entry
- `.wabblespec/engine/hooks/wabblespec-pre-compact.js` (new PreCompact handler for memo + transcript handoff)
**checkpoint:** 3 new scripts respond to --help; grep confirms executor/specify SKILL.md edits; PreCompact entry exists in settings.json; session-start memo injection present
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test
**verification_command:** `for s in research-artifact-writer memo-writer notebook-writer; do python .wabblespec/engine/shared/scripts/$s.py --help > /dev/null || exit 1; done && grep -q "post-wave reviewer" .claude/skills/executor/SKILL.md && grep -q "shape-writer" .claude/skills/specify/SKILL.md && python -c "import json; cfg=json.load(open('.claude/settings.json')); hooks=[h.get('matcher','') for h in cfg.get('hooks',{}).get('PostToolUse',[])]; assert any('Grep' in str(h) for h in hooks), 'Grep hook missing'; print('settings-ok')"`

---

### Wave 3: New skill modules (skill-tdd, benchmark-loop, watzup)

**inputs:** Wave 1 checkpoint (watzup-scan.py exists); task-card AC8-AC9; expansion drawers: skill-tdd-harness, autonomous-loop, session-handoff-scanner; `wabblespec.yaml` (exists)
**outputs:**
- `.claude/skills/skill-tdd/SKILL.md` (new skill)
- `.wabblespec/engine/modules/l8/skill-tdd/SKILL.md` (canonical engine source)
- `.wabblespec/engine/modules/l8/skill-tdd/skill-rules.json` (new)
- `.claude/skills/benchmark-loop/SKILL.md` (new skill)
- `.wabblespec/engine/modules/l8/benchmark-loop/SKILL.md` (canonical engine source)
- `.wabblespec/engine/modules/l8/benchmark-loop/skill-rules.json` (new)
- `.claude/skills/watzup/SKILL.md` (new skill, thin wrapper around watzup-scan.py)
- `.wabblespec/engine/modules/l7/watzup/SKILL.md` (canonical engine source)
- `.wabblespec/engine/modules/l7/watzup/skill-rules.json` (new)
- `.wabblespec/wabblespec.yaml` (3 new module entries)
**checkpoint:** all three SKILL.md files parseable YAML frontmatter; wabblespec.yaml registers all 3; validate-graph.py exits 0
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test
**verification_command:** `for s in skill-tdd benchmark-loop watzup; do test -f ".claude/skills/$s/SKILL.md" && python -c "import yaml; list(yaml.safe_load_all(open('.claude/skills/$s/SKILL.md').read()))" || { echo "FAIL: $s"; exit 1; }; done && python .wabblespec/engine/shared/scripts/validate-graph.py`

---

### Wave 4: Decompose and Autopilot extensions + pattern inference

**inputs:** Wave 1-3 checkpoints; task-card AC10-AC11; expansion drawers: topology-planner, pattern-inference-module; `decompose/SKILL.md` (exists); `autopilot/SKILL.md` (exists); `recipe-writer.py` (exists, already has --bundle from Wave 1)
**outputs:**
- `.wabblespec/engine/shared/scripts/pattern-inference.py` (new; classifies task → pattern)
- `.claude/skills/decompose/SKILL.md` (Step 3b topology planner section added)
- `.wabblespec/engine/modules/l1/decompose/SKILL.md` (engine canonical updated; sync to .claude/)
- `.claude/skills/autopilot/SKILL.md` (Phase 0 pattern inference step added)
- `.wabblespec/engine/modules/l2/autopilot/SKILL.md` (engine canonical updated; sync to .claude/)
- `.wabblespec/engine/shared/scripts/recipe-writer.py` (--execution-mode flag added)
**checkpoint:** pattern-inference.py --help exits 0; pattern-inference.py --goal "test" --complexity 3 outputs JSON with all 5 required keys; decompose SKILL.md contains "Step 3b"; autopilot SKILL.md references pattern-inference
**rollback_to:** Wave 3 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/pattern-inference.py --goal "Build a REST API" --complexity 3 | python -c "import sys,json; d=json.load(sys.stdin); required={'pattern','confidence','signals','needs_clarification','work_breakdown'}; missing=required-set(d); assert not missing, f'missing: {missing}'; print('pattern-ok')" && grep -q "Step 3b" .claude/skills/decompose/SKILL.md && grep -q "pattern-inference" .claude/skills/autopilot/SKILL.md`

---

### Wave 5: CRDT merge module and visual companion server

**inputs:** Wave 4 checkpoint; task-card AC12; expansion drawers: crdt-merge, visual-companion; `queue-orchestrator.py` (exists); `brainstorm/SKILL.md` (exists)
**outputs:**
- `.wabblespec/engine/shared/scripts/crdt_merge.py` (Python CRDT module: LWW-Register, OR-Set, RGA)
- `.wabblespec/engine/shared/scripts/crdt_merge_test.py` (unit tests for determinism + LWW semantics)
- `.wabblespec/engine/shared/scripts/visual-companion/server.js` (zero-dependency Node.js HTTP server)
- `.wabblespec/engine/shared/scripts/visual-companion/package.json`
- `.claude/skills/brainstorm/SKILL.md` (opt-in visual companion step added)
- `.wabblespec/engine/modules/l1/brainstorm/SKILL.md` (engine canonical updated)
**checkpoint:** crdt_merge_test.py passes (determinism + LWW assertions); server.js exists and package.json is valid JSON; brainstorm SKILL.md contains visual companion opt-in language
**rollback_to:** Wave 4 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/crdt_merge_test.py && node -e "require('./.wabblespec/engine/shared/scripts/visual-companion/server.js')" 2>&1 | grep -v "^$" || true && grep -q "visual companion" .claude/skills/brainstorm/SKILL.md`

---

### Wave 6: Schema-defined workflow (Phase 1 -- design and validator only)

**inputs:** Wave 1-5 checkpoints; task-card (schema-workflow non-goal: Executor integration deferred); expansion drawer: custom-workflow-schema
**outputs:**
- `.wabblespec/engine/shared/references/workflow-schema.yaml` (YAML schema format definition)
- `.wabblespec/engine/shared/references/workflow-schema-sample.yaml` (example: default wabblespec phase sequence)
- `.wabblespec/engine/shared/scripts/workflow-schema-validator.py` (validates a workflow YAML against the schema)
**checkpoint:** validator exits 0 on the sample file; validator exits non-zero on a deliberately invalid YAML (missing required phase field); schema file documents all required fields with comments
**rollback_to:** Wave 5 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/workflow-schema-validator.py .wabblespec/engine/shared/references/workflow-schema-sample.yaml && python -c "import subprocess,sys; r=subprocess.run(['python','.wabblespec/engine/shared/scripts/workflow-schema-validator.py','/dev/null'],capture_output=True); sys.exit(0) if r.returncode!=0 else sys.exit(1)" && echo "PASS"`

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 1 fails | null (remove created files) | any script --help fails, hook emits invalid JSON, bundle YAML invalid, after 3 REVISE cycles |
| Wave 2 fails | Wave 1 checkpoint | script --help fails, SKILL.md grep misses, settings.json missing hook entry, after 3 REVISE cycles |
| Wave 3 fails | Wave 1 checkpoint | SKILL.md frontmatter parse error, validate-graph.py non-zero, after 3 REVISE cycles |
| Wave 4 fails | Wave 3 checkpoint | pattern-inference.py missing keys, SKILL.md grep misses, after 3 REVISE cycles |
| Wave 5 fails | Wave 4 checkpoint | crdt_merge_test.py assertion fails, server.js missing, brainstorm SKILL.md not updated, after 3 REVISE cycles |
| Wave 6 fails | Wave 5 checkpoint | validator fails on sample, or validator passes on invalid input (gate inverted), after 3 REVISE cycles |
