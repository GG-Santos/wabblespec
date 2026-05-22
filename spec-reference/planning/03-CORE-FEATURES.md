# WabbleSpec v6.1 Core Features

14 feature groups. What the framework does for users.

---

## 1. Target-First Routing

Recipe is the entry point for every session. Build target identified before any other decision. Target routes: platform package, spec template variant, capability gateways, verification gates, engineering modules, security modules.

No module activates before build target is known.

11 targets: Web, API/Service, Game, Mobile, Desktop, CLI, IoT/Embedded, Library/Package, Extension/Plugin, Data/Pipeline, AI/Agent.

Recipe detects target from project signals or asks when ambiguous. Once declared, target locked for session unless explicitly changed.

---

## 2. Progressive Spec Construction

Spec is the single source of truth (I1). Constructed in stages — each gates the next.

```
P1: Design Document       <- Recipe selects variant per target
P2: Systems Design + Architecture
P3: Technical Specifications
P4: Feature Specs + Standards + Rules
```

**Spec mutation control.** Apply proposes delta when it discovers better approach mid-execution. Only interface, contract, or boundary changes trigger full loop-back. Cosmetic and additive changes absorbed inline.

**Spec change classification.** Every update classified BREAKING / DEPRECATION / ADDITIVE / COSMETIC. BREAKING triggers NEEDS_REVERIFICATION on all downstream specs.

**Spec quality discipline (I12).** Bloat is a defect. Every spec evaluated on specificity, actionability, and cleanliness. Spec growing without matching scope expansion must be reviewed. Quality over volume.

---

## 3. Three-Phase Execution Per Stage

Every planning stage runs three phases in order (I2):

```
Research -> Plan -> Execute
```

**Research phase:** ReferenceLoad + MemorySearch + Explore in sequence. Evidence fetched and tagged with staleness states. Research receipt written before Plan begins.

**Plan phase:** reads Research receipt. Produces stage plan artifact. Plan receipt written before Execute begins.

**Execute phase:** reads Plan receipt. Produces output. Execution receipt written after completion.

No phase acts on evidence it cannot trace to a receipt. No phase skips ahead.

**Gate collapsing.** Plan + Execute can collapse into single context when Decompose scores complexity below deliberation threshold AND spec depth is P1 only AND Recipe declares collapse-eligible. Collapse writes combined receipt.

---

## 4. Progressive Module Loading

Four gates control what loads. Nothing preloaded (I5).

| Gate | Trigger | What loads |
|---|---|---|
| Recipe | Build target identified | Platform package, spec template, target rules |
| Stage | Planning stage entered | Stage-appropriate modules |
| Phase | Phase entered | Phase references, schemas, eval modes |
| Activation | `skill-rules.json` pattern match | Individual module SKILL.md, rules, references |

Every module declares activation patterns in `skill-rules.json`. Framework loads only what current task requires.

---

## 5. Vendor-Neutral Runtime Selection

No module hardcodes runtime, model name, or tool (I6). System adapts to active environment.

**RuntimeProbe:** reads available environment at session start.

**ModelRouter:** routes per task shape — creative, analytical, code, conversational, technical. Declares selection in runtime receipt.

**Ensemble:** activates when task spans multiple targets, no single lane covers required capability, or verification mode requires independent confirmation. Explicit trigger — never assumed. Writes combined receipt naming all lanes.

Runtime receipt required fields: `selected`, `reason`, `task_shape`, `available_tools`, `fallback`, `verification_mode`.

---

## 6. Verification System

Every output must pass a verification gate before proceeding (I4). Verification mode declared per module in `skill-rules.json`.

| Mode | Use |
|---|---|
| Test | Automated assertion against known inputs |
| Review | Structured critique |
| Audit | Compliance check against spec or standard |
| Measurement | Quantitative threshold |
| Observation | Behavioral check without automation |
| Attestation | Human sign-off — required for irreversible actions and self-modification |
| Demonstration | Working proof against real conditions |

**REVISE loop bounds.** Max 3 REVISE cycles per verification gate. Max 3 failed attempts before Attestation required. Both logged to receipt with failure reason. Grader scores gate outcomes.

**Adversarial review.** Reviewer module contains Adversary subagent (counter-analysis) and Grader subagent (evaluation). Budget-gated: triggers when ambiguity > threshold OR confidence < threshold OR impact is high OR verification mode is Attestation. Max 3 REVISE cycles before human escalation.

---

## 7. Gateway Capability System

Six capability gateways provide deep domain knowledge activated on demand.

| Gateway | Scope |
|---|---|
| Security | Threat modeling, continuous security, OWASP, pentest, compliance. Cross-cutting only — platform-specific security at L3. |
| Engineering | CI/CD, architecture review, reliability, systems design. Cross-cutting only — platform-specific engineering at L3. |
| AI | LLM evaluation, prompt engineering, chain design, agent architecture, safety. Applies to any target embedding AI features. |
| Aesthetic | Visual design, brand, style systems. |
| Design | UX, interaction design, information architecture. |
| Experience | User research, usability, accessibility. |

Multiple gateways load simultaneously for cross-domain tasks.

---

## 8. Platform Capability System

11 platform packages. Each self-contained.

Each package contains: platform SKILL.md, platform-specific dev modules, platform-specific engineering modules, platform-specific security modules, spec template variant, verification gates.

