# Module Plan — Specify (L1)

**Tier:** 1 — CRITICAL
**Layer:** L1 Spec Core
**v5.3 origin:** Specify module — enriched with spec hierarchy, delta tracking, EARS syntax, --patch mode

---

## Purpose

Formalize intent into spec artifacts. Populates each layer of the spec hierarchy at the correct stage. Single source of truth for all downstream execution (I1). Specify is the most content-producing module in the framework — everything Apply executes is grounded in a Specify output.

---

## Activation

`skill-rules.json` triggers:
- Stage gate fires (P1, P2, P3, P4)
- `--patch` flag from Apply (lightweight mid-execution amendment)
- Explicit `/specify` command
- Scope change triggers re-specify at affected stage

---

## Spec Hierarchy and Stage Mapping

| Stage | Specify Produces | Template Source |
|---|---|---|
| P1 | Design Document (target-specific variant) | Platform package templates/ |
| P2 | Systems Design + System Architecture | Framework templates |
| P3 | Technical Specifications | Platform + Engineering gateway |
| P4 | Feature Specs + Standards + Rules | Framework templates |

Each stage: Specify reads upstream spec before writing downstream. P2 reads P1. P3 reads P2. P4 reads P3.

---

## EARS Syntax

All requirements in spec artifacts use EARS (Easy Approach to Requirements Syntax). Structured for machine retrieval and verification.

| EARS Pattern | Structure | Example |
|---|---|---|
| Ubiquitous | The `<system>` shall `<action>` | The CLI shall exit with code 0 on success |
| Event-driven | When `<trigger>`, the `<system>` shall `<action>` | When user provides --help, the CLI shall print usage |
| Unwanted behavior | If `<condition>`, the `<system>` shall `<action>` | If input file is missing, the CLI shall exit with code 1 |
| State-driven | While `<state>`, the `<system>` shall `<action>` | While offline, the mobile app shall serve cached data |
| Optional feature | Where `<feature included>`, the `<system>` shall `<action>` | Where auth is enabled, the API shall require Bearer token |

Specify validates EARS compliance on all requirement statements before locking stage.

---

## Spec Artifact Structure (canonical)

Every spec artifact produced by Specify includes:

```markdown
# [Spec Name]

**canonical_name:** string
**aliases:** [list]
**stage:** P1|P2|P3|P4
**target:** build target
**version:** semver
**change_class:** BREAKING|DEPRECATION|ADDITIVE|COSMETIC
**related_files:** [paths]
**locked_at:** timestamp

## Requirements

<EARS-syntax requirements>

## Non-Goals

<explicit exclusions>

## Key Patterns

<what to do>

## Anti-Patterns

<what NOT to do>

## Dependencies

<upstream specs this artifact depends on>

## Open Questions

<unresolved items — must be empty before locking>
```

---

## Delta Proposal (--patch mode)

When Apply discovers a better approach mid-execution:

```
Apply detects deviation
  -> Classify deviation: BREAKING|DEPRECATION|ADDITIVE|COSMETIC
  -> IF ADDITIVE or COSMETIC:
       Specify --patch: amend spec inline
       Grader scores delta
       Verifier re-checks
       Receipt updated
  -> IF BREAKING or boundary change:
       Loop back to affected stage
       Full re-specify required
       Execution pauses
```

Patch receipt records: original requirement, amended requirement, classification, Grader score.

---

## Spec Change Classification

Every Specify write (new or patch) must declare:

| Class | Meaning | Downstream action |
|---|---|---|
| BREAKING | Interface, contract, or boundary changed | NEEDS_REVERIFICATION cascade via Provenance |
| DEPRECATION | Still works, removal planned | Downstream warned |
| ADDITIVE | New without breaking existing | No cascade |
| COSMETIC | No semantic change | No cascade |

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Design Document | `project/repo/specs/design-document.<ext>` | P1 spec artifact |
| Systems Design | `project/repo/specs/systems-design.md` | P2 spec artifact |
| System Architecture | `project/repo/specs/system-architecture.md` | P2 spec artifact |
| Technical Specifications | `project/repo/specs/technical-specs.md` | P3 spec artifact |
| Feature Specs | `project/repo/specs/features/` | P4 spec artifacts |
| Standards | `project/repo/specs/standards/` | P4 spec artifacts |
| Rules | `project/repo/specs/rules/` | P4 spec artifacts |
| Specify receipt | `.wabblespec/receipts/specify-receipt.md` | I10 compliance |

