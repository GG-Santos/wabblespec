---
description: Route a freeform task description to the right WabbleSpec skill with concrete next steps.
argument-hint: <freeform task description>
---

You are routing a WabbleSpec task to the right skill. The user's task is below.

User task:
$ARGUMENTS

Do this in order:

1. **Classify the task.** Identify the primary domain from the taxonomy below. Note any cross-cutting concerns.

2. **Pick the skill (or two).** Name the single best skill. If a second skill would meaningfully help as a hand-off, name it. Never list more than two.

3. **State the assumed context.** One sentence: what session state is assumed (open task, locked spec, no active session, etc.) and any constraints visible in the request. If critical context is missing, ask one direct question.

4. **Give 3–5 concrete next steps.** Real invocations the user can run — `/recipe`, `/specify`, `/executor`, `python .wabblespec/engine/shared/scripts/<script>.py`, or a file path to read. Not methodology paragraphs. Not "consider running X" — just the command or slash invocation.

5. **Note one thing to watch for.** One sentence covering a common pitfall, invariant to check, or signal that this task has more complexity than it appears.

---

Skill catalog by domain:

**Plan / Spec**
- recipe — entry gate; identifies build target and complexity; run first for every new task
- scope-frame — declares session boundaries and assumptions before spec work
- specify — produces task card with goal, non-goals, assumptions, GWT criteria
- blueprint — high-level architectural design before decompose
- brainstorm — divergent option generation before specify when solution space is open
- decompose — breaks locked task card into ordered wave plan

**Execute**
- executor — wave execution engine; runs Guard → implement → Verify per wave
- rollback — reverts to prior checkpoint after HARD failure
- wave-fix — diagnoses and repairs a failed wave
- wave-refine — improves wave output without triggering a full REVISE cycle
- wave-review — reviews pending wave diffs async; surfaces quality findings

**Review / Validate**
- guard — pre-wave invariant enforcement; checks I1/I2/I3/I6/I9/I10/I11/I12
- verifier — post-wave quality gate; issues PASS/FAIL/BLOCKED with receipts
- adversary — generates the strongest honest case against an artifact or decision
- reviewer — issues ACCEPT/REVISE/REJECT on wave output
- grader — scores output against declared criteria
- inference-guard — validates inference-time safety before high-stakes execution

**Memory / Knowledge**
- memory — read/write framework memory drawers
- dream — EMA decay + gap-map update; runs on stop hook
- entity-graph — updates the entity relationship graph
- memory-mine — indexes closet drawers; runs at 50+ drawers
- ground — grounds claims against evidence before committing to a decision

**Evolve / Improve**
- instinct — extracts behavioral patterns from seed run receipts
- synth — synthesizes instinct observations into reusable rules
- augment — applies synthesized rules to skill modules
- benchmark — measures skill performance with variance analysis
- forge — promotes augmented module after benchmark PASS
- skill-tdd — test-driven skill authoring and refinement
- skill-creator — creates or improves skills from scratch

**Reference / Research**
- ref-eval — evaluates a reference across behavior/format/interaction dimensions
- ref-plan — builds phased integration plan from ref-eval
- ref-adopt — full eval → plan → implement → audit pipeline in one invocation
- ref-comp — audits implementation fidelity against ref-plan
- research-log — logs research findings to a structured drawer
- reference-load — loads and trust-rates a reference for use in the session

**Archive / Release**
- archive — aggregates receipts into delivery receipt, bumps version, writes changelog
- changelog — writes or updates CHANGELOG.md entries
- release — prepares a versioned release artifact
- commit — creates a git commit with structured decision trailers

**Analyze / Report**
- analyze — deep analysis of an artifact or codebase area
- report — produces a structured report from findings
- audit — systematic audit of a module or subsystem
- document — writes or updates module documentation

**Platform / Scaffold**
- scaffold — generates project scaffolding for a declared platform
- platform-web / platform-cli / platform-api-service / platform-library / platform-mobile / platform-desktop — platform-specific build skills
- deps — manages dependency declarations and lockfiles

**Meta / Session**
- autopilot — full lifecycle meta-orchestrator; scale-adaptive L0-L4 autonomy
- recipe — always the entry gate; if unsure what to run first, run this
- watzup — session state summary; what is in flight, what is blocked, what is next
- economy — budget-aware execution; flags when a task exceeds token thresholds
- clean — removes stale artifacts, orphaned receipts, and temp files

---

Output format:

```
**Primary skill**: <name>
**Hand-off to (if any)**: <name or "none">

**Assumed context**: <one sentence>

**Next steps**:
1. <slash command or script invocation>
2. <slash command or script invocation>
3. <slash command or script invocation>

**Watch for**: <one sentence>
```

If the user's task would violate a WabbleSpec invariant (e.g., executing without a spec when I1 is active, writing to .wabblespec/ from product space), say so directly and name which invariant. Do not route to execution skills when the spec gate is not met.
