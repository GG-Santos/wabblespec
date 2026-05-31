# Integration Plan — toprank-main

**generated_at:** 2026-05-28T10:22:24Z
**ref_eval_report:** research/ref-eval/toprank-main.md
**risk_appetite:** balanced
**integration_goal:** Improve WabbleSpec's skill module structural quality and evaluation tooling by adopting three proven patterns from toprank: on-demand reference routing in SKILL.md bodies, LLM-as-judge eval infrastructure for the Benchmark module, and instinct drawer field naming aligned with actionable scoring terminology.

---

## Signal Summary

Ref-eval classified toprank as a **supporting reference** (overall usefulness 7/10) with six extractable benefits and five risks. Four items are excluded (domain content, hardcoded model name, OpenClaw scripts, version lockstep). Six items remain in the backlog. Three score high enough for Phase 1; two require Specify before touching framework scripts; one is blocked by the active `wave-checkpoint-v1` task card which currently holds Guard SKILL.md locked for modification.

---

## Exclusion List

| Item | Source in ref-eval | Reason Excluded |
|---|---|---|
| Google Ads / Meta Ads / SEO domain skill content | Section 4 "Avoid" | No target use case in WabbleSpec; tightly coupled to notfair.co MCP servers which are not open |
| `llm_judge.py` hardcoded `JUDGE_MODEL = 'gemini-2.0-flash'` | Section 4 "Avoid" | Direct I6 violation; named model reference prohibited in framework files |
| OpenClaw Python scripts (`openclaw/bin/*.py`) | Section 4 "Study Only" + Risk 4 | Require OpenClaw runtime (`~/.openclaw/` directory structure); WabbleSpec has no equivalent and should not add one |
| Version lockstep enforcement across three files | Section 4 "Avoid (for now)" | Only load-bearing when a plugin-discovery consumer reads multiple version files; WabbleSpec does not have that structure yet |

---

## Integration Backlog (ranked)

Scoring: `integration_score = (impact × 2) + project_fit − risk`
Map: High=3, Medium=2, Low=1

| Rank | ID | Item | Type | Phase | Impact | Risk | Project Fit | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | T1 | Situation → reference routing table in SKILL.md | Convention + content | 1 | High | Medium | Medium | 6 |
| 2 | T2 | LLM-as-judge eval architecture (rubric + collector) | New script | 2 | High | Medium | Medium | 6 |
| 3 | T3 | Instinct drawer field rename (judgment lever taxonomy) | Schema rename | 2 | High | Medium | Medium | 6 |
| 4 | T4 | `~~capability` connector placeholder convention | Writing convention | 1 | Medium | Low | Medium | 5 |
| 5 | T5 | `allowed-tools:` frontmatter enforcement | Infrastructure | 3 | Medium | Medium | Low | 3 |
| 6 | T6 | Policy safety taxonomy (Guard SKILL.md documentation) | Documentation | 1 | Low | Low | Low | 2 |

*T1/T2/T3 tie at score 6; broken by risk (all Medium — tied), then ref-eval priority ordering.*

---

## Phase 1 — Safe Wins

### T4 — `~~capability` Connector Placeholder Writing Convention

- **What:** Establish a `~~capability-name` placeholder convention in WabbleSpec skill authoring. When a SKILL.md references an external tool capability (MCP server, external API, CLI tool), it uses `~~tool-category` rather than a hardcoded provider name or prefix.
- **Where:** `CLAUDE.md` skill-authoring section (add a "Tool References" paragraph). No SKILL.md edits required immediately — the convention is declared here, then applied file-by-file as skills are touched.
- **How:** In `CLAUDE.md`, under "Doing tasks" or a new "## Skill Authoring Conventions" section, add: "When a SKILL.md references an external tool by capability (an MCP server, CLI, or API), use the `~~capability-name` placeholder form (e.g. `~~search-console`, `~~vector-store`) rather than hardcoding provider names. The shared preamble or Guard resolves the active provider at runtime." Then grep current SKILL.md files for hardcoded provider names and flag them for replacement on next touch.
- **Gate:** `CLAUDE.md` contains the `~~capability-name` convention documented with at least one example. No SKILL.md currently under active modification contains a hardcoded provider name that violates I6.
- **Reference location:** `toprank-main/README.md` "Connectors" section; `google-ads/shared/preamble.md`

---

### T1 — Situation → Reference Routing Table in SKILL.md

- **What:** Add a `## Reference Routing` section to three high-complexity WabbleSpec SKILL.md files (Benchmark, Verifier, Executor). The section is a two-column markdown table: Situation → Reference file path. For each entry added, the corresponding inline content block in that SKILL.md moves entirely to the referenced file — SKILL.md body length must go down, not stay flat.
- **Where:** Three files as the initial rollout:
  - `.claude/skills/benchmark/SKILL.md` — route "fixture integrity rules" → `rules/benchmark-discipline.md` (already exists); route "control arm types" → same reference; route "split protocol details" → could be its own reference.
  - `.claude/skills/verifier/SKILL.md` — route verification mode details to existing references.
  - `.claude/skills/executor/SKILL.md` — route tier placement rules → `_shared/references/system-prompt-tiers.md` (already exists; currently inline description duplicates it).
  - **Not Guard SKILL.md** — locked under `wave-checkpoint-v1`. Apply after that task card closes.
