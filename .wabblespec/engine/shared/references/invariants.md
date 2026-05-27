# WabbleSpec Invariants — Reference

Lookup table. 12 invariants. Consumers: guard, verifier, executor, recipe, specify.

---

| # | Name | Rule | Violation |
|---|---|---|---|
| I1 | SPEC IS SINGLE SOURCE OF TRUTH | Every execution grounded in spec. P2 blocked until P1 locked. P3 blocked until P2 locked. Execution blocked until required spec depth reached. | Execution without spec = I1 violation |
| I2 | THREE-PHASE MODEL PER STAGE | Research -> Plan -> Execute. No skip. Plan reads Research receipt. Execute reads Plan receipt. Gate collapsing: allowed only when complexity below threshold AND P1-only depth AND Recipe declares eligible. | Phase skip = I2 violation |
| I3 | BUILD TARGET ROUTES FIRST | Target identified before any other decision. No module activates before target known. Target locked for session once declared. | Module activation before target = I3 violation |
| I4 | VERIFICATION IS EXPLICIT | Every output passes a verification gate. Mode declared in skill-rules.json. Max 3 REVISE cycles per gate. At 3 failures: Attestation required. | Completion without gate = I4 violation |
| I5 | LOADING IS GATED | Nothing preloaded. Four gates in order: Recipe, Stage, Phase, Activation. Gate 4 fires per matched module. Module without skill-rules.json cannot activate. | Load without gate = I5 violation |
| I6 | RUNTIME IS VENDOR-NEUTRAL | No model names anywhere. Capability descriptors only (code-generation, analysis, synthesis, long-context). RuntimeProbe reads environment. ModelRouter routes per task shape. | Hardcoded model name = I6 violation |
| I7 | EXPRESSION IS CONTEXT-APPROPRIATE | Homowabian (voice register) and Economy (token density) are separate concerns. Security warnings and irreversible action confirmations always use normal register regardless of active register. | Register confusion or missing normal for security = I7 violation |
| I8 | SELF-IMPROVEMENT THROUGH EVIDENCE | Evolution chain: Execution -> Receipt -> Instinct -> Synth -> Blueprint -> Augment -> Benchmark -> Forge. No stage skips. Evolution modules cannot promote changes to themselves without Attestation. | Stage skip or self-promotion without Attestation = I8 violation |
| I9 | EVIDENCE HAS EXPIRY | All facts carry staleness states. EXPIRED evidence is not used. STALE evidence is flagged before use. STALENESS_VIOLATION error emitted when expired evidence used without flagging. | Using EXPIRED evidence silently = I9 violation |
| I10 | RECEIPTS ARE OPERATIONAL ARTIFACTS | Every non-trivial execution writes a receipt. Receipt chain: Plan reads Research, Execute reads Plan, Verifier reads Execute, Archive reads all. Implied completion prohibited. not_tested required in every receipt. Receipts never deleted. | Missing receipt in chain = I10 violation |
| I11 | FRAMEWORK AND PRODUCT NEVER MIX | .wabblespec/ = framework space. Project root (excluding .wabblespec/, .claude/, .git/) = product space. No crossing. Each output has exactly one owning module. Authority conflicts resolved before execution. | Framework file in product space (or reverse) = I11 violation |
| I12 | SPEC QUALITY OVER SPEC VOLUME | Spec measured by specificity, actionability, cleanliness. Growth without scope expansion triggers review. Bloat is a defect. | Redundant/conflicting/noisy spec entries = I12 violation |

---

## Gate Collapsing Conditions (I2)

All three required simultaneously:

1. Decompose scores complexity below deliberation threshold
2. Spec hierarchy depth is P1 only (no downstream specs)
3. Recipe declares `collapse_eligible: true`

Collapse writes combined receipt with `phase: "Collapsed"`.

---

## Spec Mutation Classification (I1)

| Type | Action |
|---|---|
| BREAKING | Full loop-back. Downstream specs marked NEEDS_REVERIFICATION. |
| DEPRECATION | Flag. Downstream specs notified. |
| ADDITIVE | Absorbed inline. No loop-back. |
| COSMETIC | Absorbed inline. No loop-back. |

---

## Verification Modes (I4)

| Mode | When |
|---|---|
| Test | Automated assertion against known inputs |
| Review | Structured human or agent critique |
| Audit | Compliance check against spec or standard |
| Measurement | Quantitative threshold check |
| Observation | Behavioral check without automation |
| Attestation | Human sign-off. Required for irreversible actions and self-modification. |
| Demonstration | Working proof against real conditions |
