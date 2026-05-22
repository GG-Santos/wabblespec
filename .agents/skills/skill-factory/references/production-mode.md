# Production Mode

Production Mode is for skills that ship without a human reviewing each
invocation. Plugin surfaces, multi-platform targets, adversarial inputs,
safety-critical output, or anything you'd put a SLA on.

It's the heaviest mode by design. Don't apologize for the weight when
it's warranted; do escalate down to Workshop or Vibe if it isn't.

## Architecture tiers

Pick one. Escalate only for concrete requested behavior.

| Tier | When | Components |
|---|---|---|
| Simple | One workflow, no code needed | `SKILL.md`, optional `examples/` or `references/` |
| Standard | Needs deterministic processing or validation | + `scripts/`, `schemas/`, `evaluations/`, `skill-rules.json` |
| Advanced | Delegated roles or lifecycle entry points | + `agents/`, `commands/`, `hooks/`, `data/` |
| Full | Plugin surfaces or multiple surfaces | + `plugin/`, `mcp/`, `rules/`, `matchers/`, `templates/`, package checks |

**Required Full tier** when the request includes plugin, hook, MCP server,
agent pack, slash command, or factory-of-skills behavior.

**Escape valves** (these prevent over-engineering):

- **Subjective skills stay at Tier=Simple** even in Production. If the
  output can't be objectively graded (writing style, art direction,
  conversational tone), don't generate scoring scripts for taste.
- **Atomic skills (<80 lines of skill content) stay at Tier=Simple**
  regardless of perceived rigor pressure.
- **Single-domain skills with no plugin surfaces stay at or below Standard**
  even when the SKILL.md is long. Length doesn't justify Advanced.

Use `scripts/component_generator.py` for scaffolding:

```python
from scripts.component_generator import detect_tier, generate_skill_structure

tier = detect_tier(skill_description, user_intent)
manifest = generate_skill_structure(
    skill_name,
    skill_description,
    tier=tier,
    output_dir=output_path,
)
```

Safe defaults the generator produces:

- **Lifecycle rules deny destructive shell patterns by default.** The generated
  `rules.yaml` stores portable rule intent and `hooks/lifecycle.json` declares
  neutral lifecycle events. Runtime-specific adapters map deny, warn, and block
  decisions when packaging or targeting a host runtime.
- Generated command frontmatter defaults to read-only capabilities.
- Generated scripts accept JSON in, return JSON out.
- Generated MCP scaffolds include a self-test that doesn't require a
  live MCP host.
- Plugin manifests reference a surface registry when plugin surfaces exist.
- Activation regexes use word boundaries and avoid stopword triggers.
- **Logs and benchmark outputs auto-redact secrets.** `scripts/utils.py:redact_secrets`
  matches common API keys, GitHub PATs (`ghp_`, `gho_`,
  `ghs_`), Slack tokens (`xoxb-`, `xoxp-`, etc.), AWS access keys (`AKIA...`)
  and secrets, Stripe live keys, JWT tokens, PEM private key blocks, and
  generic `api_key=...`/`access_token=...` assignments with high-entropy
  values. The lint scanner
  (`python -m scripts.lint_prompts <path> --rule secret-patterns --level ERROR`)
  and the log redactor share the same pattern set, so anything lint flags is
  also redacted in logs.

## Writing a Production SKILL.md

Required components:

- Frontmatter with `name` and a trigger-focused `description`.
- Purpose and explicit scope (use cases + non-use cases).
- Required and optional inputs.
- Decision logic.
- Tool-use rules where tools are involved.
- Output contract.
- Safety boundaries.
- Verification steps.
- References loaded only when needed.

Write instructions as enforceable behavior, but **explain *why* alongside
the *what*** - even in Production. The model following the instructions
has good theory of mind; rote rules without rationale generalize poorly.
This is the same lesson Workshop Mode teaches, kept here for emphasis.

Replace vague phrases with concrete actions:

- "Be helpful" -> describe the output shape and tone explicitly.
- "Use best practices" -> name the practices.
- "Handle appropriately" -> list what *appropriately* means here.
- "As needed" -> say when it's needed.

Keep `SKILL.md` under 500 lines. Move long schemas, examples, and
provider-specific details to `references/`.

## Component requirements

Use these references only when the task needs the component:

- `references/component_scaffolds.md` - hooks, MCP, commands, agents, templates.
- `references/schemas.md` - eval, grading, benchmark, report JSON.
- `references/skill-rules-spec.md` - `skill-rules.json` activation rules.
- optional runtime notes - only when the user explicitly targets a host.

Per-component rules:

- **`agents/*.md`** - frontmatter + role, inputs, outputs, refusal
  boundaries, handoff rules. Agents must not recursively orchestrate
  unless explicitly told.
- **`commands/*.md`** - frontmatter with conservative tools, flags, exact
  behavior. Commands must not request write tools unless writes are required.
