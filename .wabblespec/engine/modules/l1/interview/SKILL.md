---
name: interview
description: Resolves ambiguity before spec work begins. Nine ambiguity dimensions covered via Socratic questioning — no leading questions, max 3 per batch, stops when ambiguity resolved. Reads product-context.md open questions before generating its own. Produces intent.md with confirmed answers.
---

# Interview

You resolve ambiguity before Specify begins. You ask the minimum questions needed to remove ambiguity — not to be thorough.

## What this skill does

Resolves ambiguity before spec work begins. Nine ambiguity dimensions covered via Socratic questioning — no leading questions, max 3 per batch, stops when ambiguity resolved. Reads product-context.md open questions before generating its own. Produces intent.md with confirmed answers.

## When to use

- Research phase before P1 spec work when ambiguity exists
- Recipe confidence < 0.8 (build target unconfirmed)
- Triage routes a Question issue type
- Explicit `/interview` command

## Socratic rules

- No leading questions ("Is this a REST API?" → wrong. "What type of interface does this expose?" → right)
- Max 3 questions per batch — wait for answers before next batch
- Stop when ambiguity resolved — do not exhaust all dimensions if not needed
- No re-asking answered questions

## Nine ambiguity dimensions

See `rules/ambiguity-dimensions.md` for full definitions. Cover only dimensions where ambiguity exists:

1. Intent — what outcome the user wants
2. Context — what exists today (codebase, users, constraints)
3. Constraints — hard limits (budget, timeline, tech, compliance)
4. Scope — what is in and out of this task
5. Success criteria — how to know when done
6. Failure modes — what must not happen
7. Stakeholders — who is affected or must approve
8. Timeline — when it must be done
9. Risk tolerance — acceptable vs. unacceptable risk

## Process

1. Read `product-context.md` Open Questions section — cover those first
2. Read Recipe output — if confidence < 0.8, build target confirmation is first question
3. Identify which of 9 dimensions have unresolved ambiguity
4. Ask up to 3 questions covering highest-priority ambiguities
5. Record answers, reassess remaining ambiguity
6. Repeat until resolved or human stops session

## Reference Routing

| Situation | Reference |
|---|---|
| Interview receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Outputs

Write `.wabblespec/state/plans/intent.md`:

```markdown
# Intent

**Session:** ISO 8601
**Resolved dimensions:** [list]
**Unresolved:** [list — carry forward to Interview next session]

## Confirmed Answers

### <Dimension>
**Question:** string
**Answer:** string
**Confidence:** 0.0-1.0
```

## What not to do

- Do not ask more than 3 questions at once
- Do not ask leading questions
- Do not skip reading product-context.md open questions
- Do not continue once ambiguity is resolved
