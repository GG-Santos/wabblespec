---
name: ref-eval
description: Brutally practical reference evaluation. Given a path or URL to any external reference (codebase, library, framework, project) produces a structured verdict covering what to steal, what to avoid, integration fit scores 1-10, a phased extraction plan, and a final judgment. Writes a report to product space and key findings as Memory drawers. Use whenever considering borrowing patterns, architecture, or ideas from an external source. Triggers on /ref-eval, "evaluate this reference", "analyze this codebase", "should we use X as a reference", "what can we steal from Y", "is Z worth looking at", any path or repo to assess before adapting. Do NOT invoke if a ref-eval report already exists for this reference and it has not changed (use that report directly); do not invoke when the user has decided what to adopt and wants a work plan (that is ref-plan, which runs after ref-eval); do not invoke when implementation is complete and the user wants an audit against the reference (that is ref-comp).
---

# Ref-Eval

You are a brutally practical reference evaluation agent. You do not flatter references. You find what is worth taking, what is dangerous to copy, and what should be ignored entirely — and you say so directly.

## What this skill does

Receives a reference (path or URL). Loads it through ReferenceLoad (bounded, trust-rated). Analyzes it against the current project context. Produces a seven-section evaluation report and writes it to product space. Writes FRESH Memory drawers for any findings worth preserving across sessions. Delegates receipt write to `receipt-writer.py`.

## Reference Routing

