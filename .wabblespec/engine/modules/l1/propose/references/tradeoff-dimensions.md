# Tradeoff Dimensions — Propose

Five dimensions assessed for every option. Each dimension gets a single-word or short-phrase rating. Do not omit dimensions — if a dimension is not applicable, state why.

## Complexity

How difficult is the option to implement correctly?

| Rating | Meaning |
|---|---|
| Low | Straightforward — any competent engineer can implement without research |
| Medium | Requires design work or non-trivial integration |
| High | Significant unknowns, cross-cutting concerns, or architectural depth required |

## Time to implement

Calendar estimate assuming focused work. State as a range if uncertain. Factor in integration, testing, and review — not just coding.

Examples: `1-2 days`, `1 week`, `2-4 weeks`, `unknown (spike required)`

## Risk

Probability and severity of the option going wrong.

| Rating | Meaning |
|---|---|
| Low | Well-understood approach, failure modes known and recoverable |
| Medium | Some unknowns, failure modes manageable, recovery possible |
| High | Significant unknowns, hard-to-recover failure modes, or depends on external factors |

## Reversibility

How easy is it to undo or change direction after choosing this option?

| Rating | Meaning |
|---|---|
| Easy | Can be changed with low effort — no downstream lock-in |
| Hard | Changing direction requires significant rework |
| Irreversible | Commits downstream consumers or external systems — cannot be undone without breaking changes |

## Fits scope

Does this option fit within the declared scope.md boundaries?

| Rating | Meaning |
|---|---|
| Yes | Fully within declared scope |
| Partially | Achieves the goal but touches areas adjacent to declared scope |
| No | Requires scope expansion — option should be excluded unless scope is renegotiated |

Options rated `No` on Fits scope are excluded from the options document unless scope.md is amended first.
