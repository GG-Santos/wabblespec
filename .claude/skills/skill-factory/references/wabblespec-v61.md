# WabbleSpec v6.1 Build Mode

Load this alongside `references/framework-mode.md` when working inside
`C:\Vaults\WabbleSpec v6.1\` or on `.wabblespec/` module files. This
reference overrides generic Framework Mode with WabbleSpec-specific build
protocols.

WabbleSpec v6.1 is a spec-driven skill framework for the complete software
development lifecycle. 9 layers, 50+ modules, 12 invariants, zero external
dependencies. The full per-module planning is already done — your job is to
translate planning artifacts into working module files, one module at a time,
across as many sessions as it takes.

---

## Source of Truth Hierarchy

Always read sources in this order. Later sources may not override earlier ones.

1. `planning/01-INVARIANTS.md` — 12 locked invariants. All module output must comply.
2. `planning/02-ARCHITECTURE.md` — directory layout, layer map, module anatomy.
3. `planning/03-CORE-FEATURES.md` — what each layer delivers to users.
4. `planning/04-SKILLS-FLOW.md` — how modules chain, communicate, and hand off.
5. `planning/05-MODULE-IMPORTANCE.md` — tier classification, dependency chain, build order.
6. `planning/modules/P{N}-{MODULE}.md` — per-module spec. Ground truth for that module.
7. `planning/modules/PROGRESS.md` — what has been planned and what has been built.

Do not invent module behavior. If the planning doc doesn't say it, ask before adding it.

---

## Session Start Protocol

Do this at the start of every WabbleSpec build session:

1. Read `planning/modules/PROGRESS.md` — determines what's planned and what's built.
2. Check whether `.wabblespec/framework.yaml` exists. If it does, read it. If not, the build has not started.
3. Identify the lowest-priority unbuilt module group from the build order below.
4. Report current state concisely:
   - Modules built: N
   - Current build priority: P{N}
   - Next module group: {names}
   - Any `quality_floor_passed: false` entries in framework.yaml
5. Ask the user which module to work on, or proceed with the next unbuilt priority if they say "continue".

Never silently assume state. If framework.yaml is missing or stale, name the gap before proceeding.

---

## Build Order

Follows `planning/05-MODULE-IMPORTANCE.md` dependency chain. Do not skip ahead.
A module at P{N} cannot be well-built without P{N-1} modules already present.

| Priority | Module(s) | Layer |
|---|---|---|
| P1 | `skill-rules.json` schema, `receipt.base.schema.json`, `error-event.schema.json` | `_shared/schemas/` |
| P2 | Recipe, Memory, Economy | L0, L5, L2 |
| P3 | ScopeFrame, ReferenceLoad, RuntimeProbe, Provenance | L0, L5 |
| P4 | Specify, MemorySearch, ModelRouter, Homowabian | L1, L5, L2, L6 |
| P5 | Interview, Explore, Decompose, Reviewer | L1, L2 |
| P6 | Propose, Executor, Verifier | L1, L2 |
| P7 | Apply, Archive | L1, L7 |
| P8 | Autopilot, Ensemble, EntityGraph, Dream, TeamPlan | L2, L5 |
| P9 | `_shared/dev/` (languages, databases, api-consumption) | `_shared/` |
| P10 | All 11 platform packages | L3 |
| P11 | All 6 capability gateways | L4 |
| P12 | Document, Polish, ResearchLog | L6 |
| P13 | Deploy, Package, Release | L7 |
| P14 | Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge | L8 |
| P15 | 29 v5.3 carry-forward modules (see `05-MODULE-IMPORTANCE.md`) | varies |

Within a priority group, pick any order. Prefer modules with no `depends_on` entries first.

---

## Directory Layout

All framework files go in `.wabblespec/`. Product source goes in `project/repo/`.
These spaces never mix (I11). Build into the correct location — never
write module files into `project/repo/`.

```
.wabblespec/
  INDEX.md                        # module registry (human-readable)
  framework.yaml                  # manifest (machine-readable)
  memory/                         # evidence store
  runtime/                        # vendor-neutral runtime contracts
  experiments/                    # evolution isolation — never promoted directly
  plans/                          # planning artifacts
  receipts/                       # operational receipts
  _shared/
    schemas/
      skill-rules.schema.json     # P1 — built first
      receipt.base.schema.json    # P1
      error-event.schema.json     # P1
    dev/
      languages/                  # P9 — Node, Python, Go, Rust, Java
      databases/                  # P9 — SQL, NoSQL, ORM, Migration
      api-consumption/            # P9 — REST/GraphQL/gRPC/Realtime client patterns
    references/
      development-patterns.md     # P9
  modules/
    L0/intake/
      recipe/
      scopeframe/
      referenceload/
      runtimeprobe/
    L1/spec-core/
      apply/
      decompose/
      explore/
      interview/
      propose/
      specify/
    L2/orchestration/
      autopilot/
      economy/
      ensemble/
      executor/
      modelrouter/
      reviewer/
      teamplan/
      verifier/
    L3/platform/
      web/
      api-service/
      game/
      mobile/
      desktop/
      cli/
      iot-embedded/
      library-package/
      extension-plugin/
      data-pipeline/
      ai-agent/
    L4/capability/
      security/
      engineering/
      ai/
      aesthetic/
      design/
      experience/
    L5/memory/
      dream/
      entitygraph/
      forget/
      memory/
      memorymine/
      memorysearch/
      provenance/
    L6/expression/
      document/
      homowabian/
      polish/
      researchlog/
    L7/delivery/
      archive/
      deploy/
      package/
      release/
      scaffold/
      monitor/
    L8/evolution/
      instinct/
      synth/
      blueprint/
      factory/
      augment/
      benchmark/
      forge/
      feedback/
      retro/
