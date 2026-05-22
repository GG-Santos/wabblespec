# JSON Schemas

This document defines the JSON schemas used by skill-factory.

---

## evals.json

Defines the evals for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable statements
- `validated_against` *(optional)*: Records which adversarial corpus version the eval set was validated against. Shape:
  ```json
  {
    "validated_against": {
      "corpus": "adversarial-corpus",
      "corpus_version": "v1"
    }
  }
  ```
  When present, re-validate if `corpus_version` is older than the current corpus. See `references/adversarial-corpus.md` for the current version.

---

## template-contract.json

Output from `python -m scripts.template_contract . --json`. It validates
root `templates/*.j2` source templates before the generator renderer consumes
them.

```json
{
  "schema_version": "template-contract-1.0",
  "skill_path": "path/to/skill",
  "valid": true,
  "summary": {
    "templates": 11,
    "fields": 86,
    "errors": 0,
    "warnings": 0
  },
  "templates": {
    "agent.md.j2": {
      "template": "agent.md.j2",
      "fields": ["agent_name", "agent_title"],
      "field_count": 2,
      "valid": true,
      "summary": {"errors": 0, "warnings": 0},
      "findings": []
    }
  },
  "findings": []
}
```

**Fields:**
- `schema_version`: Contract version emitted by the validator.
- `skill_path`: Skill package root checked by the command.
- `valid`: False when any template has an error.
- `summary.templates`: Number of root `.j2` files checked.
- `summary.fields`: Total placeholder references across checked templates.
- `templates`: Per-template field inventory and findings.
- `findings[].severity`: `error` for missing values or unresolved placeholders,
  `warning` for unused context keys.
- `findings[].template`: Template filename that produced the finding.
- `findings[].field`: Field name when the finding maps to one context key.

The contract infers simple `{{ field_name }}` placeholders. It does not claim
full rendering support; generator wiring happens in the template-backed output
phase.

---

## history.json

Tracks version progression in Improve mode. Located at workspace root.

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**Fields:**
- `started_at`: ISO timestamp of when improvement started
- `skill_name`: Name of the skill being improved
- `current_best`: Version identifier of the best performer
- `iterations[].version`: Version identifier (v0, v1, ...)
- `iterations[].parent`: Parent version this was derived from
- `iterations[].expectation_pass_rate`: Pass rate from grading
- `iterations[].grading_result`: "baseline", "won", "lost", or "tie"
- `iterations[].is_current_best`: Whether this is the current best version

---

## repair_history.json

Tracks repair-loop causes, growth, preserve lists, and target sections. Located
at `<results-dir>/logs/repair_history.json` when `run_loop` or
`improve_description` runs with a log directory.

```json
[
  {
    "timestamp": "2026-05-19T00:00:00Z",
    "iteration": 1,
    "stage": "description_improvement",
    "causes": ["trigger_false_negative", "trigger_false_positive"],
    "critical": false,
    "before_chars": 64,
    "after_chars": 82,
    "growth_ratio": 0.281,
    "accepted": true,
    "preserve": ["benchmark this skill"],
    "targets": ["Add broader intent coverage for missed should-trigger queries."],
    "note": "provider-produced repair accepted"
  }
]
```

**Fields:**
- `timestamp`: UTC timestamp for the repair event.
- `iteration`: Loop iteration, or `0` for initial validation.
- `stage`: Repair stage such as `initial_validation` or
  `description_improvement`.
- `causes`: Normalized repair cause taxonomy.
- `critical`: Whether the cause allows growth beyond normal cap.
- `before_chars` / `after_chars`: Character counts before and after repair.
- `growth_ratio`: `(after - before) / before`, rounded.
- `accepted`: Whether the repair replaced the prior artifact/description.
- `preserve`: Good phrases or passing eval cues to keep.
- `targets`: Specific repair targets to avoid broad rewrites.
- `note`: Human-readable repair outcome.

Cause taxonomy:

`missing_file`, `invalid_yaml`, `generic_body`, `missing_safety`,
`missing_output_contract`, `verbosity`, `encoding`, `copy_path`,
`blocked_by_filter`, `trigger_false_negative`, `trigger_false_positive`,
`description_length`.

---

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "read_files": 5,
      "write_files": 2,
      "run_shell_command": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**Fields:**
