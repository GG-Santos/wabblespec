# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Framework
**complexity:** High
**collapse_eligible:** false
**generated_at:** 2026-05-29T15:30:00Z

Complexity confirmed High (re-confirmed against the full task card; bumped from Medium during the ScopeFrame re-frame when the framework-maintenance authority-owner regression was discovered).

## Waves

### Wave 1: Re-establish framework-maintenance authority owner

**inputs:** task-card AC1-AC5; scope.md; git `2371bea` module files; a fresh human-signed `one_time_use` bootstrap attestation (Wave-1 prep produces the JSON + `content_hash`; human signs before this wave runs)
**outputs:**
- `.wabblespec/engine/modules/l2/framework-maintenance/SKILL.md` (byte-identical to `2371bea`)
- `.wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py` (byte-identical to `2371bea`)
- `.wabblespec/engine/modules/l2/framework-maintenance/skill-rules.json` (verbatim + `owns` extended with `.claude/agents/**`, `engine/modules/l2/{reviewer,adversary,grader}/**`)
- `.wabblespec/wabblespec.yaml` (framework-maintenance entry re-registered, L2, type authority)
- consumed attestation moved to `.wabblespec/state/attestations/consumed/`
**checkpoint:** attestation `content_hash` matches the staged files; `validate-graph.py` exits 0; `guard-check.py authority --module framework-maintenance` returns PASS for every B1/B2 target path
**rollback_to:** null
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py && python .wabblespec/engine/shared/scripts/validate-graph.py && python .wabblespec/engine/shared/scripts/guard-check.py authority --module framework-maintenance --files ".claude/agents/wabblespec-guard.md" ".claude/agents/wabblespec-verifier.md" ".wabblespec/engine/modules/l2/reviewer/SKILL.md" ".wabblespec/engine/modules/l2/adversary/SKILL.md" ".wabblespec/engine/modules/l2/grader/SKILL.md" ".claude/skills/ref-eval/SKILL.md" ".claude/skills/ref-plan/SKILL.md" ".claude/skills/ref-comp/SKILL.md" ".wabblespec/engine/shared/scripts/wabblespec-doctor.py"`

---

### Wave 2: Add doctor shared-infra-owner check

**inputs:** Wave 1 outputs (registered owner); task-card AC6; `wabblespec-doctor.py`
**outputs:** `.wabblespec/engine/shared/scripts/wabblespec-doctor.py` (new check: shared-infra anchor paths have an authority owner; advisory severity)
**checkpoint:** `--self-test` exits 0; a normal run reports the new check green (owner present); a simulated owner-absence run emits the finding
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --self-test && python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --format json`

---

### Wave 3: Scope subagent toolsets + remove model pins (B1)

**inputs:** Wave 1 owner (authorizes `.claude/agents/**`); task-card AC7, AC8
**outputs:**
- `.claude/agents/wabblespec-guard.md` (add `tools: Read, Grep, Glob, Bash`; remove `model:` line)
- `.claude/agents/wabblespec-verifier.md` (add `tools: Read, Grep, Glob, Bash`; remove `model:` line)
**checkpoint:** each file's frontmatter declares `tools: Read, Grep, Glob, Bash` and a grep for `claude-`/`sonnet`/`opus`/`haiku` across both files returns zero matches
**rollback_to:** Wave 2 checkpoint
**verification_mode:** Test
**verification_command:** `python -c "import re,sys; [sys.exit('FAIL '+f) for f in ['.claude/agents/wabblespec-guard.md','.claude/agents/wabblespec-verifier.md'] if not re.search(r'^tools:\s*Read,\s*Grep,\s*Glob,\s*Bash', open(f,encoding='utf-8').read(), re.M) or re.search(r'claude-|sonnet|opus|haiku', open(f,encoding='utf-8').read(), re.I)]; print('PASS')"`

---

### Wave 4: Add negative-trigger clauses + sync (B2)

