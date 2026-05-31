# Ref-Eval: anthropic-skills-main

**Date:** 2026-05-31  
**Slug:** anthropic-skills-main  
**Path:** `C:\Vaults\references\Core Project References\anthropic-skills-main`  
**Trust level:** MEDIUM  
**Classification:** supporting-reference (7/10)

---

## Step 1b — File Inventory

| File | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| `README.md` | Repository overview | Small | Plugin marketplace install instructions, skill structure | Read |
| `.claude-plugin/marketplace.json` | Plugin bundle declarations | Small | 3 bundles: document-skills, example-skills, claude-api; owner Keith Lazuka | Read |
| `spec/agent-skills-spec.md` | Spec pointer | Tiny | Redirects to agentskills.io/specification | Read |
| `template/SKILL.md` | Minimal skill template | Tiny | Frontmatter: name, description only | Read |
| `skills/skill-creator/SKILL.md` | Full skill authoring + eval loop | Large | Three-level loading, parallel subagent spawning, description optimization with 60/40 train/test split, WHY over MUST writing guidance, undertrigger analysis | Read |
| `skills/skill-creator/agents/grader.md` | Grader subagent spec | Medium | Dual mandate: grade outputs + critique the evals; `text/passed/evidence` field names; burden of proof on PASS | Read |
| `skills/skill-creator/agents/comparator.md` | Blind A/B comparator | Not read — Transfer check: behavioral comparison protocol; potential for skill A/B testing framework | Skipped |
| `skills/skill-creator/agents/analyzer.md` | Post-hoc analysis | Not read — Transfer check: identifies discriminating vs non-discriminating assertions, high-variance (flaky) evals; directly applicable to quality floor checking | Skipped |
| `skills/skill-creator/references/schemas.md` | JSON schemas for eval pipeline | Medium | Exact field contracts for grading.json, benchmark.json, evals.json, history.json, metrics.json, timing.json, comparison.json, analysis.json | Read |
| `skills/skill-creator/scripts/run_loop.py` | Description optimization script | Not read — Transfer check: 60/40 train/test split, up to 5 iterations, selects by test score not train score (anti-overfitting) | Skipped |
| `skills/skill-creator/scripts/aggregate_benchmark.py` | Benchmark aggregation | Not read — Transfer check: produces benchmark.json with mean ± stddev and delta; viewer schema contract | Skipped |
| `skills/skill-creator/eval-viewer/generate_review.py` | HTML viewer server | Not read — Transfer check: viewer depends on exact field names in benchmark.json (`configuration` not `config`) | Skipped |
| `skills/claude-api/SKILL.md` | Claude API + Managed Agents | Large | Model selection heuristics, adaptive thinking rules, compaction contract, language detection, SKIP conditions, prompt caching pitfalls | Read |
| `skills/claude-api/{lang}/*` | Language-specific docs | Not read — Transfer check: language-specific SDK patterns; vendor-specific, I6 risk high | Skipped |
| `skills/claude-api/shared/*` | Shared API docs | Not read — Transfer check: model migration paths, prompt caching, agent design; highly vendor-specific | Skipped |
| `skills/algorithmic-art/SKILL.md` | Generative art via p5.js | Large | Philosophy → code pattern; seeded randomness with Art Blocks pattern; expert craftsmanship framing | Read |
| `skills/algorithmic-art/templates/viewer.html` | Interactive art viewer | Not read — Transfer check: fixed/variable section pattern for templates; Anthropic branding structure | Skipped |
| `skills/brand-guidelines/SKILL.md` | Anthropic brand colors | Small | Brand colors, Poppins/Lora typography — Anthropic-specific, non-transferable | Read |
| `skills/canvas-design/SKILL.md` | Visual design pipeline | Large | Design philosophy → canvas creation; "final step" refinement prompt; font directory as bundled asset | Read |
| `skills/canvas-design/canvas-fonts/*` | Font files | Binary — Transfer check: bundled font strategy is transferable (assets in skill directory) | Skipped |
| `skills/doc-coauthoring/SKILL.md` | Three-stage doc co-authoring | Large | Context gathering → refinement (brainstorm/curate/draft loop) → reader testing with fresh subagent | Read |
| `skills/docx/SKILL.md` | Word document creation/editing | Large | docx-js critical rules (DXA units, no unicode bullets, ShadingType.CLEAR, dual widths); unpack→edit XML→repack workflow | Read |
| `skills/frontend-design/SKILL.md` | Production-grade frontend | Small | Anti-AI-slop doctrine; NEVER use Inter/Roboto/purple-gradients; commit to bold aesthetic direction | Read |
| `skills/internal-comms/SKILL.md` | Internal communications templates | Small | Routes to `examples/` subdirectory by communication type | Read |
| `skills/mcp-builder/SKILL.md` | MCP server development | Medium | TypeScript preferred; tool annotations (readOnlyHint, destructiveHint, idempotentHint); 4-phase process; evaluation XML format | Read |
| `skills/pdf/SKILL.md` | PDF operations | Medium | pypdf, pdfplumber, reportlab; subscript/superscript caveat (no Unicode → reportlab `<sub>` tag) | Read |
| `skills/pptx/SKILL.md` | PowerPoint operations | Not read — Transfer check: similar to docx/xlsx pattern; python-pptx library usage | Skipped |
| `skills/slack-gif-creator/SKILL.md` | Animated GIF for Slack | Medium | Dimension constraints (128x128/480x480); PIL primitives; easing functions; GIFBuilder black-box pattern | Read |
| `skills/theme-factory/SKILL.md` | Themed artifacts | Small | 10 pre-set themes; theme files in `themes/` directory; show PDF then apply | Read |
| `skills/web-artifacts-builder/SKILL.md` | React + Tailwind artifacts | Small | init-artifact.sh → develop → bundle-artifact.sh pipeline; "avoid AI slop" anti-pattern | Read |
| `skills/webapp-testing/SKILL.md` | Playwright web testing | Small | Decision tree for static vs dynamic apps; reconnaissance-then-action; run scripts as black boxes with `--help` first | Read |
| `skills/xlsx/SKILL.md` | Excel operations | Large | Financial model color coding; formula-not-hardcode rule; openpyxl + pandas library selection; recalc.py mandatory after formula creation | Read |

