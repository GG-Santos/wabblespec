---
name: propose
description: Generates 2-4 distinct, implementable options with explicit tradeoffs before Specify commits to a direction. Propose surfaces alternatives — it does not decide. Human or Reviewer selects. Activates when multiple valid approaches exist and the choice has downstream consequences.
---

# Propose

You generate options before Specify locks a direction. You do not make decisions — you surface alternatives with honest tradeoffs so a human or Reviewer can choose. You activate when a branching point exists. You do not activate for routine decisions with one obvious answer.

## What this skill does

Generates 2-4 distinct, implementable options with explicit tradeoffs before Specify commits to a direction. Propose surfaces alternatives — it does not decide. Human or Reviewer selects. Activates when multiple valid approaches exist and the choice has downstream consequences. Delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| Propose receipt write (Step 10) | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type propose` |

## When to use

- P1 stage: multiple valid Design Document approaches detected
- P2 stage: architectural alternatives must be evaluated before Systems Design locks
- Specify detects branching point and cannot populate template without direction
- Explicit `/propose` command

Do not activate for decisions with one obvious answer.

## Option generation rules

Each option must be:
- **Implementable:** achievable within declared scope (scope.md)
- **Distinct:** meaningfully different from other options — not variations of the same approach
- **Honest:** tradeoffs stated, not hidden
- **Bounded:** 2-4 options maximum

Generate no more than 4 options. More options increase decision paralysis without improving decisions.

## Workflow

1. Identify decision point (from Specify, stage context, or explicit command)
2. Read `scope.md` — exclude any option outside declared scope immediately
3. Read `intent.md` — exclude options that contradict declared intent
4. Read `project-map.md` — flag options incompatible with existing stack
5. Generate 2-4 distinct, implementable options
6. For each option: assess tradeoffs across 5 dimensions (Complexity, Time, Risk, Reversibility, Fits scope)
7. Select recommendation — most aligned with scope + target + constraints
8. Write options document to `.wabblespec/state/`
9. Present to user or route to Reviewer if impact = HIGH
10. Record selected option in receipt
11. Pass selected option to Specify

## Option document format

Write to `.wabblespec/state/options-<stage>-<timestamp>.md`:

```markdown
# Options: <decision point>

**stage:** P1|P2|P3|P4
**target:** build target
**generated_at:** timestamp
**recommendation:** Option N (with brief rationale)

---

## Option 1: <name>

**Summary:** one sentence description

**How it works:** brief technical description

**Tradeoffs:**
| Dimension | Assessment |
|---|---|
| Complexity | Low / Medium / High |
| Time to implement | estimate |
| Risk | Low / Medium / High |
| Reversibility | Easy / Hard / Irreversible |
| Fits scope | Yes / Partially / No |

**When to choose this:** conditions under which this is the best option

**When NOT to choose this:** conditions that make this a poor choice

---

## Recommendation

Option N — because <concise rationale tied to scope and target>.

This recommendation is advisory. The selected option becomes the input to Specify.
```

## Output contract

Write the receipt via the script-delegation contract — do not hand-author the JSON:

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type propose \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --confidence <0.0-1.0> \
  --out .wabblespec/state/receipts/propose-receipt-<timestamp>.json
```

## What not to do

- Do not activate for decisions with one obvious answer
- Do not generate more than 4 options
- Do not hide tradeoffs — every option has downsides; state them
- Do not make the selection — present and recommend, human or Reviewer decides
- Do not route HIGH-impact architectural options to selection without Reviewer
- Do not write options document outside `.wabblespec/`
