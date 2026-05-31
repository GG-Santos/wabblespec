---
name: ref-adopt
description: Full reference adoption pipeline in one invocation. Sequences ref-eval -> ref-plan -> implementation -> ref-comp autonomously. Evaluates a reference across all three dimensions (behavior, format, file interactions), builds a phased integration plan, implements Phase 1 safe wins directly, then audits execution fidelity. Trigger on: /ref-adopt, "run the full reference pipeline for X", "adopt patterns from X", "evaluate and implement from reference X", "do the whole ref pipeline", "evaluate this and then build it in", any time the user wants to go from raw reference to implemented and verified integration without manually running four separate skills.
---

# Ref-Adopt

Full autonomous reference adoption pipeline.

```
ref-eval → ref-plan → IMPLEMENT → ref-comp
```

Individual skills (`/ref-eval`, `/ref-plan`, `/ref-comp`) remain available for partial runs. Use `/ref-adopt` when you want the full pipeline in one invocation with no manual hand-offs.

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `reference_path` | string | yes | Absolute path or URL to the reference |
| `reference_type` | string | no | Hint: `skill`, `codebase`, `library`, `framework`, `docs`, `other` (auto-detected) |
| `focus_areas` | list | no | Dimensions to prioritize: `behavior`, `format`, `interactions`, `testing`, `naming` |
| `risk_appetite` | `conservative` / `balanced` / `aggressive` | no | Default: `balanced` |
| `autonomous` | bool | no | Default: false. Skip Gate B (implementation preview). |
| `phases_to_implement` | `1` / `1-2` | no | Default: `1`. Phase 2 requires `--autonomous` or explicit user confirm. |

---

## Phase 0 — Load Project Context

Before touching the reference:

- If `.wabblespec/state/plans/task-card.md` exists: read `Goal` and `Platform`.
- Else: read `CLAUDE.md` for project identity and current version.
- Check Memory index for a prior ref-eval drawer for this reference. If FRESH: use it as Phase 1 output and skip to Phase 2.

---

## Phase 1 — Evaluate the Reference

### Load, inventory, and map the reference

**Step 1a — Load:** Call ReferenceLoad with `map_first: true`, `trust_level: MEDIUM`. Use the reference card as the anchor. If ReferenceLoad flags `do_not_copy` entries, carry them into Section 4.

**Step 1b — File inventory:** Catalogue every file in the reference. For each: path, purpose (one line), size signal (large/medium/small), key contents (the most important specific thing inside), Read/Summary/Skipped status with reason for Skipped, and a Transfer check for any Skipped file (skimmed for transferable content — design theory, evaluation frameworks, vocabulary tables, anti-pattern catalogs, self-critique protocols, and production-hardened implementation knowledge such as exact unit systems, validation scripts, non-obvious API gotchas, and schema field contracts — independent of implementation domain). A file not read cannot be assessed. **Directory-level skip decisions are prohibited** — every file in `docs/`, `guides/`, `references/`, and non-primary skill subdirectories must appear as an individual row before any scope decision is made. Scope decisions are content-level, not directory-level.

**Step 1c — Connection map:** Trace every connection between files. Types to find: imports, call chains (with data passed), shared state (which files touch it), data flows (enter → transform → exit), event/hook wiring, schema contracts (producer output shape → consumer input shape), sequencing constraints. Output: `[File A] --[type]--> [File B]: [what is passed]`. Note what would break in File B if File A changed the interface.

Produce inventory and connection map before beginning dimensional extraction.

### Extract three dimensions at depth before writing any section

Before producing the seven-section evaluation, extract all three dimensions at full depth. Pattern level is insufficient — go to operational detail.

**Dimension 1 — Behavior (operational detail required):** What the reference does, and specifically how. Capture: exact decision branches and their conditions, named threshold values (counts, percentages, timeouts), priority orderings (which rule wins when multiple apply), exact failure recovery actions, judgment heuristics with their specific trigger conditions, banned/allowed enumerations (quote them in full — do not summarize), schema shapes with required fields named.

**Dimension 2 — Format (identifier level):** How the reference is organized down to naming conventions at the variable/function level, exact schema field names and types, template section order, output shapes field by field, comment conventions (do they explain why or just what?), error message format.

**Dimension 3 — Interactions (contract level):** For every connection from Step 1c, state: what the producer outputs (exact shape), what the consumer expects (exact shape), what breaks when the contract is violated. Shared state: which files touch it, in what order, under what conditions. Sequencing constraints that enforce ordering across the system.