- `expectations[]`: Graded expectations with evidence
- `summary`: Aggregate pass/fail counts
- `execution_metrics`: Tool usage and output size (from executor's metrics.json)
- `timing`: Wall clock timing (from timing.json)
- `claims`: Extracted and verified claims from the output
- `user_notes_summary`: Issues flagged by the executor
- `eval_feedback`: (optional) Improvement suggestions for the evals, only present when the grader identifies issues worth raising

---

## metrics.json

Output from the executor agent. Located at `<run-dir>/outputs/metrics.json`.

```json
{
  "tool_calls": {
    "read_files": 5,
    "write_files": 2,
    "run_shell_command": 8,
    "edit_files": 1,
    "list_files": 2,
    "search_files": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**Fields:**
- `tool_calls`: Count per tool type
- `total_tool_calls`: Sum of all tool calls
- `total_steps`: Number of major execution steps
- `files_created`: List of output files created
- `errors_encountered`: Number of errors during execution
- `output_chars`: Total character count of output files
- `transcript_chars`: Character count of transcript

---

## timing.json

Wall clock timing for a run. Located at `<run-dir>/timing.json`.

**How to capture:** When a subagent task completes, the task notification includes `total_tokens` and `duration_ms`. Save these immediately — they are not persisted anywhere else and cannot be recovered after the fact.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

Output from Benchmark mode. Located at `benchmarks/<timestamp>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "provider-default",
    "analyzer_model": "most-capable-model",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3,
    "run_counts_by_configuration": {
      "with_skill": 3,
      "without_skill": 3
    },
    "candidate_configuration": "with_skill",
    "baseline_configuration": "without_skill",
    "invalid_run_counts": {
      "malformed_run_dirs": 0,
      "missing_grading": 0,
      "invalid_json": 0,
      "invalid_grading": 0,
      "unreadable_grading": 0,
      "invalid_timing": 0
    }
  },

  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "Used 2023 data, may be stale",
        "Fell back to text overlay for non-fillable fields"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
    "Eval 3 shows high variance (50% ± 40%) - may be flaky or model-dependent",
    "Without-skill runs consistently fail on table extraction expectations",
    "Skill adds 13s average execution time but improves pass rate by 50%"
  ]
}
```

**Fields:**
- `metadata`: Information about the benchmark run
  - `skill_name`: Name of the skill
  - `timestamp`: When the benchmark was run
  - `evals_run`: List of eval names or IDs
  - `runs_per_configuration`: Maximum observed runs for any config
  - `run_counts_by_configuration`: Observed run count per config
  - `candidate_configuration`: Primary/candidate config used for delta ordering
  - `baseline_configuration`: Baseline config used for delta ordering
  - `invalid_run_counts`: Counts of malformed/skipped run inputs encountered during aggregation
- `runs[]`: Individual run results
  - `eval_id`: Numeric eval identifier
  - `eval_name`: Human-readable eval name (used as section header in the viewer)
  - `configuration`: Must be `"with_skill"` or `"without_skill"` (the viewer uses this exact string for grouping and color coding)
  - `run_number`: Integer run number (1, 2, 3...)
  - `result`: Nested object with `pass_rate`, `passed`, `total`, `time_seconds`, `tokens`, `errors`
- `run_summary`: Statistical aggregates per configuration
  - `with_skill` / `without_skill`: Each contains `pass_rate`, `time_seconds`, `tokens` objects with `mean` and `stddev` fields
  - `delta`: Difference strings like `"+0.50"`, `"+13.0"`, `"+1700"`
- `notes`: Freeform observations from the analyzer

**Important:** The viewer reads these field names exactly. Using `config` instead of `configuration`, or putting `pass_rate` at the top level of a run instead of nested under `result`, will cause the viewer to show empty/zero values. Always reference this schema when generating benchmark.json manually.

---

## feedback.json

Output from the eval-viewer (v11) when the user reviews a workspace. Located
at `<workspace>/feedback.json`. The viewer writes this on every autosave and
when the user clicks **Finalize**.

```json
{
  "schemaVersion": "feedback-1.1",
  "skill_name": "example-skill",
  "iteration": null,
  "status": "complete",
  "reviews": [
    {
      "run_id": "iteration-1-eval-0-with_skill",
      "configuration": "with_skill",
      "status": "approved",
      "severity": "none",
      "feedback": "Output looks correct. Axis labels are present.",
      "checklist": {
        "output_inspected": true,
        "grades_checked": true,
        "previous_output_checked": true,
        "benchmark_checked": true,
        "feedback_decision": true
      },
      "file_reviews": [
        {
          "key": "outputs/chart.png:0",
          "file_index": 0,
          "file_name": "chart.png",
          "type": "image",
          "inspected": true,
          "decision": "accepted",
          "severity": "none",
          "feedback": ""
        }
      ],
      "qa_warnings": [],
      "timestamp": "2026-01-15T10:42:11Z"
    }
  ],
  "ui_state": { "...": "viewer-only restoration state" }
}
```

**Top-level fields:**
- `schemaVersion`: Always `"feedback-1.1"` for the current viewer. Earlier
  schemas exist; refuse to act on anything that isn't `"feedback-1.1"` and
  ask the user to regenerate from the current viewer.
- `status`: `"in_progress"` while the user is still reviewing, `"complete"`
  once they click **Finalize**. Treat `"in_progress"` as a draft — the user
  may not be done; check with them before iterating on it.
- `reviews[]`: One entry per run. Always present in `reviews`, even when the
  user left a run untouched (status will be `"unreviewed"`).
- `ui_state`: Viewer restoration state. Ignore it.

**Per-review fields, in order of how much signal they carry:**
- `status`: `"approved"` | `"needs_changes"` | `"blocked"` | `"unreviewed"`.
  This is the headline signal — a `blocked` run with empty `feedback` text
  is a *much* louder signal than a fully-written paragraph on an `approved`
  run. Don't only read `feedback`.
- `severity`: `"critical"` > `"major"` > `"minor"` > `"unknown"` > `"none"`.
  Prioritize fixes by severity; a critical issue on one eval outranks ten
  minor ones.
- `feedback`: Free-text comment. Often empty when the user expressed their
  opinion via `status` + `severity` alone.
- `file_reviews[]`: Per-file decisions. `decision` is `"accepted"` |
  `"skipped"` | `"issue"` | `"blocked"`. The per-file `feedback` field
  carries notes scoped to one output file — this is finer-grained than the
  run-level `feedback`, and often where the actionable detail lives.
- `checklist`: Which review steps the user actually completed. If a key is
  `false` on a `"complete"` run, the user finalized despite a missing step;
  treat their feedback as lower-confidence for that axis.
- `qa_warnings[]`: The viewer's own warnings on the *feedback content* —
  e.g., it looks garbled, contains repeated URLs, or may include a secret.
  Don't act on flagged content; ignore the run or ask the user to clarify.
- `timestamp`: When this review was last edited.

**How to read it.** Sort runs by `status` (blocked → needs_changes →
approved → unreviewed), then within each by `severity`. Improve the skill
to address the blocked and needs_changes runs first; empty feedback on an
`approved` run is the user saying "fine, move on." Look at
`file_reviews[].feedback` for any run that has issue/blocked file
decisions — that's where per-file specifics live.

---

## framework.yaml

The framework manifest. Root file for Framework mode. Located at the
framework root. Read by `agents/navigator.md`, `agents/module-auditor.md`,
and `agents/framework-validator.md`.

```yaml
framework:
  name: string           # kebab-case framework name
  version: string        # semver
  description: string    # one sentence, under 200 chars

