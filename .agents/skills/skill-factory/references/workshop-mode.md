# Workshop Mode

Workshop is the pedagogical loop: draft, run the draft on a few realistic
test prompts, the user reviews the outputs, you improve, repeat. The user
is the most important grader and stays on the critical path.

This is the right mode for most skills that aren't Vibe-shaped and aren't
full plugins. Use it when the user has a clear domain and time to iterate.

## The loop

```
draft -> test -> review -> improve -> (repeat) -> package
```

1. **Capture intent.** What should the skill do, when should it trigger,
   what does success look like? Extract from conversation history first;
   don't re-interview if the workflow is already there.
2. **Interview where needed.** Edge cases, input/output formats, example
   files, dependencies. Wait to write test prompts until you've ironed
   this out. Come prepared.
3. **Draft the SKILL.md.** Use the writing guidance below.
4. **Write 2-3 realistic test prompts.** Not abstract - the kind of thing
   a real user types, with file paths and personal framing. Show them to
   the user: *"Here are a few test cases. Do these look right, or do you
   want more?"*
5. **Run the test prompts.** Subagents in parallel where available;
   sequentially otherwise. Save outputs into `<skill>-workspace/iteration-N/`.
6. **Generate the eval-viewer before reviewing the outputs yourself.** The
   user is a better grader than you are. Get the outputs in front of them
   first. Invocation form and flag guidance live in *The eval-viewer
   ritual* below.
7. **Read `feedback.json` when they're done.** It's `feedback-1.1` shape
   (see `references/schemas.md`). Read `status` and `severity` per run, not
   just the `feedback` text - a `blocked` run with empty text is louder
   than a paragraph on an `approved` one. Per-file notes live in
   `file_reviews[].feedback`; that's where the actionable detail usually
   is. Skip anything `qa_warnings` flagged.
8. **Improve the skill.** Generalize from feedback (see the next section).
9. **Repeat from step 5.** Continue until one of these is true:
   - All `feedback.json` runs are `approved` with `severity: none`
   - Two consecutive iterations produce < 0.05 pass-rate delta and no `blocked` runs remain
   - The user explicitly says stop
   When the loop exits without full approval, name the open issues in the handoff.
10. **Package.** `python -m scripts.package_skill <path>` -> installable
    `.skill` bundle.

## How to write a Workshop-mode SKILL.md

Same warmth rules as Vibe Mode - write in a voice the agent will adopt at
invocation. But Workshop skills have more rigor, so the anatomy expands:

```
---
name: kebab-case
description: One-or-two-sentence trigger-focused description.
---

# Skill Name

Greeting paragraph in the skill's voice.

## What this skill does
2-4 sentences, concrete.

## When to use / when not to use
Two short bullet lists. The "not to use" matters: it prevents misfires.

## Inputs
What the skill expects to receive.

## How to do it
The actual instructions. 30-150 lines depending on domain. Use examples
inline. Explain *why* alongside *what*.

## Output contract
What the agent produces. Format, length, anything required.

## A note on common failure modes
1-3 known pitfalls with the fix for each.
```

Keep the whole SKILL.md under 500 lines. Move long reference material to
`references/` and tell the agent when to load it.

## The improvement step is the heart of the loop

This is where the skill actually gets better. A few principles:

### Generalize from the feedback

The user's feedback is about three specific examples. The skill needs to
work on a million. If the feedback is "the chart is missing axis labels,"
don't add a rule that says "always add axis labels" - figure out what
general failure pattern that points to. Probably: the skill needs to make
the agent think about *presentation completeness*, not just data
correctness. So the fix is a sentence in the "how to do it" section about
checking that the output is self-readable, with axis labels named as one
example of what that means.

### Keep the prompt lean

Read the agent transcripts, not just the final outputs. If the skill is
making the agent waste time on unproductive steps (loading references it
doesn't need, writing throwaway helper code), delete the parts of the
skill that cause that. Lean prompts beat verbose ones every time.

### Explain the *why*

Today's models have good theory of mind. If you tell them why something
matters, they generalize correctly. If you give them a rigid rule, they
follow it stupidly. Write instructions as if explaining the task to a
smart new hire, not configuring a regex.

A yellow flag: if you find yourself writing ALWAYS or NEVER in caps, or
using progressively rigid structures, try reframing and explaining the
reasoning. Almost always it's stronger.

### Look for repeated work across test cases

Read the transcripts from each test run. If all three independently wrote
similar helper scripts or took the same multi-step approach to something,
that's a strong signal: bundle the script. Write it once, put it in
`scripts/`, tell the skill to use it. Save every future invocation from
reinventing the wheel.

## Test-case writing

Save to `evals/evals.json`. Don't write assertions on the first pass -
just the prompts:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's actual task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

What makes a good test prompt: it's specific, it has context, it sounds
like a real human in a real situation.

Bad: *"summarize this PDF."*

Good: *"hey, my advisor sent over a draft chapter (it's in my downloads,
'thesis_v3 (annotated).pdf') and asked for a paragraph summary I can send
to the committee - keep it under 150 words, formal-ish but not stuffy."*

For non-trivial skills, include should-trigger, should-not-trigger, edge,
and at least one adversarial case (a prompt designed to break the skill in
a domain-relevant way). The subjective creative skills are exempt - they
get human review instead.

