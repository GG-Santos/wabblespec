# WabbleSpec v6.1 — Evolution

**Layer:** L8 Evolution
**Document scope:** All L8 modules — Instinct, Synth, Blueprint, Factory, Augment, Benchmark, Forge, Retro, Feedback
**Depends on:** L7 Archive (release signals), L7 Deploy (deployment signals), L5 Memory (evidence storage), L5 Dream (pattern decay), L2 Executor (wave signals)

---

## Overview

L8 Evolution is the framework's self-improvement layer. Where L7 Delivery ships product, L8 observes what happened, accumulates evidence, proposes improvements, and — with explicit human authorization — promotes changes back into the live framework. Evolution is the only layer that modifies framework files, and it does so through the most restricted process in WabbleSpec.

Nine modules:

| Module | Tier | Purpose |
|---|---|---|
| Instinct | 3 — SUPPORTING | Observe execution events, extract patterns, write tracker.json |
| Synth | 3 — SUPPORTING | Synthesize high-confidence patterns into improvement proposals |
| Blueprint | 3 — SUPPORTING | Convert proposals into concrete implementable specs |
| Factory | 3 — SUPPORTING | Scaffold new module structure from Blueprint |
| Augment | 3 — SUPPORTING | Apply content changes to experiments |
| Benchmark | 3 — SUPPORTING | Evaluate experiments against acceptance criteria |
| Forge | 3 — SUPPORTING | Promote validated experiments to live framework (Attestation required) |
| Retro | 3 — SUPPORTING | Structured retrospective after each release cycle |
| Feedback | 3 — SUPPORTING | Capture and structure explicit human feedback signals |

---

## Layer Invariants

**I8: Human gates for self-modification**

All Evolution writes go to `.wabblespec/experiments/` — never to live framework files. Forge is the only module that promotes from `experiments/` to production. Every Forge promotion requires Attestation. Self-modification of Evolution modules themselves (changes to their own SKILL.md or skill-rules.json) requires double Attestation — two separate human confirmations.

**Experiments isolation**

Active execution reads no content from `experiments/` unless explicitly loaded for Benchmark evaluation. The live framework and in-progress experiments are fully separated.

**No auto-promotion**

Forge activates only on explicit `/forge <experiment-id>` command. No module can trigger Forge automatically.

**Receipt chain**

No Evolution module advances without the prior module's receipt:

```
Instinct receipt
  -> Synth receipt (requires Instinct patterns)
  -> Blueprint receipt (requires Synth proposal)
  -> Factory receipt (requires Blueprint, if new-module)
  -> Augment receipt (requires Blueprint + Factory if new-module)
  -> Benchmark receipt (requires Augment)
  -> Forge (requires Benchmark PASS + Attestation)
```

---

## Pipeline Overview

```
Execution observations (waves, deploys, releases)
  -> Instinct: extract patterns, write tracker.json
  -> Synth: cluster high-confidence patterns into proposals
  -> Blueprint: convert proposals into implementable specs
  -> Factory: scaffold new module structure (if new-module spec)
  -> Augment: write content to experiments/
  -> Benchmark: evaluate experiments against acceptance criteria
  -> Forge: promote to live framework (Attestation required)

Parallel feedback channels:
  -> Retro: structured retrospective after each release (feeds Synth)
  -> Feedback: explicit human signal capture (feeds Instinct + Synth + Triage)
```

Autopilot schedules Evolution runs after major execution waves or on explicit command. Evolution never runs during active execution.

---

## Instinct

### Purpose

Observe execution events and extract patterns. Primary data source for the entire Evolution pipeline. Instinct is passive during execution — it observes, never intervenes. Instinct also feeds Dream (pattern decay signal) and Archive (pattern signal on release).

### What Instinct Observes

| Signal source | What is observed |
|---|---|
| Executor wave completion | Pass/fail/revise cycles, wave outcome |
| Verifier gate results | Which modes triggered, which failed |
| Error events | Error types and frequency (from error-event.schema.json) |
| Reviewer budget gates | When gates open, when they block |
| Decompose complexity scores | Declared complexity vs. actual execution difficulty |
| Homowabian register | Auto-switch events and trigger conditions |
| Deploy events | Deployment outcomes, environment, version |
| Release events | Release cycle completion, cycle duration |