```

---

## Module Anatomy

Every module needs these files. No exceptions. Read `planning/02-ARCHITECTURE.md`
section "Module Anatomy" for authority.

```
modules/{layer-dir}/{module-name}/
  SKILL.md                       # required — orchestration spec, routing, decision logic
  skill-rules.json               # required — activation patterns + module authority
  schemas/
    receipt.schema.json          # required — extends receipt.base.schema.json
  tests/
    acceptance.md                # required — checkable acceptance criteria
  receipts/
    MODULE-RECEIPT.md            # required — generation receipt (operational artifact, I10)
```

Conditional additions (only when needed — don't scaffold empty dirs):
- `references/` — domain knowledge loaded on demand
- `rules/` — constraints, policy, validation
- `evaluations/` — eval cases and assertions
- `agents/` — subagent role definitions
- `scripts/` — deterministic computation offloaded from LLM
- `schemas/` — additional input/output schemas
- `templates/` — output templates

### skill-rules.json minimum structure

```json
{
  "module": "module-name",
  "layer": "L0|L1|L2|L3|L4|L5|L6|L7|L8",
  "authority": ["list of output artifacts this module owns"],
  "activation": {
    "patterns": ["keyword patterns that trigger this module"],
    "stage": ["P1|P2|P3|P4|execution"],
    "phase": ["research|plan|execute|any"]
  },
  "verification_mode": "Test|Review|Audit|Measurement|Observation|Attestation|Demonstration",
  "revise_max_cycles": 3
}
```

Authority declarations must be unique across modules. If two modules claim
the same output, resolve the conflict before writing either module.

### receipt.schema.json minimum fields (beyond base)

Every module's receipt schema extends the base with module-specific fields.
Required base fields (from `_shared/schemas/receipt.base.schema.json`):
`module`, `layer`, `runtime`, `platforms`, `inputs`, `outputs`,
`tools_used`, `memory_updates`, `validation`, `not_tested`, `confidence`.

Not-tested is mandatory. Implied completion is a defect.

---

## Per-Module Build Workflow

For each module:

1. **Read the planning doc.** `planning/modules/P{N}-{MODULE}.md`. Read the full
   doc before writing any file. The planning doc is the spec. Implement it exactly.

2. **Read upstream planning docs** if the module has `depends_on` entries in
   `planning/05-MODULE-IMPORTANCE.md`. You need their output artifacts to define
   this module's inputs correctly.

3. **Check invariant compliance.** Before writing SKILL.md, run through the
   12-invariant checklist below. Note which invariants apply to this module.

4. **Write module files** in the correct directory. SKILL.md first, then
   skill-rules.json, then schemas/receipt.schema.json, then tests/acceptance.md.

5. **Write MODULE-RECEIPT.md.** Record what was built, what was not built,
   confidence level, and any open decisions from the planning doc.

6. **Update framework.yaml.** Add or update the module entry. Mark
   `planning_complete: true` and `build_complete: true` (or `false` with
   a note if the module is partial).

7. **Run module-auditor.** Read `agents/module-auditor.md` and run a
   lightweight quality pass on the new module's SKILL.md before moving on.

Build one module per chunk of work. Don't start a second module until the
first has its receipt written and framework.yaml updated.

---

## 12-Invariant Compliance Checklist

Apply these checks to every module SKILL.md before shipping. Not all invariants
apply to every module — mark N/A with a reason when skipping.

| Inv | Check | Applies to |
|---|---|---|
| I1 | Module references spec hierarchy correctly (P1-P4 stages) | Specify, Apply, all spec-producing modules |
| I2 | Research → Plan → Execute phases declared or invoked | Every module that produces output |
| I3 | Build target routed before any decisions | L0 modules, platform packages |
| I4 | Verification mode declared in skill-rules.json | Every module |
| I5 | Activation patterns declared in skill-rules.json | Every module |
| I6 | No hardcoded runtime, model name, or tool name | Every module SKILL.md |
| I7 | Expression register (Homowabian level) declared or deferred to Economy | L6 modules, any module producing user-facing prose |
| I9 | Evidence tagged with staleness state | L5 modules, any module reading external sources |
| I10 | Receipt written after execution. Not-tested field populated. | Every module |
| I11 | Writes to correct space (.wabblespec/ not project/repo/) | Every module, especially L7 Delivery |
| I12 | SKILL.md is minimal and actionable. No bloat. | Every module |

I8 (self-improvement) applies only to L8 Evolution modules. Self-modification
of Evolution modules requires Attestation verification mode — declare this in
skill-rules.json if the module belongs to L8.

---

## WabbleSpec framework.yaml Schema

Generic `framework.yaml` from framework-mode.md is the starting point.
Add these WabbleSpec-specific fields per module entry:

```yaml
modules:
  - id: recipe
    path: .wabblespec/modules/L0/intake/recipe/
    type: skill
    layer: L0
    tier: 1                         # 1-5 per 05-MODULE-IMPORTANCE.md
    planning_doc: planning/modules/P2-RECIPE.md
    planning_complete: true
    build_complete: true            # false if module is partial
    depends_on: []
    activation_stage: [session-start]
    activation_phase: [any]
    verification_mode: Observation
    last_validated: "2026-05-21"
    quality_floor_passed: true
    open_decisions: []              # list unresolved items from planning doc