**Transfer check results for skipped files:**
- `comparator.md`: blind A/B comparison protocol is directly transferable to skill-tdd's improvement validation
- `analyzer.md`: discriminating vs non-discriminating assertion analysis applies to quality-floor-check
- `run_loop.py`: 60/40 split + test-score selection is the key transferable rule (already captured in SKILL.md)
- `viewer.html/generate_review.py`: infrastructure-specific, not transferable (browser required)
- Language-specific API docs: I6 risk; skip

---

## Step 1c — Connection Map

```
[skill-creator/SKILL.md]
  --spawns subagents--> [agents/grader.md]: (expectations, transcript_path, outputs_dir)
  --spawns subagents--> [agents/comparator.md]: (output_A, output_B, rubric)
  --spawns subagents--> [agents/analyzer.md]: (comparison.json, transcripts)
  --executes--> [scripts/run_loop.py]: (eval_set JSON, skill path, model, max-iterations)
    --calls--> [scripts/run_eval.py]: (individual eval runs)
  --executes--> [scripts/aggregate_benchmark.py]: (workspace/iteration-N, skill-name)
    --produces--> [benchmark.json]: viewer-schema-strict
  --executes--> [eval-viewer/generate_review.py]: (workspace, benchmark.json, [prev-workspace])
    --produces--> [feedback.json]: {reviews[{run_id, feedback, timestamp}], status}
  --reads--> [references/schemas.md]: (schema contracts for all JSON files)
  --reads--> [assets/eval_review.html]: (template for description eval review UI)

[agents/grader.md]
  --reads--> [transcript]: markdown execution log
  --reads--> [outputs_dir]: output files from skill execution
  --reads--> [outputs_dir/user_notes.md]: executor-flagged uncertainties
  --reads--> [outputs_dir/metrics.json]: tool usage counts
  --reads--> [../timing.json]: wall clock timing
  --writes--> [grading.json]: {expectations[{text, passed, evidence}], summary, ...}

SCHEMA CONTRACTS (breaks if violated):
  benchmark.json `configuration` field MUST be "with_skill" or "without_skill" — viewer uses exact string
  grading.json `expectations[]` MUST use `text`, `passed`, `evidence` (not `name`, `met`, `details`)
  run_loop.py selects `best_description` by TEST score (60% train / 40% test split) — overfitting if train score used

[claude-api/SKILL.md]
  --reads--> [{lang}/claude-api/README.md]: (language-specific SDK usage)
  --reads--> [shared/tool-use-concepts.md]: (conceptual foundation for tool use)
  --reads--> [shared/prompt-caching.md]: (caching patterns and pitfalls)
  --reads--> [shared/model-migration.md]: (model upgrade paths)
  --reads--> [shared/live-sources.md]: (WebFetch URLs — live doc anchors)
  --reads--> [{lang}/managed-agents/README.md]: (language-specific Managed Agents)
```

