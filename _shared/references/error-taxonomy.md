# WabbleSpec Error Taxonomy — Reference

Lookup table. Consumers: guard, verifier, executor, triage.
Schema: `shared/schemas/error-event.schema.json`

---

## Error Types and Routing

| Type | recoverable | routing.action | routing.target |
|---|---|---|---|
| SOFT | true | retry | same module |
| HARD | false | halt | — |
| DEPENDENCY | false | pause | human checkpoint |
| CONTEXT_EXHAUSTION | true | compress | Economy module |
| SPEC_VIOLATION | false | loop_back | spec stage that produced the artifact |
| STALENESS_VIOLATION | false | quarantine | Memory module for re-fetch |

---

## Type Definitions

**SOFT** — Recoverable transient failure. Retry is viable. Example: tool call timeout, partial output.

**HARD** — Unrecoverable failure. Execution cannot continue. Example: file write permission denied, schema parse error on required input.

**DEPENDENCY** — Required upstream module failed or its receipt is absent. Cannot proceed without upstream. Execution pauses for human review. Example: Decompose receipt missing when Executor tries to start.

**CONTEXT_EXHAUSTION** — Context limit hit. Compress and retry via Economy module. Example: conversation context too large for next phase.

**SPEC_VIOLATION** — Output contradicts the spec. Loop back to the spec stage that owns the violated rule. Example: Executor produces output that violates an acceptance criterion in Specify's receipt.

**STALENESS_VIOLATION** — Evidence used past its expiry without flagging (I9). Quarantine the evidence. Requires fresh fetch before execution continues. Example: ReferenceLoad result used after EXPIRED status set.

---

## Emitting an Error Event

All fields except optional ones are required. `recoverable` must be set correctly — it drives the routing decision.

Required for DEPENDENCY: set `upstream_module`.
Required for SPEC_VIOLATION or STALENESS_VIOLATION: set `artifact` and (for staleness) `staleness_state`.

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
