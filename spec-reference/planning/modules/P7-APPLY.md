# Module Plan — Apply (L1)

**Tier:** 2 — CORE
**Layer:** L1 Spec Core
**v5.3 origin:** Apply module — gateway routing engine, multi-module context assembly, delta proposal mechanism

---

## Purpose

Implement tasks from a locked spec via gateway routing. Apply is the execution workhorse — it reads wave spec sections, routes to the correct platform and capability modules, assembles multi-module context, and writes implementation to `project/repo/`. Apply does not make architecture decisions. It implements what Specify declared.

---

## Activation

`skill-rules.json` triggers:
- Executor invokes Apply for each wave
- `--patch` flag from Specify (lightweight spec amendment during execution)

Apply never activates without a locked spec section as input.

---

## Gateway Routing Engine

Apply routes to the correct modules based on the wave spec and build target. Routing happens at invocation — Apply does not preload all modules.

```
Wave spec section arrives
  -> Read technology signals in spec (language, framework, target)
  -> Route to platform package modules (from recipe.json target)
  -> Route to _shared/dev/ modules (languages, databases, api-consumption as needed)
  -> Route to capability gateway modules (Security, Engineering, AI, etc. as declared in spec)
  -> Assemble multi-module context from all routed modules
  -> Implement against assembled context
```

Multi-module loading: a single wave can activate multiple platform modules, shared language modules, and capability gateway modules simultaneously. Apply assembles context from all, respects Economy context placement rules.

---

## Delta Proposal Mechanism

When Apply discovers a better approach during implementation:

```
Apply detects deviation from spec
  -> Classify: BREAKING | DEPRECATION | ADDITIVE | COSMETIC
  -> IF ADDITIVE or COSMETIC:
       Generate delta proposal
       Route to Specify --patch
       Grader scores delta inline
       Verifier re-checks affected output
       Receipt updated with patch note
  -> IF BREAKING or boundary change:
       Halt wave
       Write deviation receipt
       Signal Executor: SPEC_VIOLATION
       Executor loops back to Specify for correction
       Execution resumes after spec updated
```

Delta proposal does NOT let Apply silently deviate. Every deviation is classified and routed. Spec remains source of truth (I1).

---

## Context Assembly Rules

Apply assembles context for each wave following Economy placement rules:

```
1. Constraints and invariants from spec    <- top
2. Spec artifact sections for this wave   <- upper middle
3. Platform module SKILL.md content       <- middle
4. Capability gateway references          <- middle
5. _shared/dev/ language/database refs   <- lower middle
6. Active task description for wave       <- near end
7. Recent tool output                     <- end
```

Context is assembled fresh per wave. No carryover from prior wave context.

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Implemented artifacts | `project/repo/` | Product code and assets |
| Delta proposals | Routed to Specify --patch | Spec amendments |
| Deviation receipts | `.wabblespec/receipts/deviation-<wave>-<timestamp>.md` | BREAKING deviation records |
| Apply receipt | `.wabblespec/receipts/apply-<wave>-<timestamp>.md` | I10 compliance per wave |

Apply writes ONLY to `project/repo/`. Never to `.wabblespec/` directly (I11). Receipt writing is via Executor.

---

## Workflow

```
1. Receive from Executor: wave spec sections + runtime lane + loaded module list

2. Parse wave spec sections:
   -> Identify implementation tasks
   -> Identify technology signals
   -> Identify scope boundaries (scope.md)

3. Route to modules:
   -> Platform modules for target
   -> _shared/dev/ as needed
   -> Capability gateways as declared

4. Assemble context (Economy placement rules)

5. Implement:
   -> Write to project/repo/
   -> Track deviations

6. For each deviation detected:
   -> Classify BREAKING vs. ADDITIVE/COSMETIC
   -> Route appropriately (Specify --patch or Executor halt)

7. Report to Executor:
   -> Output artifacts written
   -> Delta proposals (if any)
   -> Errors (typed)

8. Executor invokes Verifier
   -> Apply may receive REVISE guidance from Verifier
   -> Apply applies fix, re-reports
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over project/repo/ writes |
| `rules/routing-table.md` | Rules | Technology signal to module routing map |
| `rules/delta-classification.md` | Rules | BREAKING vs. ADDITIVE/COSMETIC classification criteria |
| `rules/context-assembly.md` | Rules | Multi-module context assembly order |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Executor | Executor invokes Apply per wave, receives output and error reports |
| Specify | Apply reads spec artifacts as ground truth. BREAKING deviations loop back to Specify. |
| Platform packages | Apply routes to active platform package per target |
| _shared/dev/ | Apply loads language/database/api-consumption references as needed |
| Capability gateways | Apply loads gateway references when spec declares domain concerns |
| Verifier | Verifier checks Apply output at wave checkpoint |
| Economy | Apply assembles context using Economy placement rules |

---

## Verification Mode

**Test** (primary) — automated assertion against Apply output. Mode declared per wave in Decompose wave plan. May be Review or Observation for non-code waves.

---

## Receipt Extension Fields

```json
{
  "wave": "integer",
  "spec_sections_used": "array",
  "modules_routed": "array",
  "files_written": "integer",
  "files_modified": "integer",
  "delta_proposals": "integer",
  "breaking_deviations": "integer",
  "patch_applied": "boolean"
}
```

---

## v5.3 Mapping

| v5.3 Apply | v6.1 Apply |
|---|---|
| Gateway routing engine | Same — extended to 11 platform targets |
| Multi-module context assembly | Same |
| Delta proposal mechanism (v5.2+) | Same |
| `--patch` mode via Specify (v5.2+) | Same |
| Writes to project source | Same — project/repo/ only (I11 enforced) |
| Apply managed its own wave loop | Wave loop moved to Executor — Apply implements per-wave only |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Context window management | Economy handles (current) vs. Apply requests Economy explicitly | Per-module planning |
| Multi-module conflict resolution | Last-loaded wins vs. explicit precedence rules | Per-module planning |
| LSP integration | Apply reads LSP diagnostics (v5.3) vs. separate Review step | Resolve during Test/Review carry-forward |
