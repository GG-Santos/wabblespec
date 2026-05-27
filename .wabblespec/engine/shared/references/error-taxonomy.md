# WabbleSpec Error Taxonomy — Reference

Lookup table. Consumers: guard, verifier, executor, triage.
Schema: `shared/schemas/error-event.schema.json`

---

## Error Types and Routing

| Type | recoverable | routing.action | routing.target | gate_type |
|---|---|---|---|---|
| SOFT | true | retry | same module | Revision |
| HARD | false | halt | — | Pre-flight or Abort |
| DEPENDENCY | false | pause | human checkpoint | Pre-flight |
| CONTEXT_EXHAUSTION | true | compress | Economy module | Revision |
| SPEC_VIOLATION | false | loop_back | spec stage that produced the artifact | Revision or Escalation |
| STALENESS_VIOLATION | false | quarantine | Memory module for re-fetch | Pre-flight |
| COMMAND_RISK | false | abort | — | Pre-flight |

---

## Type Definitions

**SOFT** — Recoverable transient failure. Retry is viable. Example: tool call timeout, partial output.

**HARD** — Unrecoverable failure. Execution cannot continue. Example: file write permission denied, schema parse error on required input.

**DEPENDENCY** — Required upstream module failed or its receipt is absent. Cannot proceed without upstream. Execution pauses for human review. Example: Decompose receipt missing when Executor tries to start.

**CONTEXT_EXHAUSTION** — Context limit hit. Compress and retry via Economy module. Example: conversation context too large for next phase.

**SPEC_VIOLATION** — Output contradicts the spec. Loop back to the spec stage that owns the violated rule. Example: Executor produces output that violates an acceptance criterion in Specify's receipt.

**STALENESS_VIOLATION** — Evidence used past its expiry without flagging (I9). Quarantine the evidence. Requires fresh fetch before execution continues. Example: ReferenceLoad result used after EXPIRED status set.

**COMMAND_RISK** — Shell command in wave plan classified BLOCK by Guard Layer 5 command-risk policy. Wave cannot proceed. Executor must replace or remove the offending command before re-submitting. Always includes the specific command and the safer alternative from `.wabblespec/engine/shared/references/command-risk-policy.md`.

---

## Emitting an Error Event

All fields except optional ones are required. `recoverable` must be set correctly — it drives the routing decision.

Required for DEPENDENCY: set `upstream_module`.
Required for SPEC_VIOLATION or STALENESS_VIOLATION: set `artifact` and (for staleness) `staleness_state`.

---

## Gate Type Taxonomy

Gate type describes WHEN in the lifecycle a gate stops flow — distinct from error type, which describes WHAT went wrong.

| Gate type | When it fires | WabbleSpec enforcement point |
|---|---|---|
| Pre-flight | Before a wave begins — prerequisites not met | Guard Layers 1–5: schema HARD, DEPENDENCY, COMMAND_RISK, STALENESS_VIOLATION |
| Revision | After output produced — quality or compliance issue | Verifier REVISE cycle; SOFT retry; SPEC_VIOLATION loop-back |
| Escalation | Revision ceiling reached — human sign-off required | Attestation gate (I4: 3-REVISE ceiling); SPEC_VIOLATION after max cycles |
| Abort | Terminal — no recovery path exists | HARD errors with `recoverable: false`; COMMAND_RISK; framework/product boundary crossed |

Gate type is metadata on an error event — it does not replace or change `recoverable` or `routing.action`. It adds lifecycle precision to error routing decisions. Consumers that need to communicate gate state to humans (Recipe, Executor) use gate_type to surface the right resolution path.

---

## Guard Enforcement

Guard checks for invariant violations and emits typed errors:

| Invariant violation | Error type emitted |
|---|---|
| Missing upstream receipt | DEPENDENCY |
| Framework/product boundary crossed | HARD |
| Expired evidence used | STALENESS_VIOLATION |
| Spec stage gate violated (P2 before P1 locked) | SPEC_VIOLATION |
| Authority conflict (two modules own same artifact) | HARD |
| Evolution self-promotion without Attestation | SPEC_VIOLATION |
| BLOCK-classified shell command in wave plan | COMMAND_RISK |