**inputs:** Wave 1 owner (authorizes review-trio engine paths + `.claude/skills/**`); task-card AC10
**outputs:**
- `.claude/skills/ref-eval/SKILL.md`, `.claude/skills/ref-plan/SKILL.md`, `.claude/skills/ref-comp/SKILL.md` (description negative triggers)
- `.wabblespec/engine/modules/l2/reviewer/SKILL.md`, `.../adversary/SKILL.md`, `.../grader/SKILL.md` (description negative triggers, canonical source)
- re-synced `.claude/skills/` copies for the review-trio
**checkpoint:** each of the six descriptions names its sibling boundary; every touched SKILL.md parses (frontmatter loads); sync reports zero divergence between engine and `.claude/` for the review-trio
**rollback_to:** Wave 3 checkpoint
**verification_mode:** Test
**verification_command:** `python .wabblespec/engine/scripts/wabblespec-sync-skills.py; python -c "import yaml,sys; [yaml.safe_load(open(f,encoding='utf-8').read().split('---')[1]) for f in ['.claude/skills/ref-eval/SKILL.md','.claude/skills/ref-plan/SKILL.md','.claude/skills/ref-comp/SKILL.md','.claude/skills/reviewer/SKILL.md','.claude/skills/adversary/SKILL.md','.claude/skills/grader/SKILL.md']]; print('PARSE-OK')"`
**reviewer_note:** sync runs WITHOUT `--filter-recipe` — recipe.json `active_skills` is `[]`, and a filtered sync could prune `.claude/skills/` to empty. Full sync propagates the review-trio engine edits to `.claude/`.

---

### Wave 5: Demonstrate subagent regression-free behavior (B1 gate)

**inputs:** Wave 3 scoped subagents; task-card AC9
**outputs:** a demonstration record — the scoped `wabblespec-guard` and `wabblespec-verifier` invoked on a representative wave (Waves 2-4 already exercise them in-band via Executor's pre-wave Guard and post-wave Verifier), with valid JSON receipts and no tool-call failure
**checkpoint:** both subagents return their declared JSON receipt (guard `overall`/`status`; verifier `verdict`/`status`); each subagent's prompt body invokes no tool outside its declared `tools:` set (static subset check)
**rollback_to:** Wave 4 checkpoint
**verification_mode:** Demonstration
**verification_command:** `python -c "import re,sys; t=open('.claude/agents/wabblespec-guard.md',encoding='utf-8').read()+open('.claude/agents/wabblespec-verifier.md',encoding='utf-8').read(); bad=sorted(set(re.findall(r'\b(Write|Edit|MultiEdit|NotebookEdit|WebFetch|WebSearch|Task)\b', t))); sys.exit('FAIL ungranted tools referenced: '+str(bad)) if bad else print('SUBSET-OK')" && ls .wabblespec/state/receipts/guard-*agent-creator*.json .wabblespec/state/receipts/verifier-*agent-creator*.json`
**reviewer_note:** static subset check is the reliable in-session gate. The live demonstration may not exercise the edited definitions if the harness caches subagent files mid-session — a definitive live run may require a fresh session. Executor must name its W2-W4 guard/verifier receipts with the session id so the `ls` glob resolves.

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 1 fails | null (restore deleted-state: remove framework-maintenance dir + yaml entry) | Attestation hash mismatch, validate-graph fail, or authority not PASS after 3 REVISE cycles |
| Wave 2 fails | Wave 1 checkpoint | doctor `--self-test` fails or new check misbehaves after 3 REVISE cycles |
| Wave 3 fails | Wave 2 checkpoint | tools line absent or model name remains after 3 REVISE cycles |
| Wave 4 fails | Wave 3 checkpoint | description missing trigger, parse error, or sync divergence after 3 REVISE cycles |
| Wave 5 fails | Wave 4 checkpoint | subagent returns invalid receipt or references an ungranted tool |
