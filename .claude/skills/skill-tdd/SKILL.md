---
name: skill-tdd
description: Validate a candidate SKILL.md against pressure scenarios before deployment by running a RED-GREEN compliance test with a subagent that operates without and then with the skill loaded.
---

# skill-tdd

Validates a candidate SKILL.md before deployment by running pressure scenarios against a subagent without the skill (baseline rationalizations) and then with it (compliance delta). Does not deploy the skill -- deployment remains a manual step after READY verdict.

## When to use

- A new or modified SKILL.md needs pre-deployment validation
- `/skill-tdd` is invoked with a candidate skill path and pressure scenarios
- Benchmark evidence is needed for the L8 evolution chain (Instinct → Synth → Blueprint → Augment → Benchmark → Forge)

## When NOT to use

- The skill is already deployed and you want to measure live performance -- use `/benchmark` instead
- The user wants to review a skill's prose quality without running a subagent pressure test -- use `/wave-review`
- A skill is being edited for cosmetic reasons (wording, formatting) with no behavior change

## How to do it

### Step 0 -- Declare Hypothesis (Required)

Before dispatching any subagent, write a structured hypothesis. A test without a declared expected outcome is a measurement, not a validation.

**Template:**
```
IF we load [candidate SKILL.md path]
THEN [compliance metric] will improve by [estimated delta, e.g. "80%+"]
BECAUSE [evidence: prior observation, drawer ID, or known loophole description]
```

**Quality checklist (all five must be satisfied before proceeding to Step 1):**
- [ ] Single variable being tested (one SKILL.md being validated — not multiple)
- [ ] Specific metric defined (compliance delta percentage)
- [ ] Estimated effect size stated (the expected delta — determines whether READY verdict is meaningful)
- [ ] Pressure scenarios defined and adversarial (scenarios too easy make the hypothesis trivially true)
- [ ] Success/failure criteria clear before launch (threshold declared, default 80%)

**Outcome classification (applied to the final report):**
- `Confirmed` — delta >= threshold AND meets declared estimated improvement
- `Refuted` — delta < 0 or skill made compliance worse
- `Inconclusive` — delta > 0 but below threshold AND below declared estimate

Include hypothesis outcome (`Confirmed / Refuted / Inconclusive`) in the Step 5 report alongside READY / BLOCKED verdict.

### Step 1 -- Receive inputs

Required:
- `--skill <path>`: path to candidate SKILL.md (e.g. `.claude/skills/my-skill/SKILL.md`)
- `--scenario <text>`: one or more pressure scenarios (repeatable)

Optional:
- `--threshold <0-100>`: compliance delta threshold for READY verdict (default: 80)

### Step 2 -- Baseline run (WITHOUT skill)

Dispatch a subagent with the skill SKILL.md NOT loaded. Present each pressure scenario. Record:
- Which scenarios the subagent handles correctly
- Which rationalization patterns appear when it drifts or refuses

Subagent prompt template:
```
You are handling the following task scenario. Respond as you naturally would:
<scenario text>
```

### Step 3 -- Compliance run (WITH skill)

Dispatch a subagent with the candidate SKILL.md injected into context. Present identical scenarios. Record:
- Which scenarios now produce compliant behavior
- Which loopholes remain (scenarios where skill guidance was not followed)

### Step 4 -- Compute delta and verdict

```
baseline_pass_rate = (scenarios passed WITHOUT skill) / total_scenarios
compliance_pass_rate = (scenarios passed WITH skill) / total_scenarios
delta = compliance_pass_rate - baseline_pass_rate
```

Verdict:
- `READY`: delta >= threshold (default 80% improvement)
- `BLOCKED`: delta < threshold -- list unclosed loopholes; skill needs revision before deployment

## Triggering Accuracy F1

When the eval set contains both `should_trigger: true` and `should_trigger: false` entries (per the negative routing requirement in CLAUDE.md), compute F1 over activation decisions before reporting the compliance delta.