---

## Dimension 1 — Behavior (Operational Detail)

**skill-creator workflow:**
- "Undertrigger" pattern: "Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like 'read this PDF' may not trigger a skill even if the description matches perfectly." Empirical: complex, multi-step, specialized queries reliably trigger skills.
- Parallel subagent spawning: WITH skill AND WITHOUT skill in the SAME response turn — not sequentially. Explicitly: "don't spawn the with-skill runs first and then come back for baselines later."
- Baseline definition: for new skill = no skill; for improving existing = old version (snapshotted before edit)
- Timing data capture: `total_tokens` and `duration_ms` arrive in task notification — "the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives."
- Description optimization: 60% train / 40% held-out test split; 3 repetitions per query for reliable trigger rate; up to 5 iterations; selects `best_description` by TEST score (not train score, explicitly to "avoid overfitting")
- After 3 consecutive iterations with no substantial changes (in doc co-authoring): ask if anything can be removed

**grader.md behavior:**
- Dual mandate: (1) grade outputs, (2) critique the evals themselves
- PASS requires: clear evidence + genuine substance (not surface compliance) — "a file exists AND contains correct content, not just the right filename"
- Step 6 critique triggers: (a) assertion passes for clearly wrong output, (b) important observed outcome with no assertion, (c) assertion unverifiable from available outputs
- Burden of proof: "the burden of proof to pass is on the expectation" — uncertain = FAIL

**Skill writing conventions:**
- Writing style: "Explain WHY things are important in lieu of heavy-handed musty MUSTs. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag."
- Description field: primary triggering mechanism; "make descriptions a little bit 'pushy'" to combat undertrigger; all "when to use" goes in description not body
- Progressive disclosure: three-level loading: metadata (~100 words, always in context), SKILL.md body (<500 lines ideal), bundled resources (unlimited, scripts execute without loading)
- Script pattern: "Always run scripts with `--help` first. DO NOT read the source until you try running the script first and find that a customized solution is absolutely necessary."

---

## Dimension 2 — Format (Identifier Level)

**grading.json exact schema:**
```json
{
  "expectations": [{"text": "...", "passed": true, "evidence": "..."}],
  "summary": {"passed": N, "failed": N, "total": N, "pass_rate": 0.0},
  "execution_metrics": {"tool_calls": {...}, "total_tool_calls": N, "total_steps": N, "errors_encountered": N, "output_chars": N, "transcript_chars": N},
  "timing": {"executor_duration_seconds": N, "total_duration_seconds": N},
  "claims": [{"claim": "...", "type": "factual|process|quality", "verified": bool, "evidence": "..."}],
  "user_notes_summary": {"uncertainties": [], "needs_review": [], "workarounds": []},
  "eval_feedback": {"suggestions": [{"assertion": "...", "reason": "..."}], "overall": "..."}
}
```

**benchmark.json critical fields:** `configuration` must be `"with_skill"` or `"without_skill"` (exact strings); `result.pass_rate` not top-level; `run_summary.{with_skill|without_skill}.{pass_rate|time_seconds|tokens}.{mean|stddev}`.

**eval directory structure:** `<workspace>/iteration-<N>/eval-<descriptive-name>/with_skill/outputs/` and `without_skill/outputs/` — descriptive name not `eval-0`.