### tracker.json

Instinct is the sole writer to `.wabblespec/memory/tracker.json`. Dream decays it; Instinct writes to it.

```json
{
  "patterns": [
    {
      "id": "pattern-id",
      "description": "string",
      "observations": 0,
      "last_observed": "ISO 8601",
      "confidence": 0.5,
      "category": "execution|verification|routing|expression|error",
      "evidence_drawer_refs": ["drawer-id"]
    }
  ],
  "last_updated": "ISO 8601",
  "total_observations": 0
}
```

**Confidence formula (EMA):** `confidence_new = confidence_old × 0.9 + outcome × 0.1`

New patterns start at confidence 0.5. Confidence >= 0.8 = high-confidence pattern eligible for Synth.

### Workflow

```
1. Execution event received (wave complete, release, deploy)

2. Extract observable signals from receipt

3. Match signals to existing patterns in tracker.json:
   -> Match: increment observations, update confidence (EMA)
   -> No match: create new pattern (confidence = 0.5)

4. Write evidence drawer to Memory (observation note)

5. Update tracker.json

6. Write Instinct receipt
```

### Activation

`skill-rules.json` triggers Instinct on:
- Any Executor wave completion (auto-observe)
- Archive completion signal (release cycle)
- Deploy completion signal
- Explicit `/instinct` command

### Integration Points

| Module | Relationship |
|---|---|
| Executor | Instinct reads wave completion receipts |
| Archive | Archive notifies Instinct on release; Instinct processes release cycle signal |
| Deploy | Deploy notifies Instinct on deployment event |
| Dream | Dream decays tracker.json pattern confidence via EMA inverse |
| Synth | Instinct's high-confidence patterns are Synth's primary input |
| Memory | Instinct writes observation drawers per event |
| Feedback | Feedback corrections decrement pattern confidence; endorsements increment |

### Verification Mode

**Observation** — tracker.json updated, evidence drawers written, receipt written.

### Receipt Extension Fields

```json
{
  "observations_processed": 0,
  "patterns_updated": 0,
  "patterns_created": 0,
  "high_confidence_patterns": 0
}
```

---

## Synth

### Purpose

Synthesize high-confidence patterns from tracker.json into improvement proposals. Synth reads patterns, clusters related patterns, and produces structured proposals for framework changes. Proposals are problem statements with evidence — not implementations.

### Activation

`skill-rules.json` triggers Synth on:
- Instinct surfaces >= 3 high-confidence patterns in the same category
- Autopilot schedules after N Instinct runs (default N = 10)
- Explicit `/synth` command

### Proposal Structure

Each proposal written to `.wabblespec/experiments/proposals/`:

```markdown
# Improvement Proposal — <title>

**proposal_id:** string
**generated_at:** ISO 8601
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
**self_modifying:** true|false
```

`self_modifying: true` means the proposal changes an Evolution module itself — this flag propagates through Blueprint, Augment, and Forge to trigger double Attestation.

### Workflow

```
1. Read tracker.json — filter patterns with confidence >= 0.8

2. Cluster by category and evidence overlap

3. For each cluster: generate improvement proposal

4. Write proposals to .wabblespec/experiments/proposals/

5. Write Synth receipt
```

### Integration Points

| Module | Relationship |
|---|---|
| Instinct | Instinct's high-confidence patterns are Synth's primary input |
| Blueprint | Synth proposals become Blueprint's input |
| Reviewer | Synth proposals reviewed before Blueprint begins |
| Retro | Retro routes confirmed framework improvement items to Synth |
| Feedback | Feedback complaints routed to Synth for proposal evaluation |

### Verification Mode

**Observation** — proposals written to experiments/proposals/, each proposal has evidence from tracker.json, receipt written.

### Receipt Extension Fields

```json
{
  "patterns_read": 0,
  "proposals_generated": 0,
  "high_blast_radius_proposals": 0,
  "self_modifying_proposals": 0
}
```