## Running the test prompts

Two patterns, depending on runtime:

**With subagents.** For each test case, spawn two
subagents in the same turn - one with the skill, one without (baseline).
Launch all of them at once.

**Without subagents.** You are simultaneously the skill and the evaluator,
which collapses the with-skill vs baseline distinction. Compensate with
these four rules:

1. Read the SKILL.md fully before processing *any* prompt. Then clear your working summary of it — process each prompt as if the skill is the only instruction in context.
2. For each test prompt: produce output, then immediately grade it against the eval assertions before reading the next prompt. Don't batch — serial grading prevents earlier outputs from anchoring later ones.
3. Run 2× the normal number of test prompts to compensate for no baseline. Flag any output where you notice yourself improvising beyond what the SKILL.md says — that improvisation is what a skill-free baseline would have done.
4. Present results inline: prompt → output → assertion grades, one case at a time. Skip the benchmark tab in the eval-viewer (no comparative data); use it for qualitative review only.

This is less rigorous than subagent runs, and the human review is load-bearing. Don't skip the eval-viewer step.

Either way, save outputs under
`<skill-name>-workspace/iteration-<N>/eval-<id>/`.

## The eval-viewer ritual

Once the runs are done: **generate the eval-viewer before doing your own
review**. The user is a better grader than you are, and "generate the
viewer first" is a hard-won lesson that prevents you from rubber-stamping
your own work.

```bash
python <skill-factory-path>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "<skill-name>" \
  --benchmark <workspace>/iteration-N/benchmark.json
```

On iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`
so the viewer can show last iteration's outputs and feedback as context.
Skip `--benchmark` if you didn't aggregate one this iteration; skip
`--skill-name` and the viewer falls back to the workspace directory name.

In environments without a display, add
`--static <output.html>` to write a standalone HTML file instead of
starting the server. Then proffer a link the user can click.

What the user sees, briefly: each run shows the prompt, the produced
output files (rendered inline where possible), and - when present -
formal grades, previous output, and previous feedback. Per run they pick
a **status** (`approved` / `needs_changes` / `blocked`), a **severity**
(`none` / `minor` / `major` / `critical`), can leave free-text feedback,
and can flag individual output files. A Benchmark tab shows the
quantitative comparison if you passed `--benchmark`. When they're done
they hit **Finalize**, which writes `feedback.json` to the workspace.

When you read `feedback.json`, treat `status` and `severity` as the
headline signal (see step 7 and `references/schemas.md`). The free-text
`feedback` field is one input of several, not the whole story.

## Verification gates in Workshop Mode

Lighter than Production:

| Gate | Workshop | Implemented by |
|---|---|---|
| `quick_validate` | run before handoff | `scripts/quick_validate.py` |
| `syntax_check scripts/` | run if scripts exist | `scripts/syntax_check.py` |
| `lint_prompts` | run and surface to user | `scripts/lint_prompts.py` |
| `review_skill` | run on the final output skill | `scripts/review_skill.py` |
| `package_skill --dry-run` | on user request | `scripts/package_skill.py` |
| Eval set run | mandatory each iteration | `scripts/run_eval.py` |
| Benchmark aggregation | run if more than one iteration | `scripts/aggregate_benchmark.py` |
| Output-quality grading (v4) | run on the final iteration | spawn `agents/grader.md` with `eval_target=skill_creation` |
| Adversarial test cases | required for non-subjective skills | adversarial eval cases through `run_eval` |
| Production Shipping Checklist | not required | - |

In Workshop, output-quality grading is on the final iteration, not every
iteration. Pattern scoring is expensive (the grader spawns the
invocation simulation); use it as a checkpoint, not a per-step gate.
When the grader fails (overall score < 4.5), the loop continues - the
failing pattern is now the highest-priority axis for the next iteration.

## Workshop output

The skill directory, plus:

- `evals/evals.json` - final test cases and assertions.
- `<skill-name>-workspace/` - iteration history.
- Whatever scripts, references, or examples emerged.

When handing off:

> The skill is at `<path>`. We did N iterations; the final test pass rate
> was X/Y. Open questions: [if any]. Known gaps: [if any]. Run
> `python -m scripts.package_skill <path>` when you want a `.skill`
> bundle for installation.

## Headless-runtime notes

- Subagents work, so the main workflow goes parallel.
- No browser/display, so generate the eval-viewer with
  `--static <output_path>` and proffer the file link.
- The user finalizes via the **Finalize** button, which in `--static`
  mode downloads `feedback.json` (the server-side autosave isn't
  available without the running server). After they download it, copy
  it into the workspace directory before iterating.
- The eval-viewer is easy to forget in headless runs. Do not forget to
  generate it. The whole loop depends on it.

## No-subagent runtime notes

- No subagents -> run test prompts yourself, sequentially.
- No display -> present results inline. Show prompt + output for each.
- Save artifact files to disk and tell the user the path so they can
  download. Ask for inline feedback: *"How does this look?"*
- Skip the benchmarking - without baselines it's not informative.
- Skip blind comparison - needs subagents.
- The iteration loop is the same; you just do more of it yourself.

