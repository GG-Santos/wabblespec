# Ambiguity Dimensions

Nine dimensions. Cover only those with unresolved ambiguity.

| # | Dimension | What to resolve | Example question |
|---|---|---|---|
| 1 | Intent | What outcome the user wants (not what to build) | "What improves for your users when this is done?" |
| 2 | Context | What exists today — codebase, users, existing constraints | "What does the current system do that this replaces or extends?" |
| 3 | Constraints | Hard limits: budget, timeline, tech stack, compliance | "Are there technologies or approaches that are off the table?" |
| 4 | Scope | What is explicitly in and out of this task | "What is the smallest version of this that would be useful?" |
| 5 | Success criteria | How to know when done | "How will you verify this is working correctly?" |
| 6 | Failure modes | What must not happen | "What outcome would make this a failure even if it technically works?" |
| 7 | Stakeholders | Who is affected or must approve | "Who else needs to sign off before this ships?" |
| 8 | Timeline | When it must be done | "Is there a date this must be done by, or is timeline flexible?" |
| 9 | Risk tolerance | Acceptable vs. unacceptable risk | "Is it acceptable to ship with known limitations if they're documented?" |

## Priority order for questions

When ambiguity exists across multiple dimensions, ask in this priority:
1. Scope (I12 — prevents unbounded execution)
2. Intent (grounds everything downstream)
3. Constraints (hard limits before spec is written)
4. Success criteria (verification needs this)
5. Failure modes (Guard uses this for scope validation)
6. Context, Stakeholders, Timeline, Risk — lower priority, cover if time permits
