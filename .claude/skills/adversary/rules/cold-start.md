# Cold-Start Behavior — Adversary

Defines what Adversary does when its artifact input or budget gate are absent.

## Absent: artifact to challenge

Condition: Adversary invoked without a declared artifact or decision to challenge.
Action: Surface: "Adversary requires an artifact to challenge. Specify the output, decision, or spec to challenge."
Do NOT: Generate a challenge without a declared target.

## Absent: challenger_mode declaration

Condition: Adversary invoked without specifying `open` or `spec-bound` mode.
Action: Surface: "Specify challenger_mode: 'open' (challenge on own merits) or 'spec-bound' (challenge against declared spec)."
Do NOT: Default to either mode — they produce materially different challenges.

## Absent: spec_artifact (when spec-bound mode declared)

Condition: challenger_mode is `spec-bound` but no spec artifact path provided.
Action: BLOCK. Surface: "spec-bound mode requires a spec_artifact. Provide the task card or scope.md path."
Do NOT: Proceed in spec-bound mode without a ground truth spec.

## Absent: budget gate check

Condition: Adversary is about to be invoked but budget gate has not been evaluated.
Detection: Budget gate evaluation missing from caller's flow.
Action: Evaluate budget gate first. Adversary is mandatory when: output confidence < 0.7 OR impact = HIGH OR complexity = High with security/infra/irreversible scope. Block if gate not met and caller did not pass gate evaluation.
Do NOT: Invoke Adversary unconditionally (wasteful) or skip it unconditionally (risky on high-impact decisions).

## Absent: isolation from primary reasoning

Condition: Adversary is invoked in the same reasoning thread that produced the artifact.
Detection: Adversary and primary reasoning share context without a deliberate separation.
Action: Note in receipt: "isolation not guaranteed — same session produced both artifact and challenge." This reduces adversarial validity.
Do NOT: Suppress the challenge because isolation is imperfect. Proceed and flag.

## Default state on cold start

| Field | Default |
|---|---|
| `challenger_mode` | Not declared — must be specified |
| `challenge_domains` | Weaknesses, Missed alternatives, Unstated assumptions, Failure scenarios — all four always evaluated |
| `isolation` | Best-effort within session; noted in receipt |
| `challenge_depth` | Match artifact complexity (Low: 3+ points; Medium: 5+ points; High: 8+ points) |
| `output_path` | `.wabblespec/receipts/adversary-receipt-<timestamp>.json` |