---

## Blueprint

### Purpose

Convert Synth proposals into concrete, implementable specs. Blueprint produces the equivalent of a P3 Technical Specification for a framework improvement. Requirements in EARS syntax. Blueprint is where the proposal becomes a plan — specific files, specific changes, checkable acceptance criteria, rollback specification.

### Activation

`skill-rules.json` triggers Blueprint on:
- Explicit `/blueprint <proposal-id>` command
- Synth proposal selected for development (human or Autopilot decision)

Cannot activate without Synth proposal receipt.

### Blueprint Spec Structure

Written to `.wabblespec/experiments/blueprints/`:

```markdown
# Blueprint — <title>

**blueprint_id:** string
**proposal_ref:** proposal-id
**generated_at:** ISO 8601
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

<checkable criteria — how Blueprint success is measured by Benchmark>

## Rollback Specification

<how to undo this change if Forge promotes and it fails>
```

All requirements in EARS syntax — I12 applies to Evolution specs as much as to product specs.

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

### Integration Points

| Module | Relationship |
|---|---|
| Synth | Blueprint converts Synth proposals into implementable specs |
| Factory | Factory reads Blueprint for new-module scaffolding |
| Augment | Augment reads Blueprint change specification for content writes |
| Benchmark | Benchmark reads Blueprint acceptance criteria and requirements |
| Reviewer | Blueprint routes through Reviewer before Factory/Augment begins |

### Verification Mode

**Observation** — Blueprint written to experiments/blueprints/, all changes declared explicitly, acceptance criteria present, rollback specification present, receipt written.

### Receipt Extension Fields

```json
{
  "proposal_ref": "string",
  "blueprint_id": "string",
  "target_modules": ["string"],
  "spec_type": "new-module|modify-existing|schema-change|rule-change",
  "requirements_count": 0,
  "acceptance_criteria_count": 0
}
```

---

## Factory

### Purpose

Generate new module scaffolding from Blueprint specifications. Factory creates file structure, SKILL.md skeleton, skill-rules.json template, schema stubs, and test stubs for new modules declared in Blueprint. Factory writes to `experiments/` only — never to the live framework.

Factory generates structure and contracts. It does not write implementation content — Augment fills that in.

### Activation

`skill-rules.json` triggers Factory on:
- Explicit `/factory <blueprint-id>` command
- Blueprint `spec_type = new-module`

Cannot activate without Blueprint receipt. If `spec_type` is not `new-module`, Factory is not needed — proceed to Augment directly.

### What Factory Generates

For each new module declared in Blueprint:

```
experiments/modules/<module-name>/
  SKILL.md                     <- skeleton with Blueprint requirements embedded
  skill-rules.json             <- activation patterns skeleton
  schemas/
    receipt.schema.json        <- base receipt schema extended
  tests/
    acceptance.md              <- acceptance criteria from Blueprint
  references/                  <- empty directory (structure declared)
  rules/                       <- empty directory (structure declared)
```

### Workflow

```
1. Read Blueprint — identify new modules declared

2. For each new module:
   -> Generate directory structure in experiments/modules/
   -> Write SKILL.md skeleton (purpose, activation, workflow stubs from Blueprint requirements)
   -> Write skill-rules.json template
   -> Write receipt.schema.json (base receipt extended)
   -> Write acceptance.md from Blueprint acceptance criteria

3. Write Factory receipt
```

### Integration Points

| Module | Relationship |
|---|---|
| Blueprint | Factory reads Blueprint for module specifications |
| Augment | Augment fills Factory-scaffolded structure with content |
| Benchmark | Benchmark evaluates Factory output for structural completeness |

### Verification Mode

**Observation** — all declared module directories created in experiments/, SKILL.md skeleton present, acceptance.md populated, receipt written.

### Receipt Extension Fields

```json
{
  "blueprint_ref": "string",
  "modules_scaffolded": 0,
  "files_generated": 0,
  "output_paths": ["string"]
}
```

---

## Augment

### Purpose

