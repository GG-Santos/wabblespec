# Session Scope

**target:** Framework
**complexity:** Medium
**locked_at:** 2026-05-29T14:52:00Z
**session_id:** agent-creator-integration-20260529

## In Scope

- **B1** — Add an explicit minimal `tools:` line to `.claude/agents/wabblespec-guard.md` (currently absent → inherits all tools) matching its actual invocations.
- **B1** — Add an explicit minimal `tools:` line to `.claude/agents/wabblespec-verifier.md` (currently absent → inherits all tools) matching its actual invocations.
- **B1+ (I6 fix, re-framed in)** — Remove the hardcoded `model: claude-sonnet-4-6` line from both subagent files (omit `model:` so the lane is selected by capability per I6/ModelRouter).
- **B1 gate** — Verify both subagents still produce valid guard/verification receipts after scoping (regression check).
- **B2** — Add negative-trigger clauses to the ref-* skill descriptions (`ref-eval`, `ref-plan`, `ref-comp`), each pointing at its sibling.
- **B2** — Add negative-trigger clauses to the review-trio descriptions (`reviewer`, `adversary`, `grader`).
- Determine the source-of-truth for the edited files (direct `.claude/` vs sync-generated from `.wabblespec/engine/`) and edit the correct copy, re-syncing if needed.

## Out of Scope

- **B3** (subagent-vs-skill rubric in CLAUDE.md / authoring conventions) — deferred to Phase 2, gated behind the framework-maintenance authority owner and its own Specify cycle.
- Any change that introduces or references a model name (I6 hard guardrail).
- Importing the reference's token-budget numbers as justification.
- Adopting the unverified `skills:` frontmatter field.
- Changing subagent prompt logic/behavior beyond the `tools:` frontmatter, or skill bodies beyond the `description` string.
- Any product-space change (I11 — framework-only).

## Assumptions

- foundation-hardening (v0.46.0) is complete and archived; this builds on that baseline.
- `research/ref-eval/agent-creator.md` and `research/ref-plan/agent-creator.md` are the authoritative source of work items.
- The two subagents invoke a determinable, finite tool set (Read/Grep/Glob/Bash + receipt/JSON writers) — to be confirmed by reading their definitions during Specify.
- Authority for `.claude/agents/*` writes is unsettled (analogous to finding #29) — to be resolved at Guard Layer 4 during execution; the framework-maintenance owner may or may not cover this surface.
- Python 3.8+ with pyyaml/duckdb available.
- No project-standard drawers discovered in Memory.

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
| 2026-05-29T14:52:00Z | Initial scope locked (Phase 1: B1 + B2) | user-confirmed |
| 2026-05-29T15:00:00Z | Re-framed in: remove hardcoded `model: claude-sonnet-4-6` (I6 fix) from both subagent files — discovered during Specify file read | user-confirmed |