Detect reference type and maturity:
- **Reference type**: production app, skill/behavioral spec, tutorial, boilerplate, research prototype, docs, library
- **Maturity signals**: active tests, CI, versioned releases, real usage evidence
- **Red flags**: no tests, AI-generated patterns, no real-world usage, abandoned structure

**Domain framing quarantine:** The detected reference type is diagnostic — not a read filter. A reference characterized as "video rendering" or "e-commerce" may still encode transferable behavioral heuristics, evaluation protocols, vocabulary tables, visual style taxonomies, and self-critique gates in its documentation and secondary skill files. Do not use domain characterization to justify directory-level skips. Ask per file: "Does this file contain principles or frameworks that transfer across domains?" — not "Is this file in a domain that matches ours?"

For production implementations (document format skills, data processing pipelines, communication templates, output format libraries): extend the question one step further — "Could the project implement this capability natively using this skill as a production implementation guide?" A skill that produces .docx or .xlsx files is not just a domain-specific tool; it is a production-hardened specification of non-obvious gotchas (unit systems, schema contracts, validation sequences) that the project would otherwise have to rediscover independently. These are Tier 7 candidates even when the primary domain differs.

### Seven-section evaluation

Every benefit and risk names an exact reference location.

---

**Section 1 — Reference Summary**

- What type this is and what problem it solves
- Behavioral content: logic, decisions, workflows, domain knowledge it encodes
- Structural content: organization, format conventions, layout
- Interaction content: how parts connect, cross-file contracts
- What parts are mature, experimental, outdated, or unclear

---

**Section 2 — Benefits We Can Get**

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|

Cover all four dimensions:
- **Behavioral**: decision logic worth porting, domain heuristics, failure mode patterns, escalation flows, trigger/gate conditions, judgment rules, workflow sequences
- **Format**: structural conventions, naming patterns, schema shapes, template layouts, API contract designs, configuration idioms
- **Interaction**: cross-file handoff patterns, dependency structures, shared state contracts, sequencing enforced across module boundaries
- **Capability expansion**: reference skills that the project could implement natively to produce a new output type, serve a new platform, or fill a current gap. The question here is not "can we adapt this pattern?" but "could we build this capability using this skill as a production implementation guide?" A reference skill that produces .docx/.pdf/.xlsx is evaluated not just for behavioral patterns — it is evaluated as a potential native capability the project currently lacks.

Also cover: UX/dev workflow, testing and validation ideas, automation, performance/security/reliability benefits.

Prefer 5 real benefits over 15 padded ones.

---

**Section 3 — Negative Effects / Risks**

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|

Cover: bad architecture habits, overengineering, misfit, security risks, dependency bloat, licensing, AI-slop risk, conflicts with project direction, coupling risks from interaction patterns.

---

**Section 4 — Adapt vs Avoid**

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|

Every item from Sections 2 and 3 appears here.

---

**Section 5 — Integration Fit**

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | | |
| Architecture fit | | |
| Implementation fit | | |
| Maintenance fit | | |
| Risk level | | (10 = very risky) |
| Overall usefulness | | |

Overall usefulness 7+: worth active use. Below 5: inspiration-only or ignore.

---

**Section 6 — Recommended Extraction Plan**

Phase 1 (Safe Learning) → Phase 2 (Low-Risk Adaptation) → Phase 3 (Deeper Integration) → Phase 4 (Do Not Cross).

Each phase item names exact reference locations.

---

**Section 7 — Final Verdict**

Blunt judgment. Best 3 to steal/adapt (with locations). Worst 3 to avoid (with locations). Reference classification: critical / supporting / inspiration-only / ignore. Recommended next action.

---

**Section 8 — Project Synthesis**

The generative section. Ask: what novel patterns become possible only by combining this reference's approaches with the current project's specific capabilities? Do not summarize what the reference does — that is Sections 1–7. Generate ideas that require both inputs.

For each synthesis idea: What / Reference contribution / Project contribution / Target (exact file) / Gap closed.

Aim for 2–5 ideas. Zero is valid if there is no meaningful intersection — say so explicitly. Every synthesis idea that emerges here must appear in Tier 6 of Phase 2 (ref-plan).

---

**Section 9 — Expansion Opportunities**

The growth section. Ask a different question from Section 8: what can this reference do that the project **cannot do at all**? Not adaptation — net-new capability that would require building something from scratch. Section 8 finds synthesis. Section 9 finds growth.