Apply content improvements to existing modules or fill in Factory-scaffolded modules. Augment writes implementation content to `experiments/` based on Blueprint specification. Never touches live framework files.

Augment applies only changes declared in Blueprint. It does not expand scope, modify undeclared files, or touch any live framework path.

### Activation

`skill-rules.json` triggers Augment on:
- Explicit `/augment <blueprint-id>` command
- Factory scaffolding complete (for new-module specs)

Cannot activate without Blueprint receipt. For new-module specs, also requires Factory receipt.

### What Augment Does

**For existing module modifications (`spec_type = modify-existing`):**
- Read current module content from live framework
- Apply declared changes from Blueprint (specific file modifications only)
- Write modified versions to `experiments/modules/<module-name>/` (not to live path)

**For new module content (`spec_type = new-module`, after Factory):**
- Fill in SKILL.md content from Blueprint requirements
- Write `rules/` content
- Write `references/` content
- Write evaluation content

### Change Discipline

Augment enforces strict scope adherence:
- Applies only changes declared in Blueprint's change specification
- Does not modify files not listed in Blueprint's new/modified/deleted declaration
- Writes only to `experiments/` — zero writes to live framework paths
- Scope violations (`scope_violations > 0` in receipt) are SPEC_VIOLATION errors

### Workflow

```
1. Read Blueprint change specification

2. For each declared change:
   -> Read source file (from live framework for modifications, or Factory scaffold for new modules)
   -> Apply declared modification
   -> Write result to experiments/

3. Write Augment receipt
```

### Integration Points

| Module | Relationship |
|---|---|
| Blueprint | Augment reads Blueprint change specification |
| Factory | For new-module: Augment fills in Factory-scaffolded structure |
| Benchmark | Benchmark evaluates Augment output |

### Verification Mode

**Observation** — all declared changes applied, zero undeclared file modifications, all writes to experiments/ only, receipt written.

### Receipt Extension Fields

```json
{
  "blueprint_ref": "string",
  "files_modified": 0,
  "files_created": 0,
  "scope_violations": 0,
  "output_paths": ["string"]
}
```

---

## Benchmark

### Purpose

Evaluate experiments against declared acceptance criteria and quality dimensions. Benchmark produces a PASS/FAIL/CONDITIONAL verdict with evidence. Forge reads Benchmark receipt before any promotion — CONDITIONAL or FAIL receipts block Forge.

### Activation

`skill-rules.json` triggers Benchmark on:
- Explicit `/benchmark <experiment-path>` command
- Augment completes (auto-trigger in Autopilot Evolution runs)

Cannot activate without Augment receipt (or Factory receipt for structure-only evaluation).

### Evaluation Dimensions

| Dimension | Method | Pass condition |
|---|---|---|
| Acceptance criteria | Checkable criteria from Blueprint | All criteria pass |
| Spec compliance | EARS requirements from Blueprint | All requirements addressed |
| Scope adherence | Files modified vs. Blueprint declaration | No undeclared modifications |
| Rollback viability | Rollback specification completeness | Rollback path fully specified |
| Self-modification risk | Does experiment modify Evolution modules? | Flagged for Attestation if yes |
| Integration compatibility | Changed modules' interfaces remain compatible | No breaking interface changes (or declared + Attested) |

### Benchmark Report

Written to `.wabblespec/experiments/benchmarks/`:

```markdown
# Benchmark Report — <experiment-id>

**verdict:** PASS|FAIL|CONDITIONAL
**timestamp:** ISO 8601
**blueprint_ref:** string

## Dimension Results

| Dimension | Result | Notes |
|---|---|---|
| Acceptance criteria | PASS/FAIL | details |
| Spec compliance | PASS/FAIL | details |
| Scope adherence | PASS/FAIL | details |
| Rollback viability | PASS/FAIL | details |
| Self-modification risk | PASS/FLAG | details |
| Integration compatibility | PASS/FAIL | details |

## Failures

<if FAIL: specific failures with evidence>

## Conditions (if CONDITIONAL)

<conditions that must be resolved before Forge promotion>

## Attestation Required

<list dimensions requiring human sign-off>
```