**Shared dev infrastructure** (`_shared/dev/`):
- Languages: Node, Python, Go, Rust, Java
- Databases: SQL, NoSQL, ORM, Migration
- API consumption patterns

Platform packages are not duplicated. Each module lives in one place. `_shared/dev/` is the only cross-platform dev knowledge store.

---

## 9. Memory and Evidence System

Evidence is not trusted without provenance. All sourced facts carry staleness states (I9).

**Staleness states:** FRESH -> AGING -> STALE -> EXPIRED -> NEEDS_REVERIFICATION -> SUPERSEDED

**Modules:**
- **Memory:** primary evidence store. Drawers (topics) and closets (archived). Local-first, plain files.
- **MemorySearch:** query interface. Finds evidence by topic, entity, or relationship.
- **MemoryMine:** extracts implicit knowledge from execution history.
- **EntityGraph:** tracks entities, relationships, and changes across project lifetime.
- **Provenance:** records source path, confidence, freshness, and contradiction status per evidence item.
- **Dream:** consolidation phase. Runs at zero active-session cost. Clusters patterns, decays stale entries, updates EntityGraph.
- **Forget:** structured deletion with provenance trail. Evidence archived, not silently removed.

**Staleness propagation.** When source expires, all specs citing it are marked NEEDS_REVERIFICATION. They do not auto-update.

**STALENESS_VIOLATION** error type: emitted when expired evidence is used without flagging.

---

## 10. Self-Improvement Pipeline

Framework improves from its own execution (I8). Pipeline strictly gated — no stage skips.

```
Execution -> Receipt -> Instinct -> Synth -> Blueprint -> Augment -> Benchmark -> Forge
```

**Instinct:** observes executions passively. Extraction threshold: count >= 3. Blueprint candidacy: confidence >= 0.7 AND count >= 5. Formula: `confidence_new = 0.9 * confidence_old + 0.1 * outcome_signal`. Surfaces candidates only.

**Synth:** structured improvement hypothesis. Writes to `experiments/candidates/`.

**Blueprint:** formal promotion proposal with before/after behavior, benchmark gates, affected targets, verification mode.

**Augment:** experimental implementation to `experiments/augments/`. Never to production.

**Benchmark:** AUGMENT >= 80% parity. NEW >= 60% improvement. Failure halts, appends failure note to `tracker.json`.

**Forge:** only module writing to production module space. Gates on benchmark pass receipt, Blueprint approval, no open contradictions.

**Self-modification rule:** Evolution modules cannot promote changes to themselves without Attestation.

**Build-target scoping:** patterns scoped by build target. Cross-target promotions require separate Benchmark run per target.

---

## 11. Expression System

Two orthogonal concerns (I7).

**Homowabian (L6 Expression):** voice register.
- `lite` — brief progress and status
- `full` — dense planning synthesis
- `ultra` — maximum compression between modules
- `normal` — code, commits, security warnings, irreversible actions, exact technical instructions

Security warnings and irreversible action confirmations always drop to normal.

**Economy (L2 Orchestration):** token density discipline.
- Compression by default across all modules
- Mechanical hedge detection
- Context placement: constraints at top, active task at end, references in middle
- Context-type classification with sampling parameter profiles
- `--budget` mode: session token ceiling
- Module-level override allowed with documented justification

---

## 12. Receipts and Provenance Chain

Every non-trivial execution writes a receipt (I10). Receipts are operational artifacts — inputs to next phase, not documentation.

**Receipt chain:** Plan reads Research receipt. Execute reads Plan receipt. Verification reads Execute receipt. Archive reads all.

**Module receipt required fields:** `module`, `layer`, `runtime`, `platforms`, `inputs`, `outputs`, `tools_used`, `memory_updates`, `validation`, `not_tested`, `confidence`

**Not-tested.** Every receipt explicitly records what was not verified. Implied completion prohibited. Gaps named, not hidden.

**Archive:** preserves receipts, decisions, provenance trail. Receipts never deleted — only superseded and archived.

---

## 13. Operational Integrity

**Typed error taxonomy** (`_shared/schemas/error-event.schema.json`):
SOFT / HARD / DEPENDENCY / CONTEXT_EXHAUSTION / SPEC_VIOLATION / STALENESS_VIOLATION.
Orchestration routes by type, not prose interpretation.

**State ownership.** Shared state files have exactly one owning module. Others submit change requests atomically. Prevents concurrent write contention.

**Framework-product separation (I11).** `.wabblespec/` and `project/repo/` never mix. Hard boundary enforced by directory structure and module authority declarations.

**Module authority.** Each output has exactly one owning module declared in `skill-rules.json`. Conflicts resolved before execution.

**Prompt quality.** Every prompt the framework generates can be evaluated against known failure patterns covering task, context, format, scope, reasoning, and agentic dimensions.

---

## 14. Tribal Knowledge and Context Intelligence

**Nexus:** architectural reasoning, cross-cutting relationships, change-impact analysis. Connects historical Memory with forward planning in Specify.

**EntityGraph:** entities and relationships indexed across project lifetime. Queryable via MemorySearch.

**Context placement:** constraints at top, active task at end, references in middle. Addresses "lost in the middle" degradation in long contexts.

**Spec as lookup table:** structured for retrieval, not reading. Canonical name, aliases, related file paths, key patterns, explicit "what NOT to do". Robots-first, not narrative.
