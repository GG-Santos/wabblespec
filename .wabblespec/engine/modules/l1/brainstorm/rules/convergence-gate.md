# Convergence Gate

Generation stops when a convergence signal fires. Then and only then does Brainstorm move to surfacing top options.

## Convergence signals (any one triggers convergence)

| Signal | Description |
|---|---|
| `volume_cap` | 10 or more ideas generated. Practical upper limit for a useful option set. |
| `diminishing_returns` | Last 3 ideas added no new architectural dimension and are variations on existing ideas |
| `user_signal` | User said "that's enough" or "stop generating" during a live session |
| `time_budget` | Context token budget for this pass is 80% consumed |

Record which signal fired in the receipt as `convergence_trigger`.

## Minimum before convergence

Do not converge before generating at least 5 ideas, unless `user_signal` fires. 5 is the minimum that provides meaningful option breadth. If you converge at 3 ideas, you have not brainstormed — you have listed the first options that came to mind.

## After convergence fires

1. Stop generation
2. Review full generated set
3. Select 3–5 options with the most merit for downstream evaluation
4. Write top options to `.wabblespec/brainstorm/options-<timestamp>.md`

The selection step is the only evaluation Brainstorm performs. "Most merit" = most genuinely different from each other + most actionable given declared target + complexity.

## What Propose does next

Propose receives the top options file and evaluates each against each other. Brainstorm has no further role. Do not revisit options after passing to Propose.
