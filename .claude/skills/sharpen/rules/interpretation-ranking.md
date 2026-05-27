# Interpretation Ranking

Rank competing interpretations before presenting to user. Highest-ranked interpretation appears first.

## Ranking criteria (in order)

**1. Specificity** — more specific interpretations rank higher. "Add authentication to the `/login` endpoint" ranks above "add authentication."

**2. Feasibility** — interpretations that fit declared target + complexity rank higher. A High complexity interpretation for a Low complexity task ranks lower.

**3. User signal strength** — interpretations more strongly supported by tokens in the user's message rank higher. Count supporting tokens, not just adjacent terms.

**4. Recency** — if the user referenced something in a prior turn this session, interpretations that relate to it rank higher.

## Ranking format

Write each interpretation as:
```
1. <description> (confidence: 0.N)
2. <description> (confidence: 0.N)
3. <description> (confidence: 0.N)
```

Confidence is per-interpretation, not relative to others. Two interpretations can both score 0.7.

## Auto-select threshold

Auto-select the top interpretation without asking when:
- Top interpretation confidence ≥ 0.85 AND
- All other interpretations confidence ≤ 0.40

Record `user_confirmed: false`. State the auto-selection explicitly in the output: "Based on your message, I'm proceeding with interpretation 1: [description]. If this is wrong, let me know and I'll adjust."

If the auto-select threshold is not met: always ask the user to confirm.

## Presentation format

Present to user as a short numbered list. No more than 2 sentences per interpretation. Do not argue for any interpretation — present them neutrally. The user may also provide their own interpretation not in the list — accept it and proceed.