| Situation | Reference |
|---|---|
| ref-eval receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type ref-eval` |

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

### Step 0b — Pre-screening gate (run before Step 1a)

Apply four binary pass/fail criteria before loading the reference. If 2 or more fail, write the ref-eval receipt with `status: SKIP` and surface the failure reason. Do not proceed to Step 1a.

| Gate | Pass | Fail |
|---|---|---|
| **G1 Mechanism Specificity** | Defines a specific mechanism or pattern (e.g. "recursive summarization with compression ratio", "XML-structured tool responses", "checkpoint-based state persistence") | Uses only vague terms ("improving accuracy", "better prompts", "AI best practices") without explaining how mechanistically |
| **G2 Implementable Artifacts** | Contains at least one of: code snippets, JSON/XML schemas, prompt templates with structure, architectural diagrams, API contracts, configuration examples | Zero implementable artifacts — purely conceptual or high-level overview only |
| **G3 Beyond Basics** | Discusses advanced patterns: agent state management, tool interface design, memory architecture, multi-agent coordination, evaluation methodology, context optimization | Focuses solely on basic prompt tips, introductory RAG, or introductory tutorials with no production-hardened insight |
| **G4 Source Verifiability** | Author or organization identifiable with demonstrated technical credibility: production engineering blogs from AI labs, recognized practitioners with public contributions, peer-reviewed papers | Anonymous source, unverifiable credentials, or obvious vendor marketing disguised as technical writing |

On 2+ failures: write receipt with `status: SKIP`, note which gates failed, stop.
On 0–1 failures: proceed to Step 1a and note which gate had a marginal pass.

### Step 1a — Load and map the reference

Call ReferenceLoad with:

```
source: <reference_path>
purpose: "extract behavioral logic, structural format, and cross-file interaction patterns for adaptation analysis"
trust_level: MEDIUM (default — escalate to HIGH only if canonical official source)
map_first: true
```

ReferenceLoad reads the project map or directory structure first. Use the resulting reference card as the anchor for Steps 1b and 1c. If ReferenceLoad flags `do_not_copy` entries, carry them into Section 4.

### Step 1b — File inventory

Catalogue every file in the reference. Do not stop at the top-level map — traverse subdirectories. For each file:

| File | Purpose | Size signal | Key contents | Read? | Transfer check |
|---|---|---|---|---|---|

- **Purpose**: what this file does in one line
- **Size signal**: large (>300 lines) / medium / small
- **Key contents**: the most important thing inside — a specific algorithm, a schema shape, a rule list, a config table
- **Read?**: yes (full read) / summary (frontmatter/header only) / skipped (why)
- **Transfer check**: required only when Read? = skipped. State whether the file was skimmed for transferable content (design theory, evaluation frameworks, vocabulary tables, anti-pattern catalogs, self-critique protocols, behavioral heuristics) independent of its implementation domain. Result: "skimmed — no transferable theory" / "skimmed — transferable: [what]" / "not skimmed — [reason]".

Every file marked `skipped` must have an explicit reason. "Too large" is not a reason — read the critical sections. A file that was not read cannot be assessed.

**Directory-level skip decisions are prohibited.** Every file — including files in `docs/`, `guides/`, `references/`, and non-primary files in `skills/` subdirectories — must appear as an individual inventory row before any scope decision is made. "All of docs/ is out of scope" is not a valid skip reason. "This file contains only product-specific HTML composition examples with no transferable behavioral rules" is valid. Apply scope decisions at the content level, not the directory level.

Produce the inventory before any analysis. Gaps discovered later ("we didn't realize that file existed") indicate an incomplete inventory.

### Step 1c — Connection map

Trace every connection between files in the reference. A connection is any relationship where one file depends on, calls, reads, writes, or contracts with another.

Connection types to trace:

| Type | What to look for |
|---|---|
| Import / require | Direct code dependency — file A loads file B |
| Call chain | Function in A invokes function in B; note the data passed |
| Shared state | Global, session, or file-based state that multiple files read or write |
| Data flow | What data enters the system, where it transforms, where it exits |
| Event / hook wiring | What triggers what; async connections that don't show as imports |
| Schema contract | A file's output shape is consumed as a specific input shape by another |
| Sequencing constraint | B must run after A; A must complete before C can start |

Output format:

```
[File A] --[connection type]--> [File B]: [what is passed or shared]
```

For each connection, note: what would break in File B if File A changed this interface? These are the hidden coupling points that matter most for integration.

### Step 2 — Detect reference type and extract three dimensions at depth

From the file inventory, connection map, and reference card, identify:

- **Reference type**: What category is this? (production app, skill/behavioral spec, tutorial, boilerplate, research prototype, docs, library)
- **Maturity signals**: active tests, CI config, versioned releases, populated README, dated commits, real usage evidence
- **Red flags**: no tests, AI-generated content patterns, no real-world usage evidence, abandoned or contradictory structure

**Domain framing quarantine:** The reference type and domain label are diagnostic — they are not a read filter. A reference characterized as "video rendering", "e-commerce", or any other specific domain may still encode transferable behavioral heuristics, evaluation protocols, vocabulary tables, visual style taxonomies, self-critique gates, and anti-pattern catalogs in its documentation, guidance, and secondary skill files. Do not retroactively use domain characterization to justify directory-level skips already prohibited in Step 1b. The question to ask per file is: "Does this file contain principles, frameworks, or vocabulary that transfer across domains?" — not "Is this file in a domain that matches ours?"

Before moving to the seven-section evaluation, extract all three dimensions at full depth. "Pattern level" is insufficient — go to the detail level within each dimension.

**Dimension 1 — Behavior (operational detail required)**

What the reference *does*, and specifically *how* it does it. Do not stop at "it has a deviation handling system." Go to: what are the 4 rules, in what priority order, what is the exact trigger condition for each, what is the exact action, what are the exceptions to each rule? Capture:

- Decision logic: the actual branches, conditions, and threshold values — not just "it branches"
- Algorithms: the specific steps, not just "it processes"
- Failure modes: the exact conditions that trigger each failure path, and the exact recovery action
- Escalation patterns: what specific signal triggers escalation, what happens at each level
- Judgment heuristics: the exact rules an agent uses to make a call (e.g., "5+ consecutive reads with no write = stuck")
- Named constants: any threshold, count, percentage, or timeout that governs behavior
- Banned/allowed lists: any explicit enumeration of permitted or forbidden values
- Schema shapes: exact field names, types, required vs. optional, constraints

**Dimension 2 — Format (structure at the identifier level)**

How the reference is *organized*, down to naming at the identifier level. Capture:

- File structure and directory layout
- Naming conventions: how files, functions, variables, config keys are named — the pattern, not just "they have conventions"
- Schema shapes: exact field names and nesting (not just "it has a schema")
- Template layouts: the exact sections and their order
- Output shapes: what the final artifact looks like field by field
- Comment conventions: how intent is encoded in comments — do they explain why, or just what?
- Error message patterns: how errors are reported — format, fields, verbosity

**Dimension 3 — Interactions (coupling at the contract level)**

How *parts connect*, down to the contract level. For every connection in Step 1c, state:

- What the producer outputs (exact shape, fields, types)
- What the consumer expects (exact shape, fields, types)
- What happens when the contract is violated (does it fail silently, loudly, or not at all?)
- What shared state exists and which files touch it
- Sequencing constraints that enforce ordering

A connection described as "A calls B" is not captured. "A calls B with `{wave_id, context_pct, active_module}` and B returns `{verdict, reason, gate_type}` where missing `gate_type` causes B to default to SOFT" is captured.

Record all three dimensions explicitly before producing the seven-section report. A finding that only addresses one or two dimensions is partial.

### Step 3 — Produce the seven-section evaluation

Work through each section in order. Every benefit and risk must name an exact reference location when possible — "somewhere in the repo" is not a location.

---

#### Section 1 — Reference Summary

- What type of reference this is
- What problem it solves
- **Behavioral content**: what logic, decisions, workflows, and domain knowledge it encodes
- **Structural content**: how it is organized, what format and layout conventions it uses
- **Interaction content**: how its parts connect, what cross-file or cross-component contracts exist
- What parts are mature, experimental, outdated, or unclear

---

#### Section 2 — Benefits We Can Get

For each benefit found:

| Field | Content |
|---|---|
| Location | Exact file/path/section — include line number or heading when possible |
| What to adapt | The specific idea, not the implementation |
| Why it helps | Concrete connection to current project goals |
| How to adapt | How to take the idea without blindly copying the code |
| Literal extract | Exact values, rules, schemas, or enumerations from the reference that must be preserved verbatim — not paraphrased |
| Impact | High / Medium / Low |

**Literal extract** is required whenever the reference encodes a specific value that governs behavior: a threshold (e.g., "5+ consecutive reads"), an enumeration (e.g., the banned language list), a priority rule (e.g., "Rule 4 wins before Rules 1–3"), a schema with required fields, or a named constant. These must be quoted from the source, not summarized. A paraphrased rule is a corrupted rule.

Cover all three dimensions extracted in Step 2:
- **Behavioral**: decision logic worth porting, embedded domain heuristics, failure mode patterns, escalation flows, trigger/gate conditions, judgment rules, workflow sequences — with exact thresholds and conditions
- **Format**: structural conventions, naming patterns, schema shapes at the field level, template layouts with section order, API contract designs with exact field names
- **Interaction**: cross-file handoff patterns with exact data shapes, dependency structures, shared state contracts naming every file that touches shared state, sequencing enforced across module boundaries

Also cover: UX/dev workflow improvements, testing and validation ideas, automation ideas, performance/security/reliability benefits.

Do not list a benefit unless it is genuinely applicable. Prefer 5 real benefits over 15 padded ones. Each benefit should be specific enough that an implementer could act on it without re-reading the reference.

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

Each item must name the exact reference file and section, the exact target file in the current project, and the exact change — not just the direction. An item that could be handed to ref-plan without re-reading the reference is written correctly. An item that requires re-reading the reference to understand what to do is underspecified.

**Phase 1 — Safe Learning**
- What to read or study (exact files)
- What concepts to extract (specific, not general)
- Literal values discovered that must be preserved when the concept is later implemented
- No code changes yet

**Phase 2 — Low-Risk Adaptation**
- Exact change: what to add, where, how
- Exact target file in the current project
- Literal values from the reference that the change must encode
- Validation gate: how to know the change worked

**Phase 3 — Deeper Integration**
- Exact change and exact target
- Dependencies that must exist before this starts
- Risks to resolve before implementing
- Literal schemas or contracts that must be matched

**Phase 4 — Do Not Cross**
- Items explicitly excluded — exact reference location
- Reason: invariant violated (name it), wrong stack, architecture conflict, licensing
- What to do instead if the underlying need is real

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

#### Section 8 — Project Synthesis

The generative section. Do not summarize what the reference does — that is Sections 1–7. Ask a different question: what novel patterns become possible only by combining this reference's approaches with the current project's specific capabilities?

A synthesis idea requires both inputs. It must name a mechanism from the reference AND a mechanism from the current project that together enable something neither could produce alone. A pattern that could apply to any project is not a synthesis idea.

For each synthesis idea:

| Field | Content |
|---|---|
| What | The novel pattern or capability |
| Reference contribution | Which reference behavior, design, or structure enables this |
| Project contribution | Which current project capability, artifact, or infrastructure makes it worth doing |
| Target | Exact file in the current project where this would live |
| Gap closed | What failure mode, missing behavior, or design weakness this addresses |

Aim for 2–5 synthesis ideas. Zero is a valid answer if the reference and project have no meaningful intersection — say so explicitly rather than padding.

---

#### Section 9 — Expansion Opportunities

The growth section. Section 8 asks what becomes possible by combining this reference's patterns with existing project capabilities. Section 9 asks a different question: **what can this reference do that the project cannot do at all?** Not adaptation — net-new capability that would require building something from scratch.

An expansion opportunity is not an adaptation target. It is a capability the project has zero version of: no module, no script, no hook, no skeleton. Adapting a pattern into an existing file is Tier 1–3 work. Building something the project has never had is expansion.

For each expansion opportunity:

| Field | Content |
|---|---|
| Capability | What the reference can do that the project cannot |
| Reference location | Exact file/section where this capability lives |
| Why the project lacks it | What architectural gap, missing module, or design decision is the root cause |
| What it would unlock | Concrete new behavior or user capability — not "more flexibility" |
| Dependencies | What would need to exist first (infrastructure, prior modules, external tools) |
| Effort signal | `days` / `weeks` / `months` (rough order-of-magnitude only) |
| Tier 7 candidate | Yes / No — whether this warrants a Tier 7 entry in ref-plan |

**Rules for this section:**
- Every item must be a genuine gap — not a pattern the project could adapt in an afternoon
- Do not list items already in Section 2 or Section 8 — those are adaptation and synthesis, not expansion
- Do not list items the project explicitly does not want (check non-goals and CLAUDE.md)
- Zero is a valid answer; most references do not reveal net-new capabilities

Every expansion opportunity listed here as "Tier 7 candidate: Yes" must appear in Tier 7 of the ref-plan.

---

### Step 4 — Write Memory drawers for durable findings

After completing the report, identify findings worth preserving across sessions. Write one drawer per significant finding (architectural patterns, confirmed antipatterns, licensing constraints, anything a future session would need to rediscover). Delegate to `drawer-writer.py` — do not construct drawer JSON inline.

```bash
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "<OBSERVATION_TYPE>: <finding>" \
  --wing references \
  --room <reference-slug> \
  --evidence "<finding text; include trust_level inherited from ReferenceLoad card>" \
  --confidence <0.0-1.0> \
  --staleness-state FRESH \
  --source "<reference file path or slug>" \
  --source-module ref-eval \
  --actor ref-eval
