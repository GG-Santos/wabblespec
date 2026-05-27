# Cold-Start Behavior — Plan

Defines what Plan does when its Propose output, recipe, or Adversary budget are absent.

## Absent: Propose recommendation

Condition: Plan invoked but no Propose receipt or recommendation exists.
Detection: Propose receipt absent or Propose produced no recommendation (all options at equal weight).
Action: Surface: "Plan requires a Propose recommendation. Run Propose first. If Propose produced a tie, invoke Brainstorm to resolve it before Plan."
Do NOT: Begin planning without a declared approach to stress-test.

## Absent: recipe.json

Condition: Plan invoked but no recipe.json found.
Detection: File read returns 404.
Action: BLOCK Plan. Surface: "Plan requires recipe.json. Recipe must run before Plan to establish target and complexity."
Do NOT: Infer complexity or target from the user message alone.

## Absent: Adversary (budget gate not yet evaluated)

Condition: Plan is about to complete but has not checked whether Adversary should run.
Detection: Adversary budget gate not evaluated.
Action: Evaluate budget gate before issuing go/no-go. Adversary is mandatory when: complexity = High OR task touches security/infrastructure/irreversible scope.
Do NOT: Issue go/no-go without Adversary when gate conditions are met.

## Absent: escalation-triggers.md

Condition: `rules/escalation-triggers.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md escalation rules. Log: "escalation-triggers.md missing — using SKILL.md defaults."

## Absent: expert-roles.md

Condition: `rules/expert-roles.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md expert perspective set. Log: "expert-roles.md missing — using SKILL.md defaults."

## Absent: plan-completeness.md

Condition: `rules/plan-completeness.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md completeness criteria. Log: "plan-completeness.md missing — using SKILL.md defaults."

## Default state on cold start

| Field | Default |
|---|---|
| `propose_input` | Required — Plan blocks without it |
| `complexity` | From recipe.json — not inferred |
| `adversary_required` | Evaluated per gate: true if complexity=High or security/infra/irreversible scope |
| `go_no_go` | Not issued until expert perspectives + Adversary (if required) complete |
| `plan_artifact_path` | `.wabblespec/plan-<timestamp>.md` |
