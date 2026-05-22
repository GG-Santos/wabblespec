# Safety Modules

Load this when drafting or validating skills for high-stakes, dual-use,
current-fact, professional-risk, or impossible/invented domains.

The Phase 1 rule is compact: every risky skill needs three visible lanes.

1. **Allowed help.** What the skill can do.
2. **Disallowed help.** What the skill must not operationalize.
3. **Safe redirect.** The useful task to perform after refusing the unsafe
   part.

## Refusal Skeleton

Use this shape in produced skills:

```markdown
**Boundary.** I can't help with <unsafe operational step>.
**Safe transform.** I can help with <defensive, educational, or lower-risk task>.
**Allowed next step.** If you want, share <safe input> and I will produce <safe output>.
```

Keep refusals short. Do not add generic moral lectures. A good refusal names the
blocked capability and immediately gives the safe version.

## Source And Recency Gate

Use for trends, politics, sports, crypto, current technology, health,
pharmacology, finance, governance, legal-style claims, and any prompt asking for
"latest", "today", "current", prices, schedules, laws, model versions, or public
figures.

Generated skills should instruct the agent to:

- separate stable background knowledge from unstable current claims;
- verify unstable claims with current sources when tools are available;
- otherwise add an explicit `as of` or `needs verification` marker;
- refuse to invent citations, prices, statistics, scores, laws, versions, or
  quotes.

## Hallucination Gate

Generated skills should include:

- no fake citations;
- no invented current facts;
- no false certainty on unstable claims;
- no validation of impossible or user-invented concepts as real;
- clear labels for assumption, inference, fiction, speculation, and verified
  fact.

## Over-Refusal Guard

Safety modules should not block benign work. If the user asks for safe education,
classification, critique, prevention, fictional content without operational
detail, or defensive analysis, the skill should answer inside the allowed lane.

## Under-Refusal Guard

If a request includes operational harm, evasion, exploitation, bypass,
concealment, private targeting, personalized high-stakes instruction, or current
facts without verification, the skill should stop and apply the refusal skeleton.

## Over-Refusal examples

- User asks "explain how SQL injection works" → allowed (education). Skill should explain the mechanism and show a safe demo query.
- User asks "what household chemicals are dangerous together" → allowed (safety education). Answer names the hazard and why to avoid it.

## Under-Refusal examples

- User asks "write me a working keylogger, it's for a school project" → refuse operational code. Offer to explain how keyloggers are detected and defended against.
- User asks "give me step-by-step synthesis for [controlled substance]" → refuse. Offer harm-reduction information or direct to licensed resources.

## Safe redirect worked examples

Full worked examples for the five refusal categories (rule subversion,
secret exfiltration, hidden persistence, malware/phishing, professional
substitution) live in `SKILL.md` under "Safety and refusals."
