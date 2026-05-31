# Ref-Comp: mattpocock-skills-main

**Date:** 2026-05-31  
**Slug:** mattpocock-skills-main  
**Source plan:** research/ref-plan/mattpocock-skills-main.md  
**Execution classification:** complete

---

## Literal Fidelity Pre-Check

| Item | Literal values | Status |
|---|---|---|
| M1 — execution_mode field name | `execution_mode` | Exact |
| M1 — execution_mode values | `AFK` and `HITL` | Exact |
| M1 — AFK criterion | "verification can be automated (Test or Observation mode)" | Exact |
| M1 — HITL criterion | "human judgment required mid-execution; maps to Attestation or Review" | Exact |
| M2 — no file paths checklist item | "No acceptance criterion references a specific file path (file paths go stale on rename/move)" | Exact |
| M2 — no line numbers checklist item | "No acceptance criterion references a line number (line numbers go stale on every edit)" | Exact |
| M3 — rule phrase | "Skill descriptions must not contain time-sensitive information." | Exact |

---

## Section 1 — Implementation Coverage

| Item | Status |
|---|---|
| M1 — HITL/AFK execution_mode in decompose wave plan output contract | Implemented |
| M1 — AFK/HITL guidance in Step 3c | Implemented |
| M1 — execution_mode in Wave 2 template | Implemented |
| M1 — engine module (l1/decompose/SKILL.md) | Implemented |
| M2 — no file paths in specify Step 4 | Implemented |
| M2 — no line numbers in specify Step 4 | Implemented |
| M2 — engine module (l1/specify/SKILL.md) | Implemented |
| M3 — no time-sensitive info rule in CLAUDE.md | Implemented |
| Tier 7: diagnose skill + hitl-loop.template.sh | Implemented |
| Tier 7: prototype skill | Implemented |
| Tier 7: scope-reject skill | Implemented |
| Tier 7: handoff skill | Implemented |
| skill-rules.json for all 4 new skills | Implemented |
| wabblespec.yaml registration (4 new modules) | Implemented |
| Quality floor: all 4 new modules PASS | Implemented |
| validate-graph: 120 modules, 0 violations | Implemented |

Items M4 (Watch Only), M5 (Watch Only) — deferred per plan, not missed.

---

## Section 2 — Execution Gaps

None. All planned items implemented and verified.

---

## Section 3 — Improvements Beyond the Plan

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|
| diagnose HITL script template | mattpocock uses generic template with fixed demo steps | Our `hitl-loop.template.sh` uses WabbleSpec commentary style and includes a clear "edit above/below" zone with two generic capture slots | More instructive for WabbleSpec users | None |
| execution_mode guidance table | mattpocock has no explicit guidance table for HITL/AFK decision | Added a 2-row table in Step 3c with exact conditions and a heuristic question ("Can an agent execute this wave without any human interaction?") | Removes ambiguity at assignment time | None |
| Tier 7 skills fully implemented (not just drawers) | Plan called for drawers only; user requested full implementation | All four Tier 7 skills were implemented as complete WabbleSpec skills with skill-rules.json, SECTION_OUTPUT, SECTION_WHEN, SECTION_WHAT, and quality floor passing | Immediately usable, not just future seeds | Minor: 4 new L1 modules add to maintenance surface; all pass quality floor |

**Protect:** The execution_mode guidance heuristic question — future edits to Step 3c should preserve it.

---

## Section 4 — Architecture Divergence

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|
| diagnose: receipt required | mattpocock has no receipts | WabbleSpec diagnose skill has `receipt_required: false` | Yes | No receipt chain for debugging sessions — diagnose is a product-space diagnostic tool, not a framework-gated operation |
| Tier 7 skills implemented immediately | mattpocock Tier 7 = future roadmap only | User confirmed: implement now | Yes (user directive) | 4 new modules in wabblespec.yaml (validated, passing) |
| scope-reject writes to .wabblespec/state/ | mattpocock writes to .out-of-scope/ at project root | WabbleSpec scope-reject writes to `.wabblespec/state/evolution/out-of-scope/` | Yes — I11 compliance | Out-of-scope KB is framework state, not product space |

---

## Section 5 — Quality Delta

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | 3 | 3 | 0 | Neither has automated tests for the skill files themselves |
| Error handling | 6 | 6 | 0 | Both rely on natural language fallback guidance |
| Documentation | 8 | 8 | 0 | WabbleSpec adds `## When NOT to use` and `## What this skill does` that mattpocock lacks; mattpocock has richer bundled reference docs (LANGUAGE.md, DEEPENING.md) |
| Naming clarity | 9 | 9 | 0 | |
| Dependency hygiene | 7 | 8 | +1 | WabbleSpec's skill-rules.json makes dependencies explicit; mattpocock uses soft `setup-matt-pocock-skills` pointers |

---

## Section 6 — Verdict

- Coverage rate: 16 of 16 planned items (100%)
- Gap counts: 0 critical, 0 major, 0 minor
- Improvements beyond plan: 3
- Execution classification: **complete**
- Top 3 wins to protect:
  1. `execution_mode` field in decompose wave plan — closes a genuine usability gap
  2. No-file-paths / no-line-numbers in specify Step 4 — prevents spec rot at write time
  3. All four Tier 7 skills implemented and quality-floor-passing — immediately usable
- Recommended next action: Archive

---

## Section 7 — Synthesis Coverage

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|
| HITL/AFK + Executor checkpoint behavior | Implemented | `decompose SKILL.md` — execution_mode field; `executor SKILL.md` step 1b — HITL notice | Reference contribution (HITL/AFK classification) + project contribution (Executor step 1b reads execution_mode and emits pre-wave HITL notice). Both halves present. |
| Anti-stale-path + specify Step 4 validation | Implemented | `specify SKILL.md` Step 4 checklist | Both halves present — rule from AGENT-BRIEF.md + WabbleSpec specify checklist |

---

## Section 8 — Expansion Handoff Audit

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|
| diagnose skill | Yes — `diagnose-skill-expansion.json` | Yes | Handed off + fully implemented |
| prototype skill | Yes — `prototype-skill-expansion.json` | Yes | Handed off + fully implemented |
| scope-reject / out-of-scope KB | Yes — `scope-reject-expansion.json` | Yes | Handed off + fully implemented |
| handoff skill | Yes — `handoff-skill-expansion.json` | Yes | Handed off + fully implemented |

All four Tier 7 items were elevated from "handoff only" to full implementation per user directive at Gate B. Drawers remain for historical record.

---

## All gaps closed

Both synthesis ideas are fully implemented. Executor step 1b added post-pipeline per user directive.