An expansion opportunity has zero existing hook point in the project: no module, no script, no skeleton. Adapting a pattern into an existing file is Tier 1–3. Building something the project has never had is Tier 7.

**Per-skill growth scan (run this before writing the section):** For every significant skill or component in the reference, ask one binary question: "Does the project have an equivalent capability? If no — is this a Tier 7 candidate?" Do not rely only on obvious architectural gaps. Production-hardened implementations (document format skills, communication templates, testing infrastructure, visual output tools) are Tier 7 candidates even when their primary domain differs from the project domain. This scan is what separates a thorough Section 9 from a superficial one. A reference with 17 skills that yields only 2 expansion candidates has likely under-scanned.

For each expansion opportunity: Capability / Reference location / Why the project lacks it / What it would unlock / Dependencies / Effort signal (`days`/`weeks`/`months`) / Tier 7 candidate (Yes/No).

**Gateway bundling signal:** After listing expansion opportunities, check for thematic clusters. When two or more Tier 7 items share a common output layer (e.g., all produce document formats; all produce visual artifacts), ask whether they should be implemented as a single gateway module rather than separate Tier 7 items. A gateway: reduces the integration surface, applies shared quality gates once, and is summoned by multiple calling skills rather than requiring each caller to manage format-specific dependencies. Note the bundling recommendation explicitly in the Tier 7 table.

Zero is a valid answer for individual items. Every item marked "Tier 7 candidate: Yes" must appear in Tier 7 of Phase 2 (ref-plan) and receive a memory drawer.

---

### Write Memory drawers for durable findings

Write one drawer per significant finding worth preserving. Delegate to `drawer-writer.py` — do not construct drawer JSON inline.

```bash
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "<OBSERVATION_TYPE>: <finding>" \
  --wing references \
  --room <reference-slug> \
  --evidence "<finding text; include trust_level>" \
  --confidence <0.0-1.0> \
  --staleness-state FRESH \
  --source "<reference file path or slug>" \
  --source-module ref-adopt \
  --actor ref-adopt
```

Use `--evidence-file <path>` when evidence is multi-line. ID and output path are auto-derived.

### Gate A — Verdict check

If verdict is `ignore`: write the ref-eval receipt, surface the verdict, stop. Do not proceed.

### Write Phase 1 report and receipt

**Report:** `research/ref-eval/<slug>.md`

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type ref-eval \
  --task-id <task-id> --session-id <session-id> \
  --status PASS --target <reference-slug> \
  --summary "<verdict>" --confidence <0.0-1.0> \
  --out .wabblespec/state/receipts/ref-eval-<timestamp>.json
```

---

## Phase 2 — Plan the Integration

### Extract integration signal

From the ref-eval report:
- Section 2 (Benefits): all High and Medium impact items
- Section 6 (Extraction Plan): Phases 1 and 2 items
- Low-impact Section 2 items directly relevant to the current project goal

Candidate table:

| ID | Item | Type | Ref-eval impact | Project fit | Risk |
|---|---|---|---|---|---|

Project fit: High = directly serves active goal. Low = interesting but orthogonal.

### Apply exclusion filter

Explicitly exclude with reason:
- All ref-eval Section 4 "Avoid" items
- All `do_not_copy` items
- Risk=High AND Project fit=Low
- Items conflicting with non-goals in task-card.md, scope.md, or CLAUDE.md

Exclusion List is a hard stop. To reconsider an excluded item, run a new ref-eval.

### Score and rank

```
integration_score = (impact × 2) + project_fit - risk
```

Map: High=3, Medium=2, Low=1. Sort descending. Tiebreak: lower risk first, then higher fit.

### Assign tiers

Tiers describe what kind of change an item is — additive rule vs. new module vs. architecture vs. synthesis.

**Tier 1 — Behavioral additions**: Additive to an existing file; no new files created. Target must be an exact file path.

**Tier 2 — Module-level augmentation**: Substantive extension of an existing module.

**Tier 3 — New shared infrastructure**: New reference file, schema, or shared script serving multiple modules.

**Tier 4 — New module candidates**: Entirely new skill, hook, or daemon.

**Tier 5 — Architecture-level**: Cross-cutting changes. Requires adversarial review before Specify. User confirms each.

**Tier 6 — Synthesis**: Novel patterns that require both the reference's logic AND the current project's infrastructure. Every Section 8 idea from Phase 1 must appear here. Treat as Tier 5 risk until a prototype validates.

**Tier 7 — Expansion Roadmap**: Net-new capabilities sourced from Section 9. Not implemented during this pipeline. Each item gets: What / Reference location / Why the project lacks it / What it would unlock / Dependencies / Effort signal / Session seed. Produce an Expansion Roadmap table grouped by effort (days / weeks / months). Every "Tier 7 candidate: Yes" from Section 9 must appear here and receive a memory drawer.

**Watch Only**: Unclear fit, unresolved dependencies, or dependent on Tier 5/6 completion.

Include a **Do-Not-Copy list** (items from ref-eval "Avoid" with their invariant reason) and a **Priority Implementation Order** table (Tier 1–4 items ordered with `Why first`).

### Write integration plan

**Plan:** `research/ref-plan/<slug>.md`

Each Phase 1/2 item includes: What, Where, How (specific enough to act on without re-reading ref-eval), Gate (becomes a ref-comp checkpoint), Reference location. Phase 2 adds: Specify required, Breaking change risk. Phase 3 adds: Adversarial review required, Promotion condition. Phase 4 adds: Why deferred, Promote when.

Include Execution Notes: dependencies, sequencing constraints, items that must not run in parallel.

### Write Phase 2 receipt

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type ref-plan \
  --task-id <task-id> --session-id <session-id> \
  --status PASS --target <reference-slug> \
  --requirements "<adopted-item-1>" "<adopted-item-2>" \
  --out .wabblespec/state/receipts/ref-plan-<timestamp>.json
```