modules:
  - id: string                       # kebab-case, unique across framework
    path: string                     # relative path to module directory
    type: string                     # skill | agent | script | plugin
    tags: [string]                   # activation and search tags
    consumes_schemas: [string]       # paths relative to framework root
    produces_schemas: [string]       # paths relative to framework root
    depends_on: [string]             # module ids this module depends on
    last_validated: string           # ISO date YYYY-MM-DD
    quality_floor_passed: boolean    # set by module-auditor after each audit

shared:
  schemas:
    - path: string          # relative path to schema file
      consumers: [string]   # module ids that consume this schema
      version: string       # schema version string
  references:
    - path: string
      consumers: [string]

quality_floor:
  min_pattern_score: number           # 0.0-5.0; recommended 4.0 for frameworks
  required_gates: [string]            # gate names; minimum: [quick_validate, lint_prompts]
  adversarial_required_for_tags: [string]  # tags that require adversarial evals

cascade_policy:
  schema_change_triggers_revalidation: boolean    # default true
  shared_reference_change_triggers_revalidation: boolean  # default false
```

**Required fields per module entry:** `id`, `path`, `type`, `tags`,
`last_validated`, `quality_floor_passed`. All others optional.

**Invariants validated by `agents/framework-validator.md`:**
- All `id` values unique across `modules`
- All `depends_on` values reference an existing module `id`
- No dependency cycles in `depends_on` chains
- All `consumes_schemas` and `produces_schemas` paths appear in
  `shared.schemas[].path`
- No two modules share the same `produces_schemas` path (naming collision)

---

## stress_artifact_fixture_summary.json

Output from deterministic stress artifact validation. Located at
`evaluations/stress_artifact_fixture_summary.json` when persisted.

```json
{
  "schema_version": "1.0",
  "skill_name": "skill-factory",
  "execution_mode": "deterministic_artifact_fixture_validation",
  "artifact_mode": "deterministic_fixture",
  "cases_requested": 19,
  "cases_covered": 19,
  "used_provider_network_model": false,
  "status": "pass",
  "failures": 0,
  "skipped": 0,
  "results": [
    {
      "case_id": "sf-003",
      "risk_class": "plugin-surface",
      "expected_action": "proceed",
      "artifact_mode": "deterministic_fixture",
      "generated_files": ["plugin-foundry/SKILL.md"],
      "validations_run": [
        {
          "type": "component_structure",
          "status": "pass",
          "detail": "generated-output checks passed",
          "files": []
        }
      ],
      "status": "pass",
      "failure_reasons": [],
      "skipped_reason": null,
      "used_provider_network_model": false,
      "package_validation_ran": true,
      "mcp_validation_ran": true,
      "hook_rule_validation_ran": false,
      "secret_path_safety_validation_ran": false
    }
  ]
}
```

Allowed `artifact_mode` values:

- `deterministic_fixture`
- `live_provider_artifact`
- `subagent_review`
- `action_selection`

Allowed validation `type` values are explicit checks such as
`component_structure`, `required_files`, `surface_registry`,
`mcp_python_self_test`, `mcp_typescript_static`, `hook_rule_runtime`,
`package_manifest_safety`, `secret_redaction`, `current_info_boundary`,
`exact_format`, `tool_failure_partial`, and `shipping_block`.

Do not use ambiguous labels such as `tested`, `validated`, or `reviewed` as
artifact modes or validation types.

---

## comparison.json

Output from blind comparator. Located at `<grading-dir>/comparison-N.json`.

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution with proper formatting and all required fields. Output B is missing the date field and has formatting inconsistencies.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "Well-formatted", "All fields present"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable output", "Correct basic structure"],
      "weaknesses": ["Missing date field", "Formatting inconsistencies", "Partial data extraction"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    }
  }
}
```