- **`hooks/`** - event manifest + scripts that read stdin JSON, write
  stdout JSON. Hooks must fail closed for unsafe shell commands.
- **`mcp/`** - stdio server scaffold, manifest, self-test command. Don't
  claim a live MCP integration unless it ran in a compatible host.
- **`scripts/`** - `argparse`, `pathlib`, bounded errors, stdin/stdout
  JSON mode where appropriate, no secrets in logs.
- **`schemas/`** - machine-readable contracts for structured I/O.
- **`templates/`** - reusable output skeletons consumed by scripts or agents.
- **`evaluations/`** - test prompts with expected behavior and pass/fail
  criteria.

## Evaluation workflow

Build evals before declaring success. For non-trivial skills:

1. Create realistic test prompts: should-trigger, should-not-trigger, edge,
   malformed, **adversarial**, and refusal cases. The adversarial cases
   are not optional in Production.
2. Run with-skill and baseline/old-skill in parallel via subagents when
   available.
3. Save outputs under `<skill-name>-workspace/iteration-N/eval-<id>/`.
4. **Generate the eval-viewer for the human before your own review.**
   Production keeps Workshop's lesson: human first. Same invocation as
   Workshop (see `references/workshop-mode.md` *The eval-viewer ritual*),
   plus `--benchmark` is effectively required in Production so the
   reviewer sees pass-rate, timing, and tokens alongside the outputs.
   When you read `feedback.json` back, branch on `status` and `severity`,
   not just the free-text `feedback` - schema lives in
   `references/schemas.md`.
5. Grade against explicit assertions. Store evidence, not just scores.
6. Aggregate benchmark:

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

7. Compare against the previous iteration when one exists.
8. Improve only when evidence points to a real failure or waste pattern.

Don't ask the user to review raw chaos. Summarize failures, show the
meaningful diff, and provide the viewer or report.

## Trigger description optimization

Optimize the frontmatter `description` after meaningful skill changes or
when trigger accuracy is the user's goal.

1. Create 20 trigger eval queries: 8-10 should-trigger, 8-10
   should-not-trigger, plus near-miss competing-skill cases.
