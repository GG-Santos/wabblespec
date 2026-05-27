---
name: skill-writing-contract
description: Six output quality patterns and seven named regression checks for writing WabbleSpec module SKILL.md files. Used by module-auditor and the quality floor sweep.
---

# Skill Writing Contract

WabbleSpec module SKILL.md files are fixed prefixes on every invocation of
that module. The question to ask when writing one is not "does this section
read well" but "what will the agent produce when it reads this and is asked
to do the work?" A verbose, abstract, or ambiguous SKILL.md produces a
verbose, abstract, or ambiguous agent.

This reference defines the six output quality patterns and seven named
regression checks. The module auditor (`.wabblespec/engine/shared/agents/module-auditor.md`)
uses this reference as its scoring rubric. The quality floor check
(`.wabblespec/engine/shared/scripts/quality-floor-check.py`) enforces Gate 1 and Gate 2;
this reference governs the deeper pattern quality above the floor.

---

## The Six Output Quality Patterns

### Pattern 1 — Concrete examples beat abstract rules

When you write a rule, pair it with an input → output example. The agent
copies the pattern, not the rule. An example that shows only the output side
("e.g., a high-confidence receipt") is not an example — it is a description.

**Bad:** "Write a receipt with all required fields populated."

**Good:** "The receipt must include a `confidence` field (float 0.0–1.0)
and a `reason` string. Example:
```
confidence: 0.72
reason: "build target inferred from package.json; no explicit spec file found"
```
If confidence < 0.8, also set `needs_reverification: true`."

**Discriminator:** can you name a wrong output that still follows the rule?
If yes, the rule needs an example.

---

### Pattern 2 — Theory-of-mind framing beats command framing

Explain the why. A rule tells the agent what to check. Framing tells it why
the check matters, so it generalizes to cases you didn't anticipate.

**Bad:** "ALWAYS write the receipt before returning."

**Good:** "The receipt is proof the module ran — not just that it was
invoked. Without it, the next phase has no evidence to read from. If
anything interrupts execution, write a partial receipt with
`status: interrupted` rather than no receipt at all."

**Yellow flag:** if you find yourself writing ALWAYS or NEVER in caps, the
instruction is a command. Reframe it as reasoning.

---

### Pattern 3 — Named failure modes beat generic warnings

Name the failure, name the detection signal, name the fix. Generic warnings
("be careful," "handle edge cases") produce no behavioral change at
invocation time.

**Bad:** "Be careful when the spec is incomplete."

**Good:** "**Spec underspecification** — the agent produces a receipt with
plausible field values but no upstream receipt to ground them on. Detection:
output receipt has `inputs: []`. Fix: halt and surface `SPEC_INCOMPLETE`
rather than inventing inputs."

**Minimum:** two named failure modes per module. One behavioral, one
structural. Each needs all three components: name, signal, fix.

---

### Pattern 4 — Output contracts beat output descriptions

State the exact structure, paths, and required fields. Add a worked example.
The agent pattern-matches against the example, not an abstraction.

**Bad:** "Produce a receipt in the receipts directory."

**Good:**
```
Receipt path: .wabblespec/receipts/{module}-receipt.md
Required fields: module, layer, runtime, inputs (list), outputs (list),
  confidence (0.0–1.0), not_tested (list, never empty).

Example not_tested entry:
  "Whether the upstream receipt was written in this session or carried
  over from a prior session — provenance is not checked."
```

**Rule:** the output contract must be inline in the SKILL.md core. "See
references/format.md" alone is not a contract — it is a deferral.

---

### Pattern 5 — Token density: every line must earn its place

For each paragraph, ask: if I delete this, does the downstream output get
measurably worse? If no, delete it. Verbose modules produce verbose agents.
Token cost compounds across every invocation.

**Anti-pattern:** sections that restate the module name or layer before
explaining what the module does. Cut straight to the action.

**Hard limit:** 500 lines per SKILL.md. Material beyond 500 lines belongs
in `references/` with explicit load-on-demand instructions in the core.

---

### Pattern 6 — Provider-neutral capability language (I6)

No tool names, no model names, no runtime-specific env vars in the core
SKILL.md. Violations break portability across runtime environments and
violate invariant I6.

**Bad:** "Use the Bash tool to run `pytest`."

**Good:** "Run the test suite."

**Exception:** when the user explicitly targets a runtime, runtime-specific
details belong in a clearly marked optional section, not the core.

---

## Seven Named Regression Checks

These patterns cause SKILL.md quality to degrade across iterations.
The module auditor checks all seven as binary flags. A regression in a
passing module is reported but does not fail the audit — it is a signal
for the next improvement cycle.

| # | Name | Detection signal | Fix |
|---|---|---|---|
| 1 | **Decorative "why"** | Sentence after an imperative can be deleted without changing the imperative's meaning ("This ensures..." / "This helps...") | Cut the decorative sentence or fold the why into the rule |
| 2 | **Example missing input** | Example shows only one side — no before/after pairing, no input form present | Add the input that produces the example output |
| 3 | **Output contract deferred** | Core says "see references/X" with no inline Good/Bad/Discriminator triple | Move the three-part contract inline; keep only long catalogs in references |
| 4 | **Runtime-specific unconditional** | Tool name, binary, or env var appears in core without an "if using X" guard | Move to clearly marked optional section; violates I6 |
| 5 | **No pruning over 500 lines** | `wc -l SKILL.md` > 500 | After every addition, delete the weakest existing sentence in the same section |
| 6 | **State assumption** | Phrases like "as we discussed," "from last session," "you already know" | Modules are stateless at invocation; any needed state must be read from a file |
| 7 | **Phantom instruction** | A directive both correct and incorrect outputs satisfy; wrong output still follows the rule | Replace with the specific constraint that separates good from bad |

---

## Quality Floor vs. Pattern Quality

The quality floor gates (`.wabblespec/engine/shared/references/quality-floor-gates.md`) are
binary: pass or fail. They check structure and minimum content.

The six patterns above are scored 1–5 by the module auditor. The floor
requires `floor_score >= 4.0` across Patterns 1, 3, and 4.

Passing the quality floor gates is necessary but not sufficient. A module
can pass Gate 1 and Gate 2 but still score 3.0 on named failure modes.
The pattern score is the deeper signal.

---

## Applying This Contract

When writing a new module SKILL.md:

1. Write the purpose statement, activation, input contract, output contract,
   named failure modes, and not-tested declaration (required structure).
2. Check each section against Patterns 1–4. Every abstract rule needs an
   example. Every output section needs an inline contract.
3. Apply Pattern 5: read the whole SKILL.md and delete every line that does
   not change what the agent produces.
4. Apply Pattern 6: grep for tool names and env vars. Move or remove.
5. Run `.wabblespec/engine/shared/agents/module-auditor.md` before marking `build_complete: true`.
