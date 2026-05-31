# Ref-Eval: ai-skills-main

**Reference path:** `C:\Vaults\references\Other Projects References\ai-skills-main\ai-skills-main`
**Evaluated:** 2026-05-31
**Evaluator:** ref-adopt pipeline

---

## Section 1 — Reference Summary

**Type:** Production integration skill collection (connector layer). 20 SKILL.md modules + Python scripts that connect AI coding assistants to external services — databases (postgres, mysql, mssql), Google Workspace (gmail, calendar, chat, docs, drive, sheets, slides), AI agent delegation (jules, manus), media (elevenlabs, google-tts, imagen), research (deep-research, notebooklm), and project management (atlassian, azure-devops, outline).

**What it is not:** A framework, methodology, or behavioral specification. It contains no decision trees, no escalation protocols, no receipt mechanisms, and no self-critique gates.

**Behavioral content:** Defense-in-depth query safety (3 independent protection layers), description-based intent routing, async delegation with poll-until-complete pattern, podcast generation workflow, agent profile taxonomy (lite/standard/max), hash-based deduplication for content sync, photography prompt vocabulary.

**Structural content:** Standardized SKILL.md structure (frontmatter + setup + commands + safety + troubleshooting + token management), operations reference tables, intent-routing lookup tables, exit code conventions (0/1/130).

**Interaction content:** Skill → Script delegation (SKILL.md calls Python scripts; no inline logic). SKILL.md → references/ routing for overflow content. Google OAuth shared pattern (copy-pasted across 7 skills). Auth → keyring storage contract.

