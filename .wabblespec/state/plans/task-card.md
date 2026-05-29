# Task Card

**goal:** WabbleSpec's `wabblespec-guard` and `wabblespec-verifier` subagents declare an explicit minimal `tools:` set with no hardcoded model name, and the ref-* and review-trio skill descriptions carry negative-trigger clauses, all without changing any subagent's receipt contract.
**target:** Framework
**complexity:** Medium
**change_class:** COSMETIC
**locked_at:** 2026-05-29T15:00:00Z
**session_id:** agent-creator-integration-20260529

## Non-Goals

- B3 (subagent-vs-skill rubric in CLAUDE.md / authoring conventions) — deferred to Phase 2, gated behind the framework-maintenance authority owner and its own Specify cycle.
- Any change that introduces or references a model name (I6 hard guardrail).
- Importing the reference's token-budget numbers as justification.
- Adopting the unverified `skills:` frontmatter field.
- Changing subagent prompt logic/behavior beyond the `tools:`/`model:` frontmatter, or skill bodies beyond the `description` string.
- Any product-space change (I11 — framework-only).

## Assumptions

- foundation-hardening (v0.46.0) is complete and archived; this builds on that baseline.
- `research/ref-eval/agent-creator.md` and `research/ref-plan/agent-creator.md` are the authoritative source of work items.
- The two subagents invoke a determinable, finite tool set (Read/Grep/Glob/Bash + receipt/JSON writers) — confirmed by reading their definitions during Specify.
- Authority for `.claude/agents/*` writes is unsettled (analogous to finding #29) — to be resolved at Guard Layer 4 during execution; the framework-maintenance owner may or may not cover this surface.
- Python 3.8+ with pyyaml/duckdb available.
- No project-standard drawers discovered in Memory.

## Acceptance Criteria

### Criterion 1: Guard subagent toolset scoped

Given `.claude/agents/wabblespec-guard.md` has no `tools:` frontmatter key (inherits all tools)
When an explicit `tools:` line is added containing exactly the tools its prompt invokes
Then the frontmatter declares `tools: Read, Grep, Glob, Bash` and no longer inherits the full tool set

### Criterion 2: Verifier subagent toolset scoped

Given `.claude/agents/wabblespec-verifier.md` has no `tools:` frontmatter key (inherits all tools)
When an explicit `tools:` line is added containing exactly the tools its prompt invokes
Then the frontmatter declares `tools: Read, Grep, Glob, Bash` and no longer inherits the full tool set

### Criterion 3: Hardcoded model names removed (I6)

Given both subagent files contain `model: claude-sonnet-4-6` on line 4
When the `model:` line is removed from each file
Then neither file contains any model name and a grep for `claude-` / `sonnet` / `opus` / `haiku` across both files returns zero matches

### Criterion 4: Receipt contract preserved (regression gate)

Given the scoped subagents with restricted toolsets and no model pin
When `wabblespec-guard` and `wabblespec-verifier` are each invoked on a representative wave
Then each returns its declared JSON receipt (guard receipt with `overall`/`status`; verifier receipt with `verdict`/`status`) with no tool-call failure caused by a removed tool

### Criterion 5: ref-* descriptions carry negative triggers

Given the `ref-eval`, `ref-plan`, and `ref-comp` skill descriptions
When a negative-trigger clause is added to each
Then each description names its sibling(s) as explicit NOT-for cases (e.g. ref-eval: "NOT for turning findings into a work plan — use ref-plan") and each skill still loads without a parse error

### Criterion 6: review-trio descriptions carry negative triggers

Given the `reviewer`, `adversary`, and `grader` skill descriptions
When a negative-trigger clause is added to each
Then each description names the adjacent module's boundary and each skill still loads without a parse error

### Criterion 7: Source-of-truth edited, no sync divergence

Given `.claude/agents/` and `.claude/skills/` may be sync-generated from `.wabblespec/engine/`
When the canonical source-of-truth copy is determined and edited
Then re-running the skill sync reproduces the edits in `.claude/` (or confirms `.claude/` is canonical), and `wabblespec-sync-skills.py` reports zero stale/divergent files for the touched modules
