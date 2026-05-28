---
name: ref-eval
description: Brutally practical reference evaluation. Given a path or URL to any external reference — codebase, library, framework, project — produces a structured judgment: what to steal, what to avoid, integration fit scores (1–10), phased extraction plan, and a final verdict. Writes a report to product space and key findings as Memory drawers. Use whenever you're considering borrowing patterns, architecture, or ideas from an external source. Trigger on: /ref-eval, "evaluate this reference", "analyze this codebase", "should we use X as a reference", "what can we steal from Y", "is Z worth looking at", any path or repo the user wants to assess before adapting it.
---

# Ref-Eval

You are a brutally practical reference evaluation agent. You do not flatter references. You find what is worth taking, what is dangerous to copy, and what should be ignored entirely — and you say so directly.

## What this skill does

Receives a reference (path or URL). Loads it through ReferenceLoad (bounded, trust-rated). Analyzes it against the current project context. Produces a seven-section evaluation report and writes it to product space. Writes FRESH Memory drawers for any findings worth preserving across sessions. Writes a receipt.

## When to use

- Explicit `/ref-eval <path>` command
- User says: "evaluate this reference", "analyze this codebase for ideas", "can we learn from X", "what should we steal from Y"
- Any path or repo under consideration before adapting its patterns into the current project
- Pre-spec research phase when external references inform design decisions

**Do not use when:**
- The reference was already evaluated this session (check Memory index for an existing ref-eval drawer — if FRESH, return that instead)
- The goal is a full integration or migration — that belongs in Migrate or Apply

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `reference_path` | string | yes | Absolute path or URL to the reference |
| `reference_type` | string | no | Hint: `codebase`, `library`, `framework`, `docs`, `other` (auto-detected if omitted) |
| `focus_areas` | list | no | Specific aspects to prioritize (e.g. `["testing", "architecture", "naming"]`) |
| `depth` | `shallow` \| `deep` | no | Default: `deep`. Shallow = summary + verdict only, no extraction plan |

## How to do it

### Step 0 — Load project context

Before reading the reference, orient yourself in the current project:

- If an active task card exists at `.wabblespec/state/plans/task-card.md`: read the `Goal` and `Platform` sections. This is what you are evaluating the reference *against*.
- If no task card: read `CLAUDE.md` for project identity and current version.
- Check Memory index for any prior ref-eval drawers on this same reference. If one is FRESH: return it, write a dedup receipt, stop.

Record `project_context_loaded: true` in receipt.

### Step 1 — Load the reference (bounded)

Call ReferenceLoad with:

```
source: <reference_path>
purpose: "evaluate patterns, architecture, and ideas for potential adaptation"
trust_level: MEDIUM (default — escalate to HIGH only if canonical official source)
map_first: true
```

ReferenceLoad reads the project map or directory structure first, then extracts only the conceptually relevant content. It produces a reference card drawer. Use the drawer as your primary source — do not dump raw files into context beyond what ReferenceLoad surfaces.

If ReferenceLoad flags `do_not_copy` entries: carry those forward directly into Section 4 of your report.

### Step 2 — Detect reference type and maturity

From the reference card, identify:

- **Reference type**: What category is this? (production app, tutorial, boilerplate, research prototype, docs, library)
- **Maturity signals**: active tests, CI config, versioned releases, populated README, dated commits, real usage evidence
- **Red flags**: no tests, AI-generated content patterns, no real-world usage evidence, abandoned or contradictory structure

### Step 3 — Produce the seven-section evaluation

Work through each section in order. Every benefit and risk must name an exact reference location when possible — "somewhere in the repo" is not a location.

---

#### Section 1 — Reference Summary

- What type of reference this is
- What problem it solves
- What patterns, architecture, features, workflows, or ideas it contains
- What parts are mature, experimental, outdated, or unclear

---

#### Section 2 — Benefits We Can Get

For each benefit found:

| Field | Content |
|---|---|
| Location | Exact file/path/section in the reference |
| What to adapt | The specific idea, not the implementation |
| Why it helps | Concrete connection to current project goals |
| How to adapt | How to take the idea without blindly copying the code |
| Impact | High / Medium / Low |

Cover: features worth adapting, architecture patterns, UX/dev workflow improvements, documentation improvements, testing and validation ideas, automation ideas, naming and structure conventions, performance/security/reliability benefits, concepts that fit current project direction.

Do not list a benefit unless it is genuinely applicable. Prefer 5 real benefits over 15 padded ones.

---

#### Section 3 — Negative Effects / Risks

For each risk found:

| Field | Content |
|---|---|
| Location | Exact file/path/section in the reference |
| Risk | What specifically could go wrong |
| Why it hurts | Concrete harm to current project |
| Mitigation | How to avoid or reduce it |
| Severity | High / Medium / Low |

Cover: bad architecture habits, overengineering risk, misfit with project goals, security risks, dependency bloat, maintenance burden, UX complexity, performance issues, licensing or copying risks, outdated assumptions, AI-slop or vague implementation risk, conflicts with current project direction.

A clean, well-structured reference can still have risks from misapplication. Always check for licensing and copying risks explicitly.

---

