# Task Card: toprank-integration-phase2-T2

**Session ID:** toprank-integration-phase2-T2
**Created:** 2026-05-28
**Delta class:** ADDITIVE
**Complexity:** Medium
**Status:** LOCKED
**Task type:** framework-authoring

---

## Goal

Create `llm-eval.py` — a WabbleSpec-native skill-section quality scorer that measures clarity, completeness, and actionability (each 1–5, minimum 4/5). No hardcoded model names. Add a routing pointer to Benchmark SKILL.md.

---

## Non-Goals

- Hardcoding any model name in `llm-eval.py`
- Integrating into Benchmark's automated execution path
- T3, T6, T5 (separate sessions)

---

## Assumptions

- `runtime-state.json` confirms `analysis` capability available
- Model supplied externally via `WS_ANALYSIS_MODEL` or `--model`
- Python `anthropic` SDK available at runtime

---

## Acceptance Criteria

### AC1 — Script exists and is syntactically valid

Given `.wabblespec/engine/shared/scripts/llm-eval.py`,
When this task completes,
Then the file exists and `python -m py_compile llm-eval.py` exits 0.

### AC2 — No hardcoded model name

Given `.wabblespec/engine/shared/scripts/llm-eval.py`,
When this task completes,
Then no string matching `claude-`, `gpt-`, `gemini-`, or any versioned model identifier appears in the file source.
Then the script reads model from `WS_ANALYSIS_MODEL` env var or `--model` flag.
Then the script exits with a clear error message if neither is provided.

### AC3 — Three-dimension output

Given `llm-eval.py --skill-path <any SKILL.md> --section <heading> --model <any-model-id>`,
When this task completes and a valid API key is in the environment,
Then the script produces JSON with keys `clarity`, `completeness`, `actionability` (each 1–5), `reasoning` (string), and `passed` (bool).
Then it exits 0 if all three scores ≥ 4; exits 1 otherwise.

### AC4 — Eval-log appended

Given `.wabblespec/state/evals/eval-log.json` (created on first run),
When `llm-eval.py` runs successfully,
Then one entry is appended with fields: `timestamp`, `skill_path`, `section`, `scores`, `reasoning`, `passed`.
Then the file remains valid JSON after the append.

### AC5 — Benchmark SKILL.md routing entry added

Given `.claude/skills/benchmark/SKILL.md`,
When this task completes,
Then the file contains a `## Reference Routing` section.
Then that section has an entry pointing to `.wabblespec/engine/shared/scripts/llm-eval.py` for skill-section quality evaluation.

---

## Files to be Written / Modified

| File | Operation |
|---|---|
| `.wabblespec/engine/shared/scripts/llm-eval.py` | CREATE |
| `.wabblespec/state/evals/eval-log.json` | CREATE (empty array `[]`) |
| `.claude/skills/benchmark/SKILL.md` | MODIFY — add Reference Routing section |
