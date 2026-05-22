# Output Quality - Patterns for High Downstream Output

This reference is the heart of v4's quality improvement. It codifies the
prose patterns that produce **high-quality outputs at invocation time**,
not just SKILL.md files that read well.

Load this whenever you're drafting a non-Vibe SKILL.md. (Vibe Mode's
reference already incorporates the key patterns inline.)

## The two-level model

Every SKILL.md is judged at two levels:

1. **Artifact level.** Does the SKILL.md read clearly, validate, lint
   clean, parse correctly?
2. **Output level.** When an agent later reads this SKILL.md and is
   asked to do the work, what does the agent actually produce?

The artifact level is necessary but not sufficient. A SKILL.md can
score 5/5 on structure and produce mediocre invocation outputs. v4's
goal is to maximize the output level. The patterns below are the ones
empirically observed to land well across strong instruction-following
models.

## The six patterns

### Pattern 1 - Concrete examples beat abstract rules

**When to use.** Any time you'd write a rule with a generic
abstraction ("be thorough," "use good judgment," "follow best
practices").

**What it produces.** Outputs that hit the spirit of the rule, not
just its letter. The model generalizes from an example pattern
better than from a rule statement.

**Bad -> good:**

> BAD "Always include specific evidence in your reviews."
>
> GOOD "When you flag something, point to the line and say what's
> wrong. So instead of *'this could fail,'* write *'line 42, the
> retry loop has no max - a failing dependency would spin
> forever.'*"

**Why this is better at invocation time.** The first version makes
the agent assert that evidence is present. The second teaches the
*shape* of well-grounded evidence. The agent's downstream output
will mirror the example pattern, even on cases the example didn't
cover.

### Pattern 2 - Theory-of-mind framing beats command framing

**When to use.** Any time you'd write a command ("ALWAYS do X,"
"NEVER do Y"). All-caps shouting is a red flag.

**What it produces.** Outputs that adapt the rule's spirit to
context, instead of applying the rule mechanically and missing the
point.

**Bad -> good:**

> BAD "ALWAYS verify the user has consented before processing their
> data. NEVER skip this check."
>
> GOOD "Before processing personal data, you want to know the user
> said yes - not in a previous session, in this one. So if you're
> uncertain, ask. If they're impatient with the question, that's a
> useful signal - it means they're treating consent as a formality,
> which is the exact moment you most want it on record."

**Why this is better.** The first form gets rote compliance - the
agent looks for a literal "consent" string and proceeds. The second
form puts the agent in the right mental model: it's collecting
evidence of intent, and impatience is itself evidence to weigh.
Outputs reflect the framing.

### Pattern 3 - Named failure modes beat generic warnings

**When to use.** When discussing what could go wrong. Generic
warnings ("be careful," "watch out for issues") are no-ops.

**What it produces.** Outputs that proactively avoid the named
failure, even in situations the SKILL.md author didn't anticipate.

**Bad -> good:**

> BAD "Be careful when summarizing creative writing - it's easy to
> get wrong."
>
> GOOD "Summarizing creative writing has two specific failure modes.
> First, *plot-burying*: you reduce a 200-page novel to its
> mechanics and lose what made it worth reading. Second, *theme
> imputation*: you announce themes the author didn't intend
> because you confused 'recurring image' with 'central concern.'
> The fix for both is the same - say what the book is *about* at
> least once in the author's own register, even if you also
> describe what happens."

**Why this is better.** The agent now has named patterns to detect
and named fixes to deploy. The output won't just be cautious; it'll
be specifically cautious about the right things.

### Pattern 4 - Output contracts beat output descriptions

**When to use.** When telling the agent what to produce.

**What it produces.** Outputs that match the expected shape because
the agent had a pattern to match against.

**Bad -> good:**

> BAD "Produce a summary of the document with key points and a brief
> conclusion."
>
> GOOD "Produce three sections:
>
> 1. **One-paragraph summary** (3-5 sentences, no bullets) covering
>    *what the document is about*, not what it says.
> 2. **Key points** (3-5 bullets, each <= 20 words) - what a reader
>    would need to know to discuss the document.
> 3. **One-sentence verdict** answering: *would I read this if I
>    weren't being paid to?*
>
> Example output for a paper on epoxy chemistry:
>
> > **Summary.** A 2024 review of bio-derived epoxy resins, focused
> > on three feedstocks (lignin, vegetable oil, vanillin) and their
> > mechanical-performance tradeoffs vs petroleum baselines...
> >
> > **Key points.**
> > - Lignin-based resins match tensile strength but miss impact
> >   resistance by ~30%.
> > [etc.]
> >
> > **Verdict.** Worth it for materials engineers; skim-only for
> > anyone else."

**Why this is better.** The first version describes a target shape
abstractly. The second shows the agent what the target looks like in
context, with section names, length budgets, and a worked example.
Downstream outputs match this template closely.

### Pattern 5 - Token-density calibration

**When to use.** Always. Every section's length should match the
information density it carries.

**What it produces.** Skills that are *exactly* as long as they
need to be. Models read every line; verbose skills produce verbose
agents.

**Diagnostic.** For each paragraph in your SKILL.md, ask: *if I
delete this, does the downstream output get measurably worse?* If
no, delete. If yes, the paragraph stays but should be as compact as
its information density allows.

A specific anti-pattern: **scope creep prose**. Phrases like *"this
skill is designed to provide comprehensive assistance with a wide
range of tasks involving..."* carry zero invocation-time value. They
read like marketing. Compress: *"this skill does X."*

