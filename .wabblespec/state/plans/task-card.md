# Task Card

**goal:** WabbleSpec's `wabblespec-guard`/`wabblespec-verifier` subagents and the ref-*/review-trio skill descriptions are hardened per the agent-creator ref-plan, executed under a re-established and regression-guarded `framework-maintenance` authority owner.
**target:** Framework
**complexity:** High
**change_class:** ADDITIVE
**locked_at:** 2026-05-29T15:20:00Z
**session_id:** agent-creator-integration-20260529

## Non-Goals

- Rewriting foundation-hardening's closed delivery receipt / AC8 — the regression is logged (memory + this task's receipts), not retro-edited into an archived task.
- A general "every module owns its own SKILL.md" authority-model refactor across all 103 modules — only the touched review-trio paths are added now.
- B3 (subagent-vs-skill rubric in CLAUDE.md / authoring conventions) — still deferred to a later Phase 2.
- Promoting the new doctor check to blocking — advisory-first.
- Introducing or referencing any model name (I6 hard guardrail); importing the reference's token-budget numbers; adopting the `skills:` frontmatter field.
- Changing subagent prompt logic/behavior beyond the `tools:`/`model:` frontmatter, or skill bodies beyond the `description` string.
- Any product-space change (I11 — framework-only).

## Assumptions

- foundation-hardening v0.46.0 is complete; `framework-maintenance` was unintentionally removed in commit `2f72f1c` (git-verified) and is recoverable from `2371bea`.
- A fresh `one_time_use` Attestation will be provided by the human (Gino) before Wave 1 executes — the agent cannot self-grant a root of trust. The spent bootstrap attestation cannot be reused.
- `attestation-hash.py` is restored as part of the module (it was deleted with it) and validates the new bootstrap the same way the original did.
- `ref-eval`/`ref-plan`/`ref-comp` have no engine module; `.claude/skills/` is canonical for them. `reviewer`/`adversary`/`grader` canonical source is `engine/modules/l2/<m>/SKILL.md`; `.claude/skills/` copies are sync-generated.
- `guard-check.py authority` is the Layer-4 arbiter; PASS for the target files under `framework-maintenance` (post owns-extension) is the gate.
- Python 3.8+ with pyyaml/duckdb available.
- No project-standard drawers discovered in Memory.

## Acceptance Criteria

### Criterion 1: Bootstrap attestation validates

Given a fresh `one_time_use` attestation for the framework-maintenance bootstrap and the staged restored module files
When Wave 1 begins
Then the attestation's `content_hash` equals `sha256(SKILL.md + b"\x00---attestation-separator---\x00" + skill-rules.json)` over the staged files and Guard accepts it; a mismatch MUST halt Wave 1

### Criterion 2: Module restored verbatim

Given `framework-maintenance` was deleted in commit `2f72f1c`
When the module is restored from git `2371bea`
Then `SKILL.md` and `scripts/attestation-hash.py` are byte-identical to their `2371bea` versions and `skill-rules.json` is present

### Criterion 3: authority.owns extended

Given the original `owns` list lacked `.claude/agents/**` and the review-trio paths
When the restored `skill-rules.json` is written with extensions
Then `authority.owns` contains every original entry plus `.claude/agents/**` and `engine/modules/l2/reviewer/**`, `engine/modules/l2/adversary/**`, `engine/modules/l2/grader/**`

### Criterion 4: Module re-registered

Given `wabblespec.yaml` no longer lists `framework-maintenance`
When the module is re-registered
Then `wabblespec.yaml` contains the `framework-maintenance` entry (layer L2, type authority) and `validate-graph.py` exits 0

### Criterion 5: Authority resolves for all targets

Given the registered, owns-extended module
When `guard-check.py authority --module framework-maintenance --files <target>` is run for each B1/B2 target file
Then every target returns Layer 4 PASS

### Criterion 6: Doctor owner-check added

Given `wabblespec-doctor.py` has no shared-infra-owner check
When a check is added asserting the shared-infra anchor paths have an authority owner
Then `wabblespec-doctor.py --self-test` exits 0, a normal run reports the new check green with the owner present, and a simulated owner-absence run emits the finding

### Criterion 7: Guard subagent scoped (tools + I6)

Given `.claude/agents/wabblespec-guard.md` inherits all tools and pins `model: claude-sonnet-4-6`
When it is edited under `--module framework-maintenance`
Then its frontmatter declares `tools: Read, Grep, Glob, Bash` and a grep for `claude-`/`sonnet`/`opus`/`haiku` in the file returns zero matches

### Criterion 8: Verifier subagent scoped (tools + I6)

Given `.claude/agents/wabblespec-verifier.md` inherits all tools and pins `model: claude-sonnet-4-6`
When it is edited under `--module framework-maintenance`
Then its frontmatter declares `tools: Read, Grep, Glob, Bash` and a grep for `claude-`/`sonnet`/`opus`/`haiku` in the file returns zero matches

### Criterion 9: Receipt contract preserved (regression gate)

Given the scoped subagents with restricted toolsets and no model pin
When `wabblespec-guard` and `wabblespec-verifier` are each invoked on a representative wave
Then each returns its declared JSON receipt (guard: `overall`/`status`; verifier: `verdict`/`status`) with no tool-call failure caused by a removed tool

### Criterion 10: Negative triggers added, no sync divergence

Given the `ref-eval`/`ref-plan`/`ref-comp` and `reviewer`/`adversary`/`grader` skill descriptions
When negative-trigger clauses are added (ref-* in `.claude/skills/`, review-trio in `engine/modules/l2/` source) and sync is run
Then each description names its sibling boundary, each skill still loads without a parse error, and `wabblespec-sync-skills.py` reports zero divergence between engine and `.claude/` for the review-trio modules