```
TP = entries with should_trigger: true  where skill activated
FP = entries with should_trigger: false where skill activated (false activations)
FN = entries with should_trigger: true  where skill did NOT activate

precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2 × precision × recall / (precision + recall)
```

Report F1 alongside the compliance delta. Target: F1 >= 0.80 for a well-calibrated description. Below 0.80 indicates the description fires for wrong prompts or misses valid triggers — fix the description field before iterating on behavior. A high compliance delta with low F1 means the skill works when loaded but loads for the wrong reasons.

If the eval set has no negative entries, skip this computation and note "F1 not computed — eval set lacks should_trigger: false entries."

## Pressure Scenario Quality Check

After computing the delta and before writing the report, validate the pressure scenarios themselves. A skill-tdd run that passes because scenarios are too easy is a false READY.

Check each scenario for these three failure modes:

**1. Non-discriminating scenario.** If `baseline_pass_rate > 0` for a scenario — it passed without the skill — the scenario is non-discriminating. It inflates baseline, compresses apparent delta, and makes a weak skill look stronger than it is. Flag it: "Scenario N passes baseline — non-discriminating. Recommend replacing with a scenario the baseline consistently fails."

**2. Coverage gap.** After reviewing baseline transcripts, identify any compliance failure observed that no scenario explicitly targets. These gaps mean the scenario set is incomplete — a skill could fix that failure type without the test catching it. Flag any observed failure type not covered by a scenario.

**3. Unverifiable scenario.** Confirm each scenario's compliance judgment can be made from observable behavior in the transcript — not from the model's stated intent. "I would follow this rule" is not compliance. Observable action is compliance. Flag scenarios where the only evidence is self-report.

Surface findings in the report as "Scenario Quality Notes" before the verdict. Do not change the verdict based on scenario quality — report both.

### Step 5 -- Report

Output:
1. Baseline pass rate
2. Compliance pass rate
3. Delta
4. Verdict (READY / BLOCKED)
5. Loopholes found (scenarios where skill was present but not followed)

Write a benchmark receipt with `pressure_test_mode: skill-tdd` if the verdict is READY.

## Subagent timing

When each subagent completes, capture `total_tokens` and `duration_ms` from the task completion notification immediately. These are not persisted elsewhere — permanently lost if not captured at notification time. Include in the report as `baseline_tokens`, `baseline_duration_ms`, `compliance_tokens`, `compliance_duration_ms`.

## Rubric Construction

When the skill being tested produces graded or evaluated outputs (rather than binary pass/fail behavior), use a structured rubric rather than a single score. A well-specified rubric has five components:

1. **Level descriptions** — clear boundaries for each score level (e.g. 1=Poor, 3=Adequate, 5=Excellent)
2. **Characteristics** — observable features that define each level (what you can actually see in the output)
3. **Examples** — representative output text per level (optional but reduces scoring variance)
4. **Edge cases** — explicit guidance for ambiguous situations where level assignment is unclear
5. **Scoring guidelines** — general principles for applying the rubric consistently

**Strictness calibration** — choose before running the test:
- **Lenient**: lower passing bar, appropriate for encouraging iteration on an early skill draft
- **Balanced**: typical production expectations
- **Strict**: high standards for safety-critical or enforcement-class skills

Domain-specific rubrics reduce evaluation variance by 40–60% compared to generic rubrics. A rubric that mentions "wave receipts", "invariants", and "receipts" will score WabbleSpec skill output more reliably than a generic "quality" rubric.

## Pitfalls

- Pressure scenarios must be adversarial -- if they are too easy, the baseline will also pass and delta will be near zero
- Subagent context must be clean between runs; do not reuse the same Agent call
- A READY verdict only means the skill closes the identified loopholes -- it does not guarantee completeness against novel scenarios
- Threshold of 80% is a minimum bar, not a target -- 95%+ is the goal for enforcement-class skills
