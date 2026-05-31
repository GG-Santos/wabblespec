# Ref-Eval: OpenSpec

**Reference:** `C:\Users\Kirsten\Downloads\Orchestrator\OpenSpec`
**Slug:** `openspec`
**Evaluated:** 2026-05-30
**Trust level:** MEDIUM
**Session:** agent-creator-integration-20260529

---

## Step 1b — File Inventory

| Path | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| README.md | Project overview + quickstart | Medium | Philosophy, quickstart, model recommendation (I6 flag) | Read |
| AGENTS.md | Agent guidance | Small | Empty (1 line) | Read |
| docs/concepts.md | Core concepts: specs, changes, artifacts, schemas, archive | Large | Full delta format definition, GWT scenario format, schema DAG | Read |
| docs/commands.md | Slash command reference | Large | All /opsx:* commands with behavior detail | Read |
| docs/opsx.md | OPSX workflow architecture | Large | Legacy vs. OPSX comparison, dependency graph model, CLI query pattern | Read |
| docs/workflows.md | Workflow patterns | Medium | Quick/exploratory/parallel/completion patterns | Read |
| docs/customization.md | Config + schema creation | Medium | context/rules injection format, schema resolution order | Read (partial) |
| schemas/spec-driven/schema.yaml | Default schema definition | Small | Artifact DAG, embedded instruction per artifact, apply section | Read |
| schemas/spec-driven/templates/spec.md | Spec template | Small | ADDED/MODIFIED/REMOVED section headers | Read |
| schemas/spec-driven/templates/tasks.md | Tasks template | Small | Checkbox task format | Read |
| src/core/artifact-graph/schema.ts | Schema loader + validator | Small | Zod validation, duplicate ID check, cycle detection via DFS | Read |
| src/core/artifact-graph/graph.ts | ArtifactGraph class | Small | Kahn's algorithm topological sort, BLOCKED/READY/DONE state | Read |
| src/core/command-generation/adapters/claude.ts | Claude Code adapter | Small | File path: `.claude/commands/opsx/<id>.md`, frontmatter format | Read |
| package.json | Package metadata | Small | `@fission-ai/openspec`, Node 20.19.0+ requirement | Skipped (not relevant) |
| src/commands/* | CLI command implementations | Large | 25+ command files | Skipped (implementation detail) |
| openspec/changes/* | Sample change proposals | Small | In-progress reference specs for OpenSpec itself | Skipped |
| test/* | 150+ test files | Large | vitest, strong test coverage | Skipped (implementation detail) |
| .github/workflows/* | CI pipelines | Small | ci.yml, release-prepare.yml | Skipped |

**Reference type:** Production application (TypeScript CLI, npm package). Active CI, 150+ tests, versioned npm releases, Discord community, real usage evidence.

**Red flags:** README.md line 161 recommends specific model names ("Codex 5.5 and Opus 4.7") — `do_not_copy` per I6.

---

## Step 1c — Connection Map

```
[schemas/spec-driven/schema.yaml] --defines--> [ArtifactGraph]: artifact IDs, dependency array, instruction strings, template paths
[ArtifactGraph] --produces--> [openspec status --json]: BLOCKED/READY/DONE states per artifact
[openspec instructions <id> --json] --reads--> [schema.yaml + config.yaml + templates/*.md]: merged instruction output
[openspec/config.yaml] --injects--> [instruction output]: <context> and <rules> wrapper tags
[instruction output] --consumed-by--> [.claude/commands/opsx/<id>.md / .claude/skills/openspec-*/SKILL.md]: agent receives
[agent] --writes--> [openspec/changes/<name>/proposal.md|specs/**/*.md|design.md|tasks.md]
[delta spec files] --merged-into--> [openspec/specs/<domain>/spec.md] at archive time
[.openspec.yaml in change folder] --schema-override--> [schema resolution chain]
```

Key contracts:
- If `schema.yaml artifact.requires[]` references a non-existent ID, schema validation throws `SchemaValidationError`
- If `openspec status --json` contract changes (field names), all skill files querying it break
- `<context>` injection depends on `openspec/config.yaml` being present; absent = no injection, not an error
- Delta spec headers must be exact strings: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements` — any variation causes the archive merge to silently miss sections

