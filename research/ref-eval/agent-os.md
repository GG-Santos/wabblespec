# Ref-Eval: agent-os Integration Evaluation

**Reference:** agent-os (v3.0)
**Session:** agent-creator-integration-20260529
**Evaluated:** 2026-05-30
**Author:** Brian Casel / Builder Methods

---

## File Inventory

| Path | Purpose | Size | Key Contents | Status |
|---|---|---|---|---|
| README.md | Project overview | Small | 4 capabilities, install pointer | Read |
| commands/agent-os/discover-standards.md | Slash command | Medium | 6-step codebase→standards workflow; ask-why pattern | Read |
| commands/agent-os/inject-standards.md | Slash command | Medium | Auto-suggest/explicit modes; 3-scenario context detection | Read |
| commands/agent-os/index-standards.md | Slash command | Medium | Scan→diff→ask descriptions→write index.yml | Read |
| commands/agent-os/plan-product.md | Slash command | Medium | mission/roadmap/tech-stack product doc generation | Read |
| commands/agent-os/shape-spec.md | Slash command | Medium | Plan-mode spec shaping; Task 1 invariant; YYYY-MM-DD-HHMM folder | Read |
| CHANGELOG.md | Version history | Large (31KB) | v3.0 retired orchestration/implementation phases | Read (partial) |
| scripts/common-functions.sh | Shared shell utils | Medium | Profile inheritance chain; circular dep detection | Read |
| scripts/project-install.sh | Install script | Large | --profile/--commands-only/--verbose; project install | Read (partial) |
| scripts/sync-to-profile.sh | Sync script | Large | Syncs project standards back to base profile | Skipped — not applicable |
| profiles/default/global/tech-stack.md | Default tech stack | Small | React/TS/Tailwind/Node/PostgreSQL example | Read |
| config.yml | Config | Tiny | version: 3.0, default_profile, profile inheritance | Read |
| .github/* | GitHub templates | Various | PR template, stale workflow, code of conduct | Skipped |

## Connection Map

```
discover-standards --writes-to--> agent-os/standards/{folder}/{file}.md
discover-standards --writes-to--> agent-os/standards/index.yml
index-standards --reads/writes--> agent-os/standards/index.yml
inject-standards --reads--> agent-os/standards/index.yml --reads--> individual standard files
plan-product --reads--> agent-os/standards/global/tech-stack.md (conditional)
plan-product --writes--> agent-os/product/{mission,roadmap,tech-stack}.md
shape-spec --reads--> agent-os/product/ --reads--> agent-os/standards/index.yml
shape-spec --writes--> agent-os/specs/YYYY-MM-DD-HHMM-{slug}/{plan,shape,standards,references}.md
project-install.sh --reads--> config.yml --calls--> common-functions.sh
project-install.sh --resolves--> profile chain --copies--> commands + profiles to project
```

What breaks downstream if interface changes:
- `index.yml` format change → inject-standards cannot parse suggestions
- `agent-os/product/` path change → shape-spec skips Step 4 (product context)
- Profile directory structure change → install scripts fail at chain resolution

---

## Section 1 — Reference Summary

**Type:** Product-space standards management framework for AI-assisted software development. Active, versioned (v3.0 released 2026-01-20), real-world usage (commercial product with subscribers).

**Problem it solves:** Keeping AI coding agents aligned to project conventions. Without standards, agents repeatedly guess at patterns that the team has already settled. With standards, each session can inject the relevant rules without the developer re-explaining them.

**Behavioral content:** Five slash commands encoding specific workflows — discover, inject, index, plan-product, shape-spec. Each command defines exact step sequences, decision branches, interaction patterns (AskUserQuestion tool required everywhere), and output schemas. The "ask why before drafting" protocol in discover-standards is the most distinctive behavioral content.

**Structural content:** Two-level YAML index (folder → file → description). Spec folder output bundle (plan.md + shape.md + standards.md + references.md). Product docs (mission/roadmap/tech-stack). Profile inheritance defined in central config.yml.

**Interaction content:** inject-standards is called internally by shape-spec. plan-product output is consumed by shape-spec. index.yml is the shared state across discover, index, and inject. Profile chain resolved by project-install.sh via common-functions.sh.

**Maturity signals:** Commercial product, versioned releases, changelog with bug fix references (#327, #328), POSIX compatibility fixes — evidence of real-world use and iteration. No automated tests in the repo.

**What's unclear:** No tests for command logic. v3.0 specifically retired orchestration/task breakdown that earlier versions handled — this is deliberate simplification, not abandonment.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| discover-standards.md Step 3 | "Ask why before drafting" probe questions: "What problem does this pattern solve?", "Are there exceptions?", "What's the most common mistake?" | These probes are specifically designed to elicit the non-obvious rationale that agents need — not what the pattern is, but why it exists and when it breaks | Add as standard elicitation probes to WabbleSpec's interview or ground SKILL.md | Low |
| shape-spec.md Step 6-7 | Spec folder artifact bundle: plan.md + shape.md (decisions/context) + references.md (studied code + key patterns) | WabbleSpec has task-card.md and scope.md but no `shape.md` capturing decisions made during scoping, and no `references.md` capturing what internal code was studied and what patterns were extracted | Tier 7 expansion: extend task-card-writer.py to optionally generate a shape-md artifact capturing scoping decisions and internal code references | Low |
| shape-spec.md Step 7 | "Task 1 always = Save Spec Documentation" invariant | Ensures spec artifacts are persisted before implementation begins — aligns with I10's anti-implied-completion stance | Inspiration only — WabbleSpec enforces this via receipt chain (Research → Plan → Execution), not task ordering | Low |
| inject-standards.md Step 1 | Three-scenario context detection (Conversation / Skill / Plan) before formatting injection | Allows smarter formatting decisions based on use context | Inspiration only — WabbleSpec handles this via recipe/preloading, not dynamic injection | Low |
| index-standards.md Step 6 | index.yml format: folder → file-name → description, alphabetized, no .md in keys, one-line descriptions | Clean, matchable index format | WabbleSpec's wabblespec.yaml is the module registry equivalent and already structured; no adaptation needed | Low |
| common-functions.sh get_profile_inheritance_chain | Circular dependency detection with `CIRCULAR:{path}` error prefix | Clear error messaging for circular config | Not applicable — WabbleSpec has no profile inheritance | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| All commands | AskUserQuestion tool dependency | Every command requires this tool; WabbleSpec does not use AskUserQuestion in its command model — patterns cannot be ported directly | Treat as behavioral pattern only; strip tool dependency | Low |
| commands/*, scripts/* | Product-space design (I11) | Agent-OS manages standards in `agent-os/standards/` in the project root — this is product space. WabbleSpec's I11 hard-blocks framework modules from writing product-space paths | No adaptation crosses the framework/product boundary | Medium |
| CHANGELOG.md | v3.0 retired what v2 did | Orchestration/task breakdown phases were retired because "frontier models handle this well on their own now" — this is a philosophical claim that contradicts WabbleSpec's spec-first, receipt-gated model | Recognize: agent-OS and WabbleSpec have fundamentally opposite positions on AI orchestration autonomy | Medium |
| shape-spec.md | Requires plan mode as prerequisite | WabbleSpec's workflow doesn't have a "plan mode" concept — shape-spec's hard gate is not portable | Inspiration only | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Decision | Reason | Target Area | Priority |
|---|---|---|---|---|
| "Ask why" probe questions (discover Step 3) | Study Only | Potentially useful for interview/ground SKILL.md but requires reading those skills first; active task doesn't include them | interview or ground SKILL.md | Low |
| Spec folder artifact bundle (shape.md + references.md) | Study Only | Tier 7 expansion candidate; not implementable without new scripts | task-card-writer.py future extension | Low |
| Task 1 = save docs invariant | Avoid | Already covered by WabbleSpec's receipt chain (Research → Plan phase receipts are the equivalent) | — | — |
| index.yml format | Avoid | wabblespec.yaml already serves the module registry function | — | — |
| Three-scenario injection detection | Avoid | WabbleSpec's recipe+preloading approach is more structured | — | — |
| AskUserQuestion tool pattern | Avoid | WabbleSpec does not use this tool in its command model | — | — |
| Profile inheritance + install scripts | Avoid | Architecture mismatch; not applicable | — | — |
| Standards management ecosystem (agent-os/standards/) | Avoid | I11: product-space writes are excluded from framework modules | — | — |
| "Retire orchestration to frontier models" philosophy | Avoid | I1 hard-blocks this: every execution must be spec-grounded | — | — |
| "root" keyword for top-level standards | Avoid | No analogous routing problem in WabbleSpec | — | — |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 3 | Agent-OS is product-space standards management; WabbleSpec is framework-space orchestration; different layers |
| Architecture fit | 2 | Agent-OS assumes agent-driven standards file writes into project root; WabbleSpec's I11 blocks product-space writes from framework modules |
| Implementation fit | 3 | Command structure (slash commands with 5-9 steps) is similar; but AskUserQuestion dependency, plan mode requirement, and file-path conventions are all incompatible |
| Maintenance fit | 4 | Both are markdown-based slash command specs; agent-OS's concise standards writing discipline is good practice that WabbleSpec already follows |
| Risk level | 2 | The only real risk is importing product-space patterns into framework space — easily avoided by treating this as inspiration-only |
| Overall usefulness | 4 | Inspiration-only. The behavioral patterns are not wrong — they're just aimed at a fundamentally different problem (project standards injection) than WabbleSpec's concern (spec-gated execution with receipts) |

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning):**
- Read discover-standards.md "ask why" probe questions as inspiration for WabbleSpec's elicitation patterns in interview/ground SKILL.md (when those skills are next revised)

**Phase 2 (Low-Risk Adaptation):**
- None: the low-scoring items do not clear the Tier 1 bar given active task mismatch

**Phase 3 (Deeper Integration):**
- None: architecture mismatch prevents deeper integration

**Phase 4 (Do Not Cross):**
- agent-os/standards/ file system: I11 boundary
- Retiring orchestration to frontier models: I1 violation
- AskUserQuestion as command interaction model: WabbleSpec does not use this tool

---

## Section 7 — Final Verdict

**Reference classification: inspiration-only (4/10)**

**Best 3 to study (with locations):**
1. "Ask why before drafting" probe questions — discover-standards.md Step 3: "What problem does this pattern solve? Why not the default? What's the most common mistake?" These probes elicit exactly the non-obvious rationale that makes a standard useful vs. obvious. Worth having in WabbleSpec's elicitation arsenal.
2. Spec artifact bundle structure — shape-spec.md Step 7: plan.md + shape.md (decisions/context) + references.md (code studied + key patterns). WabbleSpec lacks an analog for capturing "what existing code was studied during shaping and what patterns were extracted." This gap is real.
3. Concise standards writing discipline — discover-standards.md "Writing Concise Standards" section: lead with rule, code examples, skip obvious, one concept per file, bullet points over paragraphs. Good craft discipline that aligns with WabbleSpec's SKILL.md authoring conventions.

**Worst 3 to avoid (with locations):**
1. "Retire orchestration to frontier models" — CHANGELOG.md v3.0 rationale: violates I1 (spec-first); frontier models handling orchestration on their own is exactly what WabbleSpec's receipt-gated model prevents.
2. Product-space standards directory — all commands writing to `agent-os/standards/`: I11 boundary; framework modules cannot write project-space paths.
3. AskUserQuestion tool dependency — all commands: WabbleSpec's interaction model doesn't include this tool; patterns cannot be ported directly.

**Recommended next action:** Proceed (Gate A: not `ignore`). Write ref-plan with Tier 7 expansion items only. No Tier 1-2 items clear the bar for immediate implementation.

---

## Section 8 — Project Synthesis

Both systems process specifications and produce structured outputs. The meaningful intersection is narrow:

**S1 — Internal reference capture during Executor codebase exploration**

What: When Executor explores existing code to understand patterns before implementing, that research is currently lost (not captured in any artifact). Agent-OS's references.md (from shape-spec) captures this: for each studied code section, record Location, Relevance, and Key patterns.

Reference contribution: references.md schema (Location / Relevance / Key patterns per studied code section) + the practice of making research output a first-class artifact before implementation begins.

Project contribution: Executor SKILL.md already has wave-plan-based research steps; session-registry.py already creates per-session directories.

Target: `.wabblespec/engine/shared/scripts/research-artifact-writer.py` (new) + `engine/modules/l5/executor/SKILL.md` (additive wave step)

Gap closed: Currently, Executor research during a wave is ephemeral. A research artifact would preserve what was studied and what patterns were extracted, preventing re-exploration in later waves.

**S2 — Spec shape artifact for scoping decisions**

What: When scoping a task, decisions are made (why not X, constraint Y forced choice Z) that are currently captured only in task-card assumptions and commit trailers. Agent-OS's shape.md explicitly captures: Scope, Decisions (list), Context (visuals/references/product alignment), Standards Applied.

Reference contribution: shape.md schema; the practice of separating "shaping decisions" from "spec requirements."

Project contribution: task-card-writer.py already writes task-card.md; scope-writer.py already writes scope.md.

Target: `task-card-writer.py` (extend with optional `--shape-notes` flag) or a new `shape-writer.py` in shared/scripts/.

Gap closed: Decisions made during spec shaping are currently recoverable only from commit messages or receipts. A shape artifact would make them browsable alongside the task card.

---

## Section 9 — Expansion Opportunities

**E1 — Internal reference capture artifact**

| Field | Value |
|---|---|
| Capability | Per-wave artifact recording which existing code was studied, why it's relevant, and what patterns were extracted |
| Reference location | shape-spec.md — references.md schema (Location / Relevance / Key patterns) |
| Why the project lacks it | Executor research is ephemeral; wave receipts record decisions but not the studied inputs that informed them |
| What it would unlock | Future waves on the same task could load the references artifact instead of re-exploring; prevents pattern drift across waves |
| Dependencies | session-registry.py, Executor SKILL.md, a new research-artifact-writer.py script |
| Effort | days |
| Tier 7 candidate | Yes |

**E2 — Spec shape artifact for scoping decisions**

| Field | Value |
|---|---|
| Capability | A shape.md artifact capturing decisions made during task scoping: what was considered, what was rejected, what constraints forced the choices |
| Reference location | shape-spec.md — shape.md schema (Scope / Decisions / Context / Standards Applied) |
| Why the project lacks it | task-card.md captures requirements; scope.md captures boundaries; neither captures the reasoning behind those choices in a browsable form |
| What it would unlock | Faster task resumption after compaction; prevents re-litigating scoping decisions mid-execution; useful input for Adversary (spec challenge) |
| Dependencies | task-card-writer.py or new shape-writer.py; no new infra required beyond a new script |
| Effort | days |
| Tier 7 candidate | Yes |
