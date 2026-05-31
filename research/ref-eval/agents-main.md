# Ref-Eval: agents-main

**Reference:** `C:\Vaults\references\Other Projects References\agents-main\agents-main`
**Slug:** `agents-main`
**Date:** 2026-05-31
**Trust level:** MEDIUM
**Evaluator:** ref-adopt pipeline

---

## Step 1b — File Inventory

| Path | Purpose | Size | Key Content | Status | Transfer Check |
|---|---|---|---|---|---|
| README.md | Root overview | Large | Plugin counts, PluginEval intro, architecture summary | Read | n/a |
| CLAUDE.md | Authoring conventions | Medium | Agent/skill frontmatter schemas, 10 evaluation dimensions with weights | Read | n/a |
| docs/architecture.md | Design principles | Medium | Single responsibility, composability, 3-tier progressive disclosure, model tier criteria | Read | n/a |
| docs/plugin-eval.md | Evaluation framework docs | Large | 3 layers, 10 dimensions with weights, anti-pattern flags + thresholds, badge system, statistical methods | Read | n/a |
| docs/agent-skills.md | 129 skills catalog | Large | Skills by plugin, activation patterns, progressive disclosure structure | Read | n/a |
| docs/agents.md | 182 agents catalog | Large | Agent listing by category and model tier | Summary | Three-tier model assignment criteria (transferable capability types) |
| docs/usage.md | Usage guide | Medium | Commands, multi-agent workflow examples | Summary | Orchestration pipeline patterns |
| docs/plugins.md | Plugin catalog | Large | 75 plugins with descriptions | Summary | Plugin categorization taxonomy |
| .claude-plugin/marketplace.json | Registry | Large | All plugin paths, skills as directory refs | Skipped | Registry schema pattern (transferable) |
| .github/CONTRIBUTING.md | Contribution guide | Small | Standards for new plugins/agents/skills | Skipped | Quality standards checklist transferable |
| .github/CODE_OF_CONDUCT.md | Code of conduct | Small | Standard CoC | Skipped | None |
| .github/FUNDING.yml | Funding | Small | Sponsorship links | Skipped | None |
| .github/ISSUE_TEMPLATE/new_subagent.yml | Agent submission template | Small | Quality gates for new agent PRs | Skipped | Submission quality gate pattern transferable |
| .github/ISSUE_TEMPLATE/bug_report.yml | Bug template | Small | Standard | Skipped | None |
| .github/ISSUE_TEMPLATE/feature_request.yml | Feature template | Small | Standard | Skipped | None |
| .github/ISSUE_TEMPLATE/config.yml | Template config | Small | Standard | Skipped | None |
| .github/ISSUE_TEMPLATE/moderation_report.yml | Moderation | Small | Standard | Skipped | None |
| .gitignore | Git ignore | Small | Standard | Skipped | None |
| plugins/plugin-eval/src/plugin_eval/engine.py | Eval engine | Large | DIMENSION_WEIGHTS, LAYER_BLENDS, composite formula, layer coordination | Read | n/a |
| plugins/plugin-eval/src/plugin_eval/parser.py | Parser | Medium | ParsedSkill/ParsedAgent dataclasses, MNA count regex, cross_reference detection | Read | n/a |
| plugins/plugin-eval/src/plugin_eval/static.py | Static analyzer | Medium | Anti-pattern detection implementation | Failed (path not found) | Threshold values covered by plugin-eval.md docs |
| plugins/plugin-eval/src/plugin_eval/models.py | Pydantic models | Medium | Badge thresholds, EvalConfig, DimensionScore | Skipped | Badge thresholds confirmed in docs |
| plugins/plugin-eval/src/plugin_eval/elo.py | Elo calculator | Small | K=32, initial=1500, bootstrap CI 500 resamples | Skipped | Elo parameters transferable |
| plugins/plugin-eval/src/plugin_eval/stats.py | Statistics | Small | Wilson CI, Bootstrap, Clopper-Pearson implementations | Skipped | Pure Python, no scipy/numpy |
| plugins/plugin-eval/src/plugin_eval/corpus.py | Corpus management | Small | Gold standard index for Elo | Skipped | Corpus pattern transferable |
| plugins/plugin-eval/src/plugin_eval/reporter.py | Report generation | Small | JSON/Markdown/HTML output formats | Skipped | Report format transferable |
| plugins/plugin-eval/src/plugin_eval/cli.py | CLI | Small | score/certify/compare/init commands | Skipped | CLI structure transferable |
| plugins/plugin-eval/tests/conftest.py | Test config | Small | pytest fixtures | Skipped | Test patterns transferable |
| plugins/plugin-eval/tests/test_engine.py | Engine tests | Medium | Composite scoring tests | Skipped | Test patterns for scoring formula |
| plugins/plugin-eval/tests/test_static.py | Static tests | Medium | Anti-pattern detection tests, threshold edge cases | Skipped | Boundary coverage tests for anti-patterns |
| plugins/plugin-eval/tests/test_judge.py | Judge tests | Small | LLM judge tests | Skipped | Domain-specific |
| plugins/plugin-eval/tests/test_monte_carlo.py | MC tests | Small | Monte Carlo tests | Skipped | Domain-specific |
| plugins/plugin-eval/tests/test_models.py | Model tests | Small | Pydantic model tests | Skipped | None |
| plugins/plugin-eval/tests/test_parser.py | Parser tests | Medium | Parsing edge cases | Skipped | Edge cases transferable |
| plugins/plugin-eval/tests/test_reporter.py | Reporter tests | Small | Output format tests | Skipped | None |
| plugins/plugin-eval/tests/test_corpus.py | Corpus tests | Small | Elo corpus tests | Skipped | None |
| plugins/plugin-eval/tests/test_elo.py | Elo tests | Small | Elo rating tests | Skipped | None |
| plugins/plugin-eval/tests/test_stats.py | Statistics tests | Small | Wilson CI etc | Skipped | None |
| plugins/plugin-eval/tests/test_e2e.py | E2E tests | Medium | End-to-end tests against real plugins | Skipped | E2E test pattern transferable |
| plugins/plugin-eval/tests/test_cli.py | CLI tests | Small | CLI integration tests | Skipped | None |
| plugins/conductor/README.md | Conductor plugin | Medium | Context→Spec→Implement pipeline, artifacts, workflow | Read | n/a |
| plugins/conductor/commands/setup.md | Setup command | Small | Interactive initialization flow | Skipped | Sequential Q&A setup pattern transferable |
| plugins/conductor/commands/new-track.md | New track command | Small | Feature track creation with spec.md + plan.md | Skipped | Spec+plan generation pattern |
| plugins/conductor/commands/implement.md | Implement command | Small | TDD red-green-refactor enforcement | Skipped | Verification checkpoint pattern |
| plugins/conductor/commands/revert.md | Revert command | Small | Git-aware logical revert | Skipped | Semantic revert pattern |
| plugins/conductor/commands/status.md | Status command | Small | Project progress display | Skipped | None |
| plugins/conductor/commands/manage.md | Manage command | Small | Track lifecycle management | Skipped | Archive/restore pattern |
| plugins/conductor/templates/track-metadata.json | Track metadata schema | Small | JSON schema for track data | Skipped | Schema pattern transferable |
| plugins/conductor/templates/spec.md | Spec template | Small | Requirements template format | Skipped | Spec format may match our task-card |
| plugins/conductor/templates/plan.md | Plan template | Small | Phased plan format | Skipped | Plan format may match wave-plan |
| plugins/conductor/templates/product.md | Product template | Small | Product vision format | Skipped | Product context layer |
| plugins/conductor/templates/tech-stack.md | Tech stack template | Small | Tech preferences format | Skipped | Project context artifact |
| plugins/conductor/templates/tracks.md | Tracks registry template | Small | Track listing format | Skipped | Registry pattern |
| plugins/conductor/templates/workflow.md | Workflow template | Small | Dev practices format | Skipped | Workflow documentation |
| plugins/conductor/templates/index.md | Navigation hub | Small | Cross-reference hub | Skipped | Index pattern |
| plugins/agent-teams/README.md | Agent Teams plugin | Medium | Multi-agent orchestration, file ownership, team presets | Read | n/a |
| plugins/agent-teams/agents/team-lead.md | Team lead agent | Medium | Orchestration strategy, task decomposition | Skipped | Task decomposition + arbitration patterns |
| plugins/agent-teams/agents/team-reviewer.md | Team reviewer agent | Small | Multi-dimensional review | Skipped | Review dimension allocation |
| plugins/agent-teams/agents/team-debugger.md | Team debugger agent | Small | Hypothesis investigator | Skipped | Evidence-based falsification protocol |
| plugins/agent-teams/agents/team-implementer.md | Team implementer | Small | File-ownership-bounded builder | Skipped | File ownership constraint pattern |
| plugins/agent-teams/commands/team-spawn.md | Team spawn command | Small | Team preset spawning | Skipped | Preset team patterns |
| plugins/agent-teams/commands/team-review.md | Team review command | Small | Multi-reviewer orchestration | Skipped | None |
| plugins/agent-teams/commands/team-debug.md | Team debug command | Small | Hypothesis-driven debugging | Skipped | Competing-hypotheses protocol |
| plugins/agent-teams/commands/team-feature.md | Team feature command | Small | Parallel feature development | Skipped | None |
| plugins/agent-teams/commands/team-delegate.md | Team delegate command | Small | Task delegation dashboard | Skipped | None |
| plugins/agent-teams/commands/team-status.md | Team status command | Small | Progress display | Skipped | None |
| plugins/agent-teams/commands/team-shutdown.md | Team shutdown command | Small | Graceful shutdown | Skipped | None |
| plugins/tdd-workflows/agents/tdd-orchestrator.md | TDD orchestrator | Large | AI-generated capability list, no decision rules | Read | Negative example: bloated agent anti-pattern |
| plugins/api-scaffolding/agents/*.md | API scaffolding agents | Small | Django/FastAPI specific | Skipped | None (domain-specific) |
| plugins/c4-architecture/agents/*.md | C4 diagram agents | Small | Context/container/component/code | Skipped | C4 decomposition hierarchy transferable |
| plugins/codebase-cleanup/agents/code-reviewer.md | Code reviewer | Small | Code review agent | Skipped | None |
| plugins/debugging-toolkit/agents/*.md | Debug agents | Small | Debugger, DX optimizer | Skipped | None |
| plugins/error-debugging/agents/debugger.md | Error debugger | Small | Error debugging | Skipped | None |
| plugins/error-diagnostics/agents/debugger.md | Error diagnostics | Small | Error diagnostics | Skipped | None |
| plugins/git-pr-workflows/agents/code-reviewer.md | PR code reviewer | Small | PR review agent | Skipped | None |
| plugins/git-pr-workflows/commands/pr-enhance.md | PR enhancement | Small | PR workflow | Skipped | None |
| plugins/jvm-languages/agents/*.md | JVM agents | Small | Java/Scala/C# | Skipped | None (domain) |
| plugins/llm-application-dev/README.md | LLM dev plugin | Medium | LangGraph, RAG, vector search | Skipped | LLM eval patterns transferable |
| plugins/python-development/agents/*.md | Python agents | Small | Python/Django/FastAPI | Skipped | None (domain) |
| plugins/shell-scripting/agents/bash-pro.md | Bash agent | Small | Shell scripting | Skipped | None (domain) |
| plugins/systems-programming/agents/*.md | Systems agents | Small | Rust/Go/C/C++ | Skipped | None (domain) |
| plugins/ui-design/agents/*.md | UI design agents | Small | UI designer, accessibility | Skipped | Accessibility criteria list transferable |
| plugins/unit-testing/agents/*.md | Test agents | Small | Debugger, test-automator | Skipped | None |
| plugins/web-scripting/agents/*.md | Web scripting | Small | PHP/Ruby | Skipped | None (domain) |
| plugins/meigen-ai-design/commands/*.md | Meigen design | Small | Find/gen commands | Skipped | None |
| plugins/incident-response/agents/debugger.md | Incident debugger | Small | Incident response | Skipped | None |
| tools/yt-design-extractor.py | YouTube design tool | Small | External tool | Skipped | None |
| tools/requirements.txt | Tool deps | Small | requests | Skipped | None |

**Directory-level skip decisions:** None — every directory was surveyed and each file assigned to a row before scope decisions.

---

## Step 1c — Connection Map

```
[parser.py: parse_skill()] --ParsedSkill--> [engine.py: EvalEngine] --ParsedSkill--> [static.py: StaticAnalyzer]
[parser.py: parse_skill()] --ParsedSkill--> [judge.py: JudgeAnalyzer]
[parser.py: parse_skill()] --ParsedSkill--> [monte_carlo.py: MonteCarloAnalyzer]

[engine.py: DIMENSION_WEIGHTS dict] + [engine.py: LAYER_BLENDS dict] --blend formula--> [CompositeResult.score]
  Breaking: if a dimension added to DIMENSION_WEIGHTS but not LAYER_BLENDS, it defaults to static-only weights

[static.py] --LayerResult (layer="static", sub_scores={frontmatter_quality, orchestration_wiring, ...})--> [engine.py: _build_composite()]
[judge.py] --LayerResult (layer="judge", sub_scores={triggering_accuracy, orchestration_fitness, output_quality, scope_calibration})--> [engine.py]
[monte_carlo.py] --LayerResult (layer="monte_carlo", sub_scores={triggering:{activation_rate}, output_consistency:{mean_quality}, failure_rate:{p_fail}, token_efficiency:{efficiency_norm}})--> [engine.py: _normalize_mc_scores()]
  Breaking: if MC renames triggering.activation_rate, _normalize_mc_scores() silently reads 0.0

[.claude-plugin/marketplace.json] --plugin_paths--> [runtime Claude Code plugin loader]
  Skills registered as directory paths (./skills/skill-name), not SKILL.md paths
  Breaking: if skill directory renamed without updating marketplace.json, it goes unresolved

[conductor/commands/setup.md] --writes--> [conductor/product.md, tech-stack.md, workflow.md]
[conductor/commands/new-track.md] --reads--> [conductor/product.md, tech-stack.md] --generates--> [tracks/<id>/spec.md, plan.md]
  Breaking: if product.md absent, new-track generates generic specs with no project context

[agent-teams/agents/team-lead.md] --assigns file boundaries--> [team-implementer.md x N]
  Breaking: file boundary violation causes parallel merge conflicts (protocol-enforced only, no technical barrier)
```

---

## Dimension 1 — Behavior (Operational Detail)

**Plugin-eval composite formula (engine.py):**
```python
# DIMENSION_WEIGHTS (must sum to 1.0)
triggering_accuracy: 0.25, orchestration_fitness: 0.20, output_quality: 0.15,
scope_calibration: 0.12, progressive_disclosure: 0.10, token_efficiency: 0.06,
robustness: 0.05, structural_completeness: 0.03, code_template_quality: 0.02, ecosystem_coherence: 0.02

# Anti-pattern penalty formula
penalty = max(0.5, 1.0 - 0.05 × count)  # floor at 50%, each flag costs 5%

# Composite
Final = Σ(dimension_weight / measured_weight_sum × blended_score) × 100 × penalty
# unmeasured dimensions get -1.0 sentinel; excluded from denominator
```

**Anti-pattern detection thresholds:**
- OVER_CONSTRAINED: >15 MUST/ALWAYS/NEVER occurrences → 10% penalty
- EMPTY_DESCRIPTION: description <20 characters → 10% penalty
- MISSING_TRIGGER: no "Use when…" phrase in description → 15% penalty (largest)
- BLOATED_SKILL: >800 lines without a references/ directory → 10% penalty
- ORPHAN_REFERENCE: dead link to a file in references/ → 5% penalty
- DEAD_CROSS_REF: cross-reference to non-existent skill/agent → 5% penalty

**Static analysis sub-checks and weights:**
- frontmatter_quality: 35% (name, description length, "Use when" trigger, "Use PROACTIVELY" signal)
- orchestration_wiring: 25% (output/input docs, code examples, orchestrator anti-pattern detection)
- progressive_disclosure: 15% (200-600 line sweet spot, presence of references/ and assets/)
- structural_completeness: 10% (heading density, code blocks, examples section, troubleshooting section)
- token_efficiency: 10% (MUST/NEVER/ALWAYS density, duplicate-line detection)
- ecosystem_coherence: 5% (cross-references to other skills/agents, "related"/"see also" mentions)

**Layer blend weights (per dimension, renormalized when layers missing):**
- triggering_accuracy: static=0.15, judge=0.25, monte_carlo=0.60 (MC-dominant)
- orchestration_fitness: static=0.10, judge=0.70, monte_carlo=0.20 (judge-dominant)
- output_quality: static=0.00, judge=0.40, monte_carlo=0.60 (never from static alone)
- scope_calibration: static=0.30, judge=0.55, monte_carlo=0.15
- progressive_disclosure: static=0.80, judge=0.20, monte_carlo=0.00 (static-dominant)
- token_efficiency: static=0.40, judge=0.10, monte_carlo=0.50
- robustness: static=0.00, judge=0.20, monte_carlo=0.80
- structural_completeness: static=0.90, judge=0.10, monte_carlo=0.00
- code_template_quality: static=0.30, judge=0.70, monte_carlo=0.00
- ecosystem_coherence: static=0.85, judge=0.15, monte_carlo=0.00

**LLM Judge protocol (Layer 2):**
- triggering_accuracy: Haiku generates 10 synthetic prompts (5 should-trigger, 5 should-not), computes F1
- orchestration_fitness: 5-point anchored rubric (worker vs orchestrator role)
- output_quality: 3 realistic task simulations
- scope_calibration: 5-point anchored rubric
- All 4 run concurrently via semaphore-based throttling (max_concurrency=4 default)

**Monte Carlo (Layer 3):**
- Haiku generates 15 varied prompts; runs N simulations (50=deep, 100=thorough)
- Wilson score CI for activation rate (small-sample binomial)
- Bootstrap CI 1000 resamples for output consistency
- Clopper-Pearson exact CI for failure rate
- Token efficiency: median against 8000-token cap, normalized

**Elo system:**
- Initial rating: 1500, K-factor: 32
- Bootstrap CI: 500 resamples
- Reference selection: category match + approximate line count match
- Formula: E(A) = 1 / (1 + 10^((Rb - Ra) / 400))

**Badge thresholds (score AND Elo required when Elo available):**
- Platinum: score ≥90 + Elo ≥1600
- Gold: score ≥80 + Elo ≥1500
- Silver: score ≥70 + Elo ≥1400
- Bronze: score ≥60 + Elo ≥1300

**Three-tier progressive disclosure sweet spots:**
- Metadata (frontmatter): always loaded, ~1024 char max for description
- Instructions (SKILL.md body): 200-600 lines is sweet spot; >800 without refs/ = BLOATED_SKILL
- Resources (references/ and assets/): loaded on demand, unlimited

**Conductor pipeline order (enforced by command structure):**
1. `/conductor:setup` — Interactive Q&A, creates product.md + tech-stack.md + workflow.md
2. `/conductor:new-track` — Reads context files, generates spec.md + plan.md per feature track
3. `/conductor:implement` — TDD red-green-refactor cycle with verification checkpoints, reads plan.md
4. Revert by git commit association with track/phase/task ID

---

## Dimension 2 — Format (Identifier Level)

**Agent frontmatter schema:**
```yaml
name: agent-name              # hyphen-case, required
description: "..."            # required, includes "Use PROACTIVELY when [trigger]"
model: opus|sonnet|haiku|inherit  # required
color: blue|green|red|yellow|cyan|magenta  # optional
tools: Read, Grep, Glob       # optional, comma-separated, restricts tool access
```

**Skill frontmatter schema:**
```yaml
name: skill-name              # hyphen-case, required
description: "Use this skill when [specific trigger conditions]."  # required, <1024 chars
```

**ParsedSkill dataclass fields (parser.py):**
`path, name, description, line_count, h2_count, h3_count, code_block_count, code_block_languages: list[str], has_examples: bool, has_troubleshooting: bool, has_references: bool, has_assets: bool, reference_files: list[str], asset_files: list[str], total_content_lines: int, must_never_always_count: int, cross_references: list[str], raw_content: str, frontmatter: dict`

**ParsedAgent dataclass fields:**
`path, name, description, model: str|None, has_tools_restriction: bool, tools: list[str], has_proactive_trigger: bool, skill_references: list[str], raw_content: str, frontmatter: dict`

**MNA regex pattern (parser.py line 93):** `re.compile(r"\b(MUST|NEVER|ALWAYS)\b")`

**Cross-reference pattern (parser.py line 96):** `re.findall(r"(?:skill|skills)/([a-z0-9-]+)", body)`

**Proactive trigger detection:** `re.search(r"use proactively", description, re.IGNORECASE)`

**Examples detection:** `re.search(r"(## example|### example|## usage)", lower_body)`

**Troubleshooting detection:** `re.search(r"(## troubleshoot|## common issue|## faq)", lower_body)`

**plugin.json (auto-discovery):** `{ "name": "plugin-name" }` — only name required

**marketplace.json entry format:**
```json
{ "name": "plugin-name", "skills": ["./skills/skill-name"] }
```
Skills are directory references, not file paths. Agents auto-discovered from agents/ dir.

**Letter grade thresholds:** A+ ≥97, A ≥93, A- ≥90, B+ ≥87, B ≥83, B- ≥80, C+ ≥77, C ≥73, C- ≥70, D+ ≥67, D ≥63, D- ≥60, F <60

**Conductor track artifacts layout:**
```
conductor/
├── index.md, product.md, product-guidelines.md, tech-stack.md, workflow.md, tracks.md
├── setup_state.json
├── code_styleguides/
└── tracks/<track-id>/
    ├── spec.md, plan.md, metadata.json, index.md
```

---

## Dimension 3 — Interactions (Contract Level)

**engine.py ← parser.py contract:**
Producer: `parse_skill(skill_dir)` → `ParsedSkill`. Consumer: `EvalEngine._static.analyze_skill(skill)`. If `must_never_always_count` field renamed in ParsedSkill, static.py reads wrong count (silent failure, not type error).

**engine.py ← static.py contract:**
Producer: `StaticAnalyzer.analyze_skill()` → `LayerResult(layer="static", sub_scores={frontmatter_quality, orchestration_wiring, structural_completeness, progressive_disclosure, token_efficiency, ecosystem_coherence})`. Mapping table `STATIC_TO_DIMENSION` in engine.py maps these to dimension names. If static adds a new sub-score not in STATIC_TO_DIMENSION, it is silently ignored.

**engine.py ← monte_carlo.py contract:**
MC sub_scores are nested: `{triggering: {activation_rate: float}, output_consistency: {mean_quality: float}, failure_rate: {p_fail: float}, token_efficiency: {efficiency_norm: float}}`. `_normalize_mc_scores()` extracts these. If MC renames any key, the normalized score silently becomes 0.0.

**Renormalization contract:** When a dimension has no data from any layer, it gets score -1.0 (sentinel) and is excluded from the measured_weight_sum denominator. This means a quick eval (Layer 1 only) scores as if 6 dimensions don't exist; the other 4 dimension weights are renormalized to sum to 1.0.

**marketplace.json → runtime:** Skills registered as `./skills/skill-name` (directory). Parser auto-discovers by checking `<dir>/SKILL.md`. Renaming the directory without updating marketplace.json produces a 404-style silent miss.

**Conductor context chain:** `setup.md` writes `product.md` + `tech-stack.md`. `new-track.md` reads these before generating `spec.md`. If user runs `new-track` before `setup`, the Q&A context is absent and spec is generic. `implement.md` reads `plan.md` per track. `revert.md` uses git commit messages tagged with `[track-id]` pattern for semantic revert.

---

## Reference Type and Maturity

- **Type:** Production plugin marketplace + embedded quality evaluation framework
- **Maturity signals:** plugin-eval has 13 pytest test files, pydantic models, CI via .github/, Smithery marketplace badge with real usage
- **Red flags:**
  1. Model names hardcoded throughout all agent files and CLAUDE.md (I6 violation territory)
  2. Count inconsistencies across docs (75 vs 67 plugins, 147 vs 107 vs 129 skills — never synchronized)
  3. tdd-orchestrator is AI-generated capability-list bloat with zero decision rules
  4. agentskills.io URL cited as canonical spec — unverified, possibly speculative
  5. agent-teams requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env var — experimental API

---

## Section 1 — Reference Summary

**What type:** A production Claude Code plugin marketplace paired with a Python-based skill quality evaluation framework. The marketplace is the delivery vehicle; plugin-eval is the intellectually interesting component — a three-layer quality measurement system with statistical rigor (Wilson CI, Bootstrap CI, Clopper-Pearson), Elo ranking, and 6 named anti-pattern flags with exact thresholds.

**Behavioral content:** Plugin-eval encodes a complete skill quality judgment pipeline: static structural analysis (6 sub-checks, weighted), LLM semantic evaluation (4 dimensions, 5-point rubrics), Monte Carlo statistical reliability (N simulations, Wilson/Bootstrap/Clopper-Pearson CIs). Anti-pattern taxonomy with multiplicative penalty math. Badge thresholds. Three-tier progressive disclosure philosophy with explicit line-count sweet spots (200-600 body, >800=bloated).

**Structural content:** Each plugin is self-contained (agents/, commands/, skills/). marketplace.json is the single registry. Frontmatter schemas are minimal (name + description required). Skills registered as directories, not files. Plugin.json requires only `name`.

**Interaction content:** engine.py coordinates all three layers via a ParsedSkill data contract from parser.py. Layer results each return LayerResult with explicit field contracts. Renormalization ensures partial evaluations (fewer layers) still produce valid scores. Conductor establishes a context chain (product.md → spec.md → plan.md) where each artifact feeds the next command.

**Maturity:**
- Mature: plugin-eval (test suite, pydantic, CI), marketplace structure
- Functional: conductor, agent-teams
- Experimental: agent-teams (experimental API flag required)
- Stale/inconsistent: documentation counts, model names will age poorly
- Red flag: tdd-orchestrator shows AI-generated bloat is present in this corpus

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| docs/plugin-eval.md, engine.py | 6 anti-pattern taxonomy with exact thresholds (OVER_CONSTRAINED >15, MISSING_TRIGGER, BLOATED_SKILL >800, ORPHAN_REFERENCE, DEAD_CROSS_REF, EMPTY_DESCRIPTION <20) | Adds named, threshold-bounded anti-pattern classification to WabbleSpec quality-floor-check.py. Currently we have INLINE_DANGER and similar but not this set. | Add 4 new check classes to quality-floor-check.py (ORPHAN_REFERENCE, DEAD_CROSS_REF not yet present; OVER_CONSTRAINED threshold to confirm vs existing; BLOATED_SKILL naming). MISSING_TRIGGER partially covered by existing negative-triggers rule. | High |
| engine.py DIMENSION_WEIGHTS + LAYER_BLENDS, docs/plugin-eval.md | 10-dimension scoring formula with badge thresholds (Platinum ≥90, Gold ≥80, Silver ≥70, Bronze ≥60) and letter grades | Converts quality-floor-check.py from pass/fail to a continuous quality signal with dimension breakdown. Enables prioritizing improvement work by lowest-scoring dimension. | Add `--score` mode to quality-floor-check.py that produces dimension scores using the static sub-checks we already run, mapped through DIMENSION_WEIGHTS. Output badge + letter grade. | High |
| parser.py ParsedSkill fields | Production-tested SKILL.md parsing patterns: MNA regex `\b(MUST|NEVER|ALWAYS)\b`, cross_ref detection `(?:skill|skills)/([a-z0-9-]+)`, troubleshooting section `## troubleshoot|## common issue|## faq` | Our quality-floor-check.py likely uses similar patterns but these are production-hardened from a test suite. Cross-check and adopt any missing detection patterns. | Compare regex patterns in parser.py against quality-floor-check.py. Port any missing or divergent patterns. | Medium |
| docs/plugin-eval.md progressive_disclosure sub-check | 200-600 line sweet spot for SKILL.md body; BLOATED_SKILL name for >800 without refs/ | WabbleSpec CLAUDE.md says "<500 lines" soft limit but has no lower bound and no named flag for violations. Adding the named anti-pattern and explicit lower bound tightens authoring guidance. | Update CLAUDE.md skill authoring conventions: add "200-600 lines sweet spot" and "BLOATED_SKILL: >800 lines without Tier 3 refs/ = anti-pattern." | Medium |
| docs/plugin-eval.md Layer 2 triggering_accuracy method | F1-based triggering accuracy: generate 5 should-trigger + 5 should-not prompts, compute F1 over activation decisions | skill-tdd already has negative routing eval entries; adding F1 as a metric makes triggering quality quantifiable rather than binary pass/fail per case. | Add F1 calculation to skill-tdd SKILL.md eval harness instructions (section covering eval set reporting). | Medium |
| docs/architecture.md model tier criteria | Capability-type classification for task assignment (critical architecture/security/code review → highest capability; fast operational → fastest tier) | model-router SKILL.md can use these task-type categories as capability signals without naming models (I6 compliant). | Extract task-type classification criteria (not model names) into model-router references/task-capability-matrix.md. | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| README.md, CLAUDE.md, all agent files | Model names hardcoded (model: opus\|sonnet\|haiku) throughout | I6 violation if adopted verbatim. Any pattern copied from agent frontmatter examples brings model names into framework. | Never copy frontmatter examples literally. Adopt capability tier concept using our own descriptors. | High |
| docs/agent-skills.md, architecture.md | agentskills.io URL cited as canonical Agent Skills Specification | URL may be speculative or dead. If cited as a WabbleSpec reference, it creates a dangling reference in our docs. | Do not adopt as citation. Use actual Anthropic docs URL if needed. | Medium |
| plugins/tdd-workflows/agents/tdd-orchestrator.md | AI-generated capability-list agent pattern (10 sections, 180 lines, zero decision rules) | Represents exactly the anti-pattern WabbleSpec CLAUDE.md prohibits: agents that list what they can do without saying how decisions are made. Could be confused for "good agent authoring." | Treat as a negative example. Use plugin-eval's own MISSING_TRIGGER and OVER_CONSTRAINED checks to demonstrate the problem. | Medium |
| README.md, docs/*.md count inconsistencies | Doc counts disagree across files (75 vs 67 plugins, 147 vs 107 vs 129 skills) | Any specific statistics cited from this reference into WabbleSpec docs will be wrong at the time of reading. | Never adopt counts. Adopt only structural patterns and threshold values. | Low |
| docs/plugin-eval.md Layers 2+3 | LLM judge + Monte Carlo require claude-agent-sdk dependency | Cannot directly port Layers 2/3 without the dependency or an equivalent agent dispatch mechanism. | Port only Layer 1 (static analysis) initially. Use our existing skill-tdd infrastructure for Layer 2 analog. | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Anti-pattern taxonomy: OVER_CONSTRAINED, MISSING_TRIGGER, BLOATED_SKILL >800, ORPHAN_REFERENCE, DEAD_CROSS_REF, EMPTY_DESCRIPTION | Adapt | Production-tested thresholds; additive to existing checks; exact flag names are transferable | quality-floor-check.py | P1 |
| 10-dimension scoring formula + badge thresholds + letter grades | Adapt | Converts quality from pass/fail to continuous signal; all math is threshold-based, no vendor dependency | quality-floor-check.py --score mode | P1 |
| 200-600 line sweet spot + BLOATED_SKILL name in CLAUDE.md | Adapt | Tightens existing <500 soft limit with named anti-pattern and lower bound | CLAUDE.md skill authoring section | P1 |
| parser.py regex patterns (MNA, cross_ref, has_troubleshooting) | Adapt | Production-tested; cross-check against quality-floor-check.py for divergences | quality-floor-check.py | P2 |
| F1-based triggering accuracy eval | Adapt | Makes eval set reporting quantitative, builds on existing skill-tdd negative routing cases | skill-tdd SKILL.md | P2 |
| Task-type capability classification criteria | Adapt (carefully) | Capability types transferable; model names are not | model-router SKILL.md | P3 |
| Agent frontmatter with model: opus\|sonnet\|haiku | Avoid | I6 violation | n/a | DO NOT COPY |
| agentskills.io URL | Avoid | Speculative/unverified URL | n/a | DO NOT COPY |
| tdd-orchestrator agent style (capability lists) | Avoid | AI-generated bloat; violates CLAUDE.md authoring rules | n/a | DO NOT COPY |
| Conductor full adoption | Study Only | Conflicts with existing wave-plan/task-card approach; some template patterns interesting | n/a | P4 |
| Agent Teams full adoption | Study Only | Requires experimental API; file-ownership-boundary pattern interesting for parallel waves | n/a | P4 |
| Plugin-eval Layers 2+3 (LLM judge, Monte Carlo) | Study Only | Dependency requirement; our skill-tdd is the analog | n/a | P4 |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Plugin-eval's quality philosophy maps directly onto WabbleSpec quality gates. Anti-patterns are named and threshold-bounded exactly as our CLAUDE.md rules prefer. |
| Architecture fit | 7 | ParsedSkill data model parallels what quality-floor-check.py already does. Scoring formula is portable. Dimensions map onto checks we already run. |
| Implementation fit | 8 | Layer 1 (static) is pure Python, no external dependencies. Directly portable into quality-floor-check.py as new check classes and a scoring mode. |
| Maintenance fit | 6 | Threshold values (>15, >800, <200, <20) will need periodic review. Adding a scoring mode increases quality-floor-check.py complexity. |
| Risk level | 3 | Main risk is I6 compliance when copying examples. Static scoring has no vendor dependency. All math is threshold arithmetic. |
| Overall usefulness | 7 | Worth active use — specifically plugin-eval static analysis taxonomy, scoring formula, and CLAUDE.md authoring convention additions. |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 — Safe additions (no risk, pure additive):**
- P1.1: Port 4 anti-pattern checks into quality-floor-check.py: ORPHAN_REFERENCE, DEAD_CROSS_REF (not currently present), confirm OVER_CONSTRAINED threshold (>15 MNA), name BLOATED_SKILL for the >800-line case
- P1.2: Add "200-600 line sweet spot" and "BLOATED_SKILL: >800 lines without refs/ = anti-pattern" to CLAUDE.md skill authoring conventions

**Phase 2 — Low-risk adaptation:**
- P2.1: Add `--score` mode to quality-floor-check.py: map existing static sub-checks → 6 measurable dimensions → weighted composite → badge + letter grade output
- P2.2: Cross-check MNA regex, cross_ref detection, has_troubleshooting detection against quality-floor-check.py; port any divergences

**Phase 3 — Deeper integration (requires more design):**
- P3.1: Add F1 calculation to skill-tdd SKILL.md eval harness (requires eval sets with both positive and negative entries)
- P3.2: Extract task-type capability classification criteria into model-router references/

**Phase 4 — Do Not Cross:**
- Model names in any framework file (I6)
- Agent content from domain-specific or AI-generated agents (tdd-orchestrator pattern)
- agentskills.io URL as citation

---

## Section 7 — Final Verdict

**Classification: supporting-reference (7/10)**

**Best 3 to adapt:**
1. Anti-pattern taxonomy with exact thresholds (docs/plugin-eval.md + engine.py) — OVER_CONSTRAINED >15, MISSING_TRIGGER, BLOATED_SKILL >800, ORPHAN_REFERENCE. Directly port to quality-floor-check.py as 4 new named checks.
2. 10-dimension scoring formula with DIMENSION_WEIGHTS and badge thresholds (engine.py) — Converts quality gate from pass/fail to a continuous quality signal with actionable dimension breakdown.
3. 200-600 line sweet spot codification (docs/plugin-eval.md) — Adds an explicit lower bound and a named anti-pattern (BLOATED_SKILL) to complement our existing <500 soft limit in CLAUDE.md.

**Worst 3 to avoid:**
1. Model names in agent frontmatter (README.md, architecture.md, all agent files) — I6 violation.
2. agentskills.io URL as canonical citation (docs/agent-skills.md) — Unverified, potentially speculative.
3. tdd-orchestrator agent pattern (plugins/tdd-workflows/agents/tdd-orchestrator.md) — 180 lines of capability lists, zero decision rules, AI-generated bloat.

**Recommended next action:** Implement Phase 1 items. Anti-pattern taxonomy and CLAUDE.md convention update are both low-risk and immediately actionable.

---

## Section 8 — Project Synthesis

WabbleSpec has quality-floor-check.py (pass/fail, 30 checks), wave-review daemon (semantic diff checking), and the ref-eval pipeline (qualitative scoring). Combining with plugin-eval's dimensional scoring framework:

| What | Reference contribution | Project contribution | Target (exact file) | Gap closed |
|---|---|---|---|---|
| Ref-eval dimensional scoring | 10-dimension weights + badge thresholds + composite formula from engine.py | ref-eval Section 5 Integration Fit already has 6 1-10 scores per dimension | `.claude/skills/ref-eval/SKILL.md` → add "Composite Score" to Section 5 output | Section 5 scores are currently subjective; formula makes them reproducible and comparable across sessions |
| Wave-review anti-pattern gate | OVER_CONSTRAINED + MISSING_TRIGGER + BLOATED_SKILL + ORPHAN_REFERENCE flags with penalty math from plugin-eval | wave-review.py already parses skill diffs; verifier already has REVISE cycle | `.wabblespec/engine/modules/l6/verifier/SKILL.md` → add anti-pattern check before PASS verdict | Wave output SKILL.md files currently checked for semantic correctness, not skill-quality anti-patterns |
| L8 promotion quality gate | Badge threshold Bronze ≥60 as minimum quality before L8 promotion | Instinct → Synth → Blueprint evolution chain already exists; promotion gates on attestation | `.claude/skills/instinct/SKILL.md` → add "proposed SKILL.md must score Bronze (≥60 static quality) before Synth promotion" | L8 evolution gates on evidence and attestation but not on resulting skill quality score |

---

## Section 9 — Expansion Opportunities

Per-skill growth scan results:

**Plugin marketplace install system:** WabbleSpec has wabblespec.yaml as module registry but no installable marketplace. The selective skill preloading via `--filter-recipe` partially addresses this. Not a Tier 7 candidate — already addressed.

**C4 architecture diagram generation:** WabbleSpec has no diagram generation capability at any layer. The c4-architecture plugin (4 agents for context/container/component/code levels) represents a net-new output type.

| Capability | Reference location | Why the project lacks it | What it would unlock | Dependencies | Effort | Tier 7? |
|---|---|---|---|---|---|---|
| Automated skill quality scoring CLI (Layer 1 static) | docs/plugin-eval.md + engine.py + parser.py | quality-floor-check.py does pass/fail only; no continuous score, no badge, no CI threshold flag | CI-gatable quality gate for skills; prioritization of improvement work by dimension score | Pure Python, no deps beyond yaml/re | days | Yes |
| Elo relative skill ranking | docs/plugin-eval.md Elo section + elo.py | No relative ranking across 121 WabbleSpec skills | Identifies lowest-quality skills for focused improvement; tracks quality trend over versions | quality-score.py (above) as prerequisite | weeks | Yes |
| LLM judge for skill semantic evaluation | docs/plugin-eval.md Layer 2 + judge.py | skill-tdd tests triggering; no rubric-based semantic evaluation of orchestration_fitness or output_quality | Catches skills that pass structural checks but produce poor output or wrong role behavior | claude API or existing skill-tdd agent dispatch | weeks | Yes |
| C4 architecture diagram generation | plugins/c4-architecture/agents/c4-{context,container,component,code}.md | No diagram output module in WabbleSpec at any layer | Generates C4 docs from codebases; would complement gateway-document | visualize SKILL.md exists but produces charts, not C4 diagrams | weeks | Yes |
| Conductor-style product context layer | plugins/conductor/ (product.md, tech-stack.md, tracks.md pattern) | WabbleSpec has scope.md + task-card.md but no persistent product vision or tech preferences as managed artifacts | Product-context-aware task cards; reduces repeated context questions in new sessions | scope-frame SKILL.md would need extension | months | No — adapts existing module |

**Gateway bundling signal:** Items 1, 2, 3 (quality scoring, Elo ranking, LLM judge) are a natural quality-suite bundle. They share a parser layer, a report format, and a common use case (skill quality measurement). Implementing as a unified `quality-suite` script collection (quality-score.py + quality-rank.py + quality-judge.py) with a shared ParsedSkill data structure reduces integration surface.

**Tier 7 candidates (4):** quality-score.py (Layer 1 static scorer), quality-rank.py (Elo ranking), quality-judge.py (LLM semantic eval), C4 diagram generation.

---

*Report written: 2026-05-31 | ref-adopt pipeline*