---

## Gate B — Implementation Preview

Before implementing, present two lists to the user:

**List 1 — Tier 1–2 items for immediate implementation:**
- Item name, target file/area, one-line How summary, Gate condition

**List 2 — Expansion Preview (Tier 7):**
- For each Tier 7 item: capability name, effort signal, one-line session seed
- These are NOT implemented now. Surface them so the user sees what bigger opportunities were identified before the pipeline moves to implementation.
- Frame as: "Beyond what I'm about to implement, this reference identified N expansion opportunities for future sessions."

If `autonomous: true`: proceed automatically on both lists (Tier 1–2 only; Tier 7 is always documentation-only).
If `autonomous: false` (default): pause and wait for confirmation. Allow selective deselection of Tier 1–2 items. Tier 7 items require no user action — they are automatically written as memory drawers.

---

## Phase 3 — Implement Tier 1–2 Items

For each confirmed Tier 1–2 item, in Priority table order:

1. **Read the reference location** cited by ref-plan (exact file + section)
2. **Read the target location** in the current project (the `Target` field)
3. **Apply the change** per the `How` field using Read/Edit/Write tools directly
4. **Encode literal values** — if the item has `Literal values` in ref-plan, verify those exact values appear in the implementation. Do not approximate. Do not paraphrase. Quote or reproduce them exactly.
5. **Sync engine module** — if the target was a `.claude/skills/<name>/SKILL.md` file, check whether a matching canonical source exists at `.wabblespec/engine/modules/<layer>/<name>/SKILL.md`. If it does, apply the identical edit to the engine module file immediately after applying it to the `.claude/skills/` copy. The sync script (`wabblespec-sync-skills.py`) overwrites `.claude/skills/` from `engine/modules/` on every sync — changes written only to `.claude/skills/` will be lost on the next run. To locate the engine path: `glob.glob('.wabblespec/engine/modules/**/<name>/SKILL.md', recursive=True)`.
6. **Verify** against the `Gate` condition before proceeding to the next item

If a Gate condition fails: mark the item `PARTIAL`, record the gap, continue with remaining items. Do not abort the pipeline on a single partial.

If an item would embed a vendor name (I6): skip it, record as `SKIPPED`, continue.

Track per-item status: `IMPLEMENTED`, `PARTIAL`, `SKIPPED`.

---

## Phase 4 — Audit the Implementation

### Map what was actually built

Read every file targeted in Phase 3 fully. Do not assume — verify. For each targeted file, note: what was added, what was changed, and where each `Literal values` item from Phase 2 appears in the current implementation.

Run the **literal fidelity pre-check** first (before the seven-section audit): for every item that had `Literal values` in Phase 2, verify Exact / Adapted / Corrupted / Absent status. Corrupted and Absent items escalate into Section 2 as Wrong value or Absent literal gap types.

### Seven-section audit

Every finding names exact locations in both the current project and the reference.

---

