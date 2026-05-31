# Ref-Plan: ai-skills-main

**Source:** `research/ref-eval/ai-skills-main.md`
**Planned:** 2026-05-31

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| A1 | Photography prompt vocabulary (6 categories) | Behavioral + Format | High | High | Low |
| A2 | Defense-in-depth 3-layer query safety pattern | Behavioral | High | High | Low |
| A3 | Agent capability tier taxonomy (lite/standard/max) | Behavioral | Medium | High | Low |
| A4 | Sub-agent context enrichment + AGENTS.md template | Behavioral | Medium | Medium | Low |
| A5 | Document-to-audio workflow + podcast script schema | Behavioral | Medium | Medium | Low |
| A6 | Cost/time signal transparency for long-running tasks | Behavioral | Low | Medium | Low |

---

## Exclusion List

| Item | Reason |
|---|---|
| All model/vendor names (gemini-3-pro-image-preview, manus-1.6, etc.) | I6: No model names anywhere in framework files |
| agentskills.io URL and "Agent Skills Standard" framing | External service link; commercial registry treated as neutral standard |
| Google OAuth copy-paste architecture (7x auth.py) | Teaches duplication anti-pattern; no hook point in WabbleSpec |
| Vendor CLI commands (jules new, curl api.manus.ai) | I6 vendor specificity |
| All 7 Google Workspace skill implementations | Domain-specific; no project hook |
| NotebookLM browser automation | Too vendor-specific (Playwright + Google account) |
| Outline/Atlassian/Azure DevOps implementations | Domain-specific integrations |

---

## Integration Scores

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1

A1: (3×2) + 3 - 1 = 8
A2: (3×2) + 3 - 1 = 8
A3: (2×2) + 3 - 1 = 6
A4: (2×2) + 2 - 1 = 5
A5: (2×2) + 2 - 1 = 5
A6: (1×2) + 2 - 1 = 3
```

Priority order: A1, A2, A3, A4, A5, A6

---

## Tier Assignments

### Tier 1 — Behavioral additions (additive to existing files)

**A1 — Photography prompt vocabulary**
- What: Add a "Photorealistic Image Prompt Vocabulary" section covering 6 categories: camera/lens specs, lighting architecture, film stocks/era aesthetics, texture details, facial consistency phrases, composition framing.
- Where: `.wabblespec/engine/modules/l4/gateway-aesthetic/SKILL.md` (and `.claude/skills/gateway-aesthetic/SKILL.md`)
- How: Add a new `## Image Prompt Vocabulary` section after the existing HARD gates. Content: a table with 6 rows (Category / Examples / Effect) drawn verbatim from `imagen/reference.md` Advanced Prompting Techniques. These are the 6 categories with exact example phrases.
- Literal values: "85mm f/2.8 lens", "three-point studio lighting with soft key light from left", "Kodak Portra 400 color tones", "natural skin texture with visible pores", "Keep the facial features exactly consistent", "chest-up framing"
- Gate: Section present in both engine module and skills copy; all 6 category rows present; no vendor model names included.
- Reference location: `imagen/reference.md` lines 109–151 (Advanced Prompting Techniques section)

**A2 — Defense-in-depth 3-layer query safety pattern**
- What: Add a "Defense-in-Depth Pattern" block to gateway-security naming the 3 independent safety layers explicitly, with labels.
- Where: `.wabblespec/engine/modules/l4/gateway-security/SKILL.md` (and `.claude/skills/gateway-security/SKILL.md`)
- How: Add a `## Defense-in-Depth Pattern` section with a numbered 3-layer list (1. Connection-level enforcement, 2. Allowlist query validation, 3. Single-statement enforcement) plus secondary controls table (timeout, row limit, credential sanitization). Each layer labeled with "(primary)" / "(secondary)".
- Literal values: "connection-level enforcement", "allowlist query validation", "single-statement enforcement", "30-second query timeout", "10,000 row maximum", "credential sanitization in error messages"
- Gate: Section present in both engine module and skills copy; 3 layers labeled; secondary controls table present.
- Reference location: `postgres/SKILL.md` Safety Features; `mysql/SKILL.md` Safety Features; `mssql/SKILL.md` Safety Features

**A3 — Agent capability tier taxonomy**
- What: Add a "Capability Tier Selection" table to model-router.
- Where: `.wabblespec/engine/modules/l5/model-router/SKILL.md` (and `.claude/skills/model-router/SKILL.md`)
- How: Add a `## Capability Tier Selection` section with a 3-row table: Tier / Task complexity signal / Use when. Rows: lite (fast, single-source, time-sensitive), standard (default, most tasks), max (multi-source synthesis, parallel processing, structured report generation).
- Literal values: "fast, single-source, time-sensitive", "default, most tasks", "multi-source synthesis requiring parallel processing"
- Gate: Section present in both copies; 3 rows with complexity signal column; no model names.
- Reference location: `manus/SKILL.md` Agent Profiles section; `deep-research/SKILL.md` Cost & Time table

### Tier 2 — Module-level augmentation

