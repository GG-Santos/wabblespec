# Ref-Plan: andrej-karpathy-skills-main

**Date:** 2026-05-31
**Source eval:** `research/ref-eval/andrej-karpathy-skills-main.md`
**Trust level:** MEDIUM
**Reference classification:** supporting-reference (6/10)

---

## Candidate Table

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|
| K1 | "If multiple interpretations exist, present them — don't pick silently" | Behavioral addition | Medium | High | Low |
| K2 | "If a simpler approach exists, say so. Push back when warranted." | Behavioral addition | Medium | High | Low |
| K3 | "If you notice unrelated dead code, mention it — don't delete it" | Behavioral addition | Medium | High | Low |
| K4 | "Every changed line should trace directly to the user's request." | Behavioral addition | Low | Medium | Low |
| K5 | `→ verify:` step format as behavioral guidance | Format addition | Low | Medium | Low |

---

## Exclusion Filter

| Item | Reason |
|---|---|
| `skills/karpathy-guidelines/SKILL.md` format | Fails WabbleSpec quality floor Gate 1 — no negative triggers, no period on description, no When NOT to use |
| Plugin marketplace install instructions | External URL content; not framework material |
| CURSOR.md content | Cursor tooling setup; irrelevant to WabbleSpec |
| `→ verify:` format if adopted literally without gate/receipt reframing | Clashes with WabbleSpec's receipt-gated verification model; K5 is Watch Only until framing is resolved |

---

## Scoring and Ranking

```
integration_score = (impact × 2) + project_fit - risk
High=3, Medium=2, Low=1
```

| ID | impact×2 | project_fit | risk | score |
|---|---|---|---|---|
| K1 | 4 | 3 | 1 | 6 |
| K2 | 4 | 3 | 1 | 6 |
| K3 | 4 | 3 | 1 | 6 |
| K4 | 2 | 2 | 1 | 3 |
| K5 | 2 | 2 | 1 | 3 (Watch Only) |

---

## Tier Assignment

### Tier 1 — Behavioral Additions

**K1** — Present-multiple-interpretations rule
- What: Add "If multiple interpretations exist, present them — don't pick silently" as an explicit Approach bullet
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md`, Approach section
- How: Add one bullet after "Thorough in reasoning, concise in output." — "If multiple interpretations exist, present them; don't pick silently."
- Gate: Bullet appears verbatim in the file; does not duplicate existing content
- Reference location: `CLAUDE.md` §1 Think Before Coding
- Literal values: "If multiple interpretations exist, present them; don't pick silently."
- Why first: Highest-impact absent rule; no ambiguity in implementation

**K2** — Push-back-when-simpler-exists rule
- What: Add "If a simpler approach exists, say so before implementing" as an Approach bullet
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md`, Approach section
- How: Add one bullet after K1 — "If a simpler approach exists, say so before implementing."
- Gate: Bullet appears in the file; does not conflict with existing simplicity guidance
- Reference location: `CLAUDE.md` §1 Think Before Coding
- Literal values: "If a simpler approach exists, say so before implementing."
- Why first: Pair with K1 — both address pre-implementation disambiguation behavior

**K3** — Mention-not-delete dead code rule
- What: Add "If you notice unrelated dead code, mention it — don't delete it" as an Approach bullet
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md`, Approach section
- How: Add one bullet — "If you notice unrelated dead code, mention it — don't delete it."
- Gate: Bullet appears in the file; distinct from existing backwards-compat-hack guidance
- Reference location: `CLAUDE.md` §3 Surgical Changes
- Literal values: "If you notice unrelated dead code, mention it — don't delete it."

### Tier 2 — Module-level Augmentation

**K4** — Surgical-changes governing test
- What: Add "Every changed line should trace directly to the user's request" as a behavioral check criterion
- Where: `C:\Users\Kirsten\.claude\CLAUDE.md`, Approach section (or near existing surgical-changes-adjacent guidance)
- How: Add one bullet — "Every changed line should trace directly to the user's request."
- Gate: Bullet appears in file; does not duplicate existing guidance
- Reference location: `CLAUDE.md` §3 Surgical Changes
- Literal values: "Every changed line should trace directly to the user's request."
- Specify required: No. Breaking change risk: None.

### Watch Only

**K5** — `→ verify:` step format
- Reason: WabbleSpec already has wave plan step-verify patterns. Adapting this for CLAUDE.md behavioral guidance requires reframing to gate/receipt language, not just test assertions. Defer until a specific use case makes the reframing clear.
- Promote when: A concrete agent failure is observed where imperative-to-verifiable transformation would have helped outside formal wave execution.

---

## Do-Not-Copy List

| Item | Invariant / Reason |
|---|---|
| `skills/karpathy-guidelines/SKILL.md` as a WabbleSpec skill | Fails Gate 1 (no When NOT to use, no negative triggers, description lacks period) |
| Plugin marketplace URLs and install commands | External URLs in framework files violate WabbleSpec conventions |
| CURSOR.md tooling setup | Cursor-specific; WabbleSpec uses Claude Code only |
| `→ verify:` format without receipt/gate reframing | Would conflict with WabbleSpec's I10 receipt model if used naively |

---

## Priority Implementation Order

| Priority | ID | Item | Why first |
|---|---|---|---|
| 1 | K1 | Present-multiple-interpretations | Highest absent rule; zero implementation risk |
| 2 | K2 | Push-back-when-simpler | Pairs with K1; same location, same risk level |
| 3 | K3 | Mention-not-delete dead code | Sharpens existing guidance; distinct formulation |
| 4 | K4 | Every-changed-line governing test | Lower priority; additive precision only |

---

## Tier 7 — Expansion Roadmap

No expansion opportunities identified. Ref-eval Section 9: zero Tier 7 candidates.

---

## Execution Notes

- All four items target the same file (`~/.claude/CLAUDE.md`). Apply in sequence, one bullet at a time.
- Do not apply to `.wabblespec/` paths (I11).
- No sync to engine modules required — this is a global user CLAUDE.md, not a WabbleSpec skill module.
- K1 and K2 logically pair; implement consecutively.
- Gate B confirmation required before implementation (not autonomous).