**Why this matters.** Every word in the SKILL.md is part of the
agent's context window at invocation time. Token cost compounds with
every use. A 2x longer SKILL.md is 2x more expensive to run, 1000x
over.

### Pattern 6 - Provider-neutral capability language

**When to use.** Any time you'd reference a specific tool, CLI,
binary, or environment variable.

**What it produces.** Skills that work on any agent runtime, not
just the one the author tested on.

**Bad -> good:**

> BAD "Use the `bash` tool to run `pytest`."
>
> GOOD "Run the test suite (typically `pytest`, or whatever the
> project uses)."

**Why this matters.** The first version assumes a specific tool name
(`bash`) that exists on one runtime but not every runtime. The second
describes the capability and lets the runtime decide how to execute
it. Agents on different runtimes will find the right local equivalent.

**Exception.** When the user explicitly targets a runtime, the
runtime-specific patterns are appropriate - but they belong in a clearly
marked optional section or handoff note, not in the core SKILL.md.

## The output quality contract

Workshop and Production SKILL.md files should include an explicit
**Output quality contract** section that names:

1. What good output looks like (with an example).
2. What bad output looks like (with an example of the failure mode).
3. The discriminator - what specifically separates them.

Example contract for a "code review comments" skill:

> ## Output quality contract
>
> **Good output.** Each comment names a specific line, identifies a
> specific failure mode, and proposes a specific fix or asks a
> specific question.
>
> Example: *"L42: the retry loop has no max iteration. If
> `fetch_token` fails consistently, this will spin forever. Either
> cap retries (e.g. 3 attempts) or add a backoff that surfaces
> after N seconds."*
>
> **Bad output.** A comment that flags a generic concern without
> location or fix.
>
> Example: *"This could fail."*
>
> **The discriminator.** Good comments answer three questions: where,
> what, and what to do. Bad comments answer none of them. If a
> comment doesn't answer at least two, rewrite or delete it.

The contract is for the agent at invocation time. It's also for the
human reviewer and for `agents/grader.md` - both use the contract as a
grading rubric.

## Phase 1 safety and factuality contract

For high-risk, dual-use, current-fact, or impossible-concept domains, the
output contract also needs risk lanes. Put them in the produced SKILL.md, not
only in a reference.

**Good output.** The skill says what help is allowed, what help is disallowed,
how to redirect after a refusal, and how to handle unstable facts.

Example for a crypto skill:

> **Allowed help.** Explain wallet safety, scam signals, tokenomics, and
> high-level smart-contract risks.
> **Disallowed help.** Do not provide guaranteed returns, manipulation,
> wallet theft, phishing, laundering, or exploit instructions.
> **Current facts.** Prices, regulations, hacks, and token claims need current
> verification. Without tools, mark them `needs verification` or state an
> `as of` date.
> **Safe redirect.** Convert unsafe requests into risk analysis, scam checks,
> or secure-wallet steps.

**Bad output.** A skill that says "be safe" or "avoid hallucination" but gives
no allowed lane, no disallowed lane, no redirect, and no current-fact rule.

**The discriminator.** A reviewer should be able to point to the line that
blocks unsafe compliance and the line that prevents over-refusal of allowed
work.

## Verifying output quality via `agents/grader.md`

The v4 verification step for non-Vibe skills is the grader subagent, not
a standalone script. The grader implements the rubric for the six
patterns above - that's why scoring is consistent between the theory
here and the operational scoring there.

To run trigger evaluation:

```bash
python -m scripts.run_eval \
  --eval-set <path-to-evals.json> \
  --skill-path <path-to-skill> \
  --provider <provider> \
  --model <model-id>
```

For downstream-output grading, run a representative task with the produced
SKILL.md, save the transcript and output paths, then pass those artifacts to
`agents/grader.md` with `eval_target=skill_creation`. The grader scores task
fit, substance, format adherence, failure-mode avoidance, and coupling
cleanliness; record those results in `grading.json`.

The grader's threshold is strict: pattern average >= 4.5 to pass.
Failing patterns point to specific text in the produced SKILL.md that
violates the pattern - these are the lines to rewrite. See
`agents/grader.md` for the full sub-criterion rubric.

Use provider defaults from `config/providers.yaml`, or pass one explicit
`--provider` / `--model` pair when a runtime needs to be pinned.

## Anti-patterns the lint catches

`scripts/lint_prompts.py` v4 detects (and warns on):

- All-caps shouting (`ALWAYS`, `NEVER`, `MUST`) - see Pattern 2.
- Vendor names in skill content - see Pattern 6.
- Hard-coded tool names (`bash`, `view`, `str_replace`, etc.) without
  a capability framing - see Pattern 6.
- Scope-creep prose (matching "comprehensive," "wide range,"
  "designed to provide," "various aspects of") - see Pattern 5.
- Abstract rule phrases without examples ("best practices," "as
  appropriate," "where relevant") - see Pattern 1.

Each warning includes the line number and a pointer to the relevant
pattern. The lint is a guide, not a gate - there are legitimate uses
of every flagged term - but every warning is a place to look.

## The two principles in one sentence

> The voice and structure of the SKILL.md become the voice and
> structure of the agent's outputs at invocation time. Optimize the
> SKILL.md for what comes *after*, not what the SKILL.md *is*.

That's it. The six patterns are the operationalization.

