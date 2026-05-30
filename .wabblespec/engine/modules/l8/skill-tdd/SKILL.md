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

### Step 5 -- Report

Output:
1. Baseline pass rate
2. Compliance pass rate
3. Delta
4. Verdict (READY / BLOCKED)
5. Loopholes found (scenarios where skill was present but not followed)

Write a benchmark receipt with `pressure_test_mode: skill-tdd` if the verdict is READY.

## Pitfalls

- Pressure scenarios must be adversarial -- if they are too easy, the baseline will also pass and delta will be near zero
- Subagent context must be clean between runs; do not reuse the same Agent call
- A READY verdict only means the skill closes the identified loopholes -- it does not guarantee completeness against novel scenarios
- Threshold of 80% is a minimum bar, not a target -- 95%+ is the goal for enforcement-class skills