**xlsx color coding (financial models):**
- Blue (0,0,255): hardcoded inputs
- Black (0,0,0): ALL formulas
- Green (0,128,0): cross-sheet links
- Red (255,0,0): external file links
- Yellow (255,255,0): attention/assumptions

**docx critical pitfalls:** `ShadingType.CLEAR` not SOLID; `WidthType.DXA` not PERCENTAGE; no `\n` → separate Paragraph; no unicode bullets → `LevelFormat.BULLET`; dual table widths (`columnWidths` + cell `width`); `ImageRun` requires `type`; PageBreak must be in Paragraph.

---

## Dimension 3 — Interactions (Contract Level)

| Producer | → | Consumer | What passes | What breaks |
|---|---|---|---|---|
| Skill eval run | → | grader.md | transcript markdown, outputs_dir, user_notes.md, metrics.json, timing.json | Grader can't verify claims if outputs aren't plain text and no inspection tools provided |
| grader.md | → | aggregate_benchmark.py | grading.json at `<run-dir>/grading.json` | Wrong field names (`name` instead of `text`) produce empty benchmark |
| aggregate_benchmark.py | → | generate_review.py (viewer) | benchmark.json with exact schema | `configuration: "config"` instead of `"with_skill"` → viewer shows empty values |
| run_loop.py | → | SKILL.md frontmatter | `best_description` string | Selected by train score (not test score) → overfitted description that doesn't generalize |
| task notification | → | orchestrator (timing capture) | `total_tokens`, `duration_ms` | Not captured immediately → permanently lost (no other source) |

---

## Section 1 — Reference Summary

**Type:** Production skill library from the model vendor. 17 skills across creative design, technical tooling, enterprise communication, and document processing. Source-available (document skills) and Apache 2.0 (example skills). Used in Claude.ai paid plans today.

**Behavioral content:** The most substantial behavioral encoding is in: (1) skill-creator — full eval-driven improvement loop with parallel subagent spawning, description optimization with empirical anti-overfitting split, and a grader that critiques the evals themselves; (2) claude-api — model selection heuristics, adaptive thinking rules, compaction contract; (3) doc-coauthoring — three-stage workflow with fresh-subagent reader testing.

**Structural content:** Three-level loading system (metadata/body/resources) is the key structural convention. Skills delegate to reference files via explicit routing tables. Scripts are black boxes invoked with `--help`, never ingested. Descriptions are the triggering mechanism and should be calibrated for complex multi-step tasks.

**Interaction content:** skill-creator has the most complex pipeline: eval JSON → grader → benchmark aggregator → HTML viewer → feedback → iteration loop. Schema contracts are strict and enforced by viewer rendering.

