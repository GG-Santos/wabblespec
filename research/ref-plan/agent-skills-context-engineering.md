# Ref-Plan: Agent Skills for Context Engineering

**Slug:** `agent-skills-context-engineering`
**Plan date:** 2026-05-31
**Based on:** `research/ref-eval/agent-skills-context-engineering.md`

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| C1 | Anchored iterative summarization template (mandatory sections) | Behavioral | High | High | Low |
| C2 | Artifact trail receipt validation note | Behavioral | High | High | Low |
| C3 | Six compression evaluation dimensions + probe types | Behavioral | High | High | Low |
| C4 | Four-Bucket context management framework | Behavioral | High | High | Low |
| C5 | Quantitative context thresholds (60-70%, 70-80%, 2-3x) | Behavioral | High | High | Low |
| C6 | Four-gate research curation gatekeeper criteria | Behavioral | High | High | Low |
| C7 | Position bias mitigation protocol | Behavioral | Medium | High | Low |
| C8 | Rubric generation template (5-component + strictness calibration) | Behavioral | Medium | High | Low |
| C9 | KV-cache stability rule | Behavioral | Medium | High | Low |
| C10 | Telephone game anti-pattern + direct-pass principle | Behavioral | Medium | High | Low |
| C11 | BrowseComp 95% variance finding (token > model) | Behavioral | Medium | Medium | Low |
| C12 | Freedom calibration (high/medium/low) | Format | Medium | High | Low |
| C13 | Nested reference anti-pattern (1-level limit) | Format | Low | Medium | Low |
| C14 | Memory framework escalation path | Behavioral | Low | Low | Low |

---

## Exclusion List (hard stop — do not implement)

| Item | Invariant reason |
|---|---|
| All model names (GPT-5.2, Claude Opus 4.5, MiniMax M2.1, etc.) | I6 — no model names in framework files |
| interleaved-thinking example (rto binary + MiniMax) | I6 + platform-specific external binary |
| agentskills.io URL | Prior directive from superpowers ref-adopt |
| BDI mental states skill content | Domain-specific (RDF/SPARQL/formal ontology) — no project relevance |
| Benchmark numbers as hard-coded targets (3.70, 74%, 68.5%) | Point-in-time signals, not durable specifications |
| hosted-agents infrastructure patterns | WabbleSpec is not a hosted agent builder |

---

## Scored and Ranked Integration Items

Scoring: `integration_score = (impact × 2) + project_fit - risk`
Mapping: High=3, Medium=2, Low=1

| ID | Item | Score | Tier |
|---|---|---|---|
| C1 | Anchored iterative summarization | (3×2)+3-1 = **8** | 1 |
| C2 | Artifact trail receipt validation note | (3×2)+3-1 = **8** | 1 |
| C3 | Six compression dimensions + probes | (3×2)+3-1 = **8** | 1 |
| C4 | Four-Bucket context management | (3×2)+3-1 = **8** | 1 |
| C5 | Quantitative context thresholds | (3×2)+3-1 = **8** | 1 |
| C6 | Four-gate gatekeeper criteria | (3×2)+3-1 = **8** | 1 |
| C7 | Position bias mitigation | (2×2)+3-1 = **6** | 1 |
| C8 | Rubric generation template | (2×2)+3-1 = **6** | 1 |
| C9 | KV-cache stability rule | (2×2)+3-1 = **6** | 1 |
| C10 | Telephone game anti-pattern | (2×2)+3-1 = **6** | 1 |
| C12 | Freedom calibration | (2×2)+3-1 = **6** | 1 |
| C11 | BrowseComp 95% variance finding | (2×2)+2-1 = **5** | 2 |
| C13 | Nested reference anti-pattern | (1×2)+2-1 = **3** | 2 |
| C14 | Memory framework escalation | (1×2)+1-1 = **2** | Watch Only |

---

## Tier Assignments

### Tier 1 — Behavioral additions to existing files

