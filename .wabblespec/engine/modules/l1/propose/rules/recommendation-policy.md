# Recommendation Policy — Propose

## Recommendation is always required

Every options document includes a recommendation. Neutral presentation without recommendation is not permitted — it shifts the analysis burden to the human without adding value.

## Recommendation criteria

Select the option that best satisfies this priority order:

1. **Fits scope** — options rated `Partially` or `No` can only be recommended if no `Yes` option exists
2. **Risk** — prefer lower risk when complexity and time are comparable
3. **Reversibility** — prefer reversible approaches when correctness is uncertain
4. **Time to implement** — prefer faster when quality is equal
5. **Complexity** — prefer lower complexity when outcomes are equal

## Strong recommendation vs. neutral presentation

Use a **strong recommendation** (single clearly preferred option) when:
- One option dominates across 3+ dimensions
- Scope or invariant constraints eliminate alternatives
- Risk difference between options is High vs. Low

Use **neutral presentation** (recommendation with acknowledged uncertainty) when:
- Options are close across most dimensions
- The deciding factor is a human value judgment (e.g., speed vs. safety tradeoff)
- Impact = HIGH and Reviewer has not yet weighed in

## Reviewer trigger

Route to Reviewer before presenting to user when:
- Impact = HIGH (architectural decision with broad downstream consequences)
- Two options are tied and the distinction is a values question outside Propose's authority
- Any option is Irreversible

Reviewer routing does not delay writing the options document — write it first, then route.
