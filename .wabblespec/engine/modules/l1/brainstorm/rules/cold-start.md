# Cold-Start Behavior — Brainstorm

Defines what Brainstorm does when its problem framing or convergence inputs are absent.

## Absent: problem or prompt to brainstorm

Condition: Brainstorm invoked without a declared problem, question, or prompt.
Action: Surface: "Brainstorm requires a declared problem or question. State what you are generating ideas for."
Do NOT: Brainstorm generically — every session has a declared subject.

## Absent: divergence-rules.md

Condition: `rules/divergence-rules.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md divergence rules. Log: "divergence-rules.md missing — using SKILL.md defaults."

## Absent: convergence-gate.md

Condition: `rules/convergence-gate.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md convergence rules. Log: "convergence-gate.md missing — using SKILL.md defaults."

## Absent: prior Propose or Plan output (when Brainstorm is called to break a tie)

Condition: Brainstorm invoked because Propose produced a tie — but no Propose receipt found.
Detection: Caller indicates tie-breaking mode but no Propose receipt exists.
Action: Surface: "Brainstorm was invoked to break a Propose tie, but no Propose receipt was found. Run Propose first, or invoke Brainstorm independently with the stated options."

## Default state on cold start

| Field | Default |
|---|---|
| `divergence_target` | 5 distinct ideas (minimum before convergence evaluation) |
| `mode` | `diverge` — generate freely before evaluating |
| `convergence_gate` | Applied after divergence phase; eliminates duplicates and merges related ideas |
| `no_critique_during_diverge` | true — no evaluation during divergence phase |
| `output` | Brainstorm receipt with idea list, filtered set, and selected direction |
