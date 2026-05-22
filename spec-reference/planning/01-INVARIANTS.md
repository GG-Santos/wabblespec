# WabbleSpec v6.1 Invariants

12 invariants. 8 expanded from v5.3. 4 new. All locked.

---

## Invariant 1 — SPEC IS SINGLE SOURCE OF TRUTH

Spec is the only anchor for implementation. Every execution loop is grounded in a spec artifact. No invention, no drift.

Spec is constructed in stages. Each stage gates the next.

```
P1: Design Document       <- Recipe selects variant per build target
P2: Systems Design + Architecture
P3: Technical Specifications
P4: Feature Specs + Standards + Rules
```

P2 cannot begin until P1 is locked. P3 cannot begin until P2 is locked. Execution cannot begin until required spec depth is reached.

**Design Document variants by build target:**

| Target | Document Type |
|---|---|
| Game | GDD — Game Design Document |
| Web | WDD — Web Design Document |
| API/Service | SDD — Service Design Document |
| Mobile | PRD — Product Requirements Document |
| Desktop | SDD — Software Design Document |
| CLI | SDD — Software Design Document |
| IoT/Embedded | FDS — Firmware Design Specification |
| Library/Package | PRD — Package Requirements Document |
| Extension/Plugin | PDD — Plugin Design Document |
| Data/Pipeline | SAD — Systems Architecture Document |
| AI/Agent | ASD — AI Systems Document |

Base template is shared. Target-specific sections are additive.

**Spec as lookup table, not documentation.** Specs are structured for retrieval. Every spec includes canonical name, aliases, related file paths, key patterns, and explicit "what NOT to do" sections. Robots-first. Not narrative.

**Spec mutation control.** Apply proposes a delta when it discovers a better approach mid-execution. Only interface, contract, or boundary changes trigger full loop-back. ADDITIVE and COSMETIC changes are absorbed inline. Change must be classified: BREAKING / DEPRECATION / ADDITIVE / COSMETIC. BREAKING triggers NEEDS_REVERIFICATION on all downstream specs.

**Spec quality discipline (see I12).** Overplanned spec is not better spec. Quality over volume.

---

## Invariant 2 — THREE-PHASE MODEL PER STAGE

Every planning stage and execution stage runs three phases in order. No phase skips.

```
Research -> Plan -> Execute
```

**Research phase:** ReferenceLoad + MemorySearch + Explore run in sequence. Evidence is fetched and tagged with staleness states (I9). Research receipt written before Plan begins.

**Plan phase:** reads Research receipt. Produces stage plan artifact. Plan receipt written before Execute begins.

**Execute phase:** reads Plan receipt. Produces output. Execution receipt written after completion.

No phase acts on evidence it cannot trace to a receipt (I10).

**Gate collapsing.** Plan + Execute can collapse into a single context when:
1. Decompose scores task complexity below deliberation threshold
2. Spec hierarchy depth is P1 only (no downstream specs exist)
3. Recipe declares collapse-eligible at Intake

Collapse writes a combined receipt noting both phases ran together.

---

## Invariant 3 — BUILD TARGET ROUTES FIRST

Build target is identified before any other decision. Target routes everything: platform package, spec template variant, capability gateways, verification gates, engineering modules, security modules.

No module activates before build target is known.

**11 build targets:**

| Target | What it produces |
|---|---|
| Web | Browser apps, SPAs, PWAs |
| API/Service | REST, GraphQL, gRPC, event-driven services |
| Game | GDD-driven interactive experiences |
| Mobile | iOS, Android, cross-platform mobile |
| Desktop | Native apps, Electron, Tauri |
| CLI | Command-line tools and terminal applications |
| IoT/Embedded | Firmware, hardware-coupled software |
| Library/Package | Reusable code with public API contract |
| Extension/Plugin | Host-platform integrations |
| Data/Pipeline | ETL, batch, streaming, schema evolution systems |
| AI/Agent | LLM applications and agentic workflows |

Target declared by Recipe at session start. Detected from project signals or asked when ambiguous. Once declared, locked for session unless explicitly changed.

**Three-phase model per stage applies to all targets (I2).** Research phase structure varies per target but the phase sequence does not.

---

## Invariant 4 — VERIFICATION IS EXPLICIT

