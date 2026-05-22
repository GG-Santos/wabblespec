# WabbleSpec v6.1 Skills Flow

How modules activate, execute, hand off, and chain. Not what modules do — how they connect.

---

## 1. Primary Activation Flow

Session start triggers gate sequence. Gates fire in order. Each gate expands what is available.

```
Session start
  L-- Gate 1: Recipe
       |-- Detect or ask build target
       |-- Load Platform package
       |-- Load spec template variant
       L-- Gate 2: Stage
            |-- Identify current spec depth (P1/P2/P3/P4)
            |-- Load stage-appropriate modules
            L-- Gate 3: Phase
                 |-- Identify current phase (Research/Plan/Execute)
                 |-- Load phase references, schemas, eval modes
                 L-- Gate 4: Activation
                      L-- skill-rules.json pattern match -> load module SKILL.md
```

Gates 1-3 fire once per session context. Gate 4 fires many times — once per matched module.

---

## 2. Spec Construction Flow

Spec stages chain in order. Each stage must produce a locked artifact before next begins.

```
P1: Design Document
  |-- Recipe -> selects template variant
  |-- ScopeFrame -> defines boundaries, non-goals
  |-- Interview -> reduces ambiguity via Socratic questioning
  |-- Specify -> populates Design Document
  |-- Propose -> generates options and tradeoffs (if multiple directions)
  |-- Reviewer -> adversarial review (budget-gated)
  |-- Verifier -> gate check (Review mode)
  L-- LOCKED -> P2 gate opens

P2: Systems Design + Architecture
  |-- Explore -> maps current project state
  |-- Decompose -> breaks into subsystem responsibilities
  |-- Propose -> tradeoffs between architectural approaches
  |-- Specify -> populates Systems Design + System Architecture
  |-- Reviewer -> adversarial review
  |-- Verifier -> gate check
  L-- LOCKED -> P3 gate opens

P3: Technical Specifications
  |-- Platform modules -> target-specific technical patterns
  |-- Engineering gateway -> cross-cutting technical standards
  |-- Specify -> populates Technical Specs
  |-- Verifier -> gate check (Audit or Review mode)
  L-- LOCKED -> P4 gate opens

P4: Feature Specs + Standards + Rules
  |-- Specify -> populates Feature Specs, Standards, Rules
  |-- Decompose -> produces developer and engineer execution plans
  |-- Verifier -> gate check
  L-- LOCKED -> Execution gates open
```

**Spec mutation during execution.** Apply proposes delta. Grader scores. If ADDITIVE or COSMETIC: absorbed inline, Specify patches in place. If BREAKING or boundary-crossing: loop back to appropriate spec stage.

---

## 3. Three-Phase Flow Per Stage

Every spec stage and execution stage runs three phases. Flow is identical at each level.

```
+-----------------------------------------------------+
| RESEARCH PHASE                                      |
|  ReferenceLoad -> fetch external evidence           |
|  MemorySearch  -> query internal evidence           |
|  Explore       -> map current project state         |
|  ------------------------------------------------   |
|  -> Write: Research receipt (staleness-tagged)      |
+-----------------------------------------------------+
               | receipt required
               v
+-----------------------------------------------------+
| PLAN PHASE                                          |
|  Read: Research receipt                             |
|  Decompose / Propose / Specify (per stage)          |
|  Reviewer (budget-gated adversarial)                |
|  ------------------------------------------------   |
|  -> Write: Plan receipt                             |
+-----------------------------------------------------+
               | receipt required
               v
+-----------------------------------------------------+
| EXECUTE PHASE                                       |
|  Read: Plan receipt                                 |
|  Apply / Executor / platform modules                |
|  Verifier -> gate check                             |
|  ------------------------------------------------   |
|  -> Write: Execution receipt (includes not-tested)  |
+-----------------------------------------------------+
```

Phase cannot begin without upstream receipt. Absent receipt = phase did not complete.

**Gate collapsing.** Plan + Execute collapse when complexity below threshold AND spec depth is P1 only AND Recipe declares eligible. Single combined receipt written.

---

## 4. Execution Wave Flow

Decompose produces the wave plan. Executor runs it.

