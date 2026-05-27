# Task Card — {{task_id}}

**Created:** {{created_at}}
**Module:** {{triggering_module}}
**Complexity:** {{complexity_tier}}  <!-- L1 | L2 | L3 | L4 | L5 -->
**Status:** {{status}}  <!-- draft | active | complete | blocked -->

---

## Goal

{{goal_statement}}

One sentence. What is done when this task is done.

## Scope

**In scope:**
- {{in_scope_item_1}}

**Out of scope:**
- {{out_of_scope_item_1}}

## Inputs

| Input | Source | Required? |
|---|---|---|
| {{input_name}} | {{source}} | Yes / No |

## Acceptance criteria

Written in EARS syntax. Each criterion is independently verifiable.

- WHEN {{trigger}}, THE SYSTEM SHALL {{behavior}}.
- IF {{condition}}, THEN {{behavior}}.
- THE SYSTEM SHALL {{behavior}} WHILE {{state}}.

## Wave plan

| Wave | Goal | Modules | Acceptance criteria covered |
|---|---|---|---|
| Wave 1 | {{wave_goal}} | {{modules}} | {{criteria_ids}} |

## Constraints

- {{constraint_1}}

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| {{risk}} | Low/Med/High | Low/Med/High | {{mitigation}} |

## Receipt references

<!-- Populated by modules as they complete -->
- {{module}}: `{{receipt_path}}`
