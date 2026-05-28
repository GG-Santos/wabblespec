# Wave Plan: toprank-integration-phase2-T2

**session_id:** toprank-integration-phase2-T2
**task_card:** .wabblespec/state/plans/task-card.md
**locked_at:** 2026-05-28T11:04:00Z
**total_waves:** 2

---

## Wave 1 — Create llm-eval.py and eval-log.json

**label:** llm-eval-script
**verification_mode:** Audit

### Steps

1. Create `.wabblespec/state/evals/eval-log.json` containing `[]`.
2. Create `.wabblespec/engine/shared/scripts/llm-eval.py` implementing:
   - CLI: `--skill-path`, `--section`, `--content-file` (mutually exclusive input modes), `--model` (optional, overrides env var)
   - Model resolution: `WS_ANALYSIS_MODEL` env var → `--model` flag → error exit
   - Reads `runtime-state.json` at `.wabblespec/state/runtime/runtime-state.json`; aborts if `analysis.available != true`
   - Extracts section content from SKILL.md (finds `## <heading>` and reads until next `##`)
   - Builds three-dimension judge prompt (clarity / completeness / actionability, 1–5 rubric)
   - Calls Anthropic API via `anthropic` SDK using resolved model; requests JSON response
   - Parses response; checks all three scores ≥ 4
   - Appends entry to `.wabblespec/state/evals/eval-log.json`
   - Prints scores and reasoning; exits 0 if passed, 1 if any score < 4
3. Run `python -m py_compile .wabblespec/engine/shared/scripts/llm-eval.py` to verify syntax.

### Outputs

| Path | Operation |
|---|---|
| `.wabblespec/engine/shared/scripts/llm-eval.py` | CREATE |
| `.wabblespec/state/evals/eval-log.json` | CREATE |

### Verification gate (Audit)

- Both files exist
- `py_compile` exits 0 on `llm-eval.py`
- No model name string (claude-*, gpt-*, gemini-*) appears in `llm-eval.py` source
- AC1 and AC2 "Then" clauses satisfied

### Rollback

Delete both created files.

---

## Wave 2 — Add Reference Routing to Benchmark SKILL.md

**label:** benchmark-routing-entry
**verification_mode:** Audit

### Steps

1. Read `.claude/skills/benchmark/SKILL.md` to confirm no existing `## Reference Routing` section.
2. Add `## Reference Routing` section immediately after the opening description block (before `## When to use`), containing:

```markdown
## Reference Routing

| Situation | Reference |
|---|---|
| Benchmark discipline and integrity rules | `rules/benchmark-discipline.md` |
| Outcome declaration format and enforcement | `rules/outcome-requirement.md` |
| Skill-section quality evaluation (clarity / completeness / actionability) | `.wabblespec/engine/shared/scripts/llm-eval.py` |
```

### Outputs

| Path | Operation |
|---|---|
| `.claude/skills/benchmark/SKILL.md` | MODIFY |

### Verification gate (Audit)

- `## Reference Routing` section exists in Benchmark SKILL.md
- Table contains exactly 3 entries including the `llm-eval.py` entry
- AC5 "Then" clauses satisfied
- AC1–AC4 unaffected (script not modified in this wave)

### Rollback

Revert `.claude/skills/benchmark/SKILL.md` to pre-wave state.