```
Decompose
  L-- Produces: wave plan (ordered steps, rollback checkpoints per wave)
       L-- Executor
            |-- Wave 1: load required modules, execute, write wave receipt
            |-- [checkpoint: verify wave output before proceeding]
            |-- Wave 2: load required modules, execute, write wave receipt
            |-- [checkpoint]
            L-- Wave N -> final execution receipt

Apply (within each wave)
  |-- Reads: spec artifact for current wave
  |-- Routes: to platform modules + _shared/dev/ as needed
  |-- Executes: implementation task
  |-- Detects: scope deviation -> delta proposal
  L-- Writes: wave output + delta notes
```

**Wave rollback.** Decompose preserves rollback state between waves. Failed wave triggers rollback to last checkpoint, not full restart. Rollback always human-confirmed.

**Multi-module loading within a wave.** Single wave can activate multiple platform modules, shared language modules, and gateway capability modules simultaneously. Apply assembles context from all activated modules.

---

## 5. Verification Loop

Verifier runs at every gate. REVISE loop is bounded.

```
Verifier
  |-- Reads: execution output + spec artifact
  |-- Selects: verification mode (declared in module skill-rules.json)
  |-- Runs: gate check
  L-- Result:
       |-- PASS -> write verification receipt -> next phase opens
       L-- FAIL -> REVISE loop
            |-- Cycle 1: Reviewer + Grader -> produce fix recommendation
            |-- Cycle 2: Apply fix -> Verifier re-check
            |-- Cycle 3: Apply fix -> Verifier re-check
            L-- Cycle 4+: BLOCKED -> Attestation required (human sign-off)
                          Receipt records: cycles used, failure reason, escalation point
```

**Adversarial gate (Reviewer):**

```
Reviewer
  |-- Budget check: ambiguity > threshold OR confidence < threshold OR high impact OR Attestation mode
  |-- IF triggered:
  |    |-- Adversary -> generates counter-analysis
  |    |-- Grader -> evaluates original + counter-analysis
  |    L-- Verdict: ACCEPT / REVISE / ESCALATE
  L-- Writes: gate receipt (trigger condition, cycles, outcome)
```

---

## 6. Runtime Selection Flow

```
Session start
  L-- RuntimeProbe
       |-- Reads: active environment
       |-- Determines: available runtime lanes
       L-- Passes: capability map to ModelRouter

Task arrives
  L-- ModelRouter
       |-- Classifies: task shape (creative/analytical/code/conversational/technical)
       |-- Matches: task shape to available lane
       |-- Checks: Ensemble trigger conditions
       |    |-- Multi-target span?
       |    |-- Single lane coverage gap?
       |    |-- Attestation/Audit verification mode?
       |    L-- Below confidence threshold after single-lane attempt?
       L-- Result:
            |-- Single lane -> route, write runtime receipt
            L-- Ensemble -> coordinate lanes, write combined receipt (names all lanes)
```

Economy module applies alongside ModelRouter — classifies context type, advises sampling parameters, enforces compression level.

---

## 7. Memory Read/Write Flow

```
WRITE PATH (during execution)
  Apply / Specify / any module
    L-- Memory
         |-- Assign: drawer (topic), staleness state (FRESH)
         |-- Record: source path, confidence, contradiction status
         L-- Provenance -> log evidence entry with full lineage

READ PATH (during Research phase)
  MemorySearch
    |-- Query: by topic, entity, or relationship
    |-- Check: staleness state per result
    |    |-- FRESH/AGING -> use, include in Research receipt
    |    |-- STALE -> flag before use, note in receipt
    |    |-- EXPIRED -> quarantine, do not use, emit STALENESS_VIOLATION
    |    L-- NEEDS_REVERIFICATION -> surface for human check before use
    L-- EntityGraph -> traverse relationships for connected evidence

CONSOLIDATION (Dream - zero active-session cost)
  Dream
    |-- Cluster: related evidence across drawers
    |-- Decay: stale patterns in tracker.json
    |-- Update: EntityGraph relationships
    L-- Flag: contradictions for Provenance review

DELETION PATH (Forget)
  Forget
    |-- Archive: evidence (not silent delete)
    |-- Record: deletion reason, timestamp, requesting module
    L-- Provenance -> log deletion entry
         L-- Downstream specs citing deleted evidence -> NEEDS_REVERIFICATION
```

---

## 8. Evolution Flow

Strictly gated. No stage skips forward.

