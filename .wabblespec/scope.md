# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T11:02:00Z
**session_id:** toprank-integration-phase2-T2

## In Scope

- Create `.wabblespec/engine/shared/scripts/llm-eval.py` — three-dimension skill-section quality scorer (clarity / completeness / actionability, 1–5, min gate 4/5). Model resolved from `WS_ANALYSIS_MODEL` env var or `--model` flag — no hardcoded model name.
- Create `.wabblespec/state/evals/` directory and append-only `eval-log.json` (initialized empty on first script run)
- Add `## Reference Routing` section to `.claude/skills/benchmark/SKILL.md` with one entry pointing to `llm-eval.py`

## Out of Scope

- Hardcoding any model name in `llm-eval.py` (I6 violation)
- Copying toprank `call_judge` or `_get_client` verbatim
- Integrating `llm-eval.py` into Benchmark's automated execution path (follow-on task)
- T3 (Instinct drawer field rename) — separate session
- T6 (Guard safety taxonomy) — Guard SKILL.md still locked under wave-checkpoint-v1
- Any writes outside the three declared paths above

## Assumptions

- `runtime-state.json` at `.wabblespec/state/runtime/runtime-state.json` confirms `analysis: available=true` (verified)
- Model name is supplied externally via `WS_ANALYSIS_MODEL` env var or `--model` flag; script exits with a clear error if neither is provided
- Python `anthropic` SDK available in the environment where `llm-eval.py` runs
- Benchmark SKILL.md has no existing `## Reference Routing` section (confirmed from prior session)
- Eval-log schema: `[{timestamp, skill_path, section, scores: {clarity, completeness, actionability}, reasoning, passed}, ...]`
- This is a framework authoring task — writes to `.wabblespec/` are permitted (not a product-space task; I11 does not apply)

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
