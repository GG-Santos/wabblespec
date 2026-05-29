# Session Scope

**target:** Framework
**complexity:** High
**locked_at:** 2026-05-29T15:20:00Z
**session_id:** agent-creator-integration-20260529

## In Scope

- Restore the `framework-maintenance` L2 authority module verbatim from git `2371bea` (SKILL.md, skill-rules.json, scripts/attestation-hash.py) and re-register its `wabblespec.yaml` entry (recoverable from `2371bea`).
- Extend `framework-maintenance` `authority.owns` beyond the verbatim list with `.claude/agents/**` and `engine/modules/l2/{reviewer,adversary,grader}/**` (to cover B1 and the review-trio canonical sources).
- Add a `wabblespec-doctor.py` check asserting the shared-infra anchor paths have an authority owner; emits a finding when none exists (advisory, matching the doctor's current posture).
- **B1** — add `tools: Read, Grep, Glob, Bash` to `.claude/agents/wabblespec-guard.md` and `.claude/agents/wabblespec-verifier.md`, and remove their hardcoded `model: claude-sonnet-4-6` (I6).
- **B1 gate** — verify both subagents still return valid guard/verification JSON receipts after scoping.
- **B2** — add negative-trigger clauses to `ref-eval`/`ref-plan`/`ref-comp` (edit `.claude/skills/` — canonical for these) and `reviewer`/`adversary`/`grader` (edit `engine/modules/l2/` source, then sync).
- Perform all shared-infra writes under `--module framework-maintenance`, bootstrapped by one fresh `one_time_use` human Attestation; reconcile source-of-truth so `.claude/` and `engine/modules/` do not diverge.

## Out of Scope

- Rewriting foundation-hardening's closed delivery receipt / AC8 — the regression is logged (memory + this task's receipts), not retro-edited into an archived task.
- A general "every module owns its own SKILL.md" authority-model refactor across all 103 modules — only the touched review-trio paths are added now.
- **B3** (subagent-vs-skill rubric in CLAUDE.md / authoring conventions) — still deferred to a later Phase 2.
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

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
| 2026-05-29T14:52:00Z | Initial scope locked (Phase 1: B1 + B2) | user-confirmed |
| 2026-05-29T15:00:00Z | Re-framed in: remove hardcoded `model: claude-sonnet-4-6` (I6 fix) from both subagent files — discovered during Specify file read | user-confirmed |
| 2026-05-29T15:20:00Z | Major re-frame: add framework-maintenance restore + owns extension + doctor check + attestation bootstrap; complexity Medium→High | Decompose discovered no authority owner (finding #29 regression); user confirmed unintended |
