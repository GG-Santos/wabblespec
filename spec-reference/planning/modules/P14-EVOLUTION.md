# Module Plan — L8 Evolution Pipeline (All 7 Modules)

**Tier:** 3 — SUPPORTING
**Layer:** L8 Evolution
**v5.3 origin:** Evolution pipeline — Instinct (pattern extraction), Synth, Blueprint, Factory, Augment, Benchmark, Forge

---

## Pipeline Overview

Evolution modules operate as a sequential pipeline for framework self-improvement. They write exclusively to `.wabblespec/experiments/` until Forge promotes to production. No Evolution module modifies live framework files directly. Self-modification of Evolution modules themselves requires Attestation (I8).

```
Execution observations
  -> Instinct (pattern extraction from tracker.json)
  -> Synth (pattern synthesis into improvement proposals)
  -> Blueprint (proposals into concrete specs)
  -> Factory (scaffold new modules from spec)
  -> Augment (improve existing modules in experiments/)
  -> Benchmark (evaluate improvements against quality dimensions)
  -> Forge (promote validated experiments to production — Attestation required)
```

Each module writes a receipt. No module advances to the next without the prior module's receipt. Autopilot schedules Evolution runs after major execution waves or on explicit command — never during active execution.

---

## Invariant Enforcement (I8)

- All Evolution writes go to `.wabblespec/experiments/` — never to live framework files
- Forge is the only module that promotes from experiments/ to production
- Forge requires Attestation for any promotion — non-negotiable
- Evolution modules cannot modify their own SKILL.md or skill-rules.json without Attestation
- Experiments/ is isolated: active execution reads no experiment content unless explicitly loaded for evaluation

---

## 1. Instinct

**Purpose:** Observe execution events and extract patterns. Primary input to the Evolution pipeline. Also feeds Dream (pattern decay) and Archive (pattern signal on release). Instinct is passive during execution — it observes, not intervenes.

### Activation

- Any Executor wave completion (auto-observe)
- Archive completion (release cycle signal)
- Deploy completion (deployment pattern)
- Explicit `/instinct` command

### What Instinct observes

- Wave execution outcomes (pass/fail/revise cycles)
- Verifier gate results (which modes triggered, which failed)
- Error types and frequency (from error-event.schema.json)
- Reviewer budget gate triggers (when gates open, when they block)
- Decompose complexity scores vs. actual execution difficulty
- Homowabian register auto-switches (what triggers register changes)

### tracker.json

Instinct is the sole writer to `.wabblespec/memory/tracker.json`. Dream decays it; Instinct writes to it.

```json
{
  "patterns": [
    {
      "id": "pattern-id",
      "description": "string",
      "observations": "integer",
      "last_observed": "ISO 8601",
      "confidence": 0.0,
      "category": "execution|verification|routing|expression|error",
      "evidence_drawer_refs": ["drawer-id"]
    }
  ],
  "last_updated": "ISO 8601",
  "total_observations": "integer"
}
```