- **How:** For each target skill: (1) identify sections that already have a canonical reference document. (2) Replace the inline section body with a one-line pointer: "See `<path>`." (3) Add the routing table entry. (4) Verify reference file exists and contains the content. Do not create new reference files — only reroute to already-existing ones in Phase 1.
- **Gate:** Each modified SKILL.md has a `## Reference Routing` section. Each SKILL.md is at least 10 lines shorter than before. No inline section that was removed is missing from its target reference file.
- **Reference location:** `toprank-main/google-ads/manage/SKILL.md` routing table pattern (documented in changelog 0.11.2); `google-ads/shared/analysis-principles.md` shows the style of a lean, pointer-heavy reference.

---

### T6 — Policy Safety Taxonomy Documentation in Guard SKILL.md

- **What:** Add a `## Safety Classes` section to Guard SKILL.md documenting the three-tier action taxonomy: auto-safe (local audits, receipt writes, read-only analysis), approval-required (repo edits, external writes, PRs), blocked-from-auto (destructive mass changes, irreversible public actions). No behavioral change — documentation only, describing behavior Guard already enforces at the hook level.
- **Where:** `.claude/skills/guard/SKILL.md` — append after the "Runtime permission system boundary" section.
- **How:** Write a concise `## Safety Classes` section with three subsections mirroring the toprank policy.md three-tier structure. Explicitly note that Layer 5 (command risk) is the enforcement mechanism for BLOCK-class actions, Layer 4 (authority) covers approval-required, and auto-safe actions are never Guard-blocked.
- **Gate:** Guard SKILL.md contains `## Safety Classes` with all three tiers named and mapped to the existing Guard layer that enforces each.
- **Constraint:** **Do not apply until `wave-checkpoint-v1` task card completes.** Guard SKILL.md is currently LOCKED for modification under that task card. Queue T6 for the session after wave-checkpoint-v1 is archived.
- **Reference location:** `toprank-main/openclaw/shared/policy.md`

---

## Phase 2 — Targeted Integration

### T2 — LLM-as-Judge Eval Script

- **What:** Implement `llm-eval.py` in `.wabblespec/engine/shared/scripts/` — a WabbleSpec-native skill-section quality scorer. Scores any SKILL.md section on three dimensions: clarity (can an agent understand what each step does?), completeness (are commands, arguments, and expected behavior documented?), actionability (can an agent execute without follow-up questions?). Each dimension scored 1-5; minimum gate: 4/5 on all three.
- **Where:** `.wabblespec/engine/shared/scripts/llm-eval.py` (new file — framework space; I11 applies — this is a framework authoring task, not a product-space task). Collector output: `.wabblespec/state/evals/` directory (new, needs creation). Integrate as a `--eval-section` flag in the Benchmark skill invocation path.
- **How:**
  1. Script accepts: `--skill-path <path>` and `--section <heading>` (extracts the named section from the SKILL.md) OR `--content-file <path>` for raw content.
  2. Builds the judge prompt from `toprank-main/test/helpers/llm_judge.py` line 162-188 (the three-dimension rubric + scoring guide). Do NOT copy the `call_judge` function — replace with a call to `anthropic` SDK via `analysis` capability descriptor resolved from `runtime-state.json`. No hardcoded model name.
  3. Parses JSON response: `{clarity: N, completeness: N, actionability: N, reasoning: "..."}`.
  4. Writes one entry to `.wabblespec/state/evals/eval-log.json` (append-only, same structure as toprank `EvalTestEntry` but using WabbleSpec field names).
  5. Exits 0 if all three dimensions >= 4; exits 1 with a formatted report if any dimension < 4.
- **Specify required:** Yes — define the full script interface, eval-log schema, and integration point in Benchmark SKILL.md before implementation.
- **Breaking change risk:** None — new script and new directory; no existing behavior changes.
- **Gate:** `llm-eval.py --skill-path .claude/skills/benchmark/SKILL.md --section "Workflow"` runs without error and produces a score. Eval-log entry written. No model name appears in the script source. Exit code 0 on a clean section; exit code 1 on a section with known gaps.
- **Reference location:** `toprank-main/test/helpers/llm_judge.py` (rubric, not the model call); `toprank-main/test/helpers/eval_store.py` (collector structure); `toprank-main/seo/seo-analysis/evals/evals.json` (scenario list format)

---

### T3 — Instinct Drawer Field Rename (Judgment Lever Taxonomy)