**Maturity:** Document skills are production-used. skill-creator has real Python scripts. Disclaimer present: "implementations and behaviors you receive from Claude may differ." Creative skills (canvas-design, algorithmic-art) are high-craft but lighter on production hardening. No CI or test suite in the repo.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| `skill-creator/agents/grader.md §6 Critique the Evals` | Grader dual mandate: grade outputs AND critique the assertions themselves | WabbleSpec's skill-tdd measures compliance delta but doesn't validate whether pressure scenarios are discriminating. A trivially-easy scenario gives baseline and with-skill the same pass rate — delta zero, false negative. Adding scenario quality critique catches this. | Add `## Pressure Scenario Quality Check` section to `.claude/skills/skill-tdd/SKILL.md` with three checks: (1) scenario passes baseline unchanged (non-discriminating), (2) important compliance failure observed but no scenario covers it, (3) scenario cannot be objectively evaluated | High |
| `skill-creator/SKILL.md §Writing Style` | "If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag — explain the WHY instead" | WabbleSpec's SKILL.md files use heavy capitalized directives. This is an empirical counter-pattern: models that understand WHY handle edge cases that MUST directives miss. Directly applicable to improving authoring quality. | Add to CLAUDE.md skill authoring section: "Prefer explaining the reasoning behind a rule over capitalized commands (ALWAYS/NEVER/MUST/CRITICAL). A model that understands the WHY handles edge cases that a directive misses." | High |
| `skill-creator/SKILL.md §Progressive Disclosure` | Three-level loading reasoning: metadata (~100 words), body (<500 lines), bundled resources (unlimited) | WabbleSpec's CLAUDE.md has the 500-line guideline but not the underlying reasoning. Adding the WHY (loading budget allocation across tiers) helps skill authors decide WHERE to put content and WHEN to split to a reference file. | Add to CLAUDE.md skill authoring section: the three-tier reasoning with concrete signals for when to promote content to the next tier | High |
| `skill-creator/SKILL.md §How skill triggering works` | Undertrigger calibration: skills only trigger for complex multi-step tasks, not simple queries | WabbleSpec prohibits workflow steps in descriptions but doesn't explain why descriptions need to describe complex use cases. Adding this empirical backing helps authors calibrate description complexity. | Add one sentence to CLAUDE.md description guidance: "Descriptions calibrated for simple single-step queries will undertrigger — the triggering mechanism activates when the described use case is complex enough that the model benefits from consulting the skill." | High |
| `skill-creator/SKILL.md §Description Optimization` | 60/40 train/test split, select by test score not train score, to avoid overfitting description to eval set | If WabbleSpec builds description optimization tooling (partially planned in Tier 7 from prior sessions), this prevents eval overfitting. Can be added as a guidance note now. | Add to CLAUDE.md skill authoring section: "When evaluating skill description effectiveness against a query set, split 60% train / 40% held-out test; always select the best description by test score, not train score." | Medium |
| `skill-creator/agents/grader.md §Output Format → grading.json` | Exact field names: `text`, `passed`, `evidence` (NOT `name`/`met`/`details`) as a schema contract enforced by downstream viewers | WabbleSpec's grader (receipt-writer schema) may differ. Aligning the field names enables future integration with benchmark tooling. | Verify WabbleSpec's grader receipt schema and document the canonical field name contract | Medium |
| `skill-creator/SKILL.md §Step 3: timing` | Capture `total_tokens` and `duration_ms` at task notification time — permanently lost otherwise | WabbleSpec's skill-tdd dispatches subagents but doesn't capture timing. Adding this yields performance tracking for the evolution pipeline. | Add a note to `.claude/skills/skill-tdd/SKILL.md`: after each subagent completes, capture `total_tokens` and `duration_ms` from the task notification immediately; record in the report | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| `claude-api/SKILL.md` everywhere | Model name strings throughout (`claude-opus-4-7`, `claude-sonnet-4-6`, etc.) | I6 violation — WabbleSpec prohibits model names in any framework file | Mark as do-not-copy in full; adopt only non-naming behavioral heuristics | High |
| `skill-creator/SKILL.md §Description Optimization §Step 3` | `--model <model-id-powering-this-session>` in run_loop.py | Vendor-specific runtime assumption; would embed model ID into framework operations | Skip the optimization script entirely; adopt only the train/test split methodology | High |
| `skill-creator/SKILL.md §Language Detection` | `AskUserQuestion` tool usage | Prior ref-adopt directive (oh-my-claudecode): do not adopt AskUserQuestion | Skip any AskUserQuestion patterns | Medium |
| `README.md` disclaimer | "These skills are provided for demonstration and educational purposes only. Implementations...may differ" | Some patterns may be illustrative, not production-hardened. AI-generated without CI coverage. | Treat as supporting-reference; verify behavior empirically via skill-tdd before promoting any adopted pattern to enforcement level | Medium |
| `mcp-builder/SKILL.md §1.2` | Live URL calls to `modelcontextprotocol.io`, raw GitHub URLs | External URL dependency in SKILL.md; breaks in air-gapped or offline contexts | Skip URL-calling patterns in any WabbleSpec adoption | Low |
| `brand-guidelines/SKILL.md` | Anthropic-specific colors and fonts | Non-transferable; describes Anthropic's own brand identity | Study-only; do not incorporate Anthropic brand colors into WabbleSpec | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Grader dual mandate (grade + critique evals) | Adapt | Additive, high signal, directly applicable to skill-tdd | `.claude/skills/skill-tdd/SKILL.md` | P1 |
| WHY over MUST writing guidance | Adapt | Counter-pattern to over-specification; applicable to authoring | `~/.claude/CLAUDE.md` skill authoring section | P1 |
| Three-level loading reasoning | Adapt | Hardens existing 500-line rule with WHY | `~/.claude/CLAUDE.md` skill authoring section | P1 |
| Undertrigger calibration note | Adapt | Empirical backing for description calibration | `~/.claude/CLAUDE.md` skill authoring section | P2 |
| 60/40 train/test anti-overfitting | Adapt | Prevents description eval overfitting | `~/.claude/CLAUDE.md` skill authoring section | P2 |
| grading.json schema field names | Adapt (verify) | Interoperability with benchmark tooling | `.claude/skills/skill-tdd/SKILL.md` | P3 |
| Subagent timing capture at notification | Adapt | Performance tracking for evolution pipeline | `.claude/skills/skill-tdd/SKILL.md` | P3 |
| claude-api model name strings | Avoid | I6 violation | — | — |
| run_loop.py `--model` flag | Avoid | Vendor-specific runtime; I6 adjacent | — | — |
| AskUserQuestion tool patterns | Avoid | Prior ref-adopt directive | — | — |
| skill-creator viewer/server infrastructure | Avoid | Browser + Node.js dependency; incompatible with WabbleSpec CLI | — | — |
| agentskills.io / live URL calls | Avoid | External dependency in skill files | — | — |
| brand-guidelines Anthropic colors/fonts | Avoid | Anthropic-specific; non-transferable | — | — |
| doc-coauthoring three-stage workflow | Study Only | Strong workflow pattern but requires AskUserQuestion-adjacent human-in-loop gates not compatible with WabbleSpec's autonomous pipeline | — | — |
| Document skills (docx/pdf/xlsx/pptx scripts) | Study Only | Production implementation patterns; available if WabbleSpec adds document output capabilities | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 7 | Skill authoring conventions, eval methodology, and pressure-test critique map directly onto WabbleSpec's skill-tdd and quality-floor infrastructure |
| Architecture fit | 5 | WabbleSpec's receipt-driven pipeline is more structured than this reference's free-form eval loop; viewer/server infrastructure is incompatible |
| Implementation fit | 7 | All Tier 1 items are additive paragraph insertions into existing CLAUDE.md and skill-tdd SKILL.md files; no new files required |
| Maintenance fit | 8 | Adopted guidance (loading tiers, WHY over MUST, eval critique) are stable principles independent of model versions |
| Risk level | 3 | Main risk is I6 contamination from model names — easily filtered; other risks are low |
| Overall usefulness | 7 | Specific patterns from skill-creator and grader.md are directly applicable and under-served in current WabbleSpec |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — additive to CLAUDE.md):**
- `skill-creator/SKILL.md §Writing Style` → Add WHY over MUST authoring guidance to `~/.claude/CLAUDE.md`
- `skill-creator/SKILL.md §Progressive Disclosure` → Add three-level loading reasoning to `~/.claude/CLAUDE.md`
- `skill-creator/SKILL.md §How skill triggering works` → Add undertrigger calibration note to `~/.claude/CLAUDE.md`
- `skill-creator/SKILL.md §Description Optimization` → Add 60/40 train/test anti-overfitting rule to `~/.claude/CLAUDE.md`

