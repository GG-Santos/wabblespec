# Verifier — Pre-Emit Self-Critique

Runs immediately before writing any verification receipt. Not optional. Not abbreviated under time pressure.

## When this runs

After Step 2 (mode-specific check) returns a candidate verdict, and before Step 5 (write receipt), the Verifier scores the output on six axes. Any axis scoring below 3 triggers a revision pass — the output returns to Executor with the low-scoring axis cited as the failure reason. The revision pass does not increment the REVISE cycle counter (it is a quality pass, not a correctness failure).

## Six Axes

Score each axis 1–5. 1 = clear failure. 3 = acceptable floor. 5 = exemplary.

### IC — Invariant-compliance

**Question:** Does every claim and artifact in the output trace to a locked spec artifact? Is implied completion absent?

| Score | Meaning |
|---|---|
| 5 | Every output is grounded in the task card; every claim cites a "Then" clause or acceptance criterion |
| 4 | One minor untraced claim; no implied completion |
| 3 | All major outputs traced; minor speculative additions present but labeled |
| 2 | One untraced major claim or one instance of implied completion |
| 1 | Multiple untraced claims; implied completion present; output exceeds spec scope |

### RC — Receipt-completeness

**Question:** Are all required receipts for the current phase present, structurally valid, and populated with evidence (not empty arrays)?

| Score | Meaning |
|---|---|
| 5 | All receipts present; all evidence fields populated; evidence is capturable artifact, not assertion |
| 4 | All receipts present; one evidence field sparse but not empty |
| 3 | All receipts present; evidence thin but present |
| 2 | One receipt missing or structurally invalid |
| 1 | Multiple receipts missing; evidence arrays empty; PARTIAL receipt submitted as PASS |

### EF — Execution-fidelity

**Question:** Does the output match the spec exactly, or were silent deviations made? Did any "simplification" change the intended behavior?

| Score | Meaning |
|---|---|
| 5 | Output matches spec exactly; every deviation documented in a deviation receipt |
| 4 | One silent deviation; minor and reversible |
| 3 | Output substantially matches spec; deviations present but explainable |
| 2 | A declared behavior is missing or modified without documentation |
| 1 | Multiple silent deviations; spec and output are materially different |

### SS — Spec-specificity

**Question:** Does this output look like it was produced for this specific task and project, or could it be a generic response to any similar request?

| Score | Meaning |
|---|---|
| 5 | Output is unmistakably for this project — references specific names, paths, decisions, and constraints from the task card |
| 4 | Output references the task; some generic phrasing present but grounded |
| 3 | Output is correct but could apply to a different project with minimal changes |
| 2 | Output is largely generic; project-specific facts are incidental |
| 1 | Output is a template response; no project-specific grounding |

### SR — Scope-restraint

**Question:** Was everything outside the declared scope removed? No added abstractions, helper utilities, documentation, or future-proofing beyond what the spec required?

| Score | Meaning |
|---|---|
| 5 | Output contains exactly what was specified; nothing extra |
| 4 | One minor addition; not harmful; clearly explained |
| 3 | Small additions present; defensible as adjacencies |
| 2 | Noticeable scope creep; features or abstractions added without spec grounding |
| 1 | Significant additions beyond scope; output is larger than the spec requested |

### OV — Output-variety

**Question:** Does the structural approach of this output differ meaningfully from the last 3 outputs produced in this project? Or does it repeat the same structural pattern regardless of the content?

| Score | Meaning |
|---|---|
| 5 | Structure chosen deliberately for this content; clearly different from prior outputs in this project |
| 4 | Minor structural overlap with prior output; different enough to be intentional |
| 3 | Acceptable; some overlap but the content required this structure |
| 2 | This output uses the same structure as the immediately prior output with different content filled in |
| 1 | Output is structurally identical to multiple prior outputs; template-filling, not deliberate composition |

## Revision trigger

Any axis scoring 1 or 2 triggers a revision pass before the receipt is written. The revision pass cites the low-scoring axis and the specific failure reason — it does not merely say "revise the output." The Executor addresses the cited failure and the critique re-runs.

A receipt cannot be written while any axis is below 3.

## Stamp format

The first non-empty comment in any non-trivial output artifact carries the critique stamp:

```
/* WS · self-critique: IC5 RC5 EF5 SS4 SR5 OV5 */
```

All six axes and their scores on a single line. This stamp is evidence that the pre-emit critique ran — not decoration. A receipt that references an artifact without this stamp in it is incomplete unless the artifact type does not admit comments (binary, JSON).

For JSON artifacts, add the stamp as a top-level field:

```json
{
  "_self_critique": "IC5 RC5 EF5 SS4 SR5 OV5",
  ...
}
```
