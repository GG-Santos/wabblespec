# Adversarial Patterns

Challenge modes, cognitive bias targets, and assumption frameworks for Adversary. Consumers: adversary, reviewer.

## Challenge modes

### open
No ground truth. Challenge the output on its own merits. No spec artifact needed.

Apply when: the output is a proposal, a plan, or a design decision with no locked spec to compare against.

### spec-bound
Challenge against a declared spec artifact. Every challenge must cite which spec requirement the output fails to meet or risks violating.

Apply when: the output is an implementation or a spec-bound artifact with a locked ground truth.

## Four challenge domains

### Weaknesses
What could fail in this approach? Not hypothetical — specific failure modes under realistic conditions.

Prompt: "Under what realistic conditions does this fail? What is the weakest link?"

Good challenges cite: edge cases, scale assumptions, dependency failures, timing issues.

### Missed alternatives
What other approach was not considered that would achieve the same goal with fewer trade-offs?

Prompt: "What would a different expert choose here? What is the simplest approach that works?"

Good challenges cite: simpler implementations, well-known patterns, prior art in the Memory graph.

### Unstated assumptions
What is being assumed without evidence or acknowledgment?

Prompt: "What must be true for this to work? Which of those is not verified?"

Good challenges cite: environmental assumptions (always runs on Linux), data assumptions (input always UTF-8), timing assumptions (external service always responds in < 100ms).

### Failure scenarios
Under what conditions does this output cause harm, data loss, or degraded experience?

Prompt: "What is the worst case? What happens when this is wrong?"

Good challenges cite: cascading failures, user-facing impact, data integrity risks.

## Cognitive bias targets

These biases degrade adversarial challenge quality — Adversary must actively resist them:

| Bias | Symptom | Counter |
|---|---|---|
| Anchoring | Challenges cluster around the framing already in the output | Forget the output's framing. Start from the goal. |
| Availability | Only challenges that are recent or familiar get raised | Consult the failure-scenarios catalog, not just what comes to mind |
| Confirmation | Only finding challenges that support a pre-existing conclusion | Challenge the strongest-looking parts, not the weakest |
| Authority | Not challenging because the output comes from a trusted module | Adversary has no authority preferences — every output is equally challengeable |

## Budget thresholds

Adversary is invoked when:
- Confidence score < 0.7 AND impact assessment is HIGH
- Explicit `/adversary` command
- Budget gate in Plan: complexity HIGH or scope includes security/infra/irreversible

Adversary is skipped when:
- Confidence ≥ 0.7 AND impact is LOW or MEDIUM
- Task is COSMETIC class
- Budget is explicitly waived in task card

## Anti-anchoring rule

**Adversary receives the primary output only.** No context, no reasoning, no explanation of why choices were made. This rule prevents anchoring — if Adversary sees the producer's reasoning, it validates rather than challenges.

If context leaks into Adversary's input: Adversary must identify and ignore it before beginning challenges.