**C1 — Anchored iterative summarization**
- What: Add mandatory five-section structured summary template to CONTEXT_EXHAUSTION protocol
- Where: `.claude/skills/executor/SKILL.md` — §"CONTEXT_EXHAUSTION — compression protocol"
- How: After the existing "protected-bounds invariant" rules, add a "Structured Summary Template" subsection with five mandatory sections (Session Intent / Files Modified / Decisions Made / Current State / Next Steps), including the domain-specific variant instruction (debugging: add Root Cause; migration: add Source/Target Schema)
- Literal values: "Session Intent", "Files Modified", "Decisions Made", "Current State", "Next Steps"
- Gate: The mandatory sections appear verbatim in executor SKILL.md's CONTEXT_EXHAUSTION block

**C2 — Artifact trail receipt validation note**
- What: Add a note that receipt chain is the architectural solution to the documented artifact trail compression weakness
- Where: `.claude/skills/executor/SKILL.md` — after compression protocol section
- How: Add a one-paragraph callout: "Why receipts beat compaction for artifact tracking: Artifact trail is the weakest dimension in context compression (2.2–2.5/5.0 across all compression methods studied, including structured summarization). WabbleSpec's receipt chain is the non-compression solution: receipts track modified files, function names, and error identifiers explicitly rather than relying on summarization to preserve them."
- Gate: The note references the specific score range (2.2–2.5/5.0) and makes the connection explicit

**C3 — Six compression dimensions + probe types**
- What: Add a "Compaction Quality Verification" subsection that names the six evaluation dimensions and four probe types
- Where: `.claude/skills/executor/SKILL.md` — within CONTEXT_EXHAUSTION block, after the structured summary template
- How: Add a table of six dimensions (Accuracy, Context Awareness, Artifact Trail, Completeness, Continuity, Instruction Following) and four probe types (Recall, Artifact, Continuation, Decision) as the reference gate for what a compacted context must preserve
- Literal values: "Accuracy", "Context Awareness", "Artifact Trail", "Completeness", "Continuity", "Instruction Following"; probe types: "Recall", "Artifact", "Continuation", "Decision"
- Gate: Six dimensions and four probe types appear as named items in executor SKILL.md

**C4 — Four-Bucket context management framework**
- What: Add a "Context Failure Strategy" section with Write/Select/Compress/Isolate buckets and trigger conditions
- Where: `.claude/skills/economy/SKILL.md` — as a new top-level section after the existing mechanical rules
- How: Add a "Context Budget Strategies" section with a table: Write (save outside window, trigger at 70%), Select (filter on retrieval, trigger when distraction symptoms), Compress (reduce tokens via masking/summarization, apply observation masking), Isolate (split to sub-agents, trigger for confusion/clash)
- Literal values: "Write", "Select", "Compress", "Isolate"
- Gate: Four-bucket table with trigger conditions appears in economy SKILL.md

**C5 — Quantitative context thresholds**
- What: Add specific numeric thresholds for context budget management
- Where: `.claude/skills/executor/SKILL.md` — §"Inputs" section or a new "Context Budget Reference"
- How: Add a "Context Budget Reference" callout box: "Effective capacity: 60-70% of advertised window. Compaction trigger: 70-80% utilization. Tool schemas inflate 2-3x after JSON serialization — audit serialized counts, not source-code line counts. Tool outputs reach ~84% of tokens in agent trajectories — mask aggressively after processing."
- Literal values: 60-70%, 70-80%, 2-3x, ~84%
- Gate: All four thresholds appear in executor SKILL.md

**C6 — Four-gate gatekeeper criteria for ref-eval**
- What: Add a pre-screening gate to ref-eval before running the full nine-section evaluation
- Where: `.claude/skills/ref-eval/SKILL.md` — as a new Step 0 or pre-Step 1 check
- How: Add "Gate A — Pre-screen (run before Step 1b)" with four binary pass/fail criteria: G1 Mechanism Specificity (defines a specific mechanism, not vague "improving accuracy"), G2 Implementable Artifacts (contains code, schemas, templates, or architectural diagrams), G3 Beyond Basics (covers advanced patterns beyond introductory tutorials), G4 Source Verifiability (author/organization has demonstrated technical credibility). On 2+ failures: write ref-eval receipt with status SKIP and stop.
- Literal values: "G1", "G2", "G3", "G4", "Mechanism Specificity", "Implementable Artifacts", "Beyond Basics", "Source Verifiability"
- Gate: Four gate criteria with pass/fail logic appear in ref-eval SKILL.md before Step 1b

