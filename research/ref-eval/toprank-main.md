# Ref-Eval: toprank-main

**Reference path:** `C:\Vaults\references\Extra Project References\toprank-main`
**Evaluated against:** WabbleSpec v6.1, v0.24.0 — spec-driven SDLC framework, 99 skill modules, L0-L8 layers
**Date:** 2026-05-28
**Depth:** deep

---

## Section 1 — Reference Summary

**Type:** Production Claude Code plugin, v0.18.0, MIT license, actively maintained (v0.1.0 to v0.18.0 over ~2 months, 2026-03-26 to 2026-05-09).

**Problem it solves:** Provides AI agents (Claude Code) with structured, data-driven skills for Google Ads management, Meta Ads management, and SEO analysis — domain skills backed by real MCP data sources and a closed-loop adaptive layer.

**Patterns and architecture it contains:**
- **Plugin manifest pattern** (`.claude-plugin/plugin.json`) — explicit skill-path registry; skills not listed here do not load.
- **`~~category` connector placeholder** — tool-agnostic skill writing; `~~google-ads`, `~~search-console`, `~~cms` resolve at runtime to whatever MCP server provides that capability; skills never hardcode provider names.
- **Shared preamble pattern** (`google-ads/shared/preamble.md`) — runs on every skill entry; handles MCP detection, config load, update check, account selection in one place.
- **Situation → reference routing table** — SKILL.md files contain a short lookup table mapping diagnostic situations to the specific reference file to load on demand; keeps SKILL.md lean.
- **Evidence-first principle** (`google-ads/shared/analysis-principles.md`) — every claim cites entity name, dollar amount, metric value, and time window; "looks low without a number is a draft, not a finding."
- **Per-skill `allowed-tools:` frontmatter** (`toprank-upgrade-skill/SKILL.md`) — restricts the tool surface a specific skill can invoke.
- **OpenClaw adaptive layer** (`openclaw/`) — closed-loop operator: signals → diagnosis → action → measurement → scoring → learned priors → better next action. Artifact contract: per-run folder with `audit.json`, `action-plan.json`, `verification.json`. Per-site `learned-patterns.json` for bias across runs.
- **LLM-as-judge eval architecture** (`test/helpers/llm_judge.py`) — Gemini-based judge scoring clarity/completeness/actionability 1-5 per section; separate `SeoReportScore` struct for domain quality checks; `eval_store` collects results across the suite.
- **Policy.md safety taxonomy** (`openclaw/shared/policy.md`) — explicit `auto-safe` / `approval-required` / `blocked-from-auto` action classes.
- **Version lockstep rule** — VERSION, plugin.json, marketplace.json must all be bumped together; mismatch causes upgrade detection failures (documented in CONTRIBUTING and CLAUDE.md).
- **Self-updater skill** (`toprank-upgrade-skill/`) — versioned cache directory management, dev-symlink detection, changelog-diff display.

