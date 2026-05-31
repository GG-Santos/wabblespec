# Ref-Comp: ai-skills-main

**Source:** `research/ref-plan/ai-skills-main.md`
**Audited:** 2026-05-31

---

## Literal Fidelity Pre-Check

| Item | Literal values | Status |
|---|---|---|
| A1 — Photography prompt vocabulary | "85mm f/2.8 lens", "three-point studio lighting with soft key light from left", "Kodak Portra 400 color tones", "natural skin texture with visible pores", "Keep the facial features exactly consistent", "chest-up framing" | Exact — all 6 present in the Image Prompt Vocabulary table |
| A2 — Defense-in-depth layers | "connection-level enforcement", "allowlist query validation", "single-statement enforcement", "30-second query timeout", "10,000 row maximum", "credential sanitization in error messages" | Exact — all 6 present in the Defense-in-Depth Pattern section |
| A3 — Tier taxonomy | "fast, single-source, time-sensitive", "default, most tasks", "multi-source synthesis requiring parallel processing" | Exact — all 3 present in the Capability Tier Selection table |

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| A1 — Photography prompt vocabulary → gateway-aesthetic | Implemented |
| A2 — Defense-in-depth 3-layer pattern → gateway-security | Implemented |
| A3 — Agent capability tier taxonomy → model-router | Implemented |
| A4 — Sub-agent context enrichment + AGENTS.md template → platform-ai-agent | Implemented |
| A5 — Document-to-audio workflow → document | Implemented |
| A6 — Cost/time signal transparency → economy | Implemented |

Coverage: 6/6 (100%)

---

## Section 2 — Execution Gaps

No missed or partial items.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk |
|---|---|---|---|---|
| Photography vocabulary placement | Reference uses separate examples.md and reference.md | Added as a structured table with Category / Examples / Effect columns | Table format is scannable in agent context; reference approach is narrative and harder to apply at generation time | None |
| Defense-in-depth format | Reference uses bullet list of features | Implemented as numbered layers with "(primary)" label plus secondary controls table | Layer numbering makes the independence explicit; secondary controls table groups the supporting checks | None |
| INLINE_DANGER fix in document | Pre-existing violation in LLM-optimized output format section | Fixed `<!-- Generated: YYYY-MM-DD HH:MM:SS UTC -->` inline span → fenced code block | Fixes a quality floor regression introduced by a prior session; not from ai-skills-main but incidentally repaired | None |

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| Vendor-specific capabilities | Reference uses exact API names (gemini, manus-1.6) | All capabilities expressed as `~~tts-generator`, `~~agent-delegate` placeholders | Yes (I6 compliance) | Capability resolution deferred to runtime; no concrete implementation provided — requires a conforming provider |
| Image generation as standalone skill | Reference implements imagen as a full skill with script | Adopted vocabulary only; no skill created | Yes (Tier 7) | Image generation capability is documented in expansion drawers but not built |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 4 | 5 | +1 | Most reference skills lack tests; our adoptions are behavioral additions to existing tested modules |
| Error handling | 7 | 7 | 0 | No new error paths introduced |
| Documentation | 7 | 8 | +1 | Structured tables + concrete vocabulary examples improve on reference's prose descriptions |
| Naming clarity | 7 | 8 | +1 | Layer labeling and tier naming in our implementation is more explicit than reference's implicit ordering |
| Dependency hygiene | 8 | 9 | +1 | Our implementation uses capability placeholders; no new external dependencies introduced |

---

## Section 6 — Verdict

- **Coverage rate:** 6 of 6 planned items (100%)
- **Gap counts:** 0 critical, 0 major, 0 minor
- **Improvements beyond plan:** 3 (vocabulary table format, layer numbering, INLINE_DANGER fix)
- **Execution classification:** `complete`

**Top 3 wins to protect:**
1. Photography prompt vocabulary in `gateway-aesthetic/SKILL.md` — 6 structured categories with exact example phrases; concrete and immediately actionable
2. Defense-in-depth 3-layer pattern in `gateway-security/SKILL.md` — names independent layers explicitly, adds secondary controls table
3. INLINE_DANGER fix in `document/SKILL.md` — incidental fix for pre-existing quality floor regression

**Recommended next action:** Archive.

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| Image spec → image artifact pipeline (photography vocabulary + gateway-aesthetic HARD gates) | Implemented | `gateway-aesthetic/SKILL.md` Image Prompt Vocabulary section | Reference contribution (vocabulary) implemented; project contribution (HARD gates) was already present |
| Agent profile taxonomy + model-router capability routing | Implemented | `model-router/SKILL.md` Capability Tier Selection section | Both contributions merged into a single table |

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| Native image generation skill | `expansion-candidate-native-image-20260531.json` | Yes | Handed off |
| TTS / podcast generation skill | `expansion-candidate-tts-and-podcast-20260531.json` | Yes | Handed off |
| Database connector skills | `expansion-candidate-database-connector-20260531.json` | Yes | Handed off |
| Deep research delegation skill | `expansion-candidate-native-image-20260531.json` | Yes (noted in drawer) | Handed off |

All 4 Tier 7 items have drawers. All session seeds reference the specific reference files to consult when building the capability.