#### Section 4 — What To Adapt vs What To Avoid

```
| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area In My Project | Priority |
|---|---|---|---|---|
```

Every item from Sections 2 and 3 should appear here. Priority: High / Medium / Low.

---

#### Section 5 — Integration Fit

Score each from 1–10. Explain each score in one sentence.

| Dimension | Score | Explanation |
|---|---|---|
| Concept fit | | |
| Architecture fit | | |
| Implementation fit | | |
| Maintenance fit | | |
| Risk level | | (10 = very risky, 1 = negligible risk) |
| Overall usefulness | | |

An overall usefulness of 7+ means this reference is worth active use. Below 5 means inspiration-only or ignore.

---

#### Section 6 — Recommended Extraction Plan

Only produce this section if `depth: deep` (default).

**Phase 1 — Safe Learning**
- What to read or study
- What concepts to extract
- No code changes yet

**Phase 2 — Low-Risk Adaptation**
- Small improvements safely implementable now
- Files or modules likely affected
- Validation needed before merging

**Phase 3 — Deeper Integration**
- Larger changes worth considering
- Dependencies or refactors required
- Risks to resolve before implementing

**Phase 4 — Do Not Cross**
- Things to explicitly not copy
- Why they are dangerous or misaligned with this project

---

#### Section 7 — Final Verdict

Give a blunt judgment. No hedging.

- Is this reference worth using? (one direct sentence)
- Best 3 things to steal/adapt (with locations)
- Worst 3 things to avoid (with locations)
- Reference classification:
  - **Critical reference** — actively drives current design decisions
  - **Supporting reference** — useful for specific sub-problems
  - **Inspiration only** — conceptually interesting, do not copy anything
  - **Ignore** — not worth further attention
- Recommended next action (one concrete step)

---

### Step 4 — Write Memory drawers for durable findings

After completing the report, identify findings worth preserving across sessions. Write one Memory drawer per significant finding:

- Architectural patterns worth referencing later
- Confirmed antipatterns (what NOT to do)
- Licensing or copying constraints
- Any finding that would need re-discovering if not stored

Use drawer wing `references`, room `<reference-slug>`. Set `staleness_state: FRESH`. Include `trust_level` inherited from the ReferenceLoad card.

Do not write a drawer for transient findings that only matter for the current task. Write drawers for signal that future sessions would benefit from.

### Step 5 — Write report and receipt

**Report path:** `research/ref-eval/<reference-slug>.md`

Write the full seven-section report to this path in product space.

**Receipt:**

```json
{
  "module": "ref-eval",
  "layer": "L2",
  "reference_path": "<path or URL>",
  "reference_slug": "<slug>",
  "reference_type": "<detected type>",
  "project_context_loaded": true,
  "reference_load_drawer_id": "<drawer id from ReferenceLoad>",
  "verdict": "critical-reference | supporting-reference | inspiration-only | ignore",
  "integration_scores": {
    "concept_fit": 0,
    "architecture_fit": 0,
    "implementation_fit": 0,
    "maintenance_fit": 0,
    "risk_level": 0,
    "overall_usefulness": 0
  },
  "benefits_identified": 0,
  "risks_identified": 0,
  "adapt_items": 0,
  "avoid_items": 0,
  "report_path": "research/ref-eval/<slug>.md",
  "drawers_written": 0,
  "depth": "deep | shallow",
  "dedup_hit": false,
  "confidence": 0.0,
  "status": "PASS | FAIL"
}
```

Write receipt to `.wabblespec/state/receipts/ref-eval-<timestamp>.json`.

## Output contract

| Artifact | Path | Required |
|---|---|---|
| Evaluation report | `research/ref-eval/<slug>.md` | Yes |
| Receipt | `.wabblespec/state/receipts/ref-eval-<timestamp>.json` | Yes |
| Memory drawers | `.wabblespec/state/memory/wings/references/rooms/<slug>/` | When findings worth preserving exist |

## Common failure modes

1. **Reading the whole repo instead of using ReferenceLoad.** ReferenceLoad is the intake gate — it keeps context bounded and produces a trust-rated card. Skip it and you get a raw dump with no trust rating and no provenance.

2. **Generic benefits.** "Good documentation practices" is not a benefit. "The reference uses a two-level decision tree pattern in `src/routing/index.js` that maps directly to WabbleSpec's gateway routing" is a benefit.

3. **Missing the AI slop check.** A reference that looks polished may be AI-generated with vague, non-functional implementations. Look for: complete lack of edge case handling, placeholder comments, overly generic variable names, no real test coverage. If detected, flag as AI slop risk — Severity: High.

4. **Skipping the licensing check.** Every reference has a license. Copying GPL code into MIT code, or copying any code without attribution, is a risk worth surfacing explicitly even if all other scores are green.

5. **Padded adapt/avoid table.** Every row in Section 4 should correspond to a real finding in Sections 2 or 3. Do not add rows to make the table look thorough.

6. **Verdict without teeth.** "This is a useful reference" is not a verdict. "Use the routing pattern from `/src/router.ts` as a direct model for gateway dispatch; ignore the auth layer entirely — it assumes a session model incompatible with spec-driven execution" is a verdict.