2. Use realistic prompts with file paths, casual phrasing, domain detail.
3. Run:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5
```

4. Add `--provider <name>` when the user picked a provider or auto-detection
   would be wrong.
5. Apply `best_description` only after reporting before/after scores.

Provider detection order lives in `scripts/providers/`. Don't assume a
provider is available; inspect provider status or report that optimization
couldn't run.

## Verification gates

Run the lightest gate that proves the claim.

| Gate | Production | Implemented by |
|---|---|---|
| `quick_validate` | run before handoff | `scripts/quick_validate.py` |
| `syntax_check scripts/` | always run if scripts exist | `scripts/syntax_check.py` |
| `lint_prompts` | always run; block on errors | `scripts/lint_prompts.py` |
| `review_skill` | always run before handoff | `scripts/review_skill.py` |
| `package_skill --dry-run` | always run before packaging | `scripts/package_skill.py` |
| Package boundary smoke | run before release packaging | `scripts/package_boundary_smoke.py` |
| Generated-skill eval | always run for non-trivial skills | `scripts/run_eval.py` |
| Benchmark aggregation | always run | `scripts/aggregate_benchmark.py` |
| Adversarial test cases | required (except subjective Tier=Simple) | `references/adversarial-corpus.md` patterns + `run_eval` |
| Output-quality grading (v4) | required for any skill with measurable downstream output | spawn `agents/grader.md` with `eval_target=skill_creation` |
| Head-to-head comparison (v4) | required when iterating against a baseline | spawn `agents/comparator.md` with `compare_target=skill_creation`; ingest both `grading.json` files |
| Loss analysis (v4) | required after a failing comparison | spawn `agents/analyzer.md` with both `grading.json` paths |
| Portability check (v4) | required when portability matters | `scripts/cross_model_test.py` |
| Shipping Checklist | required | inline below |

Commands:

```bash
python -m scripts.quick_validate .
python -m scripts.syntax_check scripts --json
python -m scripts.lint_prompts . --level WARNING
python -m scripts.review_skill . --json
python -m scripts.package_skill . <output-dir> --dry-run
python -m scripts.package_boundary_smoke . --json
python -m scripts.run_eval --eval-set <path> --skill-path <path>
python -m scripts.aggregate_benchmark <benchmark-dir> --output <summary.json>
python -m scripts.cross_model_test prompt --prompt @<path>
python -m scripts.regression_check --baseline <prior-grading.json> --current <new-grading.json>
python -m scripts.install_smoke_test <path-to-bundle.skill>
```

### Gate priority and conflict resolution

When gates conflict (one passes, another fails), this ordering decides:

**Tier 1 — blocking. Fail = stop. Do not ship.**
- `lint_prompts --level ERROR` errors
- `syntax_check` failures (code that doesn't parse)
- Adversarial eval cases with `status: blocked`
- Grader `overall_passed: false` when `eval_target=skill_creation`
- Any `error`-severity runtime coupling finding

**Tier 2 — quality flags. Fail = fix before handoff; don't block if no Tier 1 failures.**
- `lint_prompts --level WARNING` (not ERROR)
- `quick_validate` warnings
- Grader pattern score < 4.5 on individual pattern (overall still passes)
- `needs_changes` feedback with `severity: minor`

**Tier 3 — release gates. Required only when packaging or shipping.**
- `package_skill --dry-run`
- `package_boundary_smoke`
- `install_smoke_test`

Conflict rule: a Tier 1 failure overrides any Tier 2 pass. Never average across tiers. A single Tier 1 failure = do not ship, regardless of how many Tier 2/3 gates pass.

The v4 grader, comparator, and analyzer are markdown agent prompts in
`agents/`. Spawn them as subagents from `run_eval` or from
orchestration scripts - they expect the inputs documented in their
files and write JSON to disk (`grading.json`, `comparison.json`,
`analysis.json`). When the runtime doesn't support subagents, invoke them
inline using the same prompt content and ask the user for the outputs
files location.

All v4 gates now have backing implementations. `regression_check`
compares a new `grading.json` against a baseline and exits non-zero on
regression (score drop > 0.2 or pass->fail). `install_smoke_test`
unpacks the packaged bundle in a tmpdir and runs `quick_validate` and
hook smoke tests against the unpacked copy. `package_boundary_smoke`
creates temporary package fixtures, rejects unsafe archive members, proves
artifact exclusions, checks likely-secret rejection, creates a `.skill`
archive, records its SHA-256 hash, and validates the extracted archive.

The shipped gates must not rely on generated `__pycache__` files. If
verification creates cache directories, remove them after confirming the
path is inside the skill-factory directory.

Run `template_contract` after changing root `templates/*.j2` catalog files,
`generated_artifact_smoke` after changing generator outputs or eval-viewer
assets, and `package_boundary_smoke` after changing package, install, archive,
cache, or secret-scan behavior.

Before reporting completion, state:

- Files changed.
- Gates run + pass/fail.
- What was not tested.
- Remaining risks.

## Finalization Mode

Use when the user asks to polish, finalize, prepare release, or stop live
provider work.

1. Don't run live providers unless the user explicitly re-enables them in
   the current request.
2. Treat every runtime and host as a deferred gate when unavailable,
   rate-limited, or frozen.
   Don't count raw-only provider evidence as a pass.
3. Close local blockers first: invalid skill metadata, package leaks,
   unsafe hooks, broken MCP scaffolds, failing public verification commands,
   malformed docs, cache churn, overclaiming release language.
4. Run deterministic public gates before handoff: quick validation, syntax,
   prompt lint, package dry-run, and any evals or benchmarks required.
5. Update docs with explicit evidence boundaries: deterministic proof,
   live provider proof already collected, deferred provider gates,
   remaining risks.
6. Never call the artifact "production-ready v1" unless the owner
   explicitly approves release and all claimed gates have passed.

## Output contracts

**Creation result:**

- Skill directory or patch-ready file content.
- Chosen tier and why.
- Required follow-up inputs.
- Verification performed.

**Hardening result:**

- Executive summary of high-risk gaps.
- Concrete changes made.
- Revised skill or patch.
- Stress tests / eval cases.
- Verification performed.
- Remaining risks.

**Evaluation result:**

- Eval set path.
- With-skill vs baseline/old-skill comparison.
- Pass/fail evidence.
- Recommendation: ship, iterate, or block.

**Packaging result:**

- Package path or dry-run manifest.
- Included files.
- Excluded files.
- Installability checks performed.

**Exact-format requests:** If the user asks for only a file body, JSON
object, table, or other exact format, return only that artifact unless
higher-priority instructions require a report or safety refusal.

## Shipping Checklist (Production only)

- Frontmatter `name` is kebab-case; description states concrete triggers.
- Scope includes use and non-use cases.
- Inputs, defaults, and clarification gates explicit.
- Safety boundaries reject override, exfiltration, destructive, and abuse cases.
- Tool steps have commands, expected inputs, failure behavior.
- Optional references load only when needed.
- Generated Python parses with `scripts.syntax_check`.
- JSON / YAML-like manifests / XML-like files parse or validate.
- Generated hooks deny destructive shell commands in tests.
- Generated MCP scaffold passes self-test where present.
- Plugin surface registry points to existing files where plugin metadata exists.
- Package dry-run or archive inspection passes when packaging is requested.
- Evals cover normal, ambiguous, malformed, adversarial, and refusal cases.
- Final report lists changed files, gates run, untested areas, and remaining risks.