**Verdict rules:**
- PASS: all dimensions pass
- FAIL: any dimension fails (except self-modification risk, which flags without failing)
- CONDITIONAL: criteria met but conditions declared — must resolve before Forge

### Workflow

```
1. Read Blueprint acceptance criteria and requirements

2. Evaluate each dimension against experiment content in experiments/

3. Produce per-dimension result

4. Compute overall verdict (PASS/FAIL/CONDITIONAL)

5. Write Benchmark report to .wabblespec/experiments/benchmarks/

6. Write Benchmark receipt
```

### Integration Points

| Module | Relationship |
|---|---|
| Blueprint | Benchmark reads Blueprint acceptance criteria and requirements |
| Augment | Benchmark evaluates Augment output |
| Forge | Forge reads Benchmark receipt — PASS required before promotion |

### Verification Mode

**Measurement** — all dimensions evaluated with evidence, verdict derived from dimension results, report written, receipt written.

### Receipt Extension Fields

```json
{
  "experiment_path": "string",
  "blueprint_ref": "string",
  "verdict": "PASS|FAIL|CONDITIONAL",
  "dimensions_passed": 0,
  "dimensions_failed": 0,
  "attestation_required": false,
  "report_path": "string"
}
```

---

## Forge

### Purpose

Promote validated experiments from `experiments/` to the live framework. Most restricted module in the framework. Every Forge promotion requires Attestation. Self-modification promotions (changes to Evolution modules themselves) require double Attestation — two separate human confirmations.

### Activation

Explicit `/forge <experiment-id>` command **only** — Forge is never auto-triggered by any other module.

Cannot activate without:
- Benchmark receipt with PASS verdict (CONDITIONAL blocks Forge)
- Attestation received
- Rollback specification present in Blueprint

### Promotion Process

```
1. Read Benchmark receipt — verify PASS verdict
   -> CONDITIONAL: abort — resolve conditions first
   -> FAIL: abort

2. Request Attestation:
   -> Display: experiment summary, affected modules, rollback plan
   -> Human confirms
   -> If self_modifying = true: second Attestation required (separate confirmation)

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

### Rollback on Verification Failure

If post-promotion verification fails, Forge immediately restores from the pre-promotion snapshot. This rollback is automatic and requires no human confirmation — it is error recovery, not a deployment decision.

### Double Attestation

When `self_modifying = true` in the Blueprint:
- First Attestation: human reviews experiment scope and approves promotion
- Second Attestation: human confirms specifically that the Evolution module change is intentional
- Both Attestations are recorded in the Forge receipt
- Two separate `/forge` invocations or a two-stage confirmation prompt — implementation detail

### Integration Points

| Module | Relationship |
|---|---|
| Benchmark | Forge reads Benchmark receipt — PASS required |
| Blueprint | Forge reads rollback specification from Blueprint |
| Archive | Forge triggers Archive for framework version bump after promotion |
| Instinct | Forge notifies Instinct: promotion event (pattern signal) |
| Autopilot | Autopilot never auto-triggers Forge — explicit command only |

### Verification Mode

**Attestation** — human sign-off required before promotion, double Attestation for self-modifying changes, post-promotion hash check, receipt written.

### Receipt Extension Fields

```json
{
  "experiment_id": "string",
  "benchmark_ref": "string",
  "attestation_count": 1,
  "self_modifying": false,
  "files_promoted": 0,
  "snapshot_path": "string",
  "post_promotion_verified": true,
  "framework_version_bump": "ADDITIVE|BREAKING"
}
```

---

## Retro

### Purpose

Structured retrospective after each release cycle. Reads Instinct patterns, all cycle receipts, Verifier not-tested lists, and open decisions to produce a human-collaborative retro artifact. Framework drafts; human reviews and confirms. Retro routes confirmed items: framework improvements to Synth, product issues to Triage.

Retro is always DRAFT until human confirms. No routing proceeds without human confirmation.

### Activation

`skill-rules.json` triggers Retro on:
- Release receipt written (always triggers Retro for that release cycle)
- Autopilot L3+ after major milestone completion
- Explicit `/retro` command

### Retro Artifact Structure

Written to `.wabblespec/plans/retro-v<version>.md`:

```markdown
# Retrospective — v<version> — <date>