---

## Dimension 1 — Behavior (Operational Detail)

**Artifact state machine:**
- BLOCKED: one or more `requires` entries not in completedSet
- READY: all `requires` entries in completedSet AND file does not exist on filesystem
- DONE: file matching `generates` glob exists on filesystem
- State transitions: BLOCKED → READY when dependency file appears on disk; READY → DONE when generated file appears on disk
- No database, no receipts — filesystem is the sole state store

**Schema resolution order (highest to lowest):**
1. `--schema <name>` CLI flag
2. `.openspec.yaml` in change folder (`schema:` field)
3. `openspec/config.yaml` (`schema:` field)
4. Default: `spec-driven`

**Cycle detection:** DFS with `inStack` set; detects and reports full cycle path (e.g., `a → b → c → a`)

**Delta archive merge rules:**
- `## ADDED Requirements`: appended to target spec
- `## MODIFIED Requirements`: replaces matched requirement by header text (whitespace-insensitive)
- `## REMOVED Requirements`: deletes matched requirement from target spec
- `## RENAMED Requirements`: FROM:/TO: format renames header text only
- Partial MODIFIED content silently drops unchanged sections — must copy full requirement block

**Context injection format (exact):**
```xml
<context>
[content from openspec/config.yaml context: field]
</context>

<rules>
[content from openspec/config.yaml rules.<artifact-id>: list]
</rules>

<template>
[artifact template content]
</template>
```

**Verification dimensions** (`/opsx:verify`): COMPLETENESS (tasks done, requirements implemented, scenarios covered), CORRECTNESS (implementation matches spec intent, edge cases handled), COHERENCE (design decisions reflected in code)

**Bulk archive conflict detection:** Detects when >1 changes touch same spec file; resolves by checking actual implementation in codebase; archives in chronological creation order

**Profile system:**
- `core` profile: propose, explore, apply, sync, archive
- `expanded` profile: adds new, continue, ff, verify, bulk-archive, onboard
- Profile selection via `openspec config profile` + `openspec update`

**Telemetry:** Collects command name + version only. Disabled in CI. Opt-out: `OPENSPEC_TELEMETRY=0` or `DO_NOT_TRACK=1`

---

## Dimension 2 — Format (Identifier Level)

**Schema YAML fields:**
```yaml
name: string           # schema identifier
version: number        # schema version
description: string    # human label
artifacts:
  - id: string         # unique artifact identifier, kebab-case
    generates: string  # glob pattern (e.g., "specs/**/*.md")
    description: string
    template: string   # filename in templates/ dir
    instruction: string # multiline agent instructions
    requires: string[] # artifact IDs this depends on
apply:
  requires: string[]   # artifact IDs that must exist before apply
  tracks: string       # file path for checkbox task tracking
  instruction: string
```

**Change metadata** (`.openspec.yaml`):
```yaml
schema: string         # schema name override
created: ISO-date
```

**Artifact status JSON** (from `openspec status --change "x" --json`):
```json
{
  "artifacts": [
    {"id": "proposal", "status": "done"},
    {"id": "specs", "status": "ready"},
    {"id": "tasks", "status": "blocked", "missingDeps": ["specs"]}
  ]
}
```

**Delta spec section headers** (exact — whitespace-sensitive):
```
## ADDED Requirements
## MODIFIED Requirements
## REMOVED Requirements
## RENAMED Requirements
```

**Requirement format:**
```markdown
### Requirement: <name>
<description using SHALL/MUST>

#### Scenario: <name>
- **WHEN** <condition>
- **THEN** <expected outcome>
```

**RFC 2119 keywords:** SHALL/MUST (absolute), SHOULD (recommended), MAY (optional)

**Task checkbox format:**
```markdown
## 1. <Group Name>
- [ ] 1.1 <Task description>
- [ ] 1.2 <Task description>
```

**Claude Code command file path:** `.claude/commands/opsx/<id>.md`
**Claude Code skill file path:** `.claude/skills/openspec-<id>/SKILL.md`
**Claude Code command frontmatter:** `name`, `description`, `category`, `tags` fields

