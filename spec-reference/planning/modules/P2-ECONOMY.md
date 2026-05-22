# Module Plan — Economy (L2)

**Tier:** 2 — CORE
**Layer:** L2 Orchestration
**v5.3 origin:** Economy module — enriched v5.3, separated from Homowabian

---

## Purpose

Token density discipline across all modules. Economy enforces compression by default, classifies context type, advises sampling parameters, enforces context placement rules, and tracks compression overrides. Economy governs output density. Homowabian governs voice register. These are orthogonal concerns.

---

## Activation

`skill-rules.json` triggers:
- Passive enforcement — active on every module output
- Explicit `--budget` flag — session token ceiling mode
- Context-type classification request from ModelRouter
- Compression override request from any module (requires justification)

Economy does not block execution. It annotates, compresses, and logs.

---

## Core Responsibilities

### 1. Compression by Default

All module output passes through compression before delivery unless:
- Verification mode is Attestation (human-readable required)
- Homowabian register is `normal` (code, commits, security, irreversible actions)
- Module has declared a compression override with documented justification

Compression removes:
- Hedges: "I think", "maybe", "perhaps", "it's worth noting", "it should be noted", "basically", "actually", "simply", "just"
- Filler transitions: "So, ...", "Now, ...", "Well, ..."
- Redundant restatements of prior output
- Explanations of what code does when identifiers are self-explanatory

Compression preserves:
- All technical content
- All precision-critical statements
- Code blocks (unchanged)
- Security warnings
- Irreversible action confirmations

### 2. Context Placement

Context assembly order (enforced on all module-assembled contexts):

```
1. Constraints and invariants      <- top
2. Spec artifacts                  <- upper middle
3. Reference material              <- middle
4. Historical context              <- lower middle
5. Active task description         <- near end
6. Recent tool output              <- end
```

Rationale: addresses "lost in the middle" degradation. Constraints at top are always in attention window. Active task at end is always freshest in context.

### 3. Context-Type Classification

Classifies incoming task into context type. Advises ModelRouter on sampling parameters.

| Context Type | Characteristics | Advised approach |
|---|---|---|
| creative | Open-ended, generative, exploratory | Higher diversity |
| analytical | Structured reasoning, comparison, evaluation | Balanced |
| code | Implementation, debugging, refactoring | Deterministic, low variation |
| conversational | Back-and-forth, clarification, interview | Responsive, concise |
| technical | Precise specification, schema, contract | Low variation, exact |

Classification is advisory — ModelRouter makes final routing decision.

### 4. Budget Mode (`--budget`)

Session token ceiling. When active:
- Economy tracks estimated token consumption per module output
- Warns when approaching ceiling (at 70%, 90%)
- At ceiling: Economy signals CONTEXT_EXHAUSTION error, Executor checkpoints

Budget is declared at session start or explicitly triggered. Not on by default.

### 5. Compression Override

Any module can request compression override with documented justification. Economy logs override to session state. Override is scoped to that module's current output only — not persistent.

Override log entry:
```
module: <name>
justification: <reason>
scope: single-output
timestamp: <time>
```

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Compressed output | Inline — replaces raw output | Density enforcement |
| Context placement advisory | Inline — annotates assembled context | Placement enforcement |
| Context-type classification | Passed to ModelRouter | Sampling parameter advice |
| Override log | `.wabblespec/meta.md` (via Autopilot) | Audit trail |
| Budget status | Session state | Token ceiling tracking |

---

## Workflow

```
1. Receive module output OR context assembly request

2. Classify context type (if task shape not yet classified)
   -> Pass classification to ModelRouter

3. Check active Homowabian register
   -> IF normal: skip compression (normal prose mode)
   -> ELSE: apply compression

4. Apply hedge detection pass (mechanical pattern matching)
   -> Remove matched hedge patterns
   -> Preserve technical content

5. If context assembly: enforce placement rules
   -> Reorder context segments if needed

6. If --budget active: estimate tokens, check ceiling
   -> IF >= 90%: emit CONTEXT_EXHAUSTION warning
   -> IF at ceiling: emit CONTEXT_EXHAUSTION error

7. Log any compression overrides

8. Return compressed output
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — passive on all output |
| `references/compression-discipline.md` | Reference | Hedge pattern list, mechanical detection rules |
| `references/context-types.md` | Reference | Context type definitions + sampling parameter profiles |
| `rules/context-placement.md` | Rules | Placement order rules and rationale |
| `rules/compression-overrides.md` | Rules | What justifications are valid for override |
| `scripts/hedge-detector.py` | Script | Deterministic hedge pattern matching |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

### compression-discipline.md content (outline)

Hedge patterns (mechanical detection):
- Softeners: "I think", "I believe", "I feel", "in my opinion", "perhaps", "maybe", "possibly", "potentially", "might", "could", "seems"
- Fillers: "basically", "actually", "simply", "just", "really", "essentially", "fundamentally"
- Throat-clearing: "it's worth noting", "it should be noted", "it's important to mention", "as mentioned", "as noted above"
- Unnecessary hedged closings: "hope this helps", "let me know if you have questions", "feel free to ask"

Source: v5.3 compression-discipline.md (carry forward).

---

## Integration Points

| Module | Relationship |
|---|---|
| Homowabian | Orthogonal. Economy handles density. Homowabian handles register. Economy reads active register to know when to skip compression. |
| ModelRouter | Economy classifies context type. ModelRouter uses classification for lane selection and sampling parameters. |
| Autopilot | Economy submits override log entries to Autopilot (owns meta.md). |
| All L1-L7 modules | Economy is passive layer on all output. Every module output passes through. |
| Executor | Economy signals CONTEXT_EXHAUSTION. Executor checkpoints in response. |

---

## Verification Mode

**Measurement** — output density above minimum threshold. Hedge count below maximum. Context placement order matches rules. Token estimate within budget (if active).

---

## Receipt Extension Fields

```json
{
  "context_type": "creative|analytical|code|conversational|technical",
  "compression_applied": "boolean",
  "hedges_removed": "integer",
  "override_logged": "boolean",
  "budget_active": "boolean",
  "tokens_estimated": "integer",
  "budget_ceiling": "integer",
  "budget_percent": "number"
}
```

---

## v5.3 Mapping

| v5.3 Economy | v6.1 Economy |
|---|---|
| Token cost discipline | Same |
| Compression by default | Same |
| Mechanical hedge detection | Same — patterns carried forward |
| Context placement rule | Same |
| Context-type classification (enriched v5.3) | Same — 5 types carried forward |
| Sampling parameter profiles per type | Same |
| `--budget` mode (new v5.3) | Same |
| Adversary budget-gating | Moved to Reviewer module |
| Conflated with Homowabian voice | SEPARATED — Economy = density only |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Hedge detection: hard rules vs. probabilistic | Mechanical pattern list (current) vs. add confidence scoring | Per-module planning |
| Budget ceiling unit | Tokens (estimated) vs. characters vs. context percentage | Per-module planning |
| Compression threshold metric | Hedge count per N words vs. compression ratio vs. density score | Per-module planning |
| Override validity period | Single output (current) vs. module-scoped vs. session-scoped | Per-module planning |
