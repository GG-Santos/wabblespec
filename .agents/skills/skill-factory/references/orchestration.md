# Orchestration — Multi-Skill Suites

Suite Mode is the answer to *"can you build me three skills that work
together?"* It exists because neither single-skill mode handles the
problems that come with multiple skills sharing data: schema drift,
versioning, naming collisions, ambiguous activation, and the trust
question of *which skill should answer this prompt*.

Suite Mode always runs **on top of** Production Mode — multi-skill
work has enough moving parts that Workshop's lightness doesn't fit.
Load `production-mode.md` first, then this.

## When you need Suite Mode

The user says one of:

- "Build me skills for X *and* Y *and* Z."
- "I want a suite for [domain]."
- "These three skills should share [thing]."
- "Make a plugin that has multiple skills inside it."

Or the work clearly requires it:

- Two or more skills naturally share the same input schema.
- A skill's output is meant to feed another skill's input.
- Multiple skills should be installable as a single bundle.
- Activation cues overlap and you need disambiguation across skills.

If the user asked for *one* skill and it would be cleaner as two, **say
so before building**. *"I'd suggest splitting this into two skills — one
for parsing the CSV and one for visualizing it, so you can use either
independently. Should I do that?"*

## Suite anatomy

```
my-suite/
├── suite.yaml                # the manifest — see below
├── shared/
│   ├── schemas/              # JSON Schemas used across skills
│   │   ├── account.json
│   │   └── transaction.json
│   ├── references/           # docs all suite members may load
│   └── data/                 # static data (CSVs, lookup tables)
├── skill-one/
│   ├── SKILL.md
│   └── scripts/
├── skill-two/
│   ├── SKILL.md
│   └── scripts/
└── skill-three/
    ├── SKILL.md
    └── scripts/
```

## The suite manifest (`suite.yaml`)

A single file at the suite root declares the members, the shared
artifacts, the handoff edges, and the activation order.

```yaml
suite:
  name: personal-finance-prep
  version: 1.0.0
  description: >-
    Three skills for getting your finances ready for a meeting with a
    professional. Does not give advice; produces material for one.
  members:
    - id: portfolio-summarizer
      path: portfolio-summarizer/
      activates_on: ["my portfolio", "investment summary", "holdings"]
      consumes_schema: shared/schemas/account.json
      produces_schema: shared/schemas/portfolio-summary.json
    - id: tax-prep-organizer
      path: tax-prep-organizer/
      activates_on: ["tax prep", "1099", "deductions list"]
      consumes_schema: shared/schemas/account.json
      produces_schema: shared/schemas/tax-bundle.json
    - id: retirement-projector
      path: retirement-projector/
      activates_on: ["retirement projection", "401k forecast"]
      consumes_schema: shared/schemas/account.json
      produces_schema: shared/schemas/retirement-projection.json
  handoffs:
    - from: portfolio-summarizer
      to: retirement-projector
      via: shared/schemas/portfolio-summary.json
      trigger: "User asks about retirement after a portfolio summary"
  activation_disambiguation:
    when_all_match:
      - "summary" + "tax"
      - prefer: tax-prep-organizer
      - reason: "Tax is the more specific intent"
  safety:
    suite_wide_refusals:
      - "Do not provide personalized financial advice. Skills may
        organize and summarize the user's own data for review by a
        qualified professional."
```

## Suite design rules

### 1. Each member is a complete skill

Every member SKILL.md is self-contained. It can be installed
individually without the others. The suite adds *integration*; it
doesn't fragment the skills' individual coherence.

A member skill shouldn't say *"after running portfolio-summarizer,
do X."* It should say *"if you're given a portfolio-summary.json
that conforms to shared/schemas/portfolio-summary.json, do X."*
The schema is the contract; the suite is the convenience.

### 2. Shared schemas live in `shared/`, not duplicated

If two members need the concept of an `account`, they reference
`shared/schemas/account.json` — they don't each redefine it.

Schemas are versioned. When a schema changes incompatibly, bump the
suite's major version and update every member's reference.
`scripts/check_schema_drift.py` catches missing schema references and
duplicate-name drift:

```bash
python -m scripts.check_schema_drift suite.yaml
```

### 3. Activation must disambiguate cleanly

The hardest suite problem: two skills could plausibly activate on the
same prompt. You handle this in `activation_disambiguation`:

```yaml
activation_disambiguation:
  when_all_match:
    - tokens: ["summary", "tax"]
      prefer: tax-prep-organizer
      reason: "Tax framing is more specific"
    - tokens: ["projection", "tax"]
      prefer: retirement-projector
      reason: "Projection language signals forecasting"
```

Each rule names the keyword set, the preferred member, and a
human-readable reason that appears in the lint report if you turn the
rule off.

When in doubt, the activation engine prefers the **more specific**
member — the one whose `activates_on` list is shorter and whose
description trigger phrases are narrower. Suite Mode generates a
disambiguation matrix automatically (see Verification below).