---

## Dimension 3 — Interactions (Contract Level)

| Producer | Consumer | Contract | Break Condition |
|---|---|---|---|
| `schema.yaml` | `ArtifactGraph` | Zod-validated YAML; `requires[]` IDs must exist in same file | Any unknown ID in `requires` → SchemaValidationError |
| `openspec status --change x --json` | Skill files (OPSX commands) | JSON with `artifacts[]` array, each entry has `id` and `status` string | Field rename breaks all skill templates |
| `openspec instructions <id> --change x --json` | Skill files | JSON with `template`, `dependencies`, `unlocks` fields | Field rename breaks agent instruction loading |
| `openspec/config.yaml` | Instruction generator | `context:` (string), `rules:` (object keyed by artifact ID) | `context` over 50KB → error; unknown artifact ID in `rules` → warning |
| Delta spec files | Archive command | Section headers must exactly match ADDED/MODIFIED/REMOVED/RENAMED | Wrong case or extra chars → silent miss |
| `tasks.md` checkboxes | `/opsx:apply` tracking | Must use `- [ ]` format exactly | `- []` or `* [ ]` or other format → not tracked |

---

## Section 1 — Reference Summary

OpenSpec is a production TypeScript CLI tool (npm: `@fission-ai/openspec`) that adds a lightweight spec layer to AI-assisted development. It solves the problem of AI coding assistants being unpredictable when requirements live only in chat history.

**Behavioral content:** Workflow state management via artifact dependency DAG; delta spec merging (ADDED/MODIFIED/REMOVED/RENAMED) into source-of-truth specs; multi-profile command dispatch (core vs. expanded); schema resolution priority chain; context/rules injection into agent instructions; bulk archive conflict detection.

**Structural content:** Change folder convention (`openspec/changes/<name>/`); schema YAML with embedded artifact instructions; delta spec headers as structural markers; checkbox task tracking; artifact status JSON protocol between CLI and agent skills.

**Interaction content:** CLI-to-skill handoff via `openspec status --json` and `openspec instructions --json`; config.yaml context injection; schema.yaml → ArtifactGraph → instruction loader → skill file pipeline.