**release_ref:** release receipt ID
**cycle_start:** timestamp (date of previous retro or project start)
**cycle_end:** timestamp (release date)
**generated_at:** ISO 8601

## What Worked

<patterns from Instinct with positive confidence trend>
<verifier gates that consistently passed>
<waves that completed without REVISE cycles>

## What Didn't

<patterns from Instinct with negative trend or high recurrence>
<verifier gates that consistently failed>
<Reviewer budget gates that triggered frequently>
<waves that required max REVISE cycles>
<items from not-tested compilation>

## Open Decisions Unresolved at Ship

<open decisions from module plans not resolved this cycle>

## What Changes

### Framework improvements → Synth

| Observation | Proposed direction |
|---|---|
| <pattern> | <high-level direction> |

### Product improvements → Triage

| Issue | Severity | Suggested type |
|---|---|---|
| <issue> | high/medium/low | bug/feature/debt |

## Human Review Section

**status:** DRAFT
**reviewer:** <assigned or unassigned>
**notes:** <human adds notes here>
```

### Workflow

```
1. Read Release receipt (cycle boundary)

2. Read Instinct tracker.json (pattern confidence trends for the cycle)

3. Read all receipts from cycle (Verifier, Reviewer, Executor waves)

4. Read not-tested compilation from Archive

5. Read open decisions from all module plans (unresolved flags)

6. Draft retro artifact:
   -> What Worked: positive patterns, clean gates
   -> What Didn't: negative patterns, failing gates, high REVISE cycles
   -> Open Decisions: unresolved items at ship
   -> What Changes: framework Synth proposals + product Triage records (DRAFT)

7. Write retro to .wabblespec/plans/retro-v<version>.md
   -> Status: DRAFT

8. Write Retro receipt

9. After human confirms:
   -> Route framework improvement items to Synth
   -> Route product issues to Triage
   -> Write confirmed retro as FRESH drawer to Memory
```

### Integration Points

| Module | Relationship |
|---|---|
| Release | Release triggers Retro; Retro reads Release receipt for cycle boundary |
| Instinct | Retro reads tracker.json for pattern confidence analysis |
| Archive | Retro reads not-tested compilation from Archive |
| Synth | Retro routes confirmed framework improvement proposals to Synth |
| Triage | Retro routes confirmed product issues to Triage |
| Memory | Confirmed retro written to Memory as FRESH drawer |

### Verification Mode

**Attestation** — human reviews DRAFT retro before routing, routing actions confirmed by human, receipt written.

### Receipt Extension Fields

```json
{
  "release_ref": "string",
  "patterns_analyzed": 0,
  "worked_items": 0,
  "didnt_work_items": 0,
  "synth_proposals_drafted": 0,
  "triage_records_drafted": 0,
  "human_confirmed": false,
  "retro_path": "string"
}
```

---

## Feedback

### Purpose

Capture and structure explicit user and stakeholder feedback signals. Distinct from Instinct, which observes execution events implicitly — Feedback captures explicit human evaluation: corrections, preferences, complaints, endorsements, and questions. Structured records written to Memory. Instinct reads them as high-signal observations — corrections decay pattern confidence, endorsements reinforce it.

### Feedback Types

| Type | Definition | Instinct signal |
|---|---|---|
| Correction | Framework did something wrong — explicit fix provided | Negative: decay related pattern confidence |
| Preference | User prefers a different approach — no hard error | Soft negative: minor confidence decay |
| Complaint | Something is frustrating — no specific fix provided | Negative: flag for Synth proposal |
| Endorsement | User explicitly approves an approach | Positive: reinforce pattern confidence |
| Question | User needed to ask something that should have been obvious | Neutral: flag as clarity gap |

Signal strength: corrections = HIGH, endorsements = MEDIUM, preferences/complaints = LOW. Instinct notified for signals >= MEDIUM.

### Feedback Record Format

Written to Memory as FRESH drawer:

```markdown
# Feedback Record — <feedback-id>