---

## stress_artifact_fixture.json

Output from deterministic stress artifact validation. Located at
`evaluations/stress_artifact_fixture_summary.json` when persisted.

```json
{
  "schema_version": "1.0",
  "skill_name": "skill-factory",
  "execution_mode": "deterministic_artifact_fixture_validation",
  "artifact_mode": "deterministic_fixture",
  "cases_requested": 36,
  "cases_covered": 36,
  "used_provider_network_model": false,
  "status": "pass",
  "failures": 0,
  "skipped": 0,
  "results": [
    {
      "case_id": "sf-003",
      "risk_class": "plugin-surface",
      "expected_action": "proceed",
      "artifact_mode": "deterministic_fixture",
      "generated_files": ["SKILL.md"],
      "validations_run": [
        {
          "type": "required_files",
          "status": "pass",
          "detail": "required files present",
          "files": ["SKILL.md"]
        }
      ],
      "status": "pass",
      "failure_reasons": [],
      "skipped_reason": null,
      "used_provider_network_model": false,
      "package_validation_ran": true,
      "mcp_validation_ran": true,
      "hook_rule_validation_ran": false,
      "secret_path_safety_validation_ran": false
    }
  ]
}
```

**Fields:**
- `execution_mode`: Must be `deterministic_artifact_fixture_validation` for local
  fixture runs. Do not use this label for provider-generated artifacts.
- `artifact_mode`: Must be explicit: `deterministic_fixture`,
  `live_provider_artifact`, `subagent_review`, or `action_selection`.
- `used_provider_network_model`: `false` for deterministic fixtures.
- `results[].generated_files`: Relative files created inside the isolated case
  workspace.
- `results[].validations_run[].type`: Specific validation type. Vague labels
  such as `tested`, `validated`, or `reviewed` are invalid.
- `results[].package_validation_ran`, `mcp_validation_ran`,
  `hook_rule_validation_ran`, `secret_path_safety_validation_ran`: Boolean
  flags for major validation classes.

---

## analysis.json

Output from post-hoc analyzer. Located at `<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary of why comparator chose winner"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling multi-page documents",
    "Included validation script that caught formatting errors"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process the document appropriately' led to inconsistent behavior",
    "No script for validation, agent had to improvise"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": ["Minor: skipped optional logging step"]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Did not use the skill's formatting template",
        "Invented own approach instead of following step 3"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process the document appropriately' with explicit steps",
      "expected_impact": "Would eliminate ambiguity that caused inconsistent behavior"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Used validation script",
    "loser_execution_pattern": "Read skill -> Unclear on approach -> Tried 3 different methods"
  }
}
```