**Mature:** Core artifact graph, schema validation, delta merge, multi-tool adapter pattern, test suite.
**Beta:** Workspace/initiative coordination, context stores.
**Experimental:** Some multi-repo workspace features.
**Unclear:** How conflict resolution in bulk-archive decides "what's implemented" (appears to be LLM judgment).

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `schemas/spec-driven/schema.yaml` instruction fields | Per-artifact instruction embedding pattern | Wave plan could embed per-wave agent instructions directly instead of relying on executor to re-derive from task card | Add optional `instruction:` field to wave plan YAML format in `wave-plan-writer.py` | Medium |
| `docs/concepts.md` §Delta Specs, `schemas/spec-driven/templates/spec.md` | ADDED/MODIFIED/REMOVED/RENAMED section structure for brownfield acceptance criteria | Most WabbleSpec tasks are brownfield framework changes; the flat GWT format doesn't distinguish new from modified from removed behaviors | Add `## Delta Acceptance Criteria Format` to `.claude/skills/specify/SKILL.md` documenting this structure as an option for change-class ADDITIVE vs. REMOVAL tasks | Medium |
| `docs/opsx.md` §Information Flow / docs/customization.md | `<context>` and `<rules>` XML tag injection pattern | Structured way to separate project context from artifact-specific rules in scope/recipe → specify chain | Document this tagging convention in `.claude/skills/scope-frame/SKILL.md` as the recommended format for injecting session constraints into downstream artifacts | Low |
| `src/core/artifact-graph/graph.ts` | Kahn's algorithm artifact ordering + BLOCKED/READY/DONE state labels | Decompose produces wave plans with sequential dependencies; explicit state labels would make wave status reports more readable | Add BLOCKED/READY/DONE label output to `wave-plan-writer.py --status` output format | Low |
| `docs/concepts.md` §Update vs. Start Fresh decision tree | Explicit heuristic for when to update vs. re-specify | Executor and Autopilot need clear rules for when scope expansion triggers re-specify vs. continues | Add this decision tree to `.claude/skills/decompose/SKILL.md` under a `## Scope Expansion Heuristic` section | Low |
| `docs/customization.md` §How It Works (context/rules injection) | `<context>` wrapping convention in config | WabbleSpec's `openspec/config.yaml` equivalent is `scope.md` + `recipe.json`; structuring the context block output in a machine-parseable way would help downstream skills | Low adoption cost; improves downstream parsing reliability | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `docs/opsx.md` §Philosophy, `docs/concepts.md` §Philosophy | "Fluid not rigid / no phase gates" philosophy | Directly contradicts I1 (SPEC IS SINGLE SOURCE OF TRUTH; P2 blocked until P1 locked). Adopting this would erode the receipt-gated enforcement model. | Treat as inspiration only; adapt specific format patterns, never the anti-gating philosophy | High |
| `README.md` line 161 | Model name recommendations ("Codex 5.5 and Opus 4.7") | I6 violation if copied verbatim | `do_not_copy`: use capability descriptors instead | High |
| Workspace/initiative beta features | Unfinished multi-repo coordination model | beta-flagged in docs; state file shapes still evolving | Do not adopt workspace concepts; repo-local patterns only | Medium |
| `src/core/artifact-graph/state.ts` | Filesystem-as-state model (existence = done) | WabbleSpec uses receipts as state; adopting pure filesystem-existence state would break the receipt chain (I10) | Adapt state labels only, not the underlying state detection mechanism | Medium |
| `docs/concepts.md` | Progressive rigor ("use lightest level that makes change verifiable") | WabbleSpec's quality floor enforces explicit receipt at every non-trivial step; "lite spec" concept would undermine I10 | Do not adopt the "lite spec" concept; WabbleSpec's explicit receipt requirement is non-negotiable | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Decision | Reason | Target Area | Priority |
|---|---|---|---|---|
| Delta spec section format (ADDED/MODIFIED/REMOVED) | Adapt | Clean brownfield change structure, no invariant conflict | `.claude/skills/specify/SKILL.md` | Medium |
| Per-artifact instruction embedding in schema YAML | Adapt | Could make wave plans more self-contained | `wave-plan-writer.py` | Low |
| `<context>` / `<rules>` XML injection convention | Adapt | Low-cost improvement to scope-frame output structure | `.claude/skills/scope-frame/SKILL.md` | Low |
| BLOCKED/READY/DONE state labels | Adapt | Readable status labels for wave plan display | `wave-plan-writer.py` | Low |
| Update vs. Start Fresh decision tree | Adapt (Study Only) | The heuristic is valid but WabbleSpec enforces this differently (re-trigger ScopeFrame); study the logic, don't copy the flow | `.claude/skills/decompose/SKILL.md` | Low |
| "Fluid not rigid" philosophy | Avoid | Contradicts I1 | All execution skills | High |
| Filesystem-as-state model | Avoid | Contradicts I10 (receipt chain) | All execution scripts | High |
| Model name recommendations (README line 161) | Avoid | I6 violation | All output artifacts | High |
| Workspace / initiative beta | Avoid | Beta-flagged, incompatible with WabbleSpec session model | N/A | Medium |
| "Lite spec" progressive rigor | Avoid | Contradicts I10 | N/A | Medium |
| npm/TypeScript CLI implementation patterns | Study Only | WabbleSpec uses Python; implementation not portable | N/A | Low |
| Multi-tool adapter pattern (25+ adapters) | Study Only | WabbleSpec targets Claude Code only; interesting for future portability | N/A | Low |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 5 | Spec-driven development concepts align at surface level; the gated-receipt vs. fluid-actions split is a fundamental divergence |
| Architecture fit | 4 | TypeScript CLI + npm vs. Python scripts + SKILL.md; slash command generation vs. WabbleSpec's skill sync; different state models (filesystem vs. receipts) |
| Implementation fit | 6 | The format patterns (delta sections, instruction embedding, context tags) are portable; the TypeScript implementation is not |
| Maintenance fit | 7 | Adopting only format conventions creates minimal maintenance burden; they are self-documenting |
| Risk level | 3 | (3 = low risk) Selected patterns can be adopted without touching invariants; the dangerous patterns (fluid philosophy, filesystem state) are clearly flagged |
| Overall usefulness | 5 | Specific format patterns have clear value; the architectural model is misaligned with WabbleSpec's enforcement design |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — do now):**
- `schemas/spec-driven/templates/spec.md` + `docs/concepts.md` §Delta Specs: Add ADDED/MODIFIED/REMOVED delta section format to `specify` SKILL.md as an optional acceptance criteria structure for brownfield task cards
- `docs/customization.md` §How It Works: Document `<context>` / `<rules>` injection convention in `scope-frame` SKILL.md