### 4. Handoff is an opt-in contract, never an opt-out

A handoff says *"this member can pass output to that member, via this
schema, when this condition holds."* It does not say *"this member
must run before that one." A user is allowed to invoke any member
directly.

When member A is *about to* hand off to member B, A's SKILL.md should
tell the agent how to make the handoff explicit to the user: *"You
have a portfolio-summary.json now. If you'd also like a retirement
projection, the `retirement-projector` skill takes this file as input
— want me to run it?"*

Asking is mandatory. Auto-chained suites become impossible to debug.

### 5. Safety is suite-wide and overrides individual skills

`suite.yaml`'s `safety.suite_wide_refusals` cascade to every member.
A finance suite that refuses to give personalized advice means *all*
members refuse, even ones that might individually be tempted (e.g., a
retirement projector that could quietly produce a recommendation).

Member SKILL.md files inherit and may add to suite-wide refusals; they
may not weaken them.

## Building a suite

The flow:

1. **Capture the intent.** What's the domain? How many members? What's
   the shared object?
2. **Identify the shared schema first.** Before writing any SKILL.md,
   write the schemas. The schemas are the contract; the skills are
   implementations against the contract.
3. **Draft member SKILL.md files** in Production Mode, each in
   isolation. Each member should pass `quick_validate` and `lint_prompts`
   independently.
4. **Write `suite.yaml`.** Declare members, handoffs, activation rules.
5. **Run suite-level verification:**

```bash
python -m scripts.suite_validate <suite-root>
```

This (in addition to running individual `quick_validate` on each
member) checks:
   - Schema references in each SKILL.md resolve.
   - Handoff edges reference real members and real schemas.
   - `activates_on` tokens have no unintended overlap (or are covered
     by `activation_disambiguation`).
   - `suite_wide_refusals` are referenced by every member.
   - The plugin manifest (if Full tier) points to existing surface files.

6. **Evaluate as a suite.** Test cases include cross-skill flows:

```json
{
  "id": 14,
  "prompt": "Show me my portfolio and then estimate my retirement.",
  "expected_flow": ["portfolio-summarizer", "retirement-projector"],
  "expected_artifacts": ["portfolio-summary.json", "retirement-projection.json"]
}
```

7. **Package.** A suite packages as one `.skill` bundle by default;
   pass `--per-member` to package individually.

```bash
python -m scripts.package_skill <suite-root> <output-dir>
```

## Disambiguation matrix

After `suite_validate` runs, it writes
`<suite-root>/disambiguation.md` — a human-readable matrix showing
which member would activate on which prompt patterns. Example:

```
                                       portfolio  tax-prep  retire
"summary of my holdings"                  ✓                       
"summary of my taxes"                                ✓
"summary"                                  ?           ?           
                                                                  ←
"forecast my 401k"                                              ✓
"summary and forecast"                     ✓                    ✓
                                                                  ←
```

The `←` markers flag rows where multiple members could activate and no
disambiguation rule applies. Fix these before shipping.

## Cross-skill testing

When evaluating a suite, run two kinds of test:

**Per-member tests** — same as Production Mode, run each member's
eval set against its skill.

**Cross-skill flow tests** — prompts that should trigger more than
one member in sequence. These check:

- The right member activates first.
- It produces a valid intermediate artifact.
- The next member consumes it correctly.
- The user is told about the handoff (not implicitly chained).

Cross-skill tests live in `<suite-root>/evaluations/cross-skill.json`.

## Common suite failure modes

**Schema drift.** Two skills end up using *almost* the same schema
because one was edited and the others weren't. Catch with
`check_schema_drift`. Prevention: edit `shared/schemas/` files only;
treat them as the source of truth.

**Activation overlap.** Two skills compete for the same prompt and the
user gets a different one each time. Catch with the disambiguation
matrix; fix with explicit `activation_disambiguation` rules.

**Implicit chaining.** Member A silently invokes Member B and the user
doesn't realize what happened. Fix: every handoff is asked, not
assumed.

**Suite-wide refusal forgotten.** Member adds a feature that violates
a suite refusal. Catch: `suite_validate` checks every SKILL.md
references the safety section.

**One member rots.** Suites tend to have a "main" skill and 1-2
peripheral ones that drift. Fix: per-member `last_modified` in
`suite.yaml` and a periodic re-eval on the whole suite, not just the
hot member.

## Suite handoff to the user

When the suite is done:

> The suite is at `<path>`. It has N members: [names]. Shared schemas:
> [names]. Handoffs declared: [count]. Disambiguation rules: [count].
> Per-member eval pass rates: [list]. Cross-skill flow tests: X/Y
> passed. Open questions: [if any]. Run
> `python -m scripts.package_skill <path>` to bundle.

This is verbose by design — suites have more moving parts than single
skills and the user needs all of it to feel confident.