**Phase 2 (Low-Risk Adaptation — additive to skill-tdd SKILL.md):**
- `skill-creator/agents/grader.md §6` → Add `## Pressure Scenario Quality Check` section to `skill-tdd/SKILL.md` (and engine module)
- `skill-creator/agents/grader.md §Output Format` → Add timing capture note to `skill-tdd/SKILL.md`

**Phase 3 (Watch Only — dependent on future infrastructure):**
- `skill-creator/references/schemas.md` → Full benchmark pipeline schema adoption; depends on skill-tdd harness expansion (Tier 7)
- `skill-creator/agents/comparator.md` and `analyzer.md` → Blind A/B comparison and flakiness detection; depends on parallel subagent infrastructure

**Phase 4 (Do Not Cross):**
- claude-api model name strings (I6)
- AskUserQuestion patterns (prior directive)
- run_loop.py with `--model` flag
- Viewer/server infrastructure

---

## Section 7 — Final Verdict

**Best 3 to steal:**
1. `skill-creator/agents/grader.md §6` — Grader dual mandate. Additive to skill-tdd with zero risk. Adds eval quality critique that catches non-discriminating scenarios (the most common false-positive failure mode in compliance testing).
2. `skill-creator/SKILL.md §Writing Style` — WHY over MUST. Empirical observation that capitalized directives produce edge-case failure. Directly applicable to WabbleSpec's SKILL.md files and authoring guidance.
3. `skill-creator/SKILL.md §Progressive Disclosure` — Three-level loading reasoning. Provides the empirical backing for WabbleSpec's existing 500-line guideline, making it actionable rather than just a rule.

