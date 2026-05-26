# Divergence Rules

Brainstorm operates in divergent mode during generation. These rules keep it divergent.

## The core rule

No evaluation during generation. An idea that is written down is not evaluated, ranked, compared, or argued against until the convergence gate fires. Every idea gets equal treatment during generation: write it down and move on.

## Divergence indicators (you are diverging correctly)

- Ideas are described in neutral terms: "approach A does X"
- No idea is described as better or worse than another during generation
- You are generating ideas in new domains, not variations on the first idea
- The idea set contains some approaches you find personally unconvincing

## Convergence indicators (you have stopped diverging — stop and restart)

- You wrote "this is better because..." during generation
- You wrote "this won't work because..." during generation
- All ideas are variations on the same architectural pattern
- You have stopped generating because "there are no more good ideas" — there are always more ideas; the question is whether they are worth surfacing

## Breadth requirement

Push across at least three of these dimensions before declaring convergence:

1. Architectural style (centralized vs distributed, sync vs async, monolith vs service)
2. Build vs reuse vs buy (custom implementation, open-source library, third-party service)
3. Scope of solution (narrow problem, broader problem, root cause vs symptom)
4. Technology profile (if the task involves technology choices)
5. Interaction model (user-facing vs system-facing, batch vs streaming)

You do not need to produce options in every dimension. But you must have considered each before convergence.

## Neutral description format

Write each idea as: "Approach: [one sentence description]. What it offers: [one sentence on value]. What it trades off: [one sentence on cost]." No more. Save analysis for Propose.