- **What:** Align WabbleSpec's instinct observation output format with the judgment lever terminology from toprank's `recommendation-quality.md`. The current Instinct output uses `Confidence: low|medium|high` — a good start, but lacks the separate scoring dimensions that make patterns actionable for Synth. Add three fields to each instinct pattern entry: `expected_impact` (estimated effect size on execution quality), `actionability_score` (is there a clear lever — specific module, specific rule — or is this vague investigation?), and `learned_multiplier` (has this pattern held across multiple receipt corpora or is it corpus-specific?).
- **Where:**
  - `.claude/skills/instinct/SKILL.md` — update the "Output contract" pattern format block to include the three new fields.
  - `.wabblespec/state/memory/instinct-observations.md` — if observations already exist, add the new fields with `null` defaults for all existing patterns. Do not re-score existing patterns retroactively; mark them `requires_scoring: true`.
- **How:**
  1. In Instinct SKILL.md `## Output contract`, extend the pattern block:
     ```
     Expected impact: null | low | medium | high
     Actionability score: null | specific-lever | investigation | vague
     Learned multiplier: null | single-corpus | cross-corpus
     ```
  2. In `instinct-observations.md`, add the three fields (with `null` values) to each existing pattern. Do not remove `Human-validated` — it remains the Synth gate field.
  3. Document in the Instinct SKILL.md that `expected_impact` is populated by the human reviewer when validating a pattern, not by automated scoring.
- **Specify required:** Yes — confirm the exact field names and value vocabularies before editing Instinct SKILL.md, since Synth reads this format.
- **Breaking change risk:** Possible — if any automation reads `instinct-observations.md` field-by-field (e.g. a script in the Synth module), adding new fields will not break readers that ignore unknown fields, but removing or renaming existing fields would. Audit Synth SKILL.md for any hardcoded field references before applying.
- **Gate:** Instinct SKILL.md pattern block contains all three new fields with documented value vocabularies. `instinct-observations.md` (if it exists) contains the three new fields on each pattern. No existing pattern has `Human-validated` removed.
- **Reference location:** `toprank-main/openclaw/shared/recommendation-quality.md` (judgment levers: `expected_impact`, `confidence_score`, `actionability_score`, `learned_multiplier`)

---

## Phase 3 — Considered Integration

### T5 — `allowed-tools:` Frontmatter Enforcement

- **What:** Add `allowed-tools:` as a recognized SKILL.md frontmatter field. When present, Guard Layer 4 (authority check) reads it and refuses tool calls from that skill that fall outside the declared list. Provides per-skill tool surface restriction at the spec level, supplementing Guard's global COMMAND_RISK policy.
- **Adversarial review required:** Yes. This changes Guard Layer 4 behavior — a field absence on existing SKILL.md files must not cause HARD errors (the field is opt-in). The enforcement must distinguish "field absent" (no restriction) from "field present but empty" (all tools blocked) from "field present with list" (restricted to list).
- **Promotion condition:** (1) `wave-checkpoint-v1` task card is archived and Guard SKILL.md is unlocked. (2) A Specify cycle has defined the exact frontmatter schema extension and the Guard Layer 4 amendment. (3) At least five SKILL.md files have been chosen as `allowed-tools:` candidates with their intended tool lists drafted.
- **Breaking change risk:** Possible — any SKILL.md that inadvertently declares `allowed-tools: []` (empty list) would block all tools for that skill. The schema must require at least one entry when the field is present, OR treat an empty list as "no restriction."
- **Reference location:** `toprank-main/toprank-upgrade-skill/SKILL.md` lines 9-12

---

## Phase 4 — Watch Only

*No items deferred to Phase 4.* All surviving signal fits within Phases 1-3.

---

## Execution Notes

**Active task card conflict:** `wave-checkpoint-v1` is LOCKED and modifies Guard SKILL.md, Guard's acceptance tests, Executor SKILL.md, and Recipe SKILL.md. **T1 (routing table) must skip Guard SKILL.md and Recipe SKILL.md until that task card is archived.** T6 (policy taxonomy) must not touch Guard SKILL.md until archived.

**Sequencing constraints:**
- T4 (connector placeholder) has no dependencies. Run first — it is documentation only and establishes the convention that guides all other skill edits.
- T1 (routing table) depends on T4 being documented (so writers know the convention exists before they reroute references).
- T2 (LLM-as-judge script) must run Specify before implementation. `runtime-state.json` must exist at the target project root before the script runs (`runtime-probe` was run previously; confirm the file is current).
- T3 (instinct drawer fields) must audit Synth SKILL.md for hardcoded field references before any file edits. Read `.claude/skills/synth/SKILL.md` first.
- T5 (allowed-tools enforcement) must not begin until `wave-checkpoint-v1` archives and Guard SKILL.md is unlocked.

**Do not run T1, T2, T3, T5 in the same wave.** Each modifies a different module layer and their receipts must chain independently.

**Do not run T2 without Specify.** The eval script touches `.wabblespec/engine/shared/scripts/` (framework space). A Specify receipt must exist before any framework script is created.

After implementation of any phase item, run `/ref-comp toprank-main` to audit execution fidelity against this plan.
