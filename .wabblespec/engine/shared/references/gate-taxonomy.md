# Gate Taxonomy

Canonical gate types used across WabbleSpec modules. Every validation checkpoint maps to one of these four types. Sourced from: `research/ref-eval/get-shit-done-redux.md` → Section 8 synthesis + B12.

---

## Gate Types

### Pre-flight Gate

**Purpose:** Validates preconditions before starting an operation.
**Behavior:** Blocks entry if conditions unmet. No partial work created.
**Recovery:** Fix the missing precondition, then retry.
**WabbleSpec examples:**
- Guard Layers 1–5 (all run before any wave touches project files)
- I1 locked-spec check (Guard Layer 3 — task card must exist before Execute)
- Decompose Step 1 (specify-receipt.json must exist before wave plan is written)
- Executor pre-execution prologue (decompose-receipt.json must exist before Wave 1)

### Revision Gate

**Purpose:** Evaluates output quality and routes to revision if insufficient.
**Behavior:** Loops back to the producer with specific feedback. Bounded by an iteration cap. Escalates early if issue count does not decrease between consecutive iterations (stall detection).
**Recovery:** Producer addresses feedback; gate re-evaluates. After cap exhaustion, escalates unconditionally.
**WabbleSpec examples:**
- Verifier REVISE loop (max 3 cycles; stall detection fires before cap if issue count plateaus)
- Reviewer adversarial review (max 3 REVISE cycles, then Attestation)
- Plan-checker in Decompose → Reviewer gate before Executor starts

### Escalation Gate

**Purpose:** Surfaces unresolvable issues to the user for a decision.
**Behavior:** Pauses workflow. Presents options and evidence. Waits for human input.
**Recovery:** User chooses action; workflow resumes on the selected path.
**WabbleSpec examples:**
- Attestation (user must explicitly confirm before execution continues)
- REVISE loop exhaustion after 3 cycles → escalate to user
- BLOCKED verdict from Verifier → surface to user for Attestation
- Scope reduction language detected in wave plan → Decompose must revise

### Abort Gate

**Purpose:** Terminates the operation to prevent damage or produce meaningless output.
**Behavior:** Stops immediately. Preserves state. Reports reason.
**Recovery:** Investigate root cause, fix, restart from checkpoint.
**WabbleSpec examples:**
- CONTEXT_EXHAUSTION error → compress, save checkpoint, surface to user
- STALENESS_VIOLATION (I9) — expired evidence → quarantine, abort wave
- I11 violation — framework space write attempted → HARD abort
- Guard HARD error — abort wave unconditionally

---

## Gate Matrix

| Module | Phase | Gate Type | What is checked | Failure behavior |
|---|---|---|---|---|
| Guard | Pre-wave (Layer 1) | Pre-flight | Schema validity | HARD abort |
| Guard | Pre-wave (Layer 2) | Pre-flight | Scope constraints | SPEC_VIOLATION |
| Guard | Pre-wave (Layer 3) | Pre-flight | Invariant compliance | HARD abort or SPEC_VIOLATION |
| Guard | Pre-wave (Layer 4) | Pre-flight | Module authority | HARD abort |
| Guard | Pre-wave (Layer 5) | Pre-flight | Command risk | HARD abort or WARN |
| Guard | Pre-wave (Layer 6) | Pre-flight | Scope reduction language in wave tasks | HARD block → Decompose revise |
| Verifier | Post-wave | Revision | Spec compliance + mode check | REVISE loop (max 3 + stall detection) |
| Verifier | Post-wave (cap hit) | Escalation | Unresolved after 3 cycles | Attestation required |
| Reviewer | Post-Decompose | Revision | Wave plan quality | REVISE to Decompose (max 3) |
| Executor | Mid-wave BREAKING | Escalation | Architectural deviation discovered | Surface to user, loop to Specify |
| Executor | Post-wave | Pre-flight | Self-check: artifacts exist + commits resolve | PARTIAL receipt if fails |
| Archive | Pre-archive | Pre-flight | All wave receipts present, all criteria covered | WARN (non-blocking) |

---

## Selection Heuristic

Start with Pre-flight. If the check happens after work is produced, it is Revision. If the Revision loop cannot resolve the issue, Escalate. If continuing is dangerous or would produce meaningless output, Abort.

When in doubt between Revision and Escalation: if automated retry has any reasonable chance of success, use Revision with a bounded cap. If the failure requires a human judgment call (ambiguous requirement, irreversible action, external dependency), Escalate immediately.

Never use Abort for failures that Revision could resolve. Reserve Abort for: context exhaustion, expired evidence, invariant boundary violations, hardware unavailability.