**timestamp:** ISO 8601
**type:** correction|preference|complaint|endorsement|question
**session_id:** string
**source:** user|stakeholder|retro

## Content

<feedback as received>

## Structured Signal

**affected_module:** string (if identifiable)
**affected_pattern:** pattern-id from tracker.json (if identifiable)
**confidence_direction:** positive|negative|neutral

## Instinct Notification

**notify_instinct:** boolean
**signal_strength:** HIGH|MEDIUM|LOW
```

### Routing After Feedback

| Feedback type | Route |
|---|---|
| Correction (with specific fix) | Triage |
| Complaint (no specific fix) | Synth (pattern issue for proposal evaluation) |
| Question | Interview (clarity gap) |
| Endorsement | Instinct only (confidence increment) |
| Preference | Instinct only (minor decay) |

### Workflow

```
1. Receive feedback (explicit command or auto-detected correction event)

2. Classify feedback type

3. Identify affected module and pattern (via EntityGraph, if identifiable)

4. Write feedback record to Memory as FRESH drawer

5. Notify Instinct if signal_strength >= MEDIUM:
   -> Correction: Instinct decrements pattern confidence
   -> Endorsement: Instinct increments pattern confidence
   -> Complaint: Instinct flags for Synth proposal evaluation

6. Route actionable feedback:
   -> Correction with fix: route to Triage
   -> Complaint: route to Synth
   -> Question: route to Interview

7. Write Feedback receipt
```

### Activation

`skill-rules.json` triggers Feedback on:
- Explicit `/feedback <type> <content>` command
- User correction auto-detected mid-session
- Session end (Feedback prompted for optional session-level feedback)
- Retro produces feedback records (routed through Feedback for structuring)

### Integration Points

| Module | Relationship |
|---|---|
| Instinct | Feedback notifies Instinct with confidence direction and signal strength |
| Memory | Feedback writes all records to Memory as FRESH drawers |
| EntityGraph | Feedback queries EntityGraph to identify affected modules and patterns |
| Triage | Corrections with fixes routed to Triage |
| Synth | Complaints routed to Synth for improvement proposal evaluation |
| Interview | Questions routed to Interview as clarity gaps |
| Retro | Retro action items structured through Feedback before routing |

### Verification Mode

**Observation** — feedback record written to Memory, Instinct notified for signals >= MEDIUM, actionable feedback routed, receipt written.

### Receipt Extension Fields

```json
{
  "feedback_id": "string",
  "type": "correction|preference|complaint|endorsement|question",
  "signal_strength": "HIGH|MEDIUM|LOW",
  "instinct_notified": false,
  "routed_to": "string",
  "affected_module": "string"
}
```

---

## L8 Layer Interactions

### Pattern lifecycle

```
Execution event
  -> Instinct: new pattern (confidence 0.5) or update (EMA)
  -> Dream: passive decay between active cycles
  -> Feedback correction: decrement confidence
  -> Feedback endorsement: increment confidence
  -> Synth: pattern confidence >= 0.8 → proposal
  -> Blueprint: proposal → spec
  -> Augment: spec → experiment content
  -> Benchmark: experiment → PASS/FAIL verdict
  -> Forge: PASS + Attestation → live framework
