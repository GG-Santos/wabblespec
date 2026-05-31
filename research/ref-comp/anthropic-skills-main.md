# Ref-Comp: anthropic-skills-main

**Date:** 2026-05-31  
**Slug:** anthropic-skills-main  
**Classification:** supporting-reference (7/10)  
**Execution classification:** complete

---

## Literal Fidelity Pre-Check

All items from ref-plan had no `Literal values` fields — behavioral guidance and schema names, not exact code strings. N/A.

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| A: Pressure scenario quality check → skill-tdd | Implemented |
| B: WHY over MUST writing guidance → CLAUDE.md | Implemented |
| C: Three-level loading reasoning → CLAUDE.md | Implemented |
| D: Undertrigger calibration note → CLAUDE.md | Implemented |
| E: 60/40 train/test anti-overfitting → CLAUDE.md | Implemented |
| F: Subagent timing capture → skill-tdd | Implemented |
| gateway-document (L4, docx/pdf/xlsx/pptx) | Implemented (new module) |
| present (L7, stakeholder slide decks) | Implemented (new module) |
| report (L7, 3P updates/status reports) | Implemented (new module) |
| visualize (L6, charts/diagrams) | Implemented (new module) |
| project-identity (L1, brand config) | Implemented (new module) |
| mcp-builder tool annotations → platform-ai-agent + gateway-ai | Implemented |
| Playwright decision tree → platform-web | Implemented |
| Agent decision tree + compaction + caching → gateway-ai | Implemented |
| Frontend-design banned font/color list → gateway-aesthetic audit-gates (AN-2/AN-3/AN-4) | Implemented |
| Doc-coauthoring reader clarity test → specify Step 3.7 | Implemented |
| Visual defaults anti-convergence rule → CLAUDE.md | Implemented |
| wabblespec.yaml +5 modules registered | Implemented |
| Sync: 112 skills (was 107) | Implemented |

---

## Section 2 — Execution Gaps

No gaps. All planned items implemented.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Ref approach | Our implementation | Why ours is better | Risk |
|---|---|---|---|---|
| gateway-document as L4 gateway | Anthropic skills are standalone skills invoked directly | Made it an L4 gateway with Phase A/B activation, audit gates, and format routing table | Integrates with the existing gateway activation chain; enforces quality gates automatically via Verifier rather than requiring caller discipline | None — additive |
| AN-2/AN-3 as HARD gates | Anthropic skill says NEVER for certain patterns | WabbleSpec promotes these to HARD audit gates (not just SOFT flags) | More enforceable; consistent with how WabbleSpec enforces other critical visual choices | Low — could be overly strict for some brand briefs; escalation path documented in gate |
| project-identity as L1 module | No equivalent in reference (brand-guidelines is Anthropic-specific) | Created as a generic project-level brand config resource feeding downstream gateways | Brand config stored once, consumed by multiple gateways — no re-elicitation per session | None |

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional | Consequence |
|---|---|---|---|---|
| Document skill deployment | Standalone skills, direct invocation | L4 gateway with Phase A/B | Yes | Fits WabbleSpec's gateway architecture; requires callers to invoke gateway-document rather than format skills directly |
| Format production scripts | Bundled scripts in skill directory | Runtime Python/Node library calls; no bundled scripts | Yes | Keeps framework SKILL.md lean; matches WabbleSpec convention; production scripts are standard pip/npm packages |
| Viewer infrastructure | HTML browser-based viewer | Not adopted | Yes (I6/dependency) | No visual benchmark viewer — DuckDB receipt analytics cover the data need |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 4 | 6 | +2 | Reference has no tests; WabbleSpec's skill-tdd provides coverage for new skills |
| Error handling | 7 | 7 | 0 | Both handle format errors similarly |
| Documentation | 8 | 8 | 0 | Reference SKILL.md files are well-documented; ours match |
| Naming clarity | 8 | 9 | +1 | gateway-document naming follows WabbleSpec convention more clearly than individual skill names |
| Dependency hygiene | 6 | 8 | +2 | Reference bundles binary scripts; ours uses standard libraries declared per-format |

---

## Section 6 — Verdict

- **Coverage rate:** 19 of 19 planned items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 3
- **Execution classification:** `complete`
- **Top 3 wins to protect:**
  1. `gateway-document` format routing + audit gate architecture — ensure future format additions follow the same Phase A/B pattern
  2. `gateway-aesthetic AN-2/AN-3 HARD gates` — do not downgrade to SOFT without evidence that HARD blocks legitimate brand briefs
  3. `skill-tdd pressure scenario quality check` — the three failure modes (non-discriminating, coverage-gap, unverifiable) are the most common false-READY sources
- **Recommended next action:** Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| Eval quality gate in skill-tdd | Implemented | `.claude/skills/skill-tdd/SKILL.md` + `engine/modules/l8/skill-tdd/SKILL.md` | Both copies updated |
| Undertrigger score in quality-floor-check | Deferred | quality-floor-check.py Gate 1 | Would require code change to quality-floor-check.py; separate session |
| Iteration lineage receipt in evolution chain | Deferred | New `skill-iteration` receipt type | Requires receipt-writer.py extension; separate session |

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Description optimization pipeline | Yes — `anthropic-skills-main/description-optimization-pipeline.json` | Yes | Handed off |
| Aggregate benchmark viewer | No drawer yet | Pending | Partial handoff — drawer needs to be written |

Writing missing drawer now.