Confidence formula: `confidence_new = confidence_old * 0.9 + outcome * 0.1` (EMA, same decay as Dream's inverse). New pattern starts at 0.5. Confidence >= 0.8 = high-confidence pattern eligible for Synth.

### Workflow

```
1. Execution event received (wave complete, release, deploy)
2. Extract observable signals from receipt
3. Match signals to existing patterns in tracker.json
   -> Match: increment observations, update confidence (EMA)
   -> No match: create new pattern (confidence = 0.5)
4. Write evidence drawer to Memory (observation note)
5. Update tracker.json
6. Write Instinct receipt
```

### Receipt Extension Fields

```json
{
  "observations_processed": "integer",
  "patterns_updated": "integer",
  "patterns_created": "integer",
  "high_confidence_patterns": "integer"
}
```

---

## 2. Synth

**Purpose:** Synthesize high-confidence patterns from tracker.json into improvement proposals. Synth reads patterns, clusters related patterns, and produces structured proposals for framework changes. Proposals are not implementations — they are problem statements with evidence.

### Activation

- Explicit `/synth` command
- Autopilot schedules after N Instinct runs (N configurable, default 10)
- Instinct surfaces >= 3 high-confidence patterns in the same category

### Proposal Structure

```markdown
# Improvement Proposal — <title>

**proposal_id:** string
**generated_at:** timestamp
**category:** execution|verification|routing|expression|error
**pattern_refs:** [pattern-ids from tracker.json]
**confidence_basis:** average confidence of contributing patterns

## Problem

<what the patterns indicate is suboptimal>

## Evidence

<pattern observations, frequencies, evidence drawer refs>

## Proposed Direction

<high-level direction — not an implementation>

## Affected Modules

<which modules would change>

## Risk Assessment

**blast_radius:** low|medium|high
**reversibility:** reversible|hard-to-reverse|irreversible
**self_modifying:** true|false (does this change an Evolution module itself?)
```

### Workflow

```
1. Read tracker.json — filter patterns with confidence >= 0.8
2. Cluster by category and evidence overlap
3. For each cluster: generate improvement proposal
4. Write proposals to .wabblespec/experiments/proposals/
5. Write Synth receipt
```

### Receipt Extension Fields

```json
{
  "patterns_read": "integer",
  "proposals_generated": "integer",
  "high_blast_radius_proposals": "integer",
  "self_modifying_proposals": "integer"
}
```

---

## 3. Blueprint

**Purpose:** Convert Synth proposals into concrete, implementable specs. Blueprint produces the equivalent of a P3 Technical Specification for a framework improvement. Blueprint is where the proposal becomes a plan.

### Activation

- Explicit `/blueprint <proposal-id>` command
- Synth proposal selected for development (human or Autopilot decision)
- Cannot activate without Synth proposal receipt

### Blueprint Spec Structure

```markdown
# Blueprint — <title>

**blueprint_id:** string
**proposal_ref:** proposal-id
**generated_at:** timestamp
**target_modules:** [module paths]
**spec_type:** new-module|modify-existing|schema-change|rule-change

## Requirements (EARS syntax)

<EARS-formatted requirements for the improvement>

## Change Specification

### New files
<files to create — paths and content specifications>

### Modified files
<files to modify — specific changes declared>

### Deleted files
<files to remove — with justification>

## Acceptance Criteria

<checkable criteria — how Blueprint success is measured>

## Rollback Specification

<how to undo this change if Forge promotes and it fails>
```

All requirements in EARS syntax (same standard as Specify — I12 applies to Evolution specs too).

### Workflow

```
1. Read Synth proposal
2. Identify affected modules and change scope
3. Write EARS requirements for the improvement
4. Declare new/modified/deleted files explicitly
5. Write acceptance criteria (must be checkable by Benchmark)
6. Write rollback specification
7. Write Blueprint to .wabblespec/experiments/blueprints/
8. Write Blueprint receipt
```

### Receipt Extension Fields

```json
{
  "proposal_ref": "string",
  "blueprint_id": "string",
  "target_modules": ["string"],
  "spec_type": "string",
  "requirements_count": "integer",
  "acceptance_criteria_count": "integer"
}
```

---

## 4. Factory

**Purpose:** Generate new module scaffolding from Blueprint specifications. Factory creates file structure, SKILL.md skeleton, skill-rules.json template, schema stubs, and test stubs for new modules declared in Blueprint. Factory writes to experiments/ only.

### Activation

- Explicit `/factory <blueprint-id>` command
- Blueprint spec_type = new-module
- Cannot activate without Blueprint receipt

### What Factory generates

For each new module declared in Blueprint:

```
experiments/modules/<module-name>/
  SKILL.md                <- skeleton with Blueprint requirements embedded
  skill-rules.json        <- activation patterns skeleton
  schemas/
    receipt.schema.json   <- base receipt schema extended
  tests/
    acceptance.md         <- acceptance criteria from Blueprint
  references/             <- empty, structure declared
  rules/                  <- empty, structure declared
```

Factory does not write implementation content — it writes structure and contracts. Augment fills in content.

### Workflow

```
1. Read Blueprint
2. For each new module in Blueprint:
   -> Generate directory structure
   -> Write SKILL.md skeleton (purpose, activation, workflow stubs from Blueprint requirements)
   -> Write skill-rules.json template
   -> Write receipt schema
   -> Write acceptance.md from Blueprint acceptance criteria
3. Write Factory receipt
```

### Receipt Extension Fields

```json
{
  "blueprint_ref": "string",
  "modules_scaffolded": "integer",
  "files_generated": "integer",
  "output_paths": ["string"]
}
```

---

## 5. Augment

**Purpose:** Apply content improvements to existing modules or fill in Factory-scaffolded modules. Augment writes implementation content to experiments/ based on Blueprint specification. Never touches live framework files.

### Activation

- Explicit `/augment <blueprint-id>` command
- Factory scaffolding complete (for new modules)
- Blueprint spec_type = modify-existing OR (new-module AND Factory complete)
- Cannot activate without Blueprint receipt (and Factory receipt for new modules)

### What Augment does

For **existing module modifications:**
- Read current module content from live framework
- Apply declared changes from Blueprint (specific file modifications only)
- Write modified versions to `experiments/modules/<module-name>/` (not live path)

For **new module content** (Factory-scaffolded):
- Fill in SKILL.md content from Blueprint requirements
- Write rules/ content
- Write references/ content
- Write evaluations/ content

### Change discipline

Augment applies only changes declared in Blueprint. It does not:
- Expand scope beyond Blueprint specification
- Modify files not declared in Blueprint's change specification
- Touch any live framework file (experiments/ only)

### Workflow

```
1. Read Blueprint change specification
2. For each declared change:
   -> Read source file (live framework or Factory scaffold)
   -> Apply declared modification
   -> Write result to experiments/
3. Write Augment receipt
```

### Receipt Extension Fields

```json
{
  "blueprint_ref": "string",
  "files_modified": "integer",
  "files_created": "integer",
  "scope_violations": "integer",
  "output_paths": ["string"]
}
```

---

## 6. Benchmark

**Purpose:** Evaluate experiments against declared acceptance criteria and quality dimensions. Benchmark does not promote — it produces a PASS/FAIL verdict with evidence. Forge reads Benchmark receipt before any promotion.

### Activation

- Explicit `/benchmark <experiment-path>` command
- Augment completes (auto-trigger in Autopilot Evolution runs)
- Cannot activate without Augment receipt (or Factory receipt for structure-only evaluation)

### Evaluation dimensions

| Dimension | Method | Pass condition |
|---|---|---|
| Acceptance criteria | Checkable criteria from Blueprint | All criteria pass |
| Spec compliance | EARS requirements from Blueprint | All requirements addressed |
| Scope adherence | Files modified vs. Blueprint declaration | No undeclared modifications |
| Rollback viability | Rollback specification completeness | Rollback path fully specified |
| Self-modification risk | Does experiment modify Evolution modules? | Flagged for Attestation if yes |
| Integration compatibility | Do changed modules' interfaces remain compatible? | No breaking interface changes (or declared and Attested) |

### Benchmark report

```markdown
# Benchmark Report — <experiment-id>

**verdict:** PASS|FAIL|CONDITIONAL
**timestamp:** ISO 8601
**blueprint_ref:** string

## Dimension Results

| Dimension | Result | Notes |
|---|---|---|
| Acceptance criteria | PASS/FAIL | details |
...

## Failures

<if FAIL: specific failures with evidence>

## Conditions (if CONDITIONAL)

<conditions that must be resolved before Forge promotion>

## Attestation Required

<list any dimensions requiring human sign-off>
```

### Workflow

```
1. Read Blueprint acceptance criteria and requirements
2. Evaluate each dimension against experiment content
3. Produce per-dimension result
4. Compute overall verdict (PASS/FAIL/CONDITIONAL)
5. Write Benchmark report to .wabblespec/experiments/benchmarks/
6. Write Benchmark receipt
```

### Receipt Extension Fields

```json
{
  "experiment_path": "string",
  "blueprint_ref": "string",
  "verdict": "PASS|FAIL|CONDITIONAL",
  "dimensions_passed": "integer",
  "dimensions_failed": "integer",
  "attestation_required": "boolean",
  "report_path": "string"
}
```

---

## 7. Forge

**Purpose:** Promote validated experiments from experiments/ to live framework. Most restricted module in the framework. Every Forge promotion requires Attestation. Self-modification promotions (changes to Evolution modules) require explicit double Attestation (two separate human confirmations).

### Activation

- Explicit `/forge <experiment-id>` command ONLY — never auto-triggered
- Cannot activate without:
  - Benchmark receipt with PASS verdict
  - Attestation received
  - Rollback specification present in Blueprint

### Promotion process

```
1. Read Benchmark receipt — verify PASS (CONDITIONAL blocked until resolved)

2. Request Attestation:
   -> Display: experiment summary, affected modules, rollback plan
   -> Human confirms
   -> If self-modifying: second Attestation required

3. Pre-promotion snapshot:
   -> Copy current live versions of all affected files to .wabblespec/experiments/rollback-<timestamp>/
   -> Write snapshot manifest

4. Promote: copy experiment files to live framework paths (overwrite)

5. Post-promotion verification:
   -> Verify promoted files match experiment files (hash check)
   -> Verify skill-rules.json parse (syntax check)

6. Update Archive: framework version bump (ADDITIVE or BREAKING per Blueprint)

7. Write Forge receipt

8. Notify Instinct: promotion event (new pattern signal)
```

### Rollback

If post-promotion verification fails, Forge immediately restores from pre-promotion snapshot — no human confirmation required for this rollback (it is an automatic error recovery, not a deployment decision).

### Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Explicit command only — never auto |
| `rules/attestation-required.md` | Rules | Every promotion requires Attestation |
| `rules/double-attestation.md` | Rules | Self-modifying changes require two Attestations |
| `rules/snapshot-policy.md` | Rules | Pre-promotion snapshot always written |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

### Receipt Extension Fields

```json
{
  "experiment_id": "string",
  "benchmark_ref": "string",
  "attestation_count": "integer",
  "self_modifying": "boolean",
  "files_promoted": "integer",
  "snapshot_path": "string",
  "post_promotion_verified": "boolean",
  "framework_version_bump": "string"
}
```

---

## Common Integration Points (all Evolution modules)

| Module | Relationship |
|---|---|
| Instinct | Reads execution receipts; writes tracker.json; feeds Synth |
| Autopilot | Autopilot schedules Evolution runs; manages sequencing |
| Dream | Dream decays Instinct's tracker.json patterns |
| Archive | Archive notifies Instinct on release; Forge triggers Archive version bump |
| Memory | Instinct writes observation drawers; all Evolution modules read Memory |
| Verifier | Benchmark acts as Verifier equivalent for experiments |
| Reviewer | Synth proposals and Blueprint specs route through Reviewer before Augment |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Synth trigger frequency | After 10 Instinct runs vs. confidence-threshold trigger | Implementation |
| Auto-run Evolution pipeline | Autopilot auto-advances Instinct→Synth→Blueprint vs. human gates each step | Implementation — default: human gates all steps past Instinct |
| Blueprint approval gate | Reviewer checks Blueprint before Factory/Augment vs. Benchmark catches issues | Implementation |
| Double Attestation UI | Two separate /forge invocations vs. single command with double confirmation prompt | Implementation |
| Experiment isolation | experiments/ fully isolated (current) vs. shadow-load for A/B evaluation | Future consideration — not v6.1 |