```

Use `--evidence-file <path>` when evidence is multi-line. Do not write drawers for transient findings that only matter for the current task.

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
  "synthesis_items": 0,
  "expansion_items": 0,
  "report_path": "research/ref-eval/<slug>.md",
  "drawers_written": 0,
  "depth": "deep | shallow",
  "dedup_hit": false,
  "confidence": 0.0,
  "status": "PASS | FAIL"
}
```

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type ref-eval \
  --task-id <task-id> \
  --session-id <session-id> \
  --status PASS \
  --target <reference-slug> \
  --summary "<verdict: critical-reference|supporting-reference|inspiration-only|ignore>" \
  --confidence <0.0-1.0> \
  --out .wabblespec/state/receipts/ref-eval-<timestamp>.json
```

## Output contract

| Artifact | Path | Required |
|---|---|---|
| Evaluation report | `research/ref-eval/<slug>.md` | Yes |
| Receipt | `.wabblespec/state/receipts/ref-eval-<timestamp>.json` | Yes |
| Memory drawers | `.wabblespec/state/memory/wings/references/rooms/<slug>/` | When findings worth preserving exist |

## Common failure modes

1. **Incomplete file inventory.** If a file was not read, it was not assessed. "Too large" is not a reason to skip — read the critical sections. Files discovered after the inventory was closed indicate a gap in Step 1b.

2. **Categorizing by directory instead of by content.** Marking `docs/`, `guides/`, or non-primary skill files as "out of scope" at the directory level without reading them is an incomplete inventory. Design theory, behavioral heuristics, evaluation frameworks, anti-pattern catalogs, visual style taxonomies, self-critique protocols, and vocabulary tables frequently live in documentation and secondary skill files rather than in implementation source. These files must appear in the inventory and be read at a summary level before being marked Skipped. The Transfer check column in the inventory exists to enforce this.

3. **Closing early on a low usefulness score.** An "inspiration-only" verdict is a verdict on the reference as a deployable system — it does NOT reduce the requirement to complete all nine sections. Inspiration-only references often yield their most distinctive value in Section 8 (synthesis) and Section 9 (expansion). Finding two implementation wins early and closing is underfitting when files remain unread in the inventory.

4. **Missing connection map.** Patterns that look independent are often coupled through shared state or data contracts. Step 1c must trace every connection — not just imports. A benefit identified without tracing its connection dependencies will fail during integration when the coupling surfaces.

5. **Reading the whole repo instead of using ReferenceLoad.** ReferenceLoad is the intake gate — it keeps context bounded and produces a trust-rated card. Skip it and you get a raw dump with no trust rating and no provenance.

6. **Generic benefits.** "Good documentation practices" is not a benefit. "The reference uses a two-level decision tree pattern in `src/routing/index.js` that maps directly to WabbleSpec's gateway routing" is a benefit.

7. **Paraphrased literal values.** If the reference has a banned language list of 12 phrases, the benefit must quote all 12 — not "a list of banned scope-reduction phrases." Paraphrasing a rule changes it. Summarizing a threshold loses it. Use the `Literal extract` field and quote the source.

8. **Missing the AI slop check.** A reference that looks polished may be AI-generated with vague, non-functional implementations. Look for: complete lack of edge case handling, placeholder comments, overly generic variable names, no real test coverage. If detected, flag as AI slop risk — Severity: High.

9. **Skipping the licensing check.** Every reference has a license. Copying GPL code into MIT code, or copying any code without attribution, is a risk worth surfacing explicitly even if all other scores are green.

10. **Padded adapt/avoid table.** Every row in Section 4 should correspond to a real finding in Sections 2 or 3. Do not add rows to make the table look thorough.

11. **Verdict without teeth.** "This is a useful reference" is not a verdict. "Use the routing pattern from `/src/router.ts` as a direct model for gateway dispatch; ignore the auth layer entirely — it assumes a session model incompatible with spec-driven execution" is a verdict.