**C7 — Position bias mitigation**
- What: Add position bias mitigation requirement to comparative evaluations
- Where: `.claude/skills/adversary/SKILL.md` — §comparative analysis or §reporting section
- How: Add: "When performing comparative evaluation between two outputs: evaluate twice with swapped positions (A vs B, then B vs A). If passes disagree, verdict is TIE with 0.5 confidence. Consistent agreement: confidence = average of individual confidences. Always require justification before the score — chain-of-thought before scoring improves reliability by 15-25%."
- Literal values: "0.5 confidence", "15-25%"
- Gate: Position swap requirement and TIE/0.5-confidence rule appear in adversary SKILL.md

**C8 — Rubric generation template**
- What: Add 5-component rubric structure and strictness calibration to skill evaluation guidance
- Where: `.claude/skills/skill-tdd/SKILL.md` — §test fixture or evaluation section
- How: Add "Rubric Construction" subsection: "A well-specified rubric has five components: (1) Level descriptions — clear boundaries for each score level; (2) Characteristics — observable features that define each level; (3) Examples — representative text per level (optional); (4) Edge cases — guidance for ambiguous situations; (5) Scoring guidelines — general principles. Set strictness calibration: lenient (lower bar, encouraging iteration), balanced (typical production), strict (safety-critical). Domain-specific rubrics reduce evaluation variance by 40-60% vs generic rubrics."
- Literal values: "40-60%", five component names
- Gate: Five rubric components and strictness calibration options appear in skill-tdd SKILL.md

**C9 — KV-cache stability rule**
- What: Add cache stability authoring convention to CLAUDE.md
- Where: `CLAUDE.md` — §Skill Authoring Conventions
- How: Add rule: "Never inject dynamic metadata (timestamps, session IDs, version numbers, request counters) into the stable system prompt prefix. Even one character change in the prefix invalidates the entire KV-cache block downstream of that point. Move all dynamic metadata into a separate user message or tool result appended after the stable prefix. Stable ordering: system instructions first, tool definitions second, templates third, dynamic content last."
- Gate: KV-cache stability rule with the stable-ordering list appears in CLAUDE.md

**C10 — Telephone game anti-pattern**
- What: Add telephone game degradation note to executor subagent dispatch guidance
- Where: `.claude/skills/executor/SKILL.md` — §Subagent Role Taxonomy or §Write Isolation
- How: Add: "Supervisor paraphrase degradation: supervisor architectures initially perform ~50% worse than optimized versions because supervisors paraphrase sub-agent responses, losing fidelity with each pass. Mitigation: when a sub-agent's response is final and complete, instruct it to pass results directly to the receipt/output without synthesis. Avoid supervisor synthesis of sub-agent findings when the sub-agent output is already correct and complete."
- Literal values: "~50% worse"
- Gate: Telephone game degradation note and direct-pass principle appear in executor SKILL.md

**C12 — Freedom calibration**
- What: Add high/medium/low freedom calibration to skill authoring conventions
- Where: `CLAUDE.md` — §Skill Authoring Conventions
- How: Add: "Match instruction specificity to task fragility — High freedom (text instructions only): use when multiple valid approaches exist and decisions depend on context. Medium freedom (pseudocode + parameters): use when a preferred pattern exists but variation is acceptable. Low freedom (exact script, no flags): use when operations are fragile and a specific sequence must be followed — database migrations, receipt writes, invariant-sensitive operations."
- Gate: Three freedom levels with examples appear in CLAUDE.md

### Tier 2 — Low-risk adaptation items

**C11 — BrowseComp 95% variance finding**
- What: Add token-vs-model tradeoff signal to model-router
- Where: `.claude/skills/model-router/SKILL.md` — §routing decision criteria
- How: Add: "Token budget vs model quality tradeoff: empirical evidence shows token usage explains ~80% of agent performance variance; model choice explains ~5%. When performance is insufficient, upgrading model quality provides more leverage than doubling token budget on a weaker model. Use this as a tiebreaker when both token expansion and model upgrade are options."
- Specify required: No
- Breaking change risk: None
- Gate: 80%/5% signal appears in model-router SKILL.md