**Maturity assessment:** Production-hardened Python scripts with error handling, timeouts, and credential sanitization. NotebookLM has an actual test suite (conftest.py, 3 test files). Most other skills lack tests. OAuth infrastructure is well-designed (PKCE, auto-refresh, keyring storage).

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| postgres/mysql/mssql SKILL.md — Safety Features | Defense-in-depth 3-layer query safety pattern: connection-level + allowlist + single statement | Reinforces gateway-security with an exact enumeration of independent safety layers with explicit layer labels | Add a "Defense-in-Depth Safety Pattern" subsection to gateway-security SKILL.md naming all 3 layers plus secondary controls (timeout, row limit, credential sanitization) | High |
| imagen/reference.md — Advanced Prompting Techniques section; imagen/examples.md | Photography prompt vocabulary: lens specs ("85mm f/2.8"), lighting setups ("three-point studio lighting with soft key light from left"), film stocks ("Kodak Portra 400 color tones"), era aesthetics, texture descriptors ("natural skin texture with visible pores"), facial consistency phrases | gateway-aesthetic has HARD gates but no specific prompt vocabulary for photorealistic image generation; these exact terms significantly improve output quality | Add a "Photorealistic Image Prompt Vocabulary" section or Tier 3 reference to gateway-aesthetic SKILL.md covering 6 vocabulary categories | High |
| manus SKILL.md — Best Practices; deep-research SKILL.md | Agent profile taxonomy: lite (fast, simple) / standard (default) / max (complex reasoning). Explicit boundaries: lite=quick lookups, standard=most research, max=deep multi-source + reports | model-router has capability descriptors but no explicit tier-name language for task complexity → capability tier mapping | Add a "Capability Tier Selection" table to model-router SKILL.md mapping task complexity signals to tier labels | Medium |
| jules SKILL.md — Smart Context Injection; AGENTS.md Template | Context enrichment before delegating to external agent: branch, recently modified files, recent commits, staged files injected into task prompt. AGENTS.md template (Project Overview, Tech Stack, Code Conventions, Testing, Build/Deploy) | platform-ai-agent skill delegates to external agents; enriching task prompts with repo context improves sub-agent output quality | Add a "Sub-Agent Context Enrichment" section to platform-ai-agent SKILL.md with the 5 context fields and the AGENTS.md template structure | Medium |
| elevenlabs/google-tts SKILL.md — Podcast Workflow | 5-step document-to-podcast workflow: extract text → generate conversation script → write JSON (`[{speaker, text}]`) → generate audio → clean up. Content guidelines: vary turn lengths, under 4000 chars per turn, intro/outro, no verbatim reading, Host 1 leads/Host 2 reacts | document SKILL.md handles text-format exports only; an audio output pathway is missing entirely | Add a "Document-to-Audio Workflow" section to document SKILL.md with the 5-step workflow and podcast script schema | Medium |
| manus SKILL.md — Best Practices + polling guidance | Research prompt specificity guidance: "specify scope, timeframe, sources, and desired output format". Agent profile cost/time signal transparency (deep-research: $2-5, 2-10 minutes shown upfront) | economy SKILL.md handles budget but lacks explicit cost transparency patterns for long-running agent tasks | Add a "Cost/Time Signal" pattern to economy SKILL.md: surface expected cost and duration to user before delegating long-running tasks | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| All SKILL.md descriptions; imagen/SKILL.md, manus/SKILL.md | I6 violations throughout: "gemini-3-pro-image-preview", "manus-1.6", "manus-1.6-max", "GEMINI_API_KEY" in description fields and skill bodies | WabbleSpec I6 prohibits model names anywhere in framework files | Do not copy any vendor model name, API endpoint, or provider-specific string. Use capability placeholders only | Critical |
| README.md; jules/SKILL.md | agentskills.io URL embedded in README and referenced as a standard | External service link that may be unstable or domain-specific; agentskills.io is a commercial registry | Do not include URL or treat it as a standard | High |
| All 7 Google Workspace skills | OAuth infrastructure copy-pasted across 7 skills (identical auth.py in each). No shared module. | Pattern teaches duplication rather than DRY; copying this architecture would create 7 divergent auth files in WabbleSpec | Do not copy the architecture; extract the pattern (keyring storage + cloud function refresh) without the 7x duplication | Medium |
| manus/SKILL.md, jules/SKILL.md | Vendor-specific delegation commands (jules new, curl manus.im) baked into SKILL.md body | Breaks I6 at the operational level; agents would execute vendor-specific CLI commands | Do not adopt the CLI command patterns; adopt only the behavioral abstractions (profile taxonomy, context enrichment) | Medium |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| Defense-in-depth 3-layer query safety | Adapt | Exact pattern for gateway-security; names independent layers precisely | gateway-security SKILL.md | 1 |
| Photography prompt vocabulary (6 categories) | Adapt | Directly improves image prompt quality in gateway-aesthetic | gateway-aesthetic SKILL.md + Tier 3 reference | 1 |
| Agent profile taxonomy | Adapt | Clean capability tier language for model-router | model-router SKILL.md | 2 |
| Sub-agent context enrichment + AGENTS.md template | Adapt | Improves platform-ai-agent delegation quality | platform-ai-agent SKILL.md | 2 |
| Document-to-audio workflow + podcast script schema | Adapt | Net-new output pathway for document skill | document SKILL.md | 3 |
| Cost/time signal pattern | Adapt | Reinforces economy transparency | economy SKILL.md | 3 |
| Model names (gemini, manus-1.6, etc.) | Avoid | I6 violation | — | — |
| agentskills.io URL | Avoid | External service link | — | — |
| Google OAuth copy-paste architecture (7x) | Avoid | Teaches duplication anti-pattern | — | — |
| Vendor CLI commands (jules new, curl manus.im) | Avoid | I6 vendor specificity | — | — |
| All 7 Google Workspace skill implementations | Avoid | Domain-specific; no hook point in WabbleSpec | — | — |
| DB connector implementations (postgres/mysql/mssql scripts) | Study Only | Production-hardened patterns worth referencing for future native connectors | Tier 7 | — |
| ElevenLabs/Google-TTS implementation scripts | Study Only | Audio generation patterns for future TTS capability | Tier 7 | — |
| NotebookLM browser automation | Study Only | Hash-based dedup + batch query pattern useful for future research tooling | Tier 7 | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 4 | WabbleSpec is an SDLC framework; this reference is a connector library. Concept overlap is thin — only behavioral patterns transfer, not the primary capability |
| Architecture fit | 5 | SKILL.md + scripts/references/ structure matches WabbleSpec exactly. The skill authoring conventions align. |
| Implementation fit | 4 | Scripts are Python + external APIs. WabbleSpec skills are behavioral specs, not external integrations. Direct implementation transfer is limited. |
| Maintenance fit | 6 | Items being adopted (vocabulary tables, tier taxonomies) are stable and low-maintenance |
| Risk level | 3 | I6 violations are the primary risk — easily avoided by not copying vendor names |
| Overall usefulness | 5 | Supporting reference. Specific behavioral vocabulary and tier patterns worth adopting; no architectural adoption |

**Overall usefulness: 5/10 — supporting-reference.** Worth active use for targeted extractions; primary implementation value is in Sections 8–9 (synthesis and expansion).

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — implement now):**
- Photography prompt vocabulary → gateway-aesthetic SKILL.md (additive, no risk)
- Defense-in-depth 3-layer pattern → gateway-security SKILL.md (reinforces existing content)
- Agent profile taxonomy → model-router SKILL.md (additive, no risk)

**Phase 2 (Low-Risk Adaptation):**
- Sub-agent context enrichment + AGENTS.md template → platform-ai-agent SKILL.md
- Document-to-audio workflow → document SKILL.md
- Cost/time signal transparency → economy SKILL.md

**Phase 3 (Deeper Integration):**
- Native image generation skill design (Tier 7 candidate)
- TTS/podcast generation skill design (Tier 7 candidate)

**Phase 4 (Do Not Cross):**
- Any skill importing specific vendor APIs, model names, or external service URLs

---

## Section 7 — Final Verdict

**Classification: supporting-reference (5/10)**