**Section 1 — Implementation Coverage**

For every Phase 1 (and optionally Phase 2) item, declare: Implemented / Partial / Missed / Deferred. Do not mark Phase 3/4 items as Missed.

---

**Section 2 — Execution Gaps**

For each Missed or Partial item:

| Item | What was planned | What was built | Gap | Impact | Severity | Recoverable |
|---|---|---|---|---|---|---|

Order by Severity descending. Severity: Critical = breaks integration goal. Major = degrades important functionality. Minor = quality-of-life only.

---

**Section 3 — Improvements Beyond the Plan**

| Feature | Reference approach | Our implementation | Why ours is better | Risk it introduces |
|---|---|---|---|---|

Mark "protect" on items that future integration could threaten.

---

**Section 4 — Architecture Divergence**

| Dimension | Reference design | Our implementation | Intentional? | Consequence |
|---|---|---|---|---|

Flag unintentional divergences not in the exclusion list.

---

**Section 5 — Quality Delta**

| Dimension | Reference (1–10) | Ours (1–10) | Delta | Notes |
|---|---|---|---|---|
| Test coverage | | | | |
| Error handling | | | | |
| Documentation | | | | |
| Naming clarity | | | | |
| Dependency hygiene | | | | |

Explain any delta of ±3 or greater with a specific example.

---

**Section 6 — Verdict**

- Coverage rate: N of M planned items (%)
- Gap counts: N critical, M major, P minor
- Improvements beyond plan: N
- Execution classification: `complete` / `substantially-complete` / `partially-complete` / `significantly-incomplete`
- Top 3 gaps to close (severity + location)
- Top 3 wins to protect (location)
- Recommended next action: complete/substantially-complete = Archive; partially-complete = follow-up wave; significantly-incomplete = re-evaluate ref-plan

---

**Section 7 — Synthesis Coverage**

Audit each Tier 6 item from Phase 2 (ref-plan) explicitly. These are the highest-value output of the pipeline and the most commonly skipped.

| Synthesis Idea | Status | Our Location | Notes |
|---|---|---|---|

Status: Implemented / Partial / Missed / Deferred. For Missed or Partial: state which half of the synthesis is absent (reference contribution or project contribution).

---

**Section 8 — Expansion Handoff Audit**

Tier 7 items are NOT implemented — they are handed off. This section confirms the handoff was clean.

For each Tier 7 item from Phase 2:

| Capability | Drawer written | Session seed present | Status |
|---|---|---|---|

Status: **Handed off** (drawer + seed exist) / **Partial handoff** (one missing) / **Dropped** (absent from ref-plan despite Section 9 candidate flag).

For each Dropped item: identify which Section 9 entry was lost and write the missing drawer now before closing.

If ref-plan had no Tier 7 items: state "No expansion opportunities identified" explicitly — do not leave this section blank.

---

### Write Memory drawers for gaps and wins

Critical or Major gaps and protected wins go in wing `references`, room `<slug>-comp`. Delegate to `drawer-writer.py` — do not construct drawer JSON inline.

```bash
# Gap drawer
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "OPEN_THREAD: gap: <feature>" \
  --wing references \
  --room <slug>-comp \
  --evidence "gap_severity: Critical|Major; feature: <name>; recoverable: true|false; detail: <description>" \
  --confidence 0.9 \
  --staleness-state FRESH \
  --source "<reference slug>" \
  --source-module ref-adopt \
  --actor ref-adopt

# Win drawer
python .wabblespec/engine/shared/scripts/drawer-writer.py \
  --topic "WORKING_SOLUTION: win: <feature>" \
  --wing references \
  --room <slug>-comp \
  --evidence "type: win; detail: <description>" \
  --confidence 0.9 \
  --staleness-state FRESH \
  --source "<reference slug>" \
  --source-module ref-adopt \
  --actor ref-adopt
```

### Write Phase 4 report and receipt

**Report:** `research/ref-comp/<reference-slug>.md`

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type ref-comp \
  --task-id <task-id> --session-id <session-id> \
  --status PASS --target <reference-slug> \
  --summary "<execution-classification>" \
  --confidence <coverage-rate-0.0-1.0> \
  --out .wabblespec/state/receipts/ref-comp-<timestamp>.json
