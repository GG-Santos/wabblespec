# Wave Plan: wave-checkpoint-v1

**Session ID:** wave-checkpoint-v1
**Created:** 2026-05-26
**Waves:** 2
**Complexity:** Medium

---

## Research Summary

Prior-session audit confirmed that the core checkpoint implementation already exists across
SKILL.md files, the schema, and acceptance tests. The only remaining gap is a path mismatch
in the Executor authority list (`.wabblespec/checkpoints/*` vs
`.wabblespec/session/checkpoints/*`) and a missing `produces_schemas` entry in framework.yaml.

Verified via `guard-check.py authority --module executor --files
".wabblespec/session/checkpoints/checkpoint-wave-1.json" --json` → FAIL,
`unauthorized_files: [".wabblespec/session/checkpoints/checkpoint-wave-1.json"]`.

---

## Wave 1 — Fix executor authority.owns and produces_schemas

**Files:** `modules/l2/executor/skill-rules.json`

**Steps:**

1. Add `.wabblespec/session/checkpoints/*` to `authority.owns` array.
2. Add `_shared/schemas/wave-checkpoint.schema.json` to `produces_schemas` array
   (field does not exist yet in skill-rules.json; create it).

**Verification:** Run `guard-check.py authority --module executor --files
".wabblespec/session/checkpoints/checkpoint-wave-1.json" --json` → expect PASS.

**Acceptance criteria covered:** AC-7 (Executor authority covers checkpoint path)

---

## Wave 2 — Update framework.yaml executor produces_schemas

**Files:** `framework.yaml`

**Steps:**

1. In the executor module entry (`modules/l2/executor/`), update `produces_schemas`
   from `[shared/schemas/receipt.base.schema.json]` to
   `[shared/schemas/receipt.base.schema.json, _shared/schemas/wave-checkpoint.schema.json]`.

**Verification:** `grep produces_schemas framework.yaml | grep wave-checkpoint` returns match.

**Acceptance criteria covered:** AC-1 (schema referenced in executor module registry),
AC-7 (schema authority declared)

---

## Non-wave items (already implemented — no action required)

The following task card deliverables were confirmed present in prior sessions:

| File | Status |
|---|---|
| `_shared/schemas/wave-checkpoint.schema.json` | EXISTS — all required fields present |
| `modules/l2/executor/SKILL.md` Step 5b | EXISTS — checkpoint write spec complete |
| `modules/l2/executor/tests/acceptance.md` | EXISTS — "Session checkpoint written after each wave" |
| `modules/l2/guard/SKILL.md` Layer 1 | EXISTS — checkpoint detection written |
| `modules/l2/guard/tests/acceptance.md` | EXISTS — "Layer 1 — Checkpoint detection on Wave 1" |
| `modules/l0/recipe/SKILL.md` Step 1b | EXISTS — checkpoint surface logic present |
| `framework.yaml` schema consumers list | EXISTS — wave-checkpoint.schema.json registered |
