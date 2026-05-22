---
name: template-skill
description: Replace with description of the skill and when the agent should use it.
---

# Insert Instructions Below

Use this as the standard skill template. Every specialty skill template is an
overlay on this upstream-compatible shape, not a replacement.

## Domain Operating Model

State what work this skill owns, what signals activate it, and what assumptions
the agent should label.

## Request Triage

Name ambiguity, safety, source, and format checks that change the response.

## Workflow

List the concrete steps the agent should follow.

## Output Contract

Specify the exact output shape and include one compact worked example.

## Output Quality Contract

Name good output, bad output, and the discriminator that separates them.

## Examples And Edge Cases

Include normal, ambiguous, and adversarial/impossible cases.

## Failure Modes

Name the mistakes this skill prevents and how to recover.