```

---

## Output Contract

| Artifact | Path | Required |
|---|---|---|
| Evaluation report | `research/ref-eval/<slug>.md` | Yes |
| Integration plan | `research/ref-plan/<slug>.md` | Yes (unless Gate A stops) |
| Audit report | `research/ref-comp/<slug>.md` | Yes (unless Gate A stops) |
| Receipts (3) | `.wabblespec/state/receipts/ref-{eval,plan,comp}-<ts>.json` | Yes |
| Memory drawers | `.wabblespec/state/memory/wings/references/rooms/<slug>/` | When findings worth preserving exist |

---

## Common Failure Modes

1. **Skipping ReferenceLoad.** It is the bounded intake gate with trust rating and provenance. Reading raw files directly produces an unbounded context dump.

2. **Categorizing by directory instead of by content.** Marking `docs/`, `guides/`, or non-primary skill files as "out of scope" at the directory level without reading them produces an incomplete inventory. Design theory, behavioral heuristics, evaluation frameworks, anti-pattern catalogs, and vocabulary tables frequently live in documentation and secondary skill files. Every such file must appear in the inventory and be skimmed for transferable content before being marked Skipped.

3. **Closing early on a low usefulness score.** An "inspiration-only" verdict covers the reference as a deployable system — it does not reduce the requirement to complete all nine sections. Low-scoring references often yield their most distinctive value in Sections 8 (synthesis) and 9 (expansion). Finding the main implementation wins and closing while files remain unread is underfitting.

4. **Extracting only one dimension.** Every reference has behavior, format, and interaction patterns. A ref-eval that only surfaces structural format missed the behavioral logic and the cross-file interaction contracts — which are often where the real value lives.

5. **Skipping Section 8.** The synthesis section is the most distinctive output of ref-eval. If Section 8 is empty, either the reference truly has no intersection with this project (state that explicitly) or the evaluation did not go deep enough.

6. **Vague Target.** "The executor skill" is not a target. `skills/executor/SKILL.md` is. Every integration item must name the exact file.

7. **Vague How descriptions.** "Adopt the routing pattern" is not a How. "Add a `## Deviation Rules` section to `skills/executor/SKILL.md` with four trigger/action rules" is a How.

8. **Implementing before Gate B.** Always surface Tier 1–4 items for review unless `autonomous: true`. Implementation is irreversible.

9. **Marking Tier 5/6 Watch-Only items as Missed.** Those are Deferred. Conflating them inflates severity counts.

10. **Dropping Tier 6 items in Phase 4.** Synthesis ideas are the hardest to implement and easiest to skip. Section 7 of the audit exists specifically to catch this.

11. **Skipping Section 9.** The expansion section is what makes the pipeline useful for growth, not just pattern transfer. A ref-eval with no Section 9 has answered "what can we adapt?" but not "what could we build?" If the reference has no net-new capabilities for the project, say so explicitly — do not leave Section 9 blank.

12. **Conflating Tier 7 with Tier 4.** Tier 4 = new module that fits in the current integration cycle. Tier 7 = net-new capability that needs its own recipe session. Assigning an expansion item to Tier 4 causes it to be "planned" without the spec card it actually needs.

13. **Writing to `.claude/skills/` without updating the engine module.** The sync script (`wabblespec-sync-skills.py`) overwrites `.claude/skills/` from `.wabblespec/engine/modules/` on every sync. Any edit applied only to `.claude/skills/<name>/SKILL.md` will be silently lost. Phase 3 Step 5 requires checking for and updating the matching `engine/modules/` file immediately after every `.claude/skills/` edit.

14. **Writing drawer JSON via Write tool instead of `drawer-writer.py`.** The drawer schema has 11 required fields including a `provenance` array and a derived ID. Inline construction produces off-schema JSON, missing fields, and IDs that don't match the auto-derivation pattern. All drawer writes must call `drawer-writer.py` — see `engine/shared/references/script-delegation-contract.md` operation #9.

15. **Treating production-hardened implementations as non-transferable domain noise.** A skill that implements docx/pdf/xlsx/pptx production patterns contains non-obvious gotchas (unit systems, dual-width requirements, formula-recalculation sequences, subscript encoding rules) that the project would have to rediscover independently. Before marking any implementation-heavy skill as "domain-specific, skip," ask: "Could the project implement this capability natively using this skill as a production guide?" That question determines Tier (1–3 = adapt existing module, Tier 7 = build net-new capability). If Tier 7 and multiple similar items exist (all document formats, all visual output tools), flag them for gateway bundling rather than listing each as a separate session. An initial Section 9 that yields only 2 items for a 17-skill reference is a signal the per-skill growth scan was not run.