**A4 — Sub-agent context enrichment + AGENTS.md template**
- What: Add a "Sub-Agent Context Enrichment" section to platform-ai-agent with 5 context fields and an AGENTS.md template structure.
- Where: `.wabblespec/engine/modules/l1/platform-ai-agent/SKILL.md` (and `.claude/skills/platform-ai-agent/SKILL.md`)
- How: Add section covering: (1) 5 context fields to inject before delegation (branch, recently modified files, recent commits, staged files, active task context), (2) AGENTS.md structure (Project Overview, Tech Stack, Code Conventions, Testing Requirements, Build & Deploy). Frame as capability-neutral, no vendor commands.
- Gate: Section present; 5 context fields listed; AGENTS.md template sections listed; no jules/manus CLI commands.
- Reference location: `jules/SKILL.md` Smart Context Injection section; AGENTS.md Template section

**A5 — Document-to-audio workflow**
- What: Add a "Document-to-Audio Output" section to document SKILL.md with 5-step workflow and podcast script schema.
- Where: `.wabblespec/engine/modules/l6/document/SKILL.md` (and `.claude/skills/document/SKILL.md`)
- How: Add section describing audio as an output type alongside text formats. Include the 5-step workflow (extract → conversation script → JSON → generate → clean up), the podcast script JSON schema (`[{"speaker": "host1|host2", "text": "..."}]`), and content guidelines (vary turn lengths, under 4000 chars, intro/outro, natural discussion). Use `~~tts-generator` capability placeholder, not a vendor name.
- Gate: Section present; 5-step workflow documented; JSON schema shown; `~~tts-generator` used (not a vendor name); content guidelines present.
- Reference location: `elevenlabs/SKILL.md` Podcast Workflow section; `google-tts/SKILL.md` Podcast from Document section

**A6 — Cost/time signal transparency**
- What: Add a "Long-Running Task Cost Transparency" guidance note to economy SKILL.md.
- Where: `.wabblespec/engine/modules/l4/economy/SKILL.md` (and `.claude/skills/economy/SKILL.md`)
- How: Add 2-sentence guidance: when delegating a long-running task with known cost or time range, surface both to the user before initiating. Example signal: "This task is expected to take 2-10 minutes and cost approximately $2-5. Proceeding?"
- Gate: Guidance present; framed as capability-neutral signal pattern; no vendor pricing.
- Reference location: `deep-research/SKILL.md` Cost & Time table; `manus/SKILL.md` Best Practices

---

## Tier 7 — Expansion Roadmap

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Session seed |
|---|---|---|---|---|---|---|
| Native image generation skill | `imagen/SKILL.md` + `scripts/generate_image.py` + `reference.md` | No image generation module | Closes spec → artifact gap; present can generate slide visuals | Image API key | days | `/recipe` → build an imagen-style skill using the photography prompt vocabulary; implement as a platform-visual or gateway-artifact module |
| TTS / podcast skill | `elevenlabs/SKILL.md` + `google-tts/SKILL.md` | document produces text only | Audio output for any document | TTS API key + ffmpeg | days | `/recipe` → build a tts skill with 5-step podcast workflow; uses `~~tts-generator` capability |
| Database connector skills | `postgres/mysql/mssql SKILL.md` + `scripts/query.py` | No data-access layer | Projects can query databases during execution | pip install + connections.json | days each | `/recipe` → build a database-connector skill using defense-in-depth 3-layer pattern |
| Deep research delegation skill | `deep-research/SKILL.md` + `manus/SKILL.md` | No formalized async research pattern | Async research sub-tasks in Decompose/Specify | External research API | days | `/recipe` → build an async-research skill with agent profile taxonomy + cost/time transparency |

---

## Do-Not-Copy List

| Item | Invariant reason |
|---|---|
| `gemini-3-pro-image-preview`, `manus-1.6`, `manus-1.6-max`, `GEMINI_API_KEY` | I6: No model names or vendor-specific identifiers in framework files |
| `agentskills.io` URL | External service reference; commercial registry |
| `jules new`, `curl api.manus.ai` | I6: vendor-specific CLI commands |
| 7 Google OAuth auth.py copies | Anti-pattern: teaches duplication; not a framework pattern |

---

## Priority Implementation Order

| Priority | Item | Why first |
|---|---|---|
| 1 | A1 — Photography prompt vocabulary → gateway-aesthetic | High impact + project fit; purely additive; directly extends an existing HARD gate area |
| 2 | A2 — Defense-in-depth pattern → gateway-security | High impact; names exact layers missing from existing content |
| 3 | A3 — Capability tier taxonomy → model-router | Medium-high; adds precision to routing that benefits every execution |
| 4 | A4 — Sub-agent context enrichment → platform-ai-agent | Medium; useful whenever external agents are delegated to |
| 5 | A5 — Document-to-audio workflow → document | Medium; new output pathway |
| 6 | A6 — Cost/time transparency → economy | Lower priority; reinforcement of existing economy guidance |

---

## Execution Notes

- A1 and A2 must sync to both `.claude/skills/` and `.wabblespec/engine/modules/` immediately after edit.
- A3, A4, A5, A6 follow the same dual-sync requirement.
- All items are independent — they can be applied in any order, no sequencing constraints.
- No items conflict with each other.