```

### Retro-Synth bridge

Retro provides a human-reviewed structured input to Synth. Where Instinct is continuous and automated, Retro is periodic and human-confirmed. Both feed Synth — Instinct provides high-volume pattern evidence, Retro provides human-validated interpretation.

### Feedback-Instinct bridge

Feedback is the explicit signal channel. Instinct observes what happened; Feedback captures what the human thought about it. High-signal feedback (corrections, endorsements) directly adjusts pattern confidence in tracker.json, accelerating or slowing the Synth trigger threshold.

### Evolution scheduling

Autopilot manages Evolution scheduling:
- Instinct runs automatically after every significant execution event
- Synth runs after N Instinct runs or when >= 3 high-confidence patterns emerge in a category
- Blueprint, Factory, Augment, Benchmark require explicit human or Autopilot selection of a proposal
- Forge never runs automatically — explicit command only
- Retro runs automatically after each Release
- Feedback runs on-demand and on auto-detected correction events

### Self-modification cascade

When a Synth proposal modifies an Evolution module:
- Proposal: `self_modifying: true` flag set
- Blueprint: rollback specification required for the Evolution module itself
- Augment: scope validation includes checking that no other Evolution modules are touched
- Benchmark: self-modification risk dimension flagged (not a FAIL — but triggers Attestation requirement)
- Forge: double Attestation required

---

## experiments/ Directory Structure

```
.wabblespec/experiments/
  proposals/
    <proposal-id>.md             <- Synth proposals
  blueprints/
    <blueprint-id>.md            <- Blueprint specs
  modules/
    <module-name>/               <- Factory scaffolding + Augment content
      SKILL.md
      skill-rules.json
      schemas/
      tests/
      rules/
      references/
  benchmarks/
    <experiment-id>-report.md    <- Benchmark reports
  rollback-<timestamp>/          <- Pre-Forge snapshot
    <affected files>
    snapshot-manifest.json
```

All Evolution artifacts are isolated in `experiments/`. The live framework under `.wabblespec/` is never modified by any Evolution module except Forge.

---

## Invariants Enforced by L8

| Invariant | How L8 enforces it |
|---|---|
| I8 (Human gates for irreversible) | Forge requires Attestation for all promotions; double Attestation for self-modifying changes; Retro requires human confirmation before routing |
| I9 (Evidence expiry) | Instinct patterns decay via EMA; expired patterns below confidence threshold removed from tracker.json consideration |
| I10 (Receipts as operational artifacts) | Every Evolution module writes receipts; no module advances without prior module receipt |
| I12 (Spec quality over volume) | Blueprint uses EARS syntax; Benchmark enforces spec compliance; Synth clusters patterns rather than generating one proposal per observation |

---

## Sub-Components Summary

| Module | Required components |
|---|---|
| Instinct | SKILL.md, skill-rules.json, schemas/receipt.schema.json |
| Synth | SKILL.md, skill-rules.json, schemas/receipt.schema.json |
| Blueprint | SKILL.md, skill-rules.json, schemas/receipt.schema.json |
| Factory | SKILL.md, skill-rules.json, templates/ (module skeleton templates), schemas/receipt.schema.json |
| Augment | SKILL.md, skill-rules.json, rules/scope-discipline.md, schemas/receipt.schema.json |
| Benchmark | SKILL.md, skill-rules.json, rules/dimension-definitions.md, schemas/receipt.schema.json |
| Forge | SKILL.md, skill-rules.json, rules/attestation-required.md, rules/double-attestation.md, rules/snapshot-policy.md, schemas/receipt.schema.json |
| Retro | SKILL.md, skill-rules.json, templates/retro.md, rules/draft-first.md, rules/no-auto-routing.md, schemas/receipt.schema.json |
| Feedback | SKILL.md, skill-rules.json, rules/signal-strength.md, rules/routing-policy.md, schemas/feedback-record.schema.json, schemas/receipt.schema.json |

---

## Cross-References

- L7 Delivery (Archive, Deploy, Release signal sources for Instinct): `WabbleSpec v6.1 — Delivery.md`
- L5 Memory (tracker.json, evidence drawers, Feedback records): `WabbleSpec v6.1 — Memory.md`
- L5 Dream (pattern decay): `WabbleSpec v6.1 — Memory.md` § Dream
- L2 Autopilot (schedules Evolution runs): `WabbleSpec v6.1 — Core.md` § L2 Orchestration
- Invariants (I8, I9, I10, I12): `WabbleSpec v6.1 — Core.md` § Invariants
- Verification modes (Attestation, Measurement, Observation): `WabbleSpec v6.1 — Core.md` § Verification Modes
- EARS syntax (Blueprint requirements format): `WabbleSpec v6.1 — Core.md` § EARS