**C13 — Nested reference anti-pattern**
- What: Add 1-level depth limit to CLAUDE.md skill authoring
- Where: `CLAUDE.md` — §Skill Authoring Conventions
- How: Add: "Skill references must be 1 level deep from SKILL.md. Nested reference chains (SKILL.md → ref-A.md → ref-B.md) cause agents to read ref-B using partial reads (head-style), producing incomplete information. All Tier 3 reference files must link directly from SKILL.md."
- Specify required: No
- Breaking change risk: None
- Gate: 1-level limit rule appears in CLAUDE.md

### Watch Only

**C14 — Memory framework escalation path:** Unclear fit. WabbleSpec's drawer system is proprietary; external framework comparison is background knowledge rather than a rule. Promote if WabbleSpec memory layer needs scaling beyond drawers.

---

## Do-Not-Copy List

| Item | Invariant |
|---|---|
| Model names: GPT-5.2, Claude Opus 4.5, MiniMax M2.1 | I6 |
| interleaved-thinking SKILL.md (rto binary + MiniMax) | I6 + external binary |
| agentskills.io URL | Prior directive |
| BDI ontology content (RDF/SPARQL/T2B2T) | Domain-specific, no relevance |
| Numeric benchmark thresholds as hard targets | Not durable specifications |
| hosted-agents infrastructure | Not WabbleSpec's domain |

---

## Priority Implementation Order

| Order | Item | Why first | Target |
|---|---|---|---|
| 1 | C1 — Anchored iterative summarization | Directly addresses executor compaction underspecification | executor SKILL.md |
| 2 | C5 — Context budget thresholds | Gives executor/guard numeric calibration | executor SKILL.md |
| 3 | C2 — Artifact trail validation note | Validates receipt chain design with production evidence | executor SKILL.md |
| 4 | C3 — Six compression dimensions + probes | Formalizes compaction quality verification | executor SKILL.md |
| 5 | C10 — Telephone game anti-pattern | Addresses supervisor synthesis degradation | executor SKILL.md |
| 6 | C4 — Four-Bucket framework | Gives economy a named decision framework | economy SKILL.md |
| 7 | C6 — Four-gate gatekeeper | Adds pre-screening to ref-eval pipeline | ref-eval SKILL.md |
| 8 | C7 — Position bias mitigation | Adversary comparative evaluation improvement | adversary SKILL.md |
| 9 | C8 — Rubric generation template | Skill evaluation formalization | skill-tdd SKILL.md |
| 10 | C9 — KV-cache stability rule | Cache stability convention | CLAUDE.md |
| 11 | C12 — Freedom calibration | Skill authoring precision | CLAUDE.md |
| 12 | C11 — BrowseComp finding | Model-router decision weight | model-router SKILL.md |
| 13 | C13 — Nested reference anti-pattern | Skill authoring quality | CLAUDE.md |

---

## Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it would unlock | Effort | Session seed |
|---|---|---|---|---|---|
| Compaction quality evaluator | context-compression/SKILL.md + docs/compression.md | Executor compacts but never probe-tests whether compaction preserved artifact trail | A compaction gate that runs 4 probe types (Recall/Artifact/Continuation/Decision) against the compacted context before wave continuation; identifies when critical context (file paths, error codes) was lost | Days | "Build a compaction quality gate using probe-based verification as described in context-compression/SKILL.md §Evaluate Compression with Probes. Integrate as an executor checkpoint after CONTEXT_EXHAUSTION fires." |
| Memory framework selection guide | memory-systems/SKILL.md | WabbleSpec drawers are proprietary; no guide for when to add vector/graph layers | When drawer count exceeds semantic searchability, guide principled decisions about Mem0/Zep/Cognee layers | Weeks | "Build a memory architecture decision guide based on memory-systems/SKILL.md framework comparison table. Entry point: drawer count at 50+ per room, or memory-search returns empty on known-populated rooms." |

---

## Execution Notes

- Items C1, C2, C3, C5, C10 all target `executor SKILL.md` — implement all five in one edit pass to avoid multiple writes to the same file
- Items C9, C12, C13 all target `CLAUDE.md` — implement together
- C6 targets `ref-eval SKILL.md` — must also update matching engine module path `.wabblespec/engine/modules/l1/ref-eval/SKILL.md`
- C7 targets `adversary SKILL.md` — must also update engine path
- C8 targets `skill-tdd SKILL.md` — must also update engine path
- C4 targets `economy SKILL.md` — must also update engine path
- No items require new files created; all are additive to existing sections