**Phase 2 (Low-Risk Adaptation — next session):**
- `schemas/spec-driven/schema.yaml` §instruction fields: Extend `wave-plan-writer.py` to optionally embed per-wave agent instructions inline in the wave plan YAML
- `src/core/artifact-graph/graph.ts` §getBuildOrder: Add BLOCKED/READY/DONE state label output to wave plan status display

**Phase 3 (Deeper Integration — deferred):**
- Multi-tool skill generation: Build a WabbleSpec skill exporter that generates skill files for tools beyond Claude Code (requires a separate recipe session)

**Phase 4 (Do Not Cross):**
- "Fluid not rigid" philosophy (contradicts I1)
- Filesystem-as-state model (contradicts I10)
- Model name verbatim copy (contradicts I6)
- Workspace/initiative beta features (incompatible)

---

## Section 7 — Final Verdict

**Reference classification: supporting-reference**

This is a production-quality, well-tested tool that solves an adjacent problem (spec-driven AI development workflow management). The conceptual overlap with WabbleSpec is real but shallow — both are spec-driven frameworks for AI-assisted work, but OpenSpec optimizes for low-friction fluidity while WabbleSpec optimizes for receipt-gated enforcement. These are not compatible design philosophies at the system level.

**Best 3 to steal:**
1. Delta spec section format (`docs/concepts.md`, `schemas/spec-driven/templates/spec.md`) — ADDED/MODIFIED/REMOVED structure is clean, explicit, and directly applicable to WabbleSpec's brownfield task cards
2. Context/rules injection convention (`docs/customization.md`) — the `<context>` / `<rules>` XML tag wrapping pattern is a low-cost improvement to scope-frame output
3. Per-artifact instruction embedding (`schemas/spec-driven/schema.yaml`) — embedding agent instructions inline in the workflow definition (rather than only in prose SKILL.md files) is a pattern worth studying for wave plan evolution

**Worst 3 to avoid:**
1. "Fluid not rigid / no phase gates" philosophy (`docs/opsx.md`, `docs/concepts.md`) — directly contradicts I1; would erode WabbleSpec's entire enforcement architecture if adopted
2. Model name recommendations (`README.md` line 161) — I6 hard violation; do not reproduce
3. Filesystem-as-state model (`src/core/artifact-graph/state.ts`) — receipt chain (I10) is WabbleSpec's audit backbone; replacing it with existence-check state would be regressive

**Recommended next action:** Adopt Phase 1 items in this session (2 Tier 1 additions to existing skill files). Defer Phase 2 to a dedicated wave. Do not adopt architectural patterns.

---

## Section 8 — Project Synthesis

**What novel patterns become possible by combining OpenSpec's approaches with WabbleSpec's specific capabilities?**

### Synthesis 1: Delta-Keyed Acceptance Criteria

**What:** A delta-structured task card where acceptance criteria are organized under ADDED/MODIFIED/REMOVED headers instead of a flat GWT list.

**Reference contribution:** OpenSpec's delta spec format — section headers that explicitly tag whether a requirement is new, changed, or deprecated.

**Project contribution:** WabbleSpec's `change_class` field in task cards (`ADDITIVE`, `REFACTOR`, `REMOVAL`); the Verifier's per-criterion verdict model which already processes criteria individually.

**Target:** `.claude/skills/specify/SKILL.md` — add an optional `## Delta Acceptance Criteria` section in the task card output when `change_class` is `ADDITIVE` or `REMOVAL`; map ADDED to new behaviors, MODIFIED to changed behaviors, REMOVED to deprecated behaviors.

