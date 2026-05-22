# Token-Saving Protocol — Runtime Reference Loading

> Purpose: Prevent re-reading raw repos during building. Load only what each phase needs.
> Rule: Never read a raw repo when a reference card exists for it.
> Format: Phase → which card(s) → which section(s) → expected token cost.

---

## The Problem This Solves

Reading raw repos during building costs 10k-100k tokens per repo.
These reference cards distill signal to ~500-2000 tokens per section.
Loading ratio: ~20-50x token savings vs. reading raw repos.

---

## Phase 0: Hook (Build First — Do This Before Any SKILL.md)

**What to load:**

| Card | Section | Why |
|---|---|---|
| `extra-refs-v61.md` | `claude-code-main` | Canonical hook pattern + exit-code contract |
| `other-refs-v61.md` | "Hook-specific refs" | Hook lifecycle + guard patterns |
| `REFERENCE-INDEX.md` | "v6.1 MVP Module → Best Reference" row: Hook | Confirm you have right refs |

**Do NOT read:**
- Raw `claude-code-main/examples/hooks/` (already extracted in extra-refs card)
- Raw `claude-code-hooks-mastery/` (signal captured in other-refs card)

**Output of this phase:** A working `.ps1` or `.py` hook script that:
1. Reads stdin JSON
2. Checks `.wabblespec/receipts/` for upstream receipt
3. Exits 2 if missing (blocks + informs Claude)
4. Exits 0 if present

**Test before moving on:** Deliberately skip a receipt. Hook must block without human prompting.

---

## Phase 1: Recipe Module

**What to load:**

| Card | Section |
|---|---|
| `core-refs-v61.md` | `get-shit-done-main` — Recipe row |
| `core-refs-v61.md` | `OpenSpec-main` — Recipe row |
| `core-refs-v61.md` | `cartographer-main` |

**Do NOT read:** Raw GSD commands directory, raw OpenSpec commands.

---

## Phase 2: Specify Module

**What to load:**

| Card | Section |
|---|---|
| `core-refs-v61.md` | `OpenSpec-main` — full card |
| `core-refs-v61.md` | `agent-os-main` — full card |
| `research-reference.md` (existing) | spec-kit section — feature-level spec structure |

**Critical lesson to apply:** OpenSpec reimplementation lesson — user-visible flow first, internal machinery second.

---

## Phase 3: Decompose Module

**What to load:**

| Card | Section |
|---|---|
| `core-refs-v61.md` | `get-shit-done-main` — Decompose row |
| `core-refs-v61.md` | `superpowers-main` — 7-stage model |

---

## Phase 4: Executor Module

**What to load:**

| Card | Section |
|---|---|
| `core-refs-v61.md` | `get-shit-done-main` — Executor row |
| `core-refs-v61.md` | `oh-my-claudecode-main` — Executor row |
| `extra-refs-v61.md` | `agent-creator` — Numbered Steps pattern, tool budget table |
| `core-refs-v61.md` | `superpowers-main` — Git worktree isolation |

---

## Phase 5: Verifier Module

**What to load:**

| Card | Section |
|---|---|
| `extra-refs-v61.md` | `toprank-main` — fixture evals + policy gates |
| `extra-refs-v61.md` | `claude-ads-main` — PASS/WARNING/FAIL scoring |
| `core-refs-v61.md` | `get-shit-done-main` — verify-work phase |
| `extra-refs-v61.md` | `agent-creator` — Quality Gates pattern |
| `other-refs-v61.md` | "Verifier / Quality gate refs" |

**Receipt format to output:**
```json
{
  "phase": "...",
  "status": "PASS | WARNING | FAIL",
  "checks_run": [...],
  "checks_failed": [...],
  "timestamp": "...",
  "wave": 0,
  "upstream_receipt": "..."
}
```

---

## Phase 6: Archive Module

**What to load:**

| Card | Section |
|---|---|
| `extra-refs-v61.md` | `pentest-ai-agents-main` — findings DB + status transitions |
| `extra-refs-v61.md` | `toprank-main` — eval persistence |
| `other-refs-v61.md` | "Archive / Receipt refs" |

**Receipt index format:**
Flat append-only index file at `.wabblespec/receipts/index.md` (or `.json`).
Each entry: phase + wave + status + timestamp + pointer to full receipt file.

---

## Phase 7: Memory Module (FRESH/EXPIRED only)

**What to load:**

| Card | Section |
|---|---|
| `core-refs-v61.md` | `mempalace-develop` — full card |
| `extra-refs-v61.md` | `context-mode-main` — SQLite/FTS5 + session continuity |
| `support-reference.md` (existing) | MemPalace full analysis |