---

## Workflow

```
1. Identify stage (P1/P2/P3/P4) from Stage gate

2. Read upstream spec (P2 reads P1, P3 reads P2, P4 reads P3)
   -> Validate upstream is LOCKED before proceeding

3. Read scope.md for boundaries and non-goals

4. Read relevant Memory drawers (via MemorySearch)
   -> Flag any STALE/NEEDS_REVERIFICATION evidence

5. Load spec template for stage + target

6. Populate template:
   -> Requirements in EARS syntax
   -> Non-goals from scope.md
   -> Key patterns and anti-patterns
   -> Dependencies (upstream spec citations -> Provenance records cited_by)

7. Validate:
   -> All requirements are EARS-compliant
   -> No open questions remain
   -> Non-goals explicitly stated
   -> No scope creep (I12 — quality over volume)

8. Route to Reviewer (adversarial review, budget-gated)

9. Apply Reviewer verdict (ACCEPT / REVISE / ESCALATE)
   -> Max 3 REVISE cycles

10. Lock spec: write artifact, write receipt, notify Provenance of citations
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + authority over specs/ directory |
| `templates/` | Templates | Per-stage, per-target spec templates (11 targets × 4 stages) |
| `references/ears-syntax.md` | Reference | EARS pattern guide with examples |
| `rules/spec-quality.md` | Rules | I12 enforcement — specificity, actionability, cleanliness |
| `rules/change-classification.md` | Rules | BREAKING/DEPRECATION/ADDITIVE/COSMETIC criteria |
| `schemas/spec-artifact.schema.json` | Schema | Spec artifact header validation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |
| `evaluations/ears-compliance.md` | Evaluations | EARS syntax check cases |

---

## Integration Points

| Module | Relationship |
|---|---|
| ScopeFrame | Reads scope.md as primary constraint |
| Interview | Delegates ambiguity resolution before populating template |
| Recipe | Reads spec_template from recipe.json |
| Propose | Propose generates options; Specify formalizes chosen option |
| Apply | Apply executes against Specify artifacts. Apply --patch triggers Specify --patch. |
| Reviewer | Routes spec draft for adversarial review |
| Provenance | Notified of spec citations (cited_by population) |
| MemorySearch | Queries for relevant evidence during spec population |
| Verifier | Verifies spec quality at stage lock |
| Decompose | Reads locked spec to produce wave plans |
| Ground | Reads spec artifacts to detect hallucinated facts |

---

## Verification Mode

**Review** — spec is reviewed by Reviewer (Adversary + Grader). EARS compliance checked. Non-goals stated. No open questions. I12 quality check passes.

---

## Receipt Extension Fields

```json
{
  "stage": "P1|P2|P3|P4",
  "spec_artifact": "string — path to produced artifact",
  "change_class": "BREAKING|DEPRECATION|ADDITIVE|COSMETIC",
  "requirements_count": "integer",
  "ears_violations": "integer",
  "patch_mode": "boolean",
  "revise_cycles": "integer",
  "provenance_citations": "integer"
}
```

---

## v5.3 Mapping

| v5.3 Specify | v6.1 Specify |
|---|---|
| Single spec artifact | Full P1-P4 hierarchy |
| No stage gating | Stage gates before each layer |
| EARS syntax | Same |
| `--patch` mode (v5.2+) | Same |
| Delta proposal | Same |
| No change classification | BREAKING/DEPRECATION/ADDITIVE/COSMETIC added |
| No Provenance integration | cited_by population on every write |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Spec artifact location | `project/repo/specs/` (current) vs. `.wabblespec/specs/` | Resolve — must not mix framework and product (I11) |
| Template count | 11 targets × 4 stages = 44 templates vs. shared base + target overrides | Per-module planning |
| EARS enforcement | Hard (reject non-EARS) vs. soft (warn only) | Per-module planning |

**Note on spec location:** spec artifacts are the bridge between framework and product. They are created by framework (Specify) but consumed by product execution (Apply into project/repo/). Current decision: specs live in `project/repo/specs/` — they are product artifacts, not framework files. Consistent with I11.