Every output must pass a verification gate before proceeding. No module signals completion without meeting an objective, checkable condition. Verification mode declared per module in `skill-rules.json`.

**7 verification modes:**

| Mode | When used |
|---|---|
| Test | Automated assertion against known inputs |
| Review | Structured human or agent critique |
| Audit | Compliance check against spec or standard |
| Measurement | Quantitative threshold check |
| Observation | Behavioral check without automation |
| Attestation | Human sign-off — required for irreversible actions and self-modification |
| Demonstration | Working proof against real conditions |

**REVISE loop bounds.** Max 3 REVISE cycles per verification gate. Max 3 failed attempts before Attestation is required. Both bounds logged to receipt with failure reason.

**Adversarial review (Reviewer module).** Adversary subagent generates counter-analysis. Grader subagent evaluates both sides. Budget-gated: triggers when ambiguity > threshold OR confidence < threshold OR impact is high OR verification mode is Attestation. Max 3 REVISE cycles before human escalation.

**Back-pressure by design.** Quality gates enforce correctness. Failures resolved by tightening gates, not by adjusting prompts.

---

## Invariant 5 — LOADING IS GATED

Modules activate only when needed. Nothing preloaded unnecessarily. Four gates fire in order.

| Gate | Trigger | Loads |
|---|---|---|
| Recipe | Build target identified | Platform package, spec template, target rules |
| Stage | Planning stage entered (P1-P4) | Stage-appropriate modules |
| Phase | Phase entered (Research/Plan/Execute) | Phase references, schemas, eval modes |
| Activation | `skill-rules.json` pattern match | Individual module SKILL.md, rules, references |

Gates 1-3 fire once per session context. Gate 4 fires many times — once per matched module.

Every module declares activation patterns in `skill-rules.json`. Module authority (which output it owns) also declared in `skill-rules.json`. Authority conflicts resolved before execution, not during.

---

## Invariant 6 — RUNTIME IS VENDOR-NEUTRAL

No module hardcodes a runtime, model name, or tool. System adapts to the active environment. Runtime selection is a first-class concern with receipts.

**RuntimeProbe:** reads available environment at session start. Determines available lanes.

**ModelRouter:** routes per task shape. Matches task type (creative, analytical, code, conversational, technical) to best available lane. Declares selection in runtime receipt.

**Ensemble:** activates when task spans multiple targets, no single lane covers required capability, or verification mode requires independent confirmation. Explicit trigger — never assumed. Writes combined receipt naming all lanes used.

Runtime receipt required fields: `selected`, `reason`, `task_shape`, `available_tools`, `fallback`, `verification_mode`.

---

## Invariant 7 — EXPRESSION IS CONTEXT-APPROPRIATE

Expression has two orthogonal concerns. Neither substitutes for the other.

**Homowabian (voice register):**

| Level | When used |
|---|---|
| lite | Brief progress and status updates |
| full | Dense planning synthesis |
| ultra | Maximum compression between modules |
| normal | Code, commits, security warnings, irreversible actions, exact technical instructions |

Register is context-driven. Security warnings and irreversible action confirmations always drop to normal regardless of active register.

**Economy (token discipline):**
- Compression by default across all modules
- Mechanical hedge detection: "I think", "maybe", "perhaps", "it's worth noting", "it should be noted"
- Context placement: constraints at top, active task at end, references in middle
- Context-type classification: creative, analytical, code, conversational, technical — with sampling parameter profiles per type
- Module-level compression override allowed with documented justification logged to session state

These are separate. Homowabian full can still be token-dense. Normal prose can still be compressed.

---

## Invariant 8 — SELF-IMPROVEMENT THROUGH EVIDENCE

The framework learns behavioral patterns from its own execution, promotes high-confidence patterns into module improvements, and validates changes against baselines before deployment. Evolution is evidence-driven. No stage skips.

```
Execution -> Receipt -> Instinct -> Synth -> Blueprint -> Augment -> Benchmark -> Forge
```

**Instinct.** Observes executions passively via `tracker.json`. Extraction threshold: count >= 3. Blueprint candidacy: confidence >= 0.7 AND count >= 5. Confidence formula: `confidence_new = 0.9 * confidence_old + 0.1 * outcome_signal`. Surfaces candidates only — proposes nothing.

