# Adversarial Spec Mode

Activated when: `delta_class = BREAKING` AND the task's tags intersect `adversarial_required_for_tags` from `framework.yaml` (current list: `security`, `enforcement`, `receipt`, `gate`).

Source pattern: `adversarial-spec-main/skills/adversarial-spec/SKILL.md` — adversarial consensus pattern.
What was not taken: multi-model provider panel, Telegram integration, session persistence, cost tracking, AWS Bedrock.

---

## When this mode fires

Specify detects the gate condition (see `modules/l1/specify/SKILL.md` Step 3.6) and passes a `adversarial_spec_mode: true` flag when invoking Reviewer. Normal Reviewer budget gate checks still apply — this mode is additive, not a bypass.

If the gate condition is not met, this mode does not activate. Normal Reviewer flow applies.

---

## What changes from normal Reviewer flow

| Normal Reviewer | Adversarial Spec Mode |
|---|---|
| Adversary receives output only | Adversary receives task card + spec-specific critique checklist |
| Adversary produces weaknesses, alternatives, assumptions, failure scenarios | Same + must identify at least 3 distinct objections before agreeing |
| Grader decides alone | Grader ACCEPT requires zero remaining HIGH/CRITICAL objections from Adversary |
| REVISE guidance is specific | REVISE guidance must map to a named criterion from the critique checklist |
| Max 3 REVISE cycles | Same — still hard limit |

---

## Spec-specific critique checklist

Adversary evaluates the task card against all of the following. Each failure is a distinct objection.

### Goal quality
- [ ] Goal is one sentence. If it contains "and," it is two goals — flag as CRITICAL.
- [ ] Goal is falsifiable: can be confirmed true or false by observable evidence. "Improve X" fails this. Flag as HIGH.
- [ ] Goal names the actor, action, and outcome. Vague verbs ("handle," "support," "manage") without specifics — flag as MEDIUM.

### Acceptance criteria
- [ ] Every "Then" clause is observable: readable in output, checkable via test, or verifiable by state inspection. "Then the system is secure" fails. Flag as HIGH.
- [ ] At least one failure-path criterion exists. Happy-path-only criteria are incomplete for HIGH complexity tasks. Flag as HIGH.
- [ ] No criterion duplicates another. Duplicate criteria dilute coverage signal. Flag as LOW.
- [ ] Criteria are independent: each tests exactly one thing. Compound criteria ("Then A and B occur") — flag as MEDIUM.
- [ ] Normative language: SHALL or MUST, not "should" or "may." Flag as MEDIUM.

### Security and enforcement (required for security/enforcement/receipt/gate tags)
- [ ] Security threats named specifically (e.g., "injection via untrusted input", "token replay"). "Security considered" is insufficient. Flag as CRITICAL.
- [ ] Enforcement boundaries stated: what can be bypassed and what cannot. Flag as HIGH.
- [ ] Receipt or gate failure modes covered: what happens when a required receipt is absent. Flag as HIGH.

### Non-goals and assumptions
- [ ] At least one non-goal is explicit. Absence of non-goals = unbounded scope. Flag as HIGH.
- [ ] Each assumption names what happens if the assumption is wrong. "Assumes X" without consequence — flag as MEDIUM.

### BREAKING-specific (required when delta_class = BREAKING)
- [ ] `change_summary` identifies every changed interface by name. Vague "some APIs change" — flag as HIGH.
- [ ] `affected_specs` lists every downstream artifact that must be updated. Flag as HIGH.
- [ ] A migration path or deprecation timeline exists or is explicitly deferred with justification. Flag as MEDIUM.

---

## Anti-laziness rule

Adversary MUST identify at least 3 distinct objections from the checklist before being allowed to produce a clean agreement.

If Adversary's first-pass response is "the spec looks complete" with fewer than 3 named checklist failures, treat as premature agreement. Reviewer re-runs Adversary with explicit instruction: "Review EACH criterion in the adversarial-spec-mode checklist. Name which you checked and what you found. Do not agree until you have reviewed all sections."

This is not optional. Adversarial review that converges in round 1 without evidence of checklist coverage provides no quality signal.

---

## Convergence condition

ACCEPT is only valid when BOTH of the following are true:

1. Adversary has zero remaining objections rated HIGH or CRITICAL (MEDIUM and LOW objections may remain if revision guidance addresses them in the next execution wave)
2. Grader confirms the task card satisfies all checklist items relevant to the active tags

If Adversary has HIGH/CRITICAL objections at REVISE cycle 3, force ESCALATE regardless of Grader verdict. Add to escalation reason: "Adversarial spec review could not resolve HIGH/CRITICAL objections in 3 cycles."

---

## Output additions to gate receipt

When adversarial spec mode was active, add to the reviewer receipt:

```json
{
  "adversarial_spec_mode": true,
  "spec_critique_rounds": "integer — adversary rounds in this mode",
  "checklist_failures": [
    {
      "criterion": "string — which checklist item failed",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "resolved": "boolean"
    }
  ],
  "premature_agreement_detected": "boolean",
  "convergence_condition_met": "boolean"
}
```

---

## What adversarial-spec does that this mode does NOT do

- **Multi-model provider panel**: the reference calls GPT, Gemini, Grok, etc. in parallel. This mode uses WabbleSpec's existing Adversary + Grader agent pair — no external API keys required.
- **Preserve-intent mode**: useful when unconventional spec choices risk being homogenized. Not implemented here — add only if real cases emerge where Adversary strips deliberate design choices.
- **Focus areas and personas**: the reference supports `--focus security` and `--persona security-engineer`. These are useful but complex. Add only when the base checklist proves insufficient for a real spec failure.