**Worst 3 to avoid:**
1. `claude-api/SKILL.md` — Model name saturation. Every section contains `claude-opus-4-7`, `claude-sonnet-4-6`, etc. Any pattern from this file risks I6 contamination.
2. `skill-creator/SKILL.md §Description Optimization §Step 3` — `--model <model-id>` runtime parameter. Cannot be cleanly extracted without embedding a vendor string.
3. `skill-creator/SKILL.md §Language Detection` — AskUserQuestion usage. Prior ref-adopt directive from oh-my-claudecode evaluation prohibits this.

**Classification:** supporting-reference (7/10). Has directly adoptable improvements to skill-tdd and CLAUDE.md authoring guidance. Not critical (no novel architecture WabbleSpec lacks).

**Recommended next action:** Gate B — implement Phase 1 and Phase 2 items.

---

## Section 8 — Project Synthesis

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Pressure scenario quality gate in skill-tdd | grader.md dual mandate: critique the evals; three trigger conditions for flagging weak assertions | skill-tdd's two-pass baseline/with-skill comparison infrastructure | `.claude/skills/skill-tdd/SKILL.md` (and engine module) | skill-tdd can currently be "passed" by trivially-easy scenarios; the dual mandate adds a quality check that catches non-discriminating scenarios before they produce false READY verdicts |
| Undertrigger score in quality-floor-check | Empirical undertrigger pattern: simple one-step queries don't trigger skills regardless of description quality | quality-floor-check.py Gate 1 description checks | `.wabblespec/engine/shared/scripts/quality-floor-check.py` | Gate 1 currently checks technical description quality (period, no workflow steps) but not triggering effectiveness; an undertrigger risk signal (description < 15 words, no complex use case) catches the most common distribution failure |
| Iteration lineage receipt in evolution chain | `history.json` schema: version/parent/pass_rate/grading_result/is_current_best tracks improvement chain | WabbleSpec's receipt chain infrastructure + skill-tdd | New receipt type `skill-iteration` in receipt-writer.py | Currently skill improvements generate benchmark receipts but no chain links them version-to-version; a `skill-iteration` receipt type would enable the Instinct → Synth → Blueprint traceability the evolution chain needs |

---

## Section 9 — Expansion Opportunities

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| Description optimization pipeline | `skill-creator/scripts/run_loop.py`, `skill-creator/SKILL.md §Description Optimization` | WabbleSpec has no mechanism for systematically testing skill trigger descriptions; quality-floor-check catches structural issues but not triggering effectiveness | Evidence-based description quality; measurable routing improvements before deployment; anti-overfitting split prevents eval gaming | skill-tdd harness (partially built per task-card), vendor-neutral eval runner (no `--model` flag) | weeks | Yes |
| Aggregate benchmark viewer | `skill-creator/eval-viewer/generate_review.py`, `skill-creator/SKILL.md §Step 4` | WabbleSpec has DuckDB receipt storage but no visual comparison of skill effectiveness across iterations | Qualitative output review + quantitative benchmark side-by-side; iteration comparison; flakiness detection | skill-tdd harness, Node.js availability | weeks | Yes |

---

## Memory Drawers Written

- `anthropic-skills-main/eval-critique-gate.json` — grader dual mandate, scenario quality checks
- `anthropic-skills-main/skill-authoring-conventions.json` — WHY over MUST, three-level loading, undertrigger calibration, 60/40 split
- `anthropic-skills-main/description-optimization-pipeline.json` — Tier 7 expansion: description eval loop
