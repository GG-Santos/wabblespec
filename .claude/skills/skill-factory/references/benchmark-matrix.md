# Benchmark Matrix Mode

Use this reference when the user asks to benchmark skill-creation agents
across categories, niches, and output complexity.

## Matrix Contract

- 39 categories.
- 3 niches per category.
- 10 output targets per niche.
- 1,170 tasks per agent.
- 3,510 tasks for three agents.

Every generated task folder must contain:

- `README.md` with the benchmark prompt and expected tree.
- `prompt.txt` with the exact universal prompt.
- `task.json` with machine-readable category, niche, target, and prompt.
- `manifest.json` with `eval_viewer.visible=true`.
- `eval.json` with the required scorecard/check skeleton.

## Commands

Stage 1, one niche per category and Skill Only:

```bash
python -m scripts.skill_benchmark_matrix --agent-name agent_name --stage 1
```

Full matrix for one agent:

```bash
python -m scripts.skill_benchmark_matrix --agent-name agent_name --stage 6
```

Full resumable pipeline for three lanes:

```bash
python -m scripts.run_benchmark_pipeline \
  --agent-name skill_factory \
  --agent-name agent_a \
  --agent-name agent_b \
  --stage 6
```

The pipeline generates missing tasks, checks matrix coverage, materializes
pending outputs, scores, runs qualitative and exhaustive audits, reports, renders static HTML,
and verifies eval-viewer visibility. Existing materialized folders are skipped
unless `--overwrite` is passed.

Verifier required by the eval-viewer visibility gate:

```bash
python -m scripts.verify_eval_viewer_outputs \
  --root evaluations/skill_benchmarks \
  --require-manifest \
  --require-eval-json \
  --require-visible-true
```

Launch the bundled static eval viewer:

```bash
python -m eval_viewer \
  --root evaluations/skill_benchmarks \
  --watch \
  --include "**/manifest.json" \
  --include "**/eval.json" \
  --include "**/README.md" \
  --port 8787
```

This serves `benchmark_report.html` from the matrix root. Use `--once --json`
for non-blocking CI checks.

Use `--dry-run` before large writes and `--limit` for smoke slices.
Use `--category`, `--niche`, and `--target` to isolate a regression.

## Stage Map

| Stage | Scope |
|---|---|
| 1 | 39 categories x first niche x Skill Only |
| 2 | 39 categories x 3 niches x Skill Only |
| 3 | Add References and Templates targets |
| 4 | Add Scripts and Hooks targets |
| 5 | Add Agents and MCP targets |
| 6 | Add 3, 5, and 10 skill system targets |

## Reviewer Notes

The matrix generator writes prompt tasks, not scored benchmark results.
After an agent produces files for a task, update `eval.json` scorecard and
checks from evidence. Keep null scores for ungraded outputs.

For autonomous structural scoring after materialization:

```bash
python -m scripts.score_benchmark_outputs \
  --root evaluations/skill_benchmarks \
  --overwrite
```

These scores are deterministic structural heuristics, not human or model
quality grades. They are useful for checking completeness across the full
matrix before deeper qualitative review.

Run qualitative audit after materialization:

```bash
python -m scripts.qualitative_benchmark_audit \
  --root evaluations/skill_benchmarks
```

This writes `qualitative_audit.json` and catches missing domain lenses, thin MCP
contracts, generic examples, and duplicated multi-skill role bodies.

Run exhaustive review when the remaining risk is whether the whole corpus was
checked, not only sampled:

```bash
python -m scripts.exhaustive_benchmark_review \
  --root evaluations/skill_benchmarks \
  --execute-python
```

This writes `exhaustive_review.json` and verifies every task directory has
traceable prompts, target-required files, manifest/eval consistency, parseable
JSON/Python, category-module safety traceability, system-role contracts, MCP
contracts, and runnable generated validators/hooks.

Generate compact reports after scoring:

```bash
python -m scripts.report_benchmark_matrix \
  --root evaluations/skill_benchmarks
```

This writes `benchmark_report.json` and `benchmark_report.md` under the
matrix root for quick review without a running viewer.

Render an offline HTML dashboard from the compact report:

```bash
python -m scripts.render_benchmark_matrix_html \
  --root evaluations/skill_benchmarks
```

This writes `benchmark_report.html` under the matrix root for static review
when the eval viewer package is not installed. If `benchmark_report.json`
does not exist, the renderer builds it first. Use `--refresh` to rebuild the
JSON report before rendering.

Safety-sensitive categories are valid benchmark cases only when the generated
skill keeps safe boundaries explicit. Defensive, educational, fictional,
summarization, and prevention tasks should not become operational harm
instructions.
