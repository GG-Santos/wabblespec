# Adversary Challenge Format

Every Adversary analysis produces four sections. All four are required in every receipt. Empty sections are valid only when `strong_output_acknowledged: true`.

## Weaknesses

What could go wrong with this approach in practice?

Look for:
- Assumptions that might not hold under real conditions
- Edge cases the output does not address
- Brittleness under changing conditions
- Missing error handling or failure modes
- Scalability limits not declared in the output

**Standard:** be specific. "This might not work" is not a weakness. "This approach reads the full file into memory and will OOM on inputs larger than available RAM" is a weakness.

## Missed alternatives

What other approach was not considered?

You are not required to prove an alternative is better — only to name it and describe what it might offer that the current approach does not. One or two genuine alternatives are more valuable than a long list of weak ones.

Do not suggest the alternative is correct or that it should be chosen. That is outside Adversary's role.

## Unstated assumptions

What is the output taking as given without stating it?

Look for:
- Environmental assumptions (OS, runtime version, file system state, available memory)
- Dependency assumptions (other modules, external services, network availability)
- User behavior assumptions (users will always X, users never do Y)
- Data format assumptions (input will always be valid, encoding is UTF-8)
- Scope assumptions (this change is isolated, there are no downstream consumers)

## Failure scenarios

Under what specific conditions does this output fail or produce incorrect results?

Format for each scenario: "If X happens, then Y breaks because Z."

Examples:
- "If the upstream service returns a 503, the retry loop runs indefinitely because there is no maximum retry count."
- "If two processes call this concurrently, both read the same file state and the second write overwrites the first."

If no failure scenarios exist under the declared scope, state: "No identified failure scenarios under declared scope." Do not fabricate scenarios to fill this section.

## Empty sections

Empty arrays in `counter_analysis` are valid only when `strong_output_acknowledged: true` is set in the receipt. An Adversary that sets empty arrays without this flag is an invariant violation (ADV-4).

## spec-bound mode additions

When `challenger_mode = spec-bound`, run an additional pass across all four sections: check whether the artifact meets each declared criterion in `spec_artifact`. Gaps against the spec are the highest-priority challenge points and must appear in the appropriate section (typically Weaknesses or Failure scenarios).