```
Execution -> Receipts -> tracker.json update
                              |
                      [count >= 3 -> extract]
                              v
                          Instinct
                      (surface candidate only)
                              |
                      [confidence >= 0.7 AND count >= 5]
                              v
                            Synth
                      (improvement hypothesis)
                      -> write to experiments/candidates/
                              |
                              v
                          Blueprint
                      (formal promotion proposal)
                      -> names: before/after, gates, targets, mode
                              |
                              v
                           Augment
                      (experimental implementation)
                      -> write to experiments/augments/
                      NEVER to production module space
                              |
                              v
                          Benchmark
                      AUGMENT: >=80% parity with current module
                      NEW: >=60% improvement over baseline
                              |
                      [FAIL -> halt, append failure note to tracker.json]
                      [PASS -> continue]
                              |
                              v
                            Forge
                      (only module writing to production module space)
                      Gates:
                        |-- Benchmark pass receipt exists
                        |-- Blueprint approval exists
                        L-- No open contradictions in tracker.json
                      After write:
                        |-- Module receipt updated
                        |-- Experiment archived with provenance trail
                        L-- Downstream specs marked NEEDS_REVERIFICATION
```

**Self-modification block.** If candidate targets an Evolution module itself, Forge requires Attestation before writing.

**Cross-target scoping.** Web instinct does not auto-promote to IoT. Cross-target promotion requires separate Benchmark run per affected target.

---

## 9. Error Routing Flow

```
Any module emits error
  L-- Error carries type: SOFT / HARD / DEPENDENCY / CONTEXT_EXHAUSTION / SPEC_VIOLATION / STALENESS_VIOLATION

Orchestration (Executor / Autopilot) receives error
  |-- SOFT -> retry, log to receipt
  |-- HARD -> halt wave, trigger rollback to last checkpoint
  |-- DEPENDENCY -> surface upstream module failure, pause execution
  |-- CONTEXT_EXHAUSTION -> Economy -> compress context, resume or checkpoint
  |-- SPEC_VIOLATION -> loop back to spec stage for correction
  L-- STALENESS_VIOLATION -> quarantine evidence, surface to MemorySearch for reverification
```

Errors never parsed from prose. Type is declared, not inferred.

---

## 10. Delivery Flow

```
Execution complete
  L-- Archive
       |-- Read: all wave receipts, verification receipts, runtime receipts
       |-- Compose: delivery receipt (what ran, outputs, not-tested, confidence)
       |-- Version bump + changelog entry
       |-- Provenance trail preserved (receipts never deleted)
       L-- State: DELIVERED

       Optional modes:
       |-- --sweep: batch entomb stale artifacts
       L-- --entomb: archive specific artifact set

  L-- Deploy (if target requires deployment)
       |-- Gate 1: spec verification (all required specs exist)
       |-- Gate 2: test verification (verification receipts pass)
       |-- Gate 3: deploy-specific gate (target-specific check)
       L-- All three gates re-run after any fix in same validation pass
```

---

## Module Communication Rules

Modules do not call each other directly. Communication is asynchronous via artifacts.

| Mechanism | Use |
|---|---|
| Receipts | Phase-to-phase handoff. Next phase reads upstream receipt before acting. |
| Spec artifacts | Apply reads spec. Specify writes spec. Verifier reads both. |
| `tracker.json` | Instinct writes. Blueprint reads. Benchmark appends. Forge reads. |
| `_shared/schemas/error-event.schema.json` | All modules emit typed errors. Orchestration reads. |
| `skill-rules.json` | Declares activation patterns and module authority. Framework reads at gate 4. |
| Session state | Economy logs compression overrides. Autopilot owns meta.md. Others submit change requests. |

---

## Flow Summary

```
Session start
  -> Recipe gate (target)
    -> Stage gate (spec depth)
      -> Phase gate (R/P/E)
        -> Activation gate (skill-rules match)

For each stage:
  Research -> Plan -> Execute (with receipts between each)

For execution:
  Decompose -> wave plan -> Executor -> Apply (per wave) -> Verifier -> Archive

For improvement:
  Instinct (observe) -> Synth (hypothesize) -> Blueprint (propose)
    -> Augment (prototype) -> Benchmark (gate) -> Forge (integrate)

For runtime:
  RuntimeProbe -> ModelRouter -> (Ensemble if triggered)

For errors:
  Typed emit -> Orchestration routes by type
```