**Best 3 to steal:**
1. Photography prompt vocabulary (`imagen/reference.md` Advanced Prompting Techniques + `imagen/examples.md`) — exact professional photography terminology that produces photorealistic output. Six categories: camera/lens specs, lighting architecture, film stocks, facial consistency phrases, texture details, composition framing.
2. Defense-in-depth 3-layer safety pattern (`postgres/mssql/mysql` Safety Features) — independently named layers with precise descriptions that reinforce gateway-security with concrete enumeration.
3. Agent profile taxonomy (`manus/SKILL.md` Agent Profiles) — explicit lite/standard/max tier naming with task complexity boundary conditions that strengthen model-router's capability routing.

**Worst 3 to avoid:**
1. All model/vendor name strings (`imagen/SKILL.md`, `manus/SKILL.md`, `jules/SKILL.md`) — embedded throughout descriptions and skill bodies; directly violates I6.
2. Google OAuth copy-paste architecture (all 7 Google skills) — 7 identical auth.py files with no shared module; teaches duplication.
3. agentskills.io as a "standard" (`README.md`) — treats a commercial registry as a neutral standard; do not reference.

**Recommended next action:** Adopt Phase 1 items (3 Tier 1 items) + document Phase 2 items in ref-plan. Write Tier 7 drawers for imagen, TTS, and DB connector expansion opportunities.

---

## Section 8 — Project Synthesis

| What | Reference contribution | Project contribution | Target | Gap closed |
|---|---|---|---|---|
| Image spec → image artifact pipeline | Photography prompt vocabulary (lens, lighting, film, texture, framing categories) | gateway-aesthetic already has HARD gates for visual identity and anti-convergence rules | `.wabblespec/engine/modules/l4/gateway-aesthetic/SKILL.md` | WabbleSpec can specify visual identity at a photographic level, not just palette/typography; closes the gap between visual spec and actual image generation output quality |
| Async sub-task delegation scorecard | Agent profile taxonomy (lite/standard/max with task complexity signals) | model-router has capability-descriptor routing | `.wabblespec/engine/modules/l5/model-router/SKILL.md` | Model routing gains explicit tier-label language aligned with task complexity, not just abstract capability names |

---

## Section 9 — Expansion Opportunities

Per-skill growth scan results:

| Capability | Reference location | Project has equivalent? | Tier 7 candidate |
|---|---|---|---|
| SQL query execution (read-only) | postgres/mysql/mssql SKILL.md + scripts | No — no database connector modules exist | Yes |
| AI image generation | imagen SKILL.md + scripts/generate_image.py | Partial — gateway-aesthetic specifies visual identity but cannot generate images | Yes |
| Text-to-speech / podcast generation | elevenlabs/google-tts SKILL.md + scripts | No — document outputs text formats only | Yes |
| Async AI agent delegation (research/coding) | jules/manus SKILL.md | Partial — platform-ai-agent exists but lacks the async delegation formalization | No (already covered via platform-ai-agent) |
| Browser-automated notebook querying | notebooklm SKILL.md + scripts | No | No (too vendor-specific) |
| Wiki management (Outline) | outline SKILL.md | No direct equivalent | No (domain-specific) |
| Jira/Confluence integration | atlassian SKILL.md | No | No (domain-specific) |
| Azure DevOps management | azure-devops SKILL.md | No | No (domain-specific) |
| Gmail/Calendar/Docs/Drive/Sheets/Slides | Google Workspace skills | No | No (domain-specific; gateway bundling not applicable — different APIs) |
| Deep research via external agent | deep-research SKILL.md | No direct equivalent | Yes (gateway bundle with manus pattern) |

**Expansion Roadmap:**

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| Native image generation skill | `imagen/SKILL.md` + `scripts/generate_image.py` + `reference.md` | No image generation module; gateway-aesthetic specs but cannot produce | Closes the gap between visual specification and artifact; present skill could generate slide visuals | External AI image API key | days | Yes |
| TTS / podcast skill | `elevenlabs/SKILL.md` + `google-tts/SKILL.md` + `scripts/` | document skill produces text only | Audio output pathway for any WabbleSpec document | ffmpeg + TTS API key | days | Yes |
| Database connector skill | `postgres/mysql/mssql SKILL.md` + `scripts/query.py` | No data-access layer | Projects using WabbleSpec can query their own DB during spec and execution | pip install + connections.json | days | Yes |
| Deep research delegation skill | `deep-research/SKILL.md` + `manus/SKILL.md` pattern | No formalized async research sub-agent pattern | Enrich spec/plan with external research without blocking the main pipeline | External research API key | days | Yes |

**Gateway bundling signal:** image generation + TTS/podcast are both "artifact generation" capabilities (non-text output). They could be bundled under a `gateway-artifact` module, paralleling the existing gateway-aesthetic/gateway-design pattern. Not mandatory — each is independently small enough to stand alone.
