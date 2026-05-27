---
name: quality-floor-gates
description: Defines the two required gates (quick_validate, lint_prompts) that every built WabbleSpec module must pass to set quality_floor_passed=true in framework.yaml. Consumed by scripts/quality-floor-check.py.
---

# Quality Floor Gates

`framework.yaml` declares:
```yaml
quality_floor:
  min_pattern_score: 4.0
  required_gates: [quick_validate, lint_prompts]
  adversarial_required_for_tags: [security, enforcement, receipt, gate]
```

Both gates must pass for a module to set `quality_floor_passed: true`.

---

## Gate 1: quick_validate

Structural checks. All must pass.

| Check | Rule |
|---|---|
| SKILL_EXISTS | `SKILL.md` present in module directory |
| RULES_EXISTS | `skill-rules.json` present in module directory |
| RULES_PARSE | `skill-rules.json` is valid JSON |
| REQUIRED_FIELDS | `module`, `layer`, `tier`, `activators`, `authority`, `verification_mode`, `receipt_required` all present |
| AUTHORITY_OWNS | `authority.owns` present and non-empty list |
| AUTHORITY_READS | `authority.reads` present (may be empty list for read-nothing modules) |
| RECEIPT_BOOL | `receipt_required` is boolean |
| ACTIVATORS_VALID | `activators` is non-empty list OR `loading_gate` is `"phase"` OR `commands` is non-empty (command-invoked modules) |

All 8 checks must pass. One FAIL = module does not pass quick_validate.

---

## Gate 2: lint_prompts

Content checks. All must pass.

| Check | Rule |
|---|---|
| FRONTMATTER | SKILL.md begins with `---` block containing `name:` and `description:` |
| DESCRIPTION_LEN | `description:` value in frontmatter is >= 20 characters |
| SECTION_WHAT | SKILL.md contains `## What this skill does` heading |
| SECTION_WHEN | SKILL.md contains `## When to use` heading (partial match sufficient) |
| SECTION_OUTPUT | SKILL.md contains at least one of: `## Output contract`, `## Outputs`, `receipt**`, `**receipt` |
| MIN_LENGTH | SKILL.md body (excluding frontmatter) is >= 200 characters |

All 6 checks must pass. One FAIL = module does not pass lint_prompts.

---

## Adversarial Requirement

If `skill-rules.json` tags include any of `[security, enforcement, receipt, gate]`, then SKILL.md must contain the word `adversarial` (case-insensitive). Failure is reported as a WARNING (not a gate FAIL) to avoid blocking modules that are secure by design without explicit adversarial passes documented.

---

## Scoring

`min_pattern_score: 4.0` maps to: quick_validate (2 points) + lint_prompts (2 points) = 4.0 maximum. A module passing both gates scores 4.0. Partial scores are not tracked — it is binary pass/fail per gate.

---

## Setting quality_floor_passed

`scripts/quality-floor-check.py --update-yaml` reads all modules, runs both gates, and prints a list of module IDs that now pass. A human manually updates `framework.yaml` or runs `--write` to patch it automatically.

Automatic writes are opt-in to avoid unreviewed framework.yaml changes.

---

## Pattern Quality (above the floor)

Passing both gates is the floor, not the ceiling. Pattern quality — whether
the SKILL.md produces good invocation output — is scored separately by
`.wabblespec/engine/shared/agents/module-auditor.md` using the six patterns and seven
regression checks defined in `.wabblespec/engine/shared/references/skill-writing-contract.md`.

A module can pass Gate 1 and Gate 2 but still score below 4.0 on Pattern 3
(named failure modes). The gates and the pattern score are independent
signals. Run the module auditor before marking `build_complete: true`.