**Gap closed:** Currently WabbleSpec's GWT criteria make no distinction between "this behavior is new" and "this behavior is changing." For framework-change tasks (most of the work), that distinction matters for Verifier — it needs to know whether to check for presence (ADDED) or for replacement (MODIFIED) or for absence (REMOVED). OpenSpec's section headers make this machine-readable.

### Synthesis 2: Instruction-Embedded Wave Plan

**What:** A wave plan format where each wave contains not just `goal` and `checkpoint` but an `instruction` block — the agent's task for that wave — eliminating the Executor's need to re-derive per-wave action from the task card.

**Reference contribution:** OpenSpec's `instruction:` field per artifact in `schema.yaml` — a self-contained behavioral description embedded directly in the workflow definition.

**Project contribution:** WabbleSpec's `wave-plan-writer.py` and the Executor skill which currently reads the task card + wave plan separately to derive per-wave action.

**Target:** `wave-plan-writer.py` (add optional `--instructions` flag + `instruction:` field in wave YAML output); `.claude/skills/executor/SKILL.md` (update wave loop to read `instruction:` field if present, fall back to task card synthesis if absent).

**Gap closed:** The Executor currently must synthesize per-wave action from the combination of task card goal + wave checkpoint description. Embedding instructions makes the wave plan self-contained and reduces Executor context requirements.

---

## Section 9 — Expansion Opportunities

**What can OpenSpec do that WabbleSpec cannot at all?**

### Expansion 1: Multi-Tool Skill Generation

**Capability:** Generate skill/command files for 25+ AI coding tools (Claude Code, Cursor, Windsurf, Copilot, Amazon Q, Gemini, etc.) from a single source schema.

**Reference location:** `src/core/command-generation/adapters/*.ts` (25+ adapter files)

**Why the project lacks it:** WabbleSpec targets Claude Code exclusively; `wabblespec-sync-skills.py` generates `.claude/skills/` only.

**What it would unlock:** WabbleSpec framework could be used with any AI coding tool, not just Claude Code. Users could switch tools without re-implementing the framework.

**Dependencies:** Abstract the skill template format away from Claude-specific frontmatter; write adapters per target tool.

**Effort signal:** weeks

**Tier 7 candidate:** Yes

### Expansion 2: Schema-Defined Custom Workflow Initialization

**Capability:** `openspec schema init <name>` — interactive wizard that creates a custom artifact dependency graph for a project's specific workflow. Non-technical users can define their own phase sequence.

**Reference location:** `src/commands/schema.ts`, `openspec schema init` command

**Why the project lacks it:** WabbleSpec's workflow (Recipe → ScopeFrame → Specify → Decompose → Execute → Verify → Archive) is hardcoded in SKILL.md prose. No mechanism for users to fork and customize the phase sequence without editing skill files.

**What it would unlock:** Teams could create custom WabbleSpec execution schemas (e.g., a `research-first` schema that adds a research phase before specification, or a `rapid` schema that collapses decompose+execute).

**Dependencies:** Externalize WabbleSpec's phase sequence into a YAML schema format; build a schema init wizard; make Executor schema-aware.

**Effort signal:** months

**Tier 7 candidate:** Yes

### Expansion 3: Parallel Change Conflict Detection

**Capability:** When multiple parallel sessions touch overlapping WabbleSpec modules, detect conflicts before archive and resolve chronologically.

**Reference location:** `docs/commands.md` §/opsx:bulk-archive, src/core/archive.ts

**Why the project lacks it:** WabbleSpec sessions are single-agent, single-task; no mechanism exists for detecting or resolving parallel session conflicts at archive time.

**What it would unlock:** Team-scale WabbleSpec usage where multiple engineers run concurrent framework evolution tasks; prevents the "two sessions modify the same skill file" silent overwrite scenario.

**Dependencies:** Session registry already exists (`session-registry.py`); would need a conflict detection script that compares changed file sets across sessions before archive.

**Effort signal:** days

**Tier 7 candidate:** Yes
