# Usability Testing

## Test Scenarios

Task-based scenarios — not feature walkthroughs. Users perform real tasks.

Good format:
> "You want to change the email address associated with your account. Please do that."

Not:
> "Find the Account Settings page and click on Email."

Scenarios derived from declared critical user journeys (Design gateway). Every critical user journey has a corresponding usability test scenario.

## Facilitator Guide

- Neutral phrasing — no leading questions
- Think-aloud protocol: participants narrate their thought process
- Probe questions prepared: "What were you expecting to happen?" / "What would you do next?"
- No coaching or hints during task — note confusion as data
- Debrief protocol: subjective experience captured after tasks complete

## Metrics

| Metric | Measurement |
|---|---|
| Task completion rate | Binary (completed / not completed) per task per participant |
| Time on task | Seconds from task start to completion or abandonment |
| Error rate | Count of errors (wrong paths, backtracking, incorrect inputs) per task |
| User satisfaction | Post-session rating (SUS scale or single ease-of-use item) |

Metrics aggregated across participants. Qualitative observations annotated alongside quantitative metrics.

## Remote vs. In-Person

Declared in spec with tooling declared:
- **Remote:** Screen sharing tool + recording declared (Lookback, Maze, UserTesting, or equivalent)
- **In-person:** Location, equipment, and consent process declared

Both formats produce equivalent artifacts. Remote note: distinguish participant technology friction from actual UX issues.

## Audit Gates

- [ ] Test scenarios are task-based (not feature walkthroughs)
- [ ] Every critical user journey has a corresponding test scenario
- [ ] Facilitator guide prepared with neutral phrasing
- [ ] All 4 metrics declared and measured
- [ ] Remote/in-person format declared with tooling
