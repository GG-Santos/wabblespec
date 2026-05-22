# Module Plan — Polish (L6)

**Tier:** 3 — SUPPORTING
**Layer:** L6 Expression
**v5.3 origin:** Polish module — refinement pass on generated output before delivery

---

## Purpose

Refinement pass on generated artifacts before delivery. Improves clarity, removes redundancy, enforces Homowabian register consistency, catches spec violations in prose. Does not change semantics — only surface quality. Runs after Executor and before Verifier's final pass, or on explicit command.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/polish <artifact>` command
- Verifier routes artifact to Polish when quality dimension fails (prose clarity, register inconsistency)
- Delivery gate triggers Polish pass on documentation artifacts before ship
- Homowabian ultra mode: Polish skipped (ultra output is already stripped)

Polish never runs on:
- Code files (Apply owns code, Polish cannot touch `project/repo/` code)
- Schema files or JSON artifacts (no prose)
- Receipts (operational artifacts — immutable after write)

---

## Polish Passes

Polish runs sequentially — each pass has a distinct scope:

### Pass 1: Register enforcement

Read active Homowabian register from meta.md. For each prose block:
- Normal register required? Check: security warnings, irreversible action context, Attestation content — enforce normal if any detected
- Full register: verify headers and tables present for structured content, fragments not used in explanatory paragraphs
- Lite register: verify no multi-paragraph prose, no trailing summaries
- Flag register violations — do not silently override

### Pass 2: Redundancy removal

Detect and remove:
- Repeated explanations of the same concept in the same artifact
- Trailing summaries that restate what was just said
- Filler phrases (exact patterns from Economy hedge list)
- Section headers with no content below them

Do not remove:
- Repetition that serves clarity (step numbers, prerequisites repeated before a destructive action)
- Intentional emphasis (bold on key terms)

### Pass 3: Structural consistency

- Table formatting: verify alignment, no empty cells without explicit N/A
- Code block labeling: language identifier present on all code blocks
- Heading hierarchy: H1 only once, H2/H3/H4 sequential — no skipped levels
- Link validity: internal links checked (file path existence), external links flagged for human review

### Pass 4: Spec compliance check (prose)

- Verify: no claims made in prose that contradict spec artifacts
- Verify: entity names match canonical names from EntityGraph
- Verify: no deprecated term usage (from Specify's non-goals or anti-patterns lists)
- Flag violations — do not silently correct

---

## Outputs

| Output | Location | Purpose |
|---|---|---|
| Polished artifact | Overwrites source artifact in place | Refined output |
| Polish diff | `.wabblespec/receipts/polish-diff-<timestamp>.md` | Change record (what was changed, why) |
| Polish receipt | `.wabblespec/receipts/polish-receipt.md` | I10 compliance |

Polish diff is mandatory — all changes recorded with pass type and reason. Never silently overwrites without a diff record.

---

## Workflow

```
1. Receive artifact path and scope (full 4-pass vs. specific pass declared)

2. Read artifact

3. Check: is artifact in excluded category (code, schema, receipt)?
   -> IF yes: abort, return error SPEC_VIOLATION

4. Read active Homowabian register from meta.md

5. Run declared passes in sequence:
   -> Pass 1: Register enforcement
   -> Pass 2: Redundancy removal
   -> Pass 3: Structural consistency
   -> Pass 4: Spec compliance check

6. Write polished artifact (overwrite in place)

7. Write polish diff

8. Write Polish receipt
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation, excluded file types |
| `rules/excluded-types.md` | Rules | What Polish cannot touch |
| `rules/pass-sequence.md` | Rules | Pass order, scope per pass |
| `rules/diff-policy.md` | Rules | Diff required, format |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Homowabian | Polish reads active register from meta.md (Homowabian owns register state) |
| Verifier | Verifier routes artifacts to Polish when quality dimension fails |
| Document | Document output is Polish's primary input for pre-delivery passes |
| Economy | Polish applies Economy hedge patterns in Pass 2 redundancy removal |
| Specify | Polish reads spec for canonical entity names in Pass 4 |
| EntityGraph | Polish queries EntityGraph for canonical name verification |

---

## Verification Mode

**Observation** — all four passes completed (or declared subset), polish diff written, no excluded types modified, receipt written.

---

## Receipt Extension Fields

```json
{
  "artifact_path": "string",
  "passes_run": ["integer"],
  "register_violations_fixed": "integer",
  "redundancies_removed": "integer",
  "structural_issues_fixed": "integer",
  "spec_violations_flagged": "integer",
  "diff_path": "string"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Polish on Memory drawers | In scope (drawers are prose) vs. excluded (Memory owns its content) | Per-module planning |
| Auto-polish on Document output | Polish auto-runs after Document vs. explicit trigger only | Implementation |
| Pass 4 severity | Flag only vs. block Delivery on spec violation in prose | Implementation |