**Maturity signals:**
- 255+ passing unit tests confirmed in changelog.
- Active security fixes (predictable tmp paths, symlink attack hardening) documented in changelog entries.
- Windows portability fixes present (POSIX `os.getuid()` → portable helper).
- Real commit cadence with breaking changes, migration notes, and real user bug reports (#44 referenced).
- CLAUDE.md is a genuine quality-culture document: "brutal honesty, relentless quality, surface tradeoffs explicitly."

**Maturity concerns:**
- Domain-specific: SEO/Ads only; no applicability to general-purpose framework engineering without abstraction.
- OpenClaw adaptive layer requires external OpenClaw runtime to be installed; it is not self-contained.
- Some skills are tightly coupled to `notfair.co` MCP servers — structural patterns can be studied but skills cannot be lifted without those servers.

---

## Section 2 — Benefits We Can Get

### Benefit 1 — `~~category` Connector Placeholder for Vendor-Neutral Tool References

| Field | Content |
|---|---|
| Location | `README.md` "Connectors" section; `google-ads/shared/preamble.md` |
| What to adapt | The `~~category` placeholder convention for naming tool capability categories in skill instructions, resolved to specific tool prefixes at runtime |
| Why it helps | WabbleSpec I6 (RUNTIME IS VENDOR-NEUTRAL) mandates no model names and only capability descriptors. The same principle should extend to MCP and external tool references within skill modules. Currently WabbleSpec skills may silently hardcode tool provider names; this pattern enforces the abstraction at the skill-authoring level |
| How to adapt | Adopt a `~~capability-name` or `[capability: name]` convention in skill SKILL.md files when referencing external tools; the skill preamble or Guard resolves the placeholder to the available provider at runtime. No code changes needed — it is a writing convention |
| Impact | Medium |

### Benefit 2 — Per-Skill `allowed-tools:` Frontmatter

| Field | Content |
|---|---|
| Location | `toprank-upgrade-skill/SKILL.md` lines 9-12: `allowed-tools: [Bash, Read, AskUserQuestion]` |
| What to adapt | The SKILL.md frontmatter field that restricts which tools a specific skill may invoke |
| Why it helps | WabbleSpec's Guard module operates at the hook level with COMMAND_RISK taxonomy. A per-skill tool allowlist at the frontmatter level gives a second, skill-scoped layer of protection — declared by the skill author, not configured globally. Particularly relevant for lower-trust skills or skills that should never touch the filesystem |
| How to adapt | Add `allowed-tools:` as a recognized frontmatter field in WabbleSpec's SKILL.md schema. Guard or the executor reads it and refuses tool calls that fall outside the declared list |
| Impact | Medium |

### Benefit 3 — Situation → Reference Routing Table in SKILL.md

| Field | Content |
|---|---|
| Location | `google-ads/manage/SKILL.md` (referenced in changelog 0.11.2): "quick-lookup table mapping situations to the right reference file" |
| What to adapt | Embedding a small routing table inside SKILL.md so the agent loads the specific reference file relevant to the current diagnostic situation, rather than loading all references or none |
| Why it helps | WabbleSpec skill modules already have references directories. The routing table pattern keeps SKILL.md bodies lean while ensuring the right context loads on demand — directly combating the context-bloat pattern WabbleSpec is actively fighting across its own module builds |
| How to adapt | Add a "## Reference Routing" section to complex WabbleSpec SKILL.md files: a markdown table mapping situation keywords to reference file paths. Model it after toprank's approach where the table is a first-class section, not an afterthought |
| Impact | High |

### Benefit 4 — LLM-as-Judge Eval Architecture

| Field | Content |
|---|---|
| Location | `test/helpers/llm_judge.py`; `test/helpers/eval_store.py`; `seo/seo-analysis/evals/evals.json` |
| What to adapt | The three-dimension judge rubric (clarity / completeness / actionability, each 1-5) with minimum thresholds per dimension; the `eval_store` collector that aggregates results; the `evals.json` scenario list as the test input manifest |
| Why it helps | WabbleSpec has Benchmark and Grader modules but no concrete LLM-as-judge implementation. This is a production, working pattern that scores skill-section quality with a second model, which is exactly what WabbleSpec's Benchmark module describes |
| How to adapt | Adapt the `llm_judge.py` pattern into WabbleSpec's `.wabblespec/engine/shared/scripts/` as an LLM-eval script. Use the three-dimension rubric for skill documentation quality scoring. The minimum thresholds (4/5 on each dimension) become the quality gate. Provider-neutral: the judge model is a `code-generation` or `analysis` capability, not a named model |
| Impact | High |

### Benefit 5 — OpenClaw Artifact Contract Mapped to WabbleSpec Receipt Chain

| Field | Content |
|---|---|
| Location | `openclaw/shared/artifact-contract.md`; `openclaw/bin/persist_run.py`; `openclaw/shared/recommendation-quality.md` |
| What to adapt | The per-run artifact folder structure (timestamped run dir, `audit.json`, `action-plan.json`, `verification.json`, `learning-log.json`); the per-site `learned-patterns.json` with confidence-weighted priors; the explicit mapping of every recommendation to a best-practice lane |
| Why it helps | WabbleSpec's receipt chain (Research → Plan → Execution → Verifier → Archive) is structurally identical to OpenClaw's per-run artifact sequence. The `learned-patterns.json` per-site file is structurally identical to WabbleSpec's instinct drawers with confidence decay. The `recommendation-quality.md` judgment levers (`expected_impact`, `confidence_score`, `actionability_score`, `learned_multiplier`) are the same signals WabbleSpec's Instinct and Synth modules need to surface |
| How to adapt | Study `recommendation-quality.md` judgment lever taxonomy directly. Map `expected_impact` / `confidence_score` / `actionability_score` / `learned_multiplier` to the fields WabbleSpec's instinct drawers already record; the labels are better than what WabbleSpec currently uses |
| Impact | High |

### Benefit 6 — Policy Safety Taxonomy (Auto-Safe / Approval-Required / Blocked)

| Field | Content |
|---|---|
| Location | `openclaw/shared/policy.md` |
| What to adapt | The three-tier classification: auto-safe (local audits, artifact writes, queue updates), approval-required (repo edits, CMS writes, PRs, content publication), blocked-from-auto (destructive mass changes, irreversible public actions) |
| Why it helps | WabbleSpec's Guard has COMMAND_RISK taxonomy but it is defined at the tool-call level. OpenClaw's policy.md defines it at the action-class level, which is more readable as documentation and easier to communicate to contributors. WabbleSpec's CLAUDE.md could be strengthened with this explicit three-tier framing |
| How to adapt | Add a "Safety Classes" section to WabbleSpec's Guard SKILL.md or to CLAUDE.md, using the three-tier framing as a readable contract rather than a hook implementation detail |
| Impact | Low |

---

## Section 3 — Negative Effects / Risks

### Risk 1 — Domain Mismatch: Lifting Skills Without Their MCP Servers

| Field | Content |
|---|---|
| Location | `.mcp.json`; `google-ads/shared/preamble.md`; `meta-ads/shared/preamble.md` |
| Risk | Attempting to adapt the Google Ads or Meta Ads skill content directly would produce skills that cannot function — they depend on `notfair.co` hosted MCP servers that require OAuth sign-in and are not open |
| Why it hurts | Time and effort spent adapting domain skills that have no target use case in WabbleSpec (which has no Google Ads or Meta Ads surface) |
| Mitigation | Do not adapt domain skill content. Adapt structural and architectural patterns only. The connector placeholder, routing table, and eval patterns are all extractable without the domain content |
| Severity | Low (easy to avoid) |

### Risk 2 — Context Bloat from Incomplete Routing Pattern Adoption

| Field | Content |
|---|---|
| Location | `google-ads/manage/SKILL.md` (see changelog 0.11.2, 0.12.0, 0.13.0, 0.18.0 — all trim SKILL.md body) |
| Risk | Adopting the routing table pattern without also committing to the slimming discipline produces SKILL.md files that have both a routing table AND dense inline content — worse than before |
| Why it hurts | WabbleSpec's current skill modules already suffer from context bloat in some areas. Adding routing tables without removing inline content would add overhead without benefit |
| Mitigation | Apply the routing table as a replacement for inline content, not an addition. For each routing entry, the inline section it replaces should move entirely to the referenced file |
| Severity | Medium |

### Risk 3 — LLM Judge Model Dependency

| Field | Content |
|---|---|
| Location | `test/helpers/llm_judge.py` line 96: `JUDGE_MODEL = 'gemini-2.0-flash'` |
| Risk | The judge is hardcoded to Gemini 2.0 Flash, requiring a `GEMINI_API_KEY`. Adapting this into WabbleSpec as-is would introduce a named model dependency (violating I6) and require a second API key |
| Why it hurts | WabbleSpec I6 prohibits named model references; a hardcoded `JUDGE_MODEL` in a framework script would be an I6 violation |
| Mitigation | Adapt the structural pattern (rubric, thresholds, eval_store collector) but route the judge call through WabbleSpec's capability descriptor system (`analysis` capability) and the existing runtime-state.json, not a hardcoded model name |
| Severity | Medium |

### Risk 4 — OpenClaw Runtime Dependency for Adaptive Layer

| Field | Content |
|---|---|
| Location | `openclaw/install/install.sh`; `openclaw/README.md` |
| Risk | The OpenClaw adaptive layer is not self-contained — it requires an external OpenClaw runtime already installed and configured. The install script copies wrapper skills into `~/.openclaw/skills/`, which requires that path to exist |
| Why it hurts | If any part of the adaptive loop pattern is adopted for WabbleSpec, it cannot be lifted from toprank as-is; the dependency on OpenClaw infrastructure would need to be replaced with WabbleSpec's own scheduler and state-writing infrastructure |
| Mitigation | Study the artifact contract and feedback-scoring logic as patterns; implement against WabbleSpec's own infrastructure rather than adopting the OpenClaw-specific scripts |
| Severity | Low (pattern is extractable; just don't copy the scripts) |

### Risk 5 — Version Lockstep Complexity

| Field | Content |
|---|---|
| Location | `CLAUDE.md` "Versioning" section; changelog multiple entries with "bump in three places" instructions |
| Risk | Toprank's version-lockstep requirement (VERSION + plugin.json + marketplace.json) is load-bearing because plugin discovery reads all three files. Adopting a similar multi-file lockstep rule for WabbleSpec without the same mechanical reason adds maintenance overhead without corresponding benefit |
| Why it hurts | WabbleSpec already has VERSION, wabblespec.yaml, and CLAUDE.md referencing version numbers. A strict lockstep rule would be correct but adds friction unless something actually breaks when they drift |
| Mitigation | Adopt the lockstep rule only if WabbleSpec adds a plugin registry or marketplace consumer that reads multiple files. Not a needed adoption right now |
| Severity | Low |

---

## Section 4 — What To Adapt vs What To Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area In My Project | Priority |
|---|---|---|---|---|
| `~~category` connector placeholder convention | Adapt | Directly enforces WabbleSpec I6 in skill authoring; zero implementation cost | Skill SKILL.md writing convention; Guard skill | High |
| Per-skill `allowed-tools:` frontmatter | Adapt | Second defense layer per skill; complements Guard hook-level COMMAND_RISK | SKILL.md schema; Guard/Executor modules | Medium |
| Situation → reference routing table | Adapt | Solves context bloat in SKILL.md; forces on-demand reference loading | All complex WabbleSpec SKILL.md modules | High |
| LLM-as-judge eval architecture (rubric + collector) | Adapt | Concrete implementation of WabbleSpec Benchmark module pattern | `.wabblespec/engine/shared/scripts/`; Benchmark skill | High |
| `recommendation-quality.md` judgment lever taxonomy | Adapt | Better labels for instinct drawer fields than WabbleSpec currently uses | Instinct / Synth modules; drawer schema | Medium |
| `openclaw/shared/policy.md` three-tier safety taxonomy | Adapt | Readable contract layer for CLAUDE.md / Guard documentation | CLAUDE.md safety section; Guard SKILL.md | Low |
| Google Ads / Meta Ads / SEO domain skill content | Avoid | No target use case in WabbleSpec; MCP dependency on notfair.co | N/A | — |
| OpenClaw Python scripts (`bin/*.py`) | Study Only | Artifact contract patterns are valuable; the scripts themselves are OpenClaw-runtime-dependent | openclaw/shared/artifact-contract.md patterns | Low |
| `llm_judge.py` hardcoded `JUDGE_MODEL` | Avoid | I6 violation if copied as-is; adapt the rubric, not the model reference | Benchmark module | Medium |
| Version lockstep enforcement across three files | Avoid (for now) | Only load-bearing if a plugin-discovery consumer reads all three; WabbleSpec does not have that yet | N/A | — |
| CLAUDE.md quality culture language | Study Only | "Brutal honesty, relentless quality, surface tradeoffs explicitly" framing is strong; WabbleSpec CLAUDE.md could be refined similarly | CLAUDE.md | Low |
| Self-updater skill architecture | Study Only | WabbleSpec does not distribute as a plugin; pattern not applicable | N/A | — |

---

## Section 5 — Integration Fit

| Dimension | Score | Explanation |
|---|---|---|
| Concept fit | 7 | The closed-loop improvement cycle, receipt-as-artifact pattern, and evidence-first principle all map directly to WabbleSpec's L8 evolution chain and I10 receipt contract |
| Architecture fit | 5 | Structural patterns (connector placeholders, routing tables, eval architecture) extract cleanly; domain content and OpenClaw runtime dependency do not fit at all |
| Implementation fit | 4 | The LLM judge and routing table are directly implementable; the MCP-dependent skills and OpenClaw scripts require WabbleSpec-native replacements rather than direct adaptation |
| Maintenance fit | 7 | Toprank has real tests, real security fixes, and real docs; patterns extracted from it will be well-reasoned, not cargo-culted |
| Risk level | 2 | MIT license, no risk of copying harm; main risks are misapplication (lifting domain content without MCP servers, copying hardcoded model names) — both easy to avoid |
| Overall usefulness | 7 | Three high-priority patterns worth immediate adaptation (connector placeholder, routing table, LLM-as-judge eval architecture); remaining findings are medium or study-only |

---

## Section 6 — Recommended Extraction Plan

### Phase 1 — Safe Learning

- Read `google-ads/shared/analysis-principles.md` in full. It is the best evidence-first writing principle document in this reference; the ideas apply directly to how WabbleSpec instinct drawers and Synth outputs should be written.
- Read `openclaw/shared/recommendation-quality.md` in full. Map each judgment lever (`expected_impact`, `confidence_score`, `actionability_score`, `learned_multiplier`, `best_practice_alignment`) to the current instinct drawer schema. Note gaps.
- Read `openclaw/shared/artifact-contract.md`. Compare per-run artifact types to WabbleSpec receipt phases. Identify naming mismatches worth resolving.
- Study `openclaw/shared/policy.md` three-tier safety taxonomy. Compare to CLAUDE.md "Executing actions with care" section.

No file changes in Phase 1.

### Phase 2 — Low-Risk Adaptation

- **Connector placeholder convention:** Add a writing guideline to WabbleSpec's skill authoring guide (or CLAUDE.md) specifying that external tool references in SKILL.md use a `~~capability` placeholder, not a provider name. Affects: `CLAUDE.md` or a new `skill-authoring-conventions.md` reference. Validate with Guard SKILL.md before broadening.
- **Routing table section:** Add a "## Reference Routing" section to 3-5 high-complexity WabbleSpec SKILL.md files (e.g. Executor, Verifier, Gateway-Design). For each entry added, remove the corresponding inline content and move it to a reference file. Validate: SKILL.md line counts must go down, not up.
- **Policy three-tier safety taxonomy:** Add a "## Safety Classes" section to Guard SKILL.md using the auto-safe / approval-required / blocked-from-auto framing. No behavior change — documentation only.

### Phase 3 — Deeper Integration

- **LLM-as-judge eval script:** Implement a WabbleSpec-native `llm-eval.py` in `.wabblespec/engine/shared/scripts/` based on the `llm_judge.py` pattern. Three dimensions: clarity / completeness / actionability. Judge model: `analysis` capability resolved via `runtime-state.json` (not a hardcoded name). Minimum thresholds: 4/5. Collector: writes to a `.wabblespec/state/evals/` directory analogous to `eval_store`. Hook into Benchmark skill.
- **`allowed-tools:` frontmatter:** Extend WabbleSpec's SKILL.md schema definition to recognize `allowed-tools:` as a valid frontmatter key. Have Guard or the Executor read it and enforce it pre-tool-call. Validation gate: any skill that declares `allowed-tools:` must pass a schema lint check.
- **Instinct drawer field rename:** Align WabbleSpec instinct drawer fields with `recommendation-quality.md` terminology where a direct mapping exists. `confidence_score`, `expected_impact`, `learned_multiplier` are better names than current WabbleSpec equivalents if the current names are vaguer.

### Phase 4 — Do Not Cross

- **Do not lift domain skill content** (Google Ads, Meta Ads, SEO SKILL.md files). They depend on the notfair.co MCP servers and have no use case in WabbleSpec.
- **Do not copy `llm_judge.py` with `JUDGE_MODEL = 'gemini-2.0-flash'` hardcoded.** I6 violation.
- **Do not adopt the OpenClaw Python scripts directly.** They require OpenClaw runtime infrastructure that WabbleSpec does not have and should not add.
- **Do not adopt the version-lockstep-three-files rule** until WabbleSpec has a plugin-discovery consumer that reads multiple version files.

---

## Section 7 — Final Verdict

This reference is worth using for its structural and architectural patterns. It is not worth using for its domain content.

**Best 3 things to steal:**

1. **Routing table pattern in SKILL.md** (`google-ads/manage/SKILL.md`, changelog 0.11.2) — the highest-leverage extraction. WabbleSpec skill modules are fighting context bloat; this pattern forces on-demand loading and makes SKILL.md bodies scannable.
2. **LLM-as-judge eval architecture** (`test/helpers/llm_judge.py`) — a working, production implementation of the pattern WabbleSpec's Benchmark module describes but does not yet implement concretely.
3. **`recommendation-quality.md` judgment lever taxonomy** (`openclaw/shared/recommendation-quality.md`) — the named score fields (`expected_impact`, `confidence_score`, `actionability_score`, `learned_multiplier`, `best_practice_alignment`) are better than what WabbleSpec's instinct drawers use and directly applicable.

**Worst 3 things to avoid:**

1. **Domain skill content** — the Google Ads / Meta Ads / SEO SKILL.md files are tightly coupled to notfair.co MCP infrastructure; they would be dead weight in WabbleSpec.
2. **`JUDGE_MODEL = 'gemini-2.0-flash'` hardcoding** (`test/helpers/llm_judge.py` line 96) — I6 violation; any eval script must route through the capability descriptor system.
3. **OpenClaw Python scripts as-is** (`openclaw/bin/*.py`) — they assume the OpenClaw runtime and its `~/.openclaw/` directory structure, which WabbleSpec has no equivalent of.

**Classification:** Supporting reference — useful for specific sub-problems (eval architecture, SKILL.md structure, safety taxonomy documentation).

**Recommended next action:** Read `openclaw/shared/recommendation-quality.md` and `google-ads/shared/analysis-principles.md` in a single sitting, then open WabbleSpec's Instinct and Benchmark SKILL.md files. Write down which instinct drawer field names should be renamed. That comparison costs 30 minutes and produces a concrete improvement target.