**Memory scope for MVP:**
- States: FRESH / EXPIRED only (not AGING/STALE/NEEDS_REVERIFICATION)
- Storage: flat files in `.wabblespec/memory/drawers/`
- Search: full-text only (no embeddings, no EntityGraph)
- No Dream, no MemoryMine, no EntityGraph

**Do NOT read:** Raw mempalace source for architecture — already extracted.

---

## Phase 8: Reviewer Agent

**What to load:**

| Card | Section |
|---|---|
| `extra-refs-v61.md` | `agent-creator` — full card |
| `other-refs-v61.md` | "MVP-Relevant" rows: awesome-claude-agents, awesome-claude-code-subagents |

**Reviewer agent design:**
- Model: `sonnet` (balanced critique)
- Tools: `Glob, Grep, Read` only (read-only enforced)
- Hard Stop pattern: DO NOT implement fixes
- Two subagents: Adversary (find problems) + Grader (score severity)
- Max 3 REVISE cycles before human escalation

---

## Phase 9: skill-rules.json Schema

**What to load:**

| Card | Section |
|---|---|
| `core-refs-v61.md` | `anthropic-skills-main` |
| `core-refs-v61.md` | `Claude-Code-Game-Studios-main` — path-scoped activation |
| `core-refs-v61.md` | `oh-my-claudecode-main` — skill scoping |
| `extra-refs-v61.md` | `agent-creator` — description as PRIMARY TRIGGERING MECHANISM |

**Canonical schema (as built — verified 2026-05-22):**
```json
{
  "module": "module-name",
  "layer": "L0|L1|L2|L3|L4|L5|L6|L7",
  "tier": 1,
  "activators": ["pattern1", "pattern2"],
  "anti_activators": ["exclusion pattern"],
  "build_targets": ["ALL"],
  "phases": ["Research|Specify|Execute"],
  "authority": {
    "owns": [".wabblespec/path/to/owned/file"],
    "reads": [".wabblespec/path/to/read/file"]
  },
  "verification_mode": "Observation|Audit",
  "receipt_required": true,
  "collapse_eligible": false,
  "gate_collapsing_conditions": null,
  "requires_receipts_from": ["upstream-module"],
  "loading_gate": "recipe|stage|phase|activation",
  "commands": ["/slash-command"],
  "file_path_patterns": ["**/pattern/**"]
}
```

**Field notes:**
- `activators` — natural language phrases that trigger this module (not `triggers`)
- `requires_receipts_from` — upstream modules whose receipts must exist (not `receipts_required`)
- `loading_gate` — when module loads: `recipe` (L0/session start), `stage` (L1/stage boundaries), `phase` (L2+L7/phase execution), `activation` (L3–L6/on demand)
- `commands` — slash commands that directly invoke this module; empty array `[]` for orchestration-triggered modules
- `file_path_patterns` — path-scoped activation for Claude Code; empty array `[]` for non-platform modules

---

## General Token Rules

1. **Never read a raw repo** if a reference card covers it.
2. **Load only the sections listed** for the current phase — not the full card.
3. **One card at a time** per session — don't front-load all cards at session start.
4. **After building a module**, note what was actually useful vs. what was noise. Update the card if the signal was wrong.
5. **If a card is stale** (repo updated), re-read only the changed file, not the whole repo.

---

## Build Order (Full MVP)

```
Phase 0: Hook          ← BUILD THIS FIRST. Without it receipts are theater.
Phase 1: Recipe        ← Entry point. Must exist before other modules activate.
Phase 2: Specify       ← One-page task card. Core claim of the framework.
Phase 3: Decompose     ← Wave breakdown. Core execution claim.
Phase 4: Executor      ← Wave runner. Core execution claim.
Phase 5: Verifier      ← Receipt writer. Core quality claim.
Phase 6: Archive       ← Receipt index. Core auditability claim.
Phase 7: Memory        ← FRESH/EXPIRED. Core differentiation claim.
Phase 8: Reviewer      ← Adversarial gate. Quality multiplier.
Phase 9: skill-rules   ← Activation wiring. Connects all modules.
```

**Do not start Phase 1 until Phase 0 hook blocks a deliberately skipped receipt.**
**Do not expand beyond Phase 9 until 3 real projects complete with receipt chains intact.**

---

## What NOT to Load (Ever, for MVP)

| What | Why |
|---|---|
| L8 Evolution refs (Instinct, Synth, Forge) | No execution data yet. Theater. |
| EntityGraph refs | LLM extraction not deterministic. v2. |
| Dream refs | Fake daemon. v2. |
| TeamPlan refs | Prove single-agent first. |
| All 11 platform package refs | Pick 1-2 targets first. |
| Vendor-neutral runtime refs | Always Claude. Abstraction for one thing. |
| Raw repo reads | Use cards instead. |
