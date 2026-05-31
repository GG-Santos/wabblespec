# Ref-Eval: Agent Skills for Context Engineering

**Slug:** `agent-skills-context-engineering`
**Reference path:** `C:\Vaults\references\Other Projects References\Agent-Skills-for-Context-Engineering-main\Agent-Skills-for-Context-Engineering-main`
**Evaluation date:** 2026-05-31
**Reference version:** 1.2.0 (collection); individual skills at v2.0.0–v4.0.0
**Evaluator:** ref-adopt
**Trust level:** MEDIUM (open-source, cited in academic papers, no formal test suite)

---

## Step 1b — File Inventory

| File | Purpose | Size | Key Contents | Status | Transfer Check |
|---|---|---|---|---|---|
| SKILL.md (root) | Collection-level metadata + skill map | Small | Progressive disclosure philosophy, skill map summary | Read | N/A — index file |
| README.md | Usage guide, installation, examples | Medium | Plugin marketplace install, skill triggers table | Read | Low — installation instructions not transferable |
| CLAUDE.md | Authoring conventions | Small | Third-person writing, Gotchas mandate, platform-agnostic rules, token-consciousness | Read | **High** — skill authoring conventions for any SKILL.md project |
| CONTRIBUTING.md | Contribution guide | Small | Skill structure requirements, 500-line limit | Read | Low |
| LICENSE | MIT license | Tiny | MIT | Skipped | None |
| .claude-plugin/marketplace.json | Plugin manifest | Small | Plugin bundling structure | Skipped | Low |
| .plugin/plugin.json | Open Plugins manifest | Small | Cross-platform plugin format | Skipped | Low |
| docs/agentskills.md | Official Agent Skills format + authoring best practices | Large | Freedom calibration (high/medium/low), nested-reference anti-pattern (max 1 deep), evaluation-driven development, checklist-before-share | Read | **High** — canonical skill authoring reference |
| docs/compression.md | Factory Research compression evaluation study | Large | 36K messages, 6-dimension rubric, probe types, Factory (3.70) vs OpenAI (3.35) vs Anthropic (3.44), artifact trail 2.2-2.5/5 universally weak | Read | **High** — production-hardened evaluation methodology |
| docs/vercel_tool.md | Vercel d0 architectural reduction case study | Medium | 17→2 tools, 100% vs 80% success, 3.5x faster, 37% fewer tokens | Read | **High** — consolidation principle evidence |
| docs/netflix_context.md | Netflix AI Summit talk on context compression | Large | Three-phase (research/plan/implement), essential vs accidental complexity, 5M tokens → 2K word spec | Read | Medium — validates WabbleSpec's existing recipe/specify pipeline |
| docs/skills-improvement-analysis.md | Self-audit against Anthropic article | Medium | Knowledge-first vs action-first gap, on-demand hooks missing, config.json missing | Read | **High** — identifies gaps applicable to WabbleSpec skill quality |
| docs/agentskills.md (authoring guide section) | Skill authoring best practices | Large | Freedom calibration, no-voodoo-constants, feedback loops, evaluation-driven development | Read | **High** |
| docs/blogs.md | External blog links | Tiny | Reference links only | Skipped | None |
| docs/claude_research.md | Claude context research notes | Medium | Summarized context engineering research | Skipped | Transfer: Medium — source material already in skills |
| docs/gemini_research.md | Gemini research notes | Medium | Gemini-specific context patterns | Skipped | Transfer: Low — provider-specific |
| docs/hncapsule.md | Karpathy HN Capsule notes | Small | Pipeline case study details | Skipped | Low — case study covered in project-development skill |
| skills/context-fundamentals/SKILL.md | Core context concepts | Medium | Attention budget, U-curve (85-95% edges, 76-82% middle), 60-70% effective capacity, tool schema 2-3x inflation, 7 gotchas | Read | **High** |
| skills/context-fundamentals/references/context-components.md | Detailed component reference | Unknown | Component implementation | Skipped | Transfer: Medium — implementation detail for context component management |
| skills/context-fundamentals/scripts/context_manager.py | Python context manager | Unknown | Code example | Skipped | Low |
| skills/context-degradation/SKILL.md | Degradation patterns | Medium | 5 patterns, four-bucket mitigation, empirical thresholds, counterintuitive findings (shuffled > coherent), 7 gotchas | Read | **High** |
| skills/context-degradation/references/patterns.md | Detection code | Unknown | Implementation patterns | Skipped | Transfer: Medium — detection code |
| skills/context-degradation/scripts/degradation_detector.py | Degradation detector | Unknown | Code | Skipped | Low |
| skills/context-compression/SKILL.md | Compression strategies | Medium | Anchored iterative vs opaque vs regenerative, 6-dim evaluation, probe types, compression ratios (98.6/98.7/99.3%), artifact trail problem | Read | **High** |
| skills/context-compression/references/evaluation-framework.md | Eval framework detail | Unknown | Scoring rubrics, LLM judge config | Skipped | Transfer: **High** — scoring rubrics for compression evaluation |
| skills/context-compression/scripts/compression_evaluator.py | Evaluator script | Unknown | Code | Skipped | Low |
| skills/context-optimization/SKILL.md | Optimization techniques | Medium | KV-cache (stable-prefix, no timestamps), masking rules (3+ turns, never current), compaction (50-70% target, <5% quality), partitioning thresholds | Read | **High** |
| skills/context-optimization/references/optimization_techniques.md | Detailed techniques | Unknown | Code patterns, threshold tables | Skipped | Transfer: Medium |
| skills/context-optimization/scripts/compaction.py | Compaction script | Unknown | Code | Skipped | Low |
| skills/multi-agent-patterns/SKILL.md | Multi-agent patterns | Medium | 3 patterns, 15x cost, telephone-game forward_message fix, BrowseComp 95% variance, supervisor 3-5 cap, sycophancy detection | Read | **High** |
| skills/multi-agent-patterns/references/frameworks.md | Framework code examples | Unknown | LangGraph/AutoGen/CrewAI code | Skipped | Low — vendor-specific |
| skills/multi-agent-patterns/scripts/coordination.py | Coordination script | Unknown | Code | Skipped | Low |
| skills/memory-systems/SKILL.md | Memory framework comparison | Large | Mem0/Zep/Letta/Cognee/LangMem comparison, LoCoMo 74% vs 68.5%, Zep 90% latency reduction, temporal KG, escalation path | Read | **High** |
| skills/memory-systems/references/implementation.md | Implementation code | Unknown | Vector stores, property graphs, consolidation code | Skipped | Transfer: Medium |
| skills/memory-systems/scripts/memory_store.py | Memory store script | Unknown | Code | Skipped | Low |
| skills/tool-design/SKILL.md | Tool design principles | Medium | Consolidation principle, 4-question description template (what/when/inputs/returns), MCP namespacing, architectural reduction, 9 gotchas | Read | **High** |
| skills/tool-design/references/architectural_reduction.md | Vercel case study detail | Unknown | Production evidence for reduction | Skipped | Transfer: **High** — production evidence for tool consolidation |
| skills/tool-design/references/best_practices.md | Best practices detail | Unknown | Tool design checklist | Skipped | Transfer: Medium |
| skills/tool-design/scripts/description_generator.py | Description generator | Unknown | Code | Skipped | Transfer: Medium — could be used for tool description optimization |
| skills/filesystem-context/SKILL.md | Filesystem patterns | Medium | 4 failure modes (missing/under/over/buried), 6 patterns (scratch pad, plan persistence, sub-agent comms, dynamic skill, terminal, self-modification), 8 gotchas | Read | **High** |
| skills/filesystem-context/references/implementation-patterns.md | Implementation detail | Unknown | Code beyond inline | Skipped | Transfer: Medium |
| skills/filesystem-context/scripts/filesystem_context.py | Filesystem script | Unknown | Code | Skipped | Low |
| skills/evaluation/SKILL.md | Evaluation methods | Medium | Multi-dimensional rubrics, BrowseComp (token usage 80% variance), 0.7/0.9 thresholds, 50+ sample size, 8 gotchas | Read | **High** |
| skills/evaluation/references/metrics.md | Metric design detail | Unknown | Scoring scales, weighted rubrics | Skipped | Transfer: **High** — rubric calculation formulas |
| skills/evaluation/scripts/evaluator.py | Evaluator script | Unknown | Code | Skipped | Low |
| skills/advanced-evaluation/SKILL.md | LLM-as-judge | Large | Direct scoring vs pairwise, position bias mitigation (swap+consistency), confidence calibration, rubric generation (40-60% variance reduction), Panel of LLMs | Read | **High** |
| skills/advanced-evaluation/references/bias-mitigation.md | Bias mitigation detail | Unknown | Detailed bias protocols | Skipped | Transfer: **High** |
| skills/advanced-evaluation/references/evaluation-pipeline.md | Pipeline diagram | Unknown | Multi-stage eval architecture | Skipped | Transfer: High |
| skills/advanced-evaluation/references/implementation-patterns.md | Implementation | Unknown | Build-from-scratch patterns | Skipped | Transfer: High |
| skills/advanced-evaluation/references/metrics-guide.md | Statistical metrics | Unknown | Spearman/Kendall/Cohen's kappa | Skipped | Transfer: High |
| skills/advanced-evaluation/scripts/evaluation_example.py | Script | Unknown | Code | Skipped | Low |
| skills/hosted-agents/SKILL.md | Background agent infra | Medium | Sandbox lifecycle, warm pools, predictive warm-up, multiplayer, per-session SQLite, 8 gotchas | Read | Low — infrastructure-specific, not WabbleSpec's domain |
| skills/hosted-agents/references/infrastructure-patterns.md | Infra patterns | Unknown | Sandbox code | Skipped | Low |
| skills/project-development/SKILL.md | LLM project methodology | Medium | Task-model fit table, acquire/prepare/process/parse/render pipeline, file-system state machine, cost formula, Vercel/Karpathy examples | Read | **High** |
| skills/project-development/references/case-studies.md | Case study detail | Unknown | Karpathy HN, Vercel d0 | Skipped | Transfer: Medium |
| skills/project-development/references/pipeline-patterns.md | Pipeline patterns | Unknown | Caching strategies, stage design | Skipped | Transfer: Medium |
| skills/bdi-mental-states/SKILL.md | BDI cognitive architecture | Medium | T2B2T paradigm, RDF/Turtle, temporal validity, SPARQL, LAG | Read | Low — highly domain-specific, minimal WabbleSpec relevance |
| skills/bdi-mental-states/references/* | BDI references | Unknown | Ontology, SPARQL | Skipped | Low |
| template/SKILL.md | Canonical skill template | Small | Section structure, Gotchas section, When-to-Activate | Read | **High** — canonical structure for any skill collection |
| examples/digital-brain-skill/HOW-SKILLS-BUILT-THIS.md | Skill traceability | Medium | 87% token reduction, cross-skill synergies, quantified impact | Read | **High** — proof that skill principles produce measurable outcomes |
| examples/digital-brain-skill/SKILLS-MAPPING.md | Skills map | Unknown | How skills map to implementation | Skipped | Transfer: Low — product-specific |
| examples/interleaved-thinking/SKILL.md | Reasoning trace optimizer | Small | Uses MiniMax M2.1 + rto CLI binary | Read | **NONE** — model names (I6) + external binary dependency |
| examples/interleaved-thinking/reasoning_trace_optimizer/*.py | Python optimizer | Unknown | Optimization loop, pattern detection | Skipped | Transfer: Low — model-specific API calls throughout |
| examples/llm-as-judge-skills/README.md | LLM judge example | Unknown | TypeScript implementation | Skipped | Transfer: Low — TypeScript/Node, vendor-specific |
| examples/llm-as-judge-skills/prompts/evaluation/* | Evaluation prompts | Unknown | Direct scoring + pairwise comparison prompt templates | Skipped | Transfer: **High** — prompt templates |
| examples/book-sft-pipeline/SKILL.md | Book SFT pipeline | Unknown | Author style training | Skipped | Transfer: Low — ML fine-tuning domain |
| examples/x-to-book-system/PRD.md | X-to-book PRD | Unknown | Product requirements | Skipped | Low |
| researcher/llm-as-a-judge.md | Research curation rubric | Large | 4-gate gatekeeper (G1-G4) + 4-dimension scoring (35/30/20/15) + thresholds (1.4/0.9) + override rules | Read | **High** — production-hardened research curation methodology |
| researcher/example_output.md | Rubric example output | Unknown | Sample evaluation JSON | Skipped | Low |

---

## Step 1c — Connection Map

```
context-fundamentals --[foundational]--> ALL OTHER SKILLS
context-degradation --[diagnosis → mitigation]--> context-optimization
context-compression --[evaluation methodology]--> evaluation
context-compression --[probe types]--> advanced-evaluation
multi-agent-patterns --[shared state]--> memory-systems
multi-agent-patterns --[tool specialization]--> tool-design
multi-agent-patterns --[context isolation]--> context-optimization
filesystem-context --[overflow layer]--> context-optimization
filesystem-context --[sub-agent workspace]--> multi-agent-patterns
evaluation --[foundational]--> advanced-evaluation
project-development --[methodology]--> ALL SKILLS (meta)
docs/compression.md --[empirical backing]--> context-compression/SKILL.md
docs/vercel_tool.md --[case study]--> tool-design/SKILL.md, project-development/SKILL.md
docs/netflix_context.md --[case study]--> context-compression/SKILL.md, project-development/SKILL.md
docs/skills-improvement-analysis.md --[self-audit]--> ALL SKILLS
researcher/llm-as-a-judge.md --[rubric source]--> advanced-evaluation/SKILL.md, evaluation/SKILL.md
examples/digital-brain-skill --[production proof]--> ALL SKILLS
```

Key contract: `context-degradation` produces a diagnosis that `context-optimization` consumes via the Four-Bucket framework. The compression evaluation in `docs/compression.md` is the empirical backing for claims in `context-compression/SKILL.md`. Breaking the compression skill's connection to the doc would leave claims ungrounded.

---

## Section 1 — Reference Summary

**Type:** Production skill collection / behavioral specification — open-source, cited in academic research (Peking University 2026 paper on meta-context engineering), actively maintained (v4.0.0 on memory-systems), platform-agnostic.

**Behavioral content:** 13 skills encoding operational logic for context management in AI agent systems. Covers: attention budget management, five degradation patterns with mitigations, three compression approaches with empirical quality scores, four context optimization strategies with numeric thresholds, three multi-agent architecture patterns, memory framework comparison with benchmark data, tool consolidation principles with production evidence, six filesystem-as-context patterns, evaluation rubric design, LLM-as-judge with bias mitigation, project development methodology, and BDI cognitive architecture.

**Structural content:** SKILL.md / references/ / scripts/ three-tier progressive disclosure pattern. Consistent section structure (When to Activate, Core Concepts, Detailed Topics, Practical Guidance, Examples, Guidelines, Gotchas, Integration, References). Template enforces Gotchas as mandatory. Skills cross-reference each other by name only (not links) to avoid directory resolution issues.

**Interaction content:** Skills are designed to be loaded independently but reference each other by slug name. `context-fundamentals` is a prerequisite for all others. Docs directory provides empirical backing for skill claims — skills are weakened if docs are ignored. `researcher/llm-as-a-judge.md` is the source rubric that informed `advanced-evaluation/SKILL.md` and `evaluation/SKILL.md`.

**Maturity:** No formal test suite. Has eval fixtures in examples directory. Cited in academic paper. Self-improvement analysis document shows active reflection. Version numbers suggest sustained maintenance. Skills-improvement-analysis.md identifies known gaps (no hooks, no config.json) suggesting honest self-assessment.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| context-compression/SKILL.md: Anchored iterative summarization structure | Mandatory sections: Session Intent / Files Modified / Decisions Made / Current State / Next Steps | WabbleSpec's executor compacts but uses freeform summarization — structure forces preservation of receipts and wave artifacts | Add mandatory section template to executor SKILL.md's compaction guidance; frame as "artifact-trail-preserving compaction" | **High** |
| docs/compression.md: Artifact trail finding | Score 2.2-2.5/5.0 even with structured summarization — weakest dimension across all methods | Validates why WabbleSpec's receipt chain is architecturally correct: receipts ARE the artifact trail solution that compression cannot provide | Add explicit note to executor SKILL.md: "Artifact trail is universally weak in context compression (2.2-2.5/5.0). WabbleSpec's receipt chain is the non-compression solution to this documented problem." | **High** |
| context-compression/SKILL.md: Six evaluation dimensions | Accuracy / Context Awareness / Artifact Trail / Completeness / Continuity / Instruction Following | WabbleSpec's verifier evaluates wave outputs but lacks a formal compression quality gate for compacted context | Add six-dimension probe evaluation to executor SKILL.md for verifying compaction quality before proceeding past compaction checkpoint | **High** |
| context-degradation/SKILL.md: Four-Bucket mitigation framework | Write / Select / Compress / Isolate — each with specific trigger conditions | WabbleSpec's economy skill lacks a unified context management decision tree with named strategies | Add Four-Bucket section to economy SKILL.md with explicit trigger conditions (70% threshold for Compress, confusion signals for Isolate) | **High** |
| context-fundamentals/SKILL.md: Quantitative thresholds | 60-70% effective capacity, 70-80% compaction trigger, 2-3x tool schema inflation, 83.9% tool output token share in agent trajectories | Executor's context management guidance currently lacks these specific thresholds | Add as a "Context Budget Reference" section to executor SKILL.md | **High** |
| researcher/llm-as-a-judge.md: 4-gate + 4-dimension rubric | G1-G4 gatekeepers + D1-D4 with weights (Technical Depth 35% / CE Relevance 30% / Evidence Rigor 20% / Novelty 15%) + thresholds (APPROVE ≥1.4, HUMAN_REVIEW 0.9-1.4, REJECT <0.9) + 4 override rules | WabbleSpec's ref-eval skill uses a subjective 1-10 scale; this rubric is more formally specified with named gates and mathematical decision thresholds | Adapt gates and dimension structure (filtering model names per I6) into ref-eval SKILL.md as a formal gatekeeper pass | **High** |
| advanced-evaluation/SKILL.md: Position bias mitigation | Position swap protocol (evaluate A-B then B-A, consistency check, TIE on disagreement), justification-before-score (15-25% reliability improvement) | WabbleSpec's adversary/grader/verifier skills don't specify bias mitigation for comparative evaluations | Add position swap requirement to adversary SKILL.md "comparative analysis" section; add justification-before-score rule to grader SKILL.md | **Medium** |
| advanced-evaluation/SKILL.md: Rubric generation structure | 5-component rubric: Level descriptions / Characteristics / Examples / Edge cases / Scoring guidelines; strictness calibration (lenient/balanced/strict) | WabbleSpec's skill-tdd and benchmark-loop lack formal rubric construction guidance | Add rubric generation template to benchmark-loop SKILL.md eval fixture section; add strictness calibration to grader SKILL.md | **Medium** |
| context-optimization/SKILL.md: KV-cache stability rules | Never include timestamps/session counters/request IDs in system prompt; stable-before-dynamic ordering (system prompt → tool definitions → templates → history → query) | WabbleSpec hooks and executor may inject dynamic metadata that breaks prefix caching | Add "Cache Stability" rule to CLAUDE.md or executor SKILL.md: "Never inject dynamic metadata (timestamps, session IDs) into the system prompt prefix — this destroys KV-cache hit rate." | **Medium** |
| multi-agent-patterns/SKILL.md: Telephone game fix | `forward_message` tool pattern: sub-agents pass responses directly to users when supervisor synthesis would lose fidelity; 50% initial performance gap | WabbleSpec's executor dispatches subagents via Agent tool but doesn't address supervisor paraphrase degradation | Add telephone game anti-pattern and forward_message principle to executor SKILL.md subagent dispatch section | **Medium** |
| context-fundamentals/SKILL.md: Gotchas | "Critical instructions in the middle get lost" (10-40% reduced recall), "Progressive disclosure that loads too eagerly defeats its purpose" | These are directly applicable to WabbleSpec's SKILL.md authoring quality | Add to CLAUDE.md skill authoring section as specific position-placement rules | **Medium** |
| evaluation/SKILL.md: BrowseComp 95% variance finding | Token usage explains 80% of agent performance variance; model quality matters more than doubling tokens | WabbleSpec's benchmark-loop and model-router decisions can be grounded in this empirical finding | Add to model-router SKILL.md as a decision weight: "Token budget explains 80% of variance; model quality change is more leverage than 2x token budget." | **Medium** |
| docs/agentskills.md: Freedom calibration | High/medium/low freedom calibration — narrow-bridge vs open-field analogy for instruction specificity | WabbleSpec's CLAUDE.md has authoring rules but lacks this systematic calibration framework | Add freedom calibration section to CLAUDE.md skill authoring conventions | **Medium** |
| docs/agentskills.md: Nested reference anti-pattern | References must be max 1 level deep from SKILL.md; Claude does partial reads (head -100) on nested references, producing incomplete information | WabbleSpec skills may have multi-level reference nesting | Add to CLAUDE.md: "Skill references must be 1 level deep from SKILL.md. Nested reference chains (SKILL.md → ref-A → ref-B) cause Claude to read ref-B incompletely using head -100." | **Low** |
| context-degradation/SKILL.md: Counterintuitive findings | "Shuffled context outperforms coherent context for retrieval tasks" / "Single distractor has step-function impact (not linear)" | These challenge naive context organization assumptions in WabbleSpec's executor | Add as gotchas to economy SKILL.md or a new context-quality reference | **Low** |
| memory-systems/SKILL.md: Framework comparison + escalation path | Filesystem → Mem0 → Zep/Graphiti → Letta/Cognee escalation; Letta filesystem 74% LoCoMo vs Mem0 68.5% (simpler wins) | WabbleSpec's memory system uses proprietary drawers; this provides evidence that simple memory can outperform complex | Add as reference to memory SKILL.md: "External benchmark: filesystem-based memory scored 74% on LoCoMo vs Mem0's 68.5% — add complexity only when retrieval quality demonstrably degrades." | **Low** |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| Multiple skills / docs | Model name contamination | Reference uses `GPT-5.2`, `Claude Opus 4.5`, `MiniMax M2.1` as LLM judge names throughout — violates I6 | Filter all model names; replace with capability descriptors (`analysis`, `code-generation`, `long-context`) | **Critical** |
| examples/interleaved-thinking/SKILL.md | External binary dependency (rto CLI) + model-specific API | Skill is powered by MiniMax M2.1 and requires `rto` external tool — completely non-transferable | Do not adopt anything from this example | **Critical** |
| Numeric thresholds (compression ratios, benchmark scores) | Threshold staleness | Scores like 3.70/3.44/3.35, 74%/68.5% LoCoMo, reflect specific model versions that will drift | Mark all numeric benchmarks as point-in-time signals, not permanent targets; add staleness caveats | **High** |
| docs/compression.md: Uses GPT-5.2 as LLM judge label | LLM judge model name | Even in the research backing doc the evaluator is named as "GPT-5.2" — cannot adopt as-is | Adopt the rubric methodology while removing the model name; replace with "independent analysis capability" | **High** |
| researcher/llm-as-a-judge.md: Weighted thresholds | Over-calibration risk | Adapting the 1.4/0.9 thresholds and 35/30/20/15 weights literally could cause ref-eval decisions to hinge on small score differences | Adopt as structural framework, not as hard-coded pass/fail numbers; retain human judgment override | **Medium** |
| BDI mental states skill | Domain-specific noise | The BDI skill is highly specialized (RDF, SPARQL, formal ontology) with minimal relevance to WabbleSpec's SDLC domain | Treat as inspiration-only; do not adopt any BDI patterns | **Low** |
| agentskills.io URL reference | Stale external URL | Reference mentions agentskills.io URL for validation tools that may not be stable | Do not reference the URL; use the conceptual framework only | **Low** |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Anchored iterative summarization template | **Adapt** | Directly applicable to executor compaction | executor SKILL.md | P1 |
| Artifact trail finding (2.2-2.5/5 weakness) | **Adapt** | Validates receipt chain architecture | executor SKILL.md | P1 |
| Six compression dimensions + probe types | **Adapt** | Formalizes compaction quality verification | executor SKILL.md | P1 |
| Four-Bucket context management framework | **Adapt** | Missing decision tree in economy | economy SKILL.md | P1 |
| Quantitative context thresholds (60-70%, 70-80%, 2-3x) | **Adapt** | Direct executor/guard calibration | executor SKILL.md | P1 |
| 4-gate + 4-dimension research curation rubric | **Adapt** (filter model names) | Formalizes ref-eval scoring | ref-eval / grader SKILL.md | P1 |
| Position bias mitigation protocol | **Adapt** | Adversary/grader missing this | adversary + grader SKILL.md | P2 |
| Rubric generation (5-component, strictness calibration) | **Adapt** | Benchmark-loop/skill-tdd improvement | benchmark-loop + skill-tdd | P2 |
| KV-cache stability rules | **Adapt** | CLAUDE.md convention gap | CLAUDE.md | P2 |
| Telephone game fix (forward_message pattern) | **Adapt** | Executor subagent dispatch | executor SKILL.md | P2 |
| BrowseComp 95% variance finding | **Adapt** | Model-router decision weight | model-router SKILL.md | P2 |
| Freedom calibration (high/medium/low) | **Adapt** | CLAUDE.md skill authoring | CLAUDE.md | P2 |
| Nested reference anti-pattern (1-level limit) | **Adapt** | CLAUDE.md skill authoring | CLAUDE.md | P3 |
| Memory framework comparison table | **Adapt** (add as reference context) | Memory SKILL.md background | memory SKILL.md | P3 |
| Four filesystem context failure modes | **Study only** | Already encoded in executor/economy; too granular | – | – |
| BrowseComp 95% finding (token > model) | **Adapt** | model-router decision grounding | model-router SKILL.md | P2 |
| BDI mental states skill | **Avoid** | Domain-specific (RDF/SPARQL); no WabbleSpec relevance | – | – |
| interleaved-thinking example | **Avoid** | Model names (I6) + external binary dependency | – | – |
| Model names everywhere | **Avoid** | Violates I6 | – | – |
| agentskills.io URL | **Avoid** | Stale external URL (prior directive) | – | – |
| Numeric benchmark thresholds as hard targets | **Study Only** | Point-in-time signals, adopt structure not numbers | – | – |
| Hosted agents infrastructure | **Study only** | WabbleSpec is not a hosted agent builder | – | – |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | **9** | Context engineering IS the operational domain of WabbleSpec's executor, guard, economy, and memory pipeline. The reference's framing of context as "finite attention budget with diminishing returns" is the same mental model WabbleSpec's SDLC framework needs for its wave execution engine. |
| Architecture fit | **8** | WabbleSpec's three-tier skill loading (frontmatter → SKILL.md body → references/) matches the reference's progressive disclosure pattern exactly. Receipt chain maps to the reference's artifact trail problem. |
| Implementation fit | **7** | Most adaptations are additive (new sections in existing skills) rather than structural. I6 filtering is required throughout but is not difficult. The biggest implementation work is the grader rubric formalization. |
| Maintenance fit | **7** | Reference is well-maintained (updated 2026-03-17 across skills). Benchmark data will age but structural patterns are durable. |
| Risk level | **2** | No architectural conflicts. No breaking changes required. Only risk is model-name contamination if filtering is missed. |
| Overall usefulness | **8** | Supporting reference, worth active use. Phase 1 items directly improve executor compaction quality and grader formalization. |

---

## Section 6 — Recommended Extraction Plan

### Phase 1 — Safe Learning (Implement now)

1. **Anchored iterative summarization template** — `executor SKILL.md` — Add mandatory section template (Session Intent / Files Modified / Decisions Made / Current State / Next Steps) to compaction guidance. Source: `context-compression/SKILL.md` §"Structure Summaries with Mandatory Sections".

2. **Artifact trail receipt validation note** — `executor SKILL.md` — Add note: "Artifact trail is universally the weakest compression dimension (2.2-2.5/5.0 even with structured summarization). WabbleSpec's receipt chain is the architectural solution to this problem — receipts track artifacts explicitly rather than relying on summarization." Source: `docs/compression.md` §"Results".

3. **Six compression dimensions + probe types** — `executor SKILL.md` — Add a "Compaction Quality Gate" section with the six evaluation dimensions and four probe types (Recall/Artifact/Continuation/Decision) as the verification gate before marking a wave compaction complete. Source: `context-compression/SKILL.md` §"Score Compression Across Six Dimensions".

4. **Four-Bucket context management framework** — `economy SKILL.md` — Add a "Context Failure Strategy" section with Write/Select/Compress/Isolate and their trigger conditions (70% threshold for Compress, confusion/clash for Isolate). Source: `context-degradation/SKILL.md` §"The Four-Bucket Mitigation Framework".

5. **Context budget thresholds** — `executor SKILL.md` — Add quantitative reference: "Effective capacity: 60-70% of advertised window. Compaction trigger: 70-80% utilization. Tool schemas inflate 2-3x after JSON serialization. Tool outputs reach 83.9% of tokens in agent trajectories." Source: `context-fundamentals/SKILL.md` §"Gotchas" + §"The Attention Budget".

6. **Gatekeeper criteria (G1-G4) in ref-eval** — `.claude/skills/ref-eval/SKILL.md` (if exists) or grader SKILL.md — Add the four-gate pre-screening (Mechanism Specificity / Implementable Artifacts / Beyond Basics / Source Verifiability) as a pre-screening step before running the full evaluation. Source: `researcher/llm-as-a-judge.md`.

### Phase 2 — Low-Risk Adaptation

7. **Position bias mitigation** — `adversary SKILL.md` + `grader SKILL.md` — Add: "For comparative evaluations: evaluate twice with swapped positions. If passes disagree, return TIE with reduced confidence. Always require justification before the score (15-25% reliability improvement)." Source: `advanced-evaluation/SKILL.md` §"Pairwise Comparison Implementation".

8. **Rubric generation template** — `benchmark-loop SKILL.md` + `skill-tdd SKILL.md` — Add 5-component rubric structure (Level descriptions / Characteristics / Examples / Edge cases / Scoring guidelines) with strictness calibration (lenient/balanced/strict). Source: `advanced-evaluation/SKILL.md` §"Rubric Generation".

9. **KV-cache stability rule** — `CLAUDE.md` — Add to skill authoring conventions: "Never inject dynamic metadata (timestamps, session IDs, version numbers) into the stable prompt prefix. Even one character change invalidates the entire KV-cache block downstream. Move dynamic metadata into a separate user message or tool result." Source: `context-optimization/SKILL.md` §"KV-Cache Optimization" Gotcha 1-2.

10. **Telephone game anti-pattern** — `executor SKILL.md` — Add: "Supervisor architectures initially perform ~50% worse than optimized versions due to the telephone game problem. Fix by implementing direct-pass patterns: sub-agents should pass final responses directly without supervisor synthesis when the sub-agent response is complete." Source: `multi-agent-patterns/SKILL.md` §"The Telephone Game Problem and Solution".

11. **Freedom calibration** — `CLAUDE.md` — Add skill authoring section: "Match instruction specificity to task fragility: High freedom (text instructions) = multiple valid approaches. Medium freedom (pseudocode + parameters) = preferred pattern with variation acceptable. Low freedom (exact script) = operations are fragile and must follow a specific sequence." Source: `docs/agentskills.md`.

### Phase 3 — Deeper Integration

12. **Nested reference anti-pattern** — `CLAUDE.md` — Add: "Keep skill references 1 level deep from SKILL.md. Nested reference chains cause Claude to use head -100 partial reads on deeply-nested files, producing incomplete information." Source: `docs/agentskills.md` §"Avoid deeply nested references".

13. **Memory framework escalation path** — `memory SKILL.md` or reference doc — Add an external framework comparison note with the escalation path (filesystem → vector store → graph DB → temporal KG) and benchmark signals (simple outperforms complex: 74% vs 68.5% LoCoMo). Source: `memory-systems/SKILL.md`.

### Phase 4 — Do Not Cross

- All model names (GPT-5.2, Claude Opus 4.5, MiniMax M2.1) — violates I6
- interleaved-thinking example — model-specific + external binary
- BDI mental states — domain-specific, not applicable
- agentskills.io URL — stale external reference
- Benchmark numbers as hard-coded targets — use as signal not specification

---

## Section 7 — Final Verdict

**Classification: Supporting reference (8/10)**

**Best 3 to steal:**
1. **Anchored iterative summarization** (`context-compression/SKILL.md` §"Structure Summaries with Mandatory Sections") — Five mandatory sections that prevent silent artifact loss. WabbleSpec's receipt chain is the right solution but its compaction guidance is underspecified.
2. **Research curation rubric** (`researcher/llm-as-a-judge.md`) — Four gatekeepers + four weighted dimensions + formal thresholds (1.4/0.9) + override rules. Most formally specified evaluation rubric in the reference. Strengthens ref-eval significantly after filtering model names.
3. **Four-Bucket context management** (`context-degradation/SKILL.md` §"The Four-Bucket Mitigation Framework") — Write/Select/Compress/Isolate with explicit trigger conditions. Economy SKILL.md needs exactly this decision tree.

**Worst 3 to avoid:**
1. **interleaved-thinking example** — Completely non-transferable (model names + external binary). Contains zero extractable patterns.
2. **BDI mental states skill** — Formally interesting but the RDF/SPARQL/ontology domain has no relevance to WabbleSpec's SDLC framework.
3. **Benchmark numbers as specifications** — Scores like 3.70/3.35 and 74%/68.5% reflect specific model versions at a point in time. Treating them as permanent targets is a staleness trap.

**Recommended next action:** Proceed to Phase 2 (ref-plan). Reference has strong behavioral content that maps well to WabbleSpec's executor/economy/grader/adversary modules with only I6 filtering required.

---

## Section 8 — Project Synthesis

The generative question: what novel patterns become possible by combining this reference's context engineering principles with WabbleSpec's specific receipt-gated, wave-based execution architecture?

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| **Receipt-aware compaction quality gate** | Six-dimension compression evaluation + probe types (Accuracy/Artifact Trail/Continuity/etc.) | Receipt chain explicitly tracks artifacts across wave boundaries — WabbleSpec knows exactly what the "artifact trail" should contain | `executor SKILL.md` §compaction | WabbleSpec's compaction has no quality gate; applying the reference's six dimensions against the receipt chain creates a verifiable compaction pass/fail |
| **Gatekeeper-first ref-eval pass** | Four gates (Mechanism Specificity/Artifacts/Beyond Basics/Source Verifiability) with binary pass/fail before full evaluation | ref-eval already has 9-section evaluation; a pre-screening gate would abort low-value references before the full pipeline runs | `ref-eval SKILL.md` Phase 1 | Current ref-eval wastes cycles on references that would fail basic quality gates; adding gatekeepers reduces wasted evaluation effort |
| **Context-budget-aware guard check** | 70-80% compaction trigger, 60-70% effective capacity cliff, distractor step-function impact | Guard currently checks authority + command risk; adding context utilization signals creates a third guard dimension | `guard SKILL.md` + `guard/skill-rules.json` | Guard has no visibility into context budget; a pre-execution context-budget check prevents degradation-induced errors from being mistaken for model capability limits |

---

## Section 9 — Expansion Opportunities

**Per-skill growth scan:**

| Capability | Reference location | WabbleSpec equivalent | Tier 7? |
|---|---|---|---|
| Context fundamentals knowledge | context-fundamentals/SKILL.md | Covered via economy + executor | No |
| Degradation pattern recognition | context-degradation/SKILL.md | Partially covered via guard/economy | No — gap is Tier 1 addition to economy |
| Compression evaluator tool | context-compression/SKILL.md + docs/compression.md | No equivalent — WabbleSpec compacts but never evaluates compaction quality | **Yes** |
| Context optimization techniques | context-optimization/SKILL.md | Covered via executor | No |
| Multi-agent coordination patterns | multi-agent-patterns/SKILL.md | Covered via autopilot/executor | No |
| Memory framework selection guide | memory-systems/SKILL.md | WabbleSpec uses proprietary drawers; no external framework comparison | **Yes** |
| Tool design principles | tool-design/SKILL.md | Covered via CLAUDE.md conventions | No |
| Filesystem-context patterns | filesystem-context/SKILL.md | Covered via existing pattern | No |
| Hosted agent infrastructure | hosted-agents/SKILL.md | Not applicable — WabbleSpec is not a hosted agent builder | No |
| Multi-dimensional evaluation rubrics | evaluation/SKILL.md | Covered via grader/verifier | No — gap is Tier 1 formalization |
| LLM-as-judge with bias mitigation | advanced-evaluation/SKILL.md | Partially covered in adversary + grader | No — gap is Tier 1 addition |
| Project development methodology | project-development/SKILL.md | Covered via recipe/specify/decompose | No |
| BDI cognitive architecture | bdi-mental-states/SKILL.md | No equivalent | No — domain-specific |
| Research curation rubric | researcher/llm-as-a-judge.md | ref-eval has informal scoring | No — Tier 1 addition to ref-eval |

**Expansion opportunities (Tier 7 candidates):**

| Capability | Reference location | Why WabbleSpec lacks it | What it would unlock | Effort | Tier 7? |
|---|---|---|---|---|---|
| **Compaction quality evaluator** | `context-compression/SKILL.md` + `docs/compression.md` | WabbleSpec's executor compacts via Claude but never evaluates whether compaction preserved artifact trail; the receipt chain tracks artifacts pre-compaction but no gate verifies the compaction output | A compaction quality gate that runs probe-based verification after each executor compaction step, preventing wave continuation when critical context (file paths, error codes, decisions) was lost | Days | **Yes** |
| **Memory framework selection guide** | `memory-systems/SKILL.md` | WabbleSpec's memory is proprietary drawer-based; no guide exists for when/whether to add external frameworks (Mem0/Zep/Cognee) as the drawer count grows | When users want to query across drawers semantically (beyond metadata search), a selection guide would enable principled decisions about adding vector/graph layers | Weeks | **Yes** |

**Gateway bundling signal:** Both Tier 7 candidates are operationally distinct (compaction evaluation vs memory framework selection) and do not share a common output layer. No bundling recommendation.

---

## Memory Drawers Written

See `.wabblespec/state/memory/wings/references/rooms/agent-skills-context-engineering/` for drawers written during this evaluation.
