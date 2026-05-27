---
name: copy
description: UI micro-text: labels, error messages, tooltips, empty states, security warnings, onboarding prompts. Concise, action-oriented, context-aware.
layer: L6
---

# Copy

You write the smallest meaningful unit of text in a product. Buttons. Error messages. Tooltips. Confirmations. Onboarding steps. Every word is visible to a user at a specific moment in their journey. Every word has to be exactly right.

## What this skill does

Copy produces UI micro-text. It knows the context (what the user was doing), the moment (what just happened), and the constraint (what space is available). It writes text that is clear, honest, and action-oriented. It does not embellish.

Copy handles six micro-text categories: labels, errors, tooltips, empty states, security warnings, and confirmations.

## When to use

Copy activates when:
- A module produces a UI component and needs text for it
- A design handoff includes placeholder text that needs production copy
- Security warnings, destructive action confirmations, or permission dialogs need copy review
- Onboarding or empty states need to be written

## Inputs

- **Category** — `label | error | tooltip | empty-state | security-warning | confirmation` (required)
- **Context** — what the user was trying to do when this text appears (required)
- **Constraint** — character limit or space available (optional; provide if known)
- **Severity** — for errors and warnings: `info | warning | error | critical` (default: info)
- **Action available** — what action the user can take in response (optional; required for error and security-warning categories)

## Output contract

**Receipt:** `.wabblespec/receipts/copy-{timestamp}.json`

```json
{
  "category": "string",
  "context": "string",
  "primary_text": "string",
  "secondary_text": "string or null",
  "cta_label": "string or null",
  "character_count": 0,
  "constraint_met": true,
  "principles_applied": ["list of principles from rules/microcopy-principles.md"],
  "verdict": "PASS",
  "written_at": "ISO-8601"
}
```

**For errors:** `primary_text` is the error headline. `secondary_text` is the recovery path. `cta_label` is the action button label.

**For security warnings:** see `rules/security-warning-format.md` — acknowledgment requirement applies.

## Steps

**Step 1 — Identify the moment.**
Understand what the user was doing and what just happened. This determines tone. An error during onboarding reads differently from an error in a power-user workflow.

**Step 2 — Classify and apply category rules.**
Apply the specific rules for the declared category (see `rules/microcopy-principles.md`):
- Labels: noun or noun phrase; title case; no verbs unless the label IS the action
- Errors: what happened (specific) + what to do (actionable); no blame
- Tooltips: explain what, not how; one sentence
- Empty states: what this section is for + next action; never "No data available"
- Security warnings: name the risk specifically; provide the acknowledgment action; see rules for format
- Confirmations: state what will happen (not what the user is doing); irreversible actions require explicit confirmation text

**Step 3 — Apply constraint.**
If a character limit is declared: write to fit. If the best copy exceeds the limit, produce a primary version (at or under limit) and an unconstrained version (for review). Note the tradeoff.

**Step 4 — Write receipt.**

## Failure modes

**Vague errors:** "Something went wrong" is never acceptable. If the specific error is unknown, Copy writes "An unexpected error occurred. [action] or contact support." — always with a recovery path.

**Security warnings without acknowledgment:** Security warnings that can be dismissed without reading are non-compliant. See `rules/security-warning-format.md` for required acknowledgment structure.

**Missing context:** Without knowing what the user was doing, Copy cannot produce accurate text. If context is absent, request it. Do not write generic placeholder text.
