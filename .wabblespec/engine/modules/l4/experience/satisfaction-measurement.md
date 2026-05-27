# Satisfaction Measurement

## SUS (System Usability Scale)

Optional baseline metric for major releases. 10-item questionnaire, 5-point Likert scale, produces 0–100 score.

Benchmarks:
- > 80: Excellent (A grade)
- 68–80: Good (B–C grade)
- 51–68: Poor (D grade)
- < 51: Unacceptable (F grade)

Declared in scope or out of scope at P1. If customer satisfaction is a stated success metric, SUS provides a standardized baseline.

## NPS (Net Promoter Score)

Optional for long-running products with recurring users. Single question: "How likely are you to recommend [product] to a colleague? (0–10)". Promoters (9–10), Passives (7–8), Detractors (0–6).

Not useful for products with < 100 active users per measurement period — sample size too small for statistical stability. Declared when in scope with measurement cadence.

## In-Product Feedback

Declared when continuous measurement is in scope:
- Micro-survey at key moments (after task completion, after error)
- Feedback widget (thumbs up/down, star rating, free text)
- Session replay sampling declared (with user consent)

Mechanism declared at P1. Data retention and anonymization declared alongside.

## Audit Gates

- [ ] SUS declared in scope or out of scope at P1
- [ ] NPS declared only when >= 100 active users per measurement period
- [ ] In-product feedback mechanism declared when continuous measurement in scope
- [ ] Data retention and anonymization declared for all satisfaction data
