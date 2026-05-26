# Reasoning Patterns

Deep thinking techniques for high-complexity tasks. Consumers: adversary, plan, specify, executor, verifier.

## When to use extended reasoning

Use structured reasoning passes (not just response generation) when:
- Task complexity is HIGH (from Recipe classification)
- The output is irreversible (architecture decisions, BREAKING changes, security configurations)
- Adversary challenge is required (adversary always reasons before challenging)
- Multiple expert perspectives must be applied (Plan module)
- The problem has multiple viable solutions with non-obvious trade-offs

## Pattern 1 — Decompose before conclude

Before writing a conclusion, list all the sub-problems. Solve each sub-problem. Then conclude.

```
Sub-problems: [list]
Sub-problem 1: [reasoning] → [conclusion]
Sub-problem 2: [reasoning] → [conclusion]
...
Overall conclusion: [synthesized from sub-conclusions]
```

Do not mix reasoning and concluding. Conclude only after all sub-problems are resolved.

## Pattern 2 — Assumption audit

Before committing to an approach, list all assumptions explicitly.

```
Assumptions:
1. [assumption] — verified by [evidence] | UNVERIFIED
2. [assumption] — verified by [evidence] | UNVERIFIED
...

If any UNVERIFIED assumptions are critical: surface them before proceeding.
```

An unverified critical assumption is a risk, not a blocker. But it must be named.

## Pattern 3 — Red team pass

After generating an initial solution, take the opposing position and argue against it.

```
Initial solution: [X]
Strongest argument against X: [Y]
Does Y invalidate X? [yes/no + reason]
If yes: revise to X' that addresses Y
If no: note Y as a known trade-off in the solution
```

This is the lightweight version of what Adversary does formally. Apply it to any HIGH-complexity decision before finalizing.

## Pattern 4 — Multiple expert perspectives

Apply three expert lenses before recommending an architecture or approach:

| Lens | Focus |
|---|---|
| Security expert | What can go wrong? What is the attack surface? |
| Operability expert | How will this behave at 3am when things go wrong? |
| Simplicity expert | What is the simplest thing that works? Is this solution simpler? |

If the three lenses agree: proceed with confidence. If they disagree: the disagreement is the risk to name.

## Pattern 5 — Confidence calibration

Before stating a conclusion, assign a confidence level:

| Confidence | Meaning | Action |
|---|---|---|
| ≥ 0.9 | Certain | State directly |
| 0.7–0.89 | Probable | State with evidence |
| 0.4–0.69 | Possible | State as hypothesis |
| < 0.4 | Speculative | State as "hypothesis requiring verification" |

Never state a < 0.7 confidence finding as if it were certain. The confidence level is part of the answer.

## Pattern 6 — Falsification check

For any rule or constraint: explicitly ask "Under what conditions would this rule be wrong?"

If no conditions exist: the rule is absolute — state it as such.
If conditions exist: document them as the rule's boundary conditions.

A rule without boundary conditions is either absolute or incomplete. Determine which.

## Pattern 7 — Pre-Commitment Prediction

Before reading the work under review, write down 3-5 most likely problem areas based on the artifact type and domain. Investigate each one specifically rather than reading passively.

```
Pre-commitment predictions:
1. [predicted problem area — based on artifact type and domain]
2. [predicted problem area]
...

Then: investigate each prediction specifically. Do not wait for them to appear — go looking.

Synthesis: compare predictions vs actual findings.
  - Predictions confirmed: [list] — confirms the search direction
  - Predictions not found: [list] — name why; were they addressed in the work, or absent?
  - Findings not predicted: [list] — these are the surprises; note which phase surfaced them
```

Purpose: converts passive reading into deliberate search. Gap detection (what's absent) is systematically missed by passive reading because the reviewer tracks what's present. Prediction forces the reviewer to name expected gaps before reading, making them visible when absent.

## Pattern 8 — Self-Audit

Before finalizing any review findings, re-read each CRITICAL or MAJOR finding and answer three questions:

```
For each CRITICAL or MAJOR finding:
  1. Confidence: HIGH / MEDIUM / LOW
  2. "Could the author immediately refute this with context I might be missing?" YES / NO
  3. "Is this a genuine flaw or a stylistic preference?" FLAW / PREFERENCE

Gate rules:
  - LOW confidence → move to Open Questions (unscored, non-blocking)
  - Author could immediately refute AND no hard evidence → move to Open Questions
  - PREFERENCE → downgrade to Minor or remove entirely
```

Apply before writing the final output. Self-audit is not optional — it is the last pass before findings become claims.

Purpose: filters false positives before they damage credibility. Five precise findings are more useful than fifteen that include ten noise items. Reviews that include low-confidence assertions get discounted; the signal-to-noise ratio is part of the review's value.

## Pattern 9 — Realist Check

For each CRITICAL or MAJOR finding that survives Pattern 8 Self-Audit, pressure-test the severity before reporting:

```
1. "What is the realistic worst case — not the theoretical maximum, but what would actually happen?"
2. "What mitigating factors already exist? (existing tests, deployment gates, monitoring, feature flags)"
3. "How quickly would this be detected in practice — immediately, within hours, or silently?"
4. "Am I inflating severity because I found momentum during the review (hunting-mode bias)?"

Downgrade rules:
  - Realistic worst case is minor inconvenience with easy rollback → CRITICAL → MAJOR
  - Mitigating factors substantially contain the blast radius → downgrade one level
  - Fast detection + straightforward fix → note this, but keep severity (still a finding)
  - Data loss, security breach, or financial impact → NEVER downgrade regardless of mitigators

Every downgrade MUST include a "Mitigated by: ..." statement.
No downgrade without an explicit mitigation rationale.
```

Purpose: prevents severity inflation from hunting-mode bias. Once a reviewer finds a CRITICAL issue they naturally look for more at that severity level. Realist Check breaks the momentum with concrete questions that require evidence, not intuition.

## Anti-patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| Reasoning in circles | Restating the problem as the solution | Force a falsification check |
| Over-hedging | Every statement qualified with "might" or "could" | Calibrate confidence explicitly; state at the right level |
| Premature convergence | Committing to the first workable solution | Apply Pattern 2 before Pattern 3 |
| Confusing effort with quality | Long reasoning = better answer | Depth is not length — a clear 3-step chain beats a rambling 10-step one |
| Rubber-stamping | Approving without verifying claims — "looks good" without checking | Apply Pattern 7 first; require evidence for every CRITICAL or MAJOR finding |
| Severity inflation | Escalating minor issues to CRITICAL because of momentum during review | Apply Pattern 9 Realist Check before reporting any CRITICAL or MAJOR finding |
| Manufactured outrage | Inventing problems to seem thorough when none exist | Apply Pattern 8 Self-Audit; if something is genuinely correct, state it plainly |