**Synth.** Produces structured improvement hypothesis. Names: affected module, behavior change, evidence, risk, rollback condition. Writes to `experiments/candidates/`.

**Blueprint.** Formal promotion proposal. Names: before/after behavior, benchmark gates, affected targets, verification mode.

**Augment.** Writes experimental implementation to `experiments/augments/`. Never to production module space.

**Benchmark.** Quality gate before any promotion.
- AUGMENT (modification of existing): >= 80% parity with current module on all criteria
- NEW (net new module): >= 60% improvement signal over baseline

Failure halts promotion and appends failure note to `tracker.json`. Does not requeue automatically.

**Forge.** Only module that writes to production module space. Gates on: benchmark pass receipt exists, Blueprint approval exists, no open contradictions in tracker.json. After write: module receipt updated, experiment archived with provenance trail, downstream specs marked NEEDS_REVERIFICATION.

**Self-modification rule.** Evolution modules cannot promote changes to themselves without Attestation verification mode (I4).

**Build-target scoping.** Patterns scoped by build target. Web instinct does not auto-apply to IoT. Cross-target promotions require separate Benchmark run per affected target.

**Spec-layer awareness.** Evolution can improve at any spec layer but each layer has its own benchmark gate. A module-level improvement does not automatically improve the feature spec that triggered it.

---

## Invariant 9 — EVIDENCE HAS EXPIRY

All sourced facts carry staleness states. Expired evidence is not used. Stale evidence is flagged before use, not silently trusted.

**Staleness states:**

| State | Meaning |
|---|---|
| FRESH | Recently verified, fully trusted |
| AGING | Approaching staleness threshold |
| STALE | Past threshold, flag before use |
| EXPIRED | Do not use. Quarantine. |
| NEEDS_REVERIFICATION | Downstream dependency changed |
| SUPERSEDED | Replaced by newer evidence |

**Staleness propagation.** When a source expires or is updated with BREAKING classification, all specs citing it are marked NEEDS_REVERIFICATION. They do not auto-update.

**STALENESS_VIOLATION** error type: emitted when expired evidence is used without flagging. Handled by orchestration error routing.

Applies to Memory, Research output, and all reference material. Not scoped to Evolution alone.

---

## Invariant 10 — RECEIPTS ARE OPERATIONAL ARTIFACTS

Every non-trivial execution writes a receipt. Receipts are not documentation — they are inputs to the next phase. A phase without a receipt did not complete.

**Receipt chain:**
- Plan reads Research receipt
- Execute reads Plan receipt
- Verifier reads Execute receipt
- Archive reads all

**Module receipt required fields:** `module`, `layer`, `runtime`, `platforms`, `inputs`, `outputs`, `tools_used`, `memory_updates`, `validation`, `not_tested`, `confidence`

**Not-tested.** Every receipt explicitly records what was not verified. Implied completion is prohibited. Gaps are named, not hidden.

**Receipts are never deleted.** Archive preserves all receipts. Superseded receipts are archived, not removed. Provenance trail is permanent.

---

## Invariant 11 — FRAMEWORK AND PRODUCT NEVER MIX

`.wabblespec/` is framework space. `project/repo/` is product source space. Hard boundary enforced by directory structure and module authority declarations.

No framework file touches product source. No product file enters the framework control plane.

| Space | Contents |
|---|---|
| `.wabblespec/` | Module rules, receipts, memory, runtime config, plans, experiments |
| `project/repo/` | Feature code, assets, builds, configs, product tests |

Forge is the only module that writes to module space during promotion — it does not touch product source.

Module authority: each output has exactly one owning module declared in `skill-rules.json`. Authority conflicts resolved before execution.

---

## Invariant 12 — SPEC QUALITY OVER SPEC VOLUME

Overplanned spec is not better spec. Bloat is a defect. Quality beats volume. Discipline beats coverage. Cleanliness beats thoroughness.

Every spec is measured by:
- **Specificity:** what exactly, not what generally
- **Actionability:** what to do, not what might be considered
- **Cleanliness:** no redundant entries, no conflicting entries, no noise

A spec that grows without a corresponding scope expansion must be reviewed. Growth alone is not improvement.

Thoroughness and bloat are not the same thing. A minimal spec that covers all requirements is better than a comprehensive spec that covers requirements plus noise.