```

Top-level framework metadata:

```yaml
framework:
  name: wabblespec
  version: 6.1.0
  description: >-
    Spec-driven skill framework for the complete software development lifecycle.
    Target-first routing. Vendor-neutral runtime. Evidence-based execution.
  build_priority_current: 2        # highest unfinished priority
  modules_planned: 0               # count from PROGRESS.md
  modules_built: 0                 # count of build_complete: true entries
  invariants_version: "6.1"
  planning_docs_path: planning/
```

---

## SKILL.md Writing Contract for WabbleSpec Modules

Every WabbleSpec module SKILL.md must have:

**An explicit purpose statement** — one sentence. What this module produces.
Not "this module helps with X" — "this module writes Y to Z."

**An activation section** — when does this module fire? Which gate? What signals?

**An output contract** — specific artifacts produced, their paths, their required fields.
Not "produces a receipt" — "writes `.wabblespec/receipts/recipe-receipt.md` with fields: target, detection_method, confidence, spec_template, collapse_eligible."

**An input contract** — what upstream receipts or artifacts this module reads.
If it reads nothing, say so explicitly.

**A named failure modes section** — at least two. One behavioral, one structural.
Bad: "The module may fail to detect the build target." 
Good: "**Silent drift** — module completes without writing recipe.json because
detection confidence was 0.78 (below 0.8 threshold) and no Interview was
triggered. Fix: any confidence below threshold must either trigger Interview
or write a receipt with confidence field and NEEDS_REVERIFICATION flag."

**A not-tested declaration** — what this module cannot verify about its own output.

---

## Slowly and Surely: Build Discipline

WabbleSpec v6.1 is large. "Not in one run" is a feature, not a constraint.
These rules keep quality from degrading under pressure to ship modules fast:

**One module per chunk.** Don't start Module B until Module A has its
receipt written and framework.yaml updated. Partial modules with no receipt
are worse than no module — they look complete but aren't.

**Planning doc is law.** If the planning doc says "Observation verification
mode," write Observation. Don't upgrade it to Review because Review feels
better. Open decisions in the planning doc are decisions to make before
building, not decisions to silently resolve by picking the more convenient option.

**Read before writing.** Every session starts with reading PROGRESS.md and
framework.yaml. Every module build starts with reading its planning doc.
Never write from memory of prior sessions.

**Receipts are not optional.** A module without a MODULE-RECEIPT.md is not
built. The receipt is the proof the module was reviewed, not just written.

**Quality floor.** `min_pattern_score: 4.0` per module (from framework-mode.md).
Run `agents/module-auditor.md` before marking `build_complete: true`.

**Open decisions block completion.** If a planning doc has an unresolved "Open
Decisions" section and building that module requires resolving one, stop and
surface it to the user. Don't silently pick an option.

---

## Session Handoff

End every session with this summary (adapt as needed):

```
Session complete.

Modules touched: [list with layer]
framework.yaml updated: yes/no
quality_floor_passed for touched modules: yes/no
Modules with build_complete: false in manifest: [count + names]
Open decisions surfaced: [list or none]

Current build priority: P{N}
Next module group: [names]
Command to resume: load wabblespec-v61 mode, read PROGRESS.md and framework.yaml
```

Never say "WabbleSpec is complete" unless every module entry has
`build_complete: true`, `quality_floor_passed: true`, and all
`open_decisions: []` in framework.yaml.
