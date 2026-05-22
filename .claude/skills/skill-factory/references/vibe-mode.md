# Vibe Mode

You picked Vibe because the work is creative, subjective, tiny, or just
needs to be drafted before the user knows what to refine. Welcome. This
reference exists because Vibe Mode is where Skill Factory historically
*lost* to earlier draft flows that produced better child skills by writing
in a warmer voice. Vibe Mode v3 is built
to close that gap.

## What Vibe Mode produces

One `SKILL.md`. That's the whole deliverable.

Optional, only if 2-3 examples genuinely clarify the skill better than
prose: an `examples/` directory with example input/output pairs.

That's it. No `scripts/`, no `evaluations/`, no `agents/`, no
`schemas/`, no `hooks/`. If you're tempted to add one, ask whether the
user would notice. Usually no.

## The Vibe Mode loop

Three steps, total.

1. **One clarifying question or zero.** If the request is ambiguous in
   a way that prevents drafting (genre, length, audience, register),
   ask one short question. Otherwise just draft. Asking three questions
   to a hobbyist about their houseplant skill is not careful — it's rude.
2. **Draft the SKILL.md.** Use the writing rules below.
3. **Hand it back.** Tell them where the file is, name the single most
   important assumption you made, and invite iteration. Don't run gates.
   Don't write a verification report.

## How to write a Vibe-mode SKILL.md

Three rules that matter more than anything else:

### 1. Write in the user's voice

The child skill's prose becomes part of the agent's invocation context
later. A warm child skill produces warm output. A clinical child skill
produces clinical output. So when you're writing the SKILL.md, write it
as if you, the parent author, are explaining to a friend (the agent)
how to do something for someone they care about (the user).

Use the user's own words from the request where you can. If they said
"chill," use "chill." If they said "no corporate fluff," put that in
the SKILL.md verbatim. The skill will sound like them because it *is*
them.

### 2. Replace rules with examples

In Vibe-mode skills, every rule should arrive *with* an example, or
preferably *as* an example. Don't write:

> The output should be warm and use the user's name.

Write:

> So if Sara says she's been overwatering, a good reply starts
> something like: "Oh, Sara — that sounds frustrating. Let me look at
> what your plants would actually like..."

Examples are also shorter than rules once you account for what the rule
would have to specify. A two-line example replaces a paragraph of
specification.

### 3. No all-caps shouting

ALWAYS, NEVER, MUST in capitals are an admission you didn't trust the
agent. The agent is smart and reads everything. If a thing is
important, explain why. If you can't explain why, it isn't actually
important.

The one exception: a safety boundary. Even then, prefer "we don't do X
here, because Y" to "NEVER DO X."

## Vibe Mode anatomy

A Vibe-mode SKILL.md, in order:

```
---
name: kebab-case-name
description: One-sentence description that includes when it should
  trigger. Friendly tone. Concrete trigger phrases.
---

# Skill Name

One-paragraph greeting that explains what this skill is for, in the
voice the skill itself will use.

## What this skill does

Two to four sentences. Concrete. Examples-first.

## How to do it

The actual instructions, written as guidance to a friend. 5-15
sentences usually does it. Include 1-3 inline examples.

## A note on [edge case the user will hit]

One or two sentences acknowledging the most likely failure mode and
what to do about it.
```

That's the whole structure. If it's much longer than 60-80 lines,
you're either over-engineering or this isn't really a Vibe-mode skill.

## Worked examples

### Example A — Houseplant conversation partner

> **User:** make me a skill that talks to me as if i'm a houseplant.

Draft (28 lines):

```markdown
---
name: houseplant-mode
description: Talk to the user as if they're a houseplant — gentle,
  affirming, occasionally remarking on light or water. Use when the
  user wants a relaxed, low-stakes conversational mode.
---

# Houseplant Mode

This skill is for those days when the user wants to be talked *to*
the way they'd talk to a quiet plant on a windowsill. Soft, attentive,
unhurried. No advice unless asked.

## What this skill does

Treats the user as a beloved houseplant the agent is checking in on.
Affirms small things. Notices weather and light. Avoids therapeutic
framing — this isn't a counseling skill, it's a vibe.

## How to do it

Open with something gentle, like noticing the day. "Good morning. The
light is soft today, isn't it." Pay attention to what the user says,
and reflect it back in plant-adjacent terms: rest, water, light, time.
Don't fix anything unless they ask. Don't psychoanalyze. If they share
hard news, sit with it: "That sounds heavy. You don't have to do
anything with it right now."

If the user says they want to switch to a normal conversation, drop
the mode immediately and reply as you usually would.

## A note on tone drift

It's tempting to lean into the plant metaphor (photosynthesis,
chlorophyll). Resist this — the metaphor works when it's quiet, not
when it's literal. The user is a houseplant *in spirit*. Mostly,
they're a person being treated kindly.
```

Why this beats what a clinical Vibe Mode would write: it uses the
user's framing ("talks to me as if i'm a houseplant"), it gives the
agent permission to drop the mode on cue, and the failure-mode note is
specific (metaphor literalism) rather than abstract.

### Example B — CSS color converter

> **User:** quick skill to convert hex / rgb / hsl / oklch back and forth.

Draft (32 lines):

```markdown
---
name: css-color-convert
description: Convert CSS color values between hex, rgb, hsl, and
  oklch notation. Use when the user pastes a color and wants it in a
  different format, or when they ask for the equivalent of a color in
  another space.
---

# CSS Color Convert

Quick utility for moving CSS colors between hex, rgb, hsl, and oklch.

## What this skill does

Takes a color in any of the four formats and returns the same color
in the other three. Preserves alpha when present.

## How to do it

Parse the input format from its syntax: `#` → hex, `rgb(` / `rgba(`
→ rgb, `hsl(` / `hsla(` → hsl, `oklch(` → oklch. Convert through a
linear-sRGB intermediate when crossing between sRGB-based formats
(hex/rgb/hsl) and oklch.

Output format: a four-line block.

```
hex:   #FF8800
rgb:   rgb(255, 136, 0)
hsl:   hsl(32, 100%, 50%)
oklch: oklch(0.745 0.187 51)
```

Round oklch chroma to 3 decimal places, hue to whole degrees. Round
hsl percentages to whole numbers.

## A note on gamut

oklch can describe colors that don't fit in sRGB. When that happens,
the hex/rgb/hsl row should be the clipped sRGB approximation, with a
parenthetical: `(clipped from oklch oklch(...))`.
```

Why this is a Vibe-mode skill rather than a Workshop or Production
one: the entire spec is one function with well-defined math. There's
nothing to iterate on with a human, and writing a `scripts/convert.py`
to do it would be 4× the work for no quality gain.

### Example C — Git commit haiku

> **User:** turn git diffs into tiny poems please

Draft (24 lines):

```markdown
---
name: git-poem
description: Turn a git diff into a tiny three-line poem describing what
  changed. Use when the user pipes a diff in and wants a poetic
  commit message, or for whimsical changelogs.
---

# Git Poem

A small ritual: every diff deserves a moment of reflection. This
skill writes that reflection as a tiny poem.

## What this skill does

Reads a git diff and produces a tiny poem in three lines.
The poem should describe the *change*, not the file. Prefer
imagery and verbs over file paths.

## How to do it

Look at what was added, what was removed, and what was reorganized.
Distill it to a verb and an image. For a bug fix, maybe water finding
a crack. For a refactor, leaves rearranging. For a delete, dusk.

Count syllables. 5-7-5 is firm; 4-7-6 is not a haiku, it's a glitch.

Example:

```
diff: changes to auth.py — removed plaintext password storage,
      added bcrypt hashing

haiku:
  Plain words turned to salt
  passwords cross the dark river
  no one reads them now
```

## A note on diffs that aren't poetic

Some diffs are just `console.log("test")` removed. That's fine —
write the haiku about the act of clearing debris. "Footprints brushed
from sand / the test that was here is gone / nothing left to prove."
```

Why this works: the rules are stated in service of the *feel*, not
the format. The examples are doing most of the teaching.

## What Vibe Mode explicitly does not do

It does not:

- Run `quick_validate` or any other gate. (The lint warnings on a
  30-line creative skill are noise.)
- Generate `evaluations/eval-set.json`. (Subjective skills have no
  objective grading.)
- Add adversarial test cases by default. (The houseplant skill does
  not need an injection-resistance test.)
- Write a "Verification performed" report. (There was no verification.)
- Refuse to ship because something is missing from the Production
  Shipping Checklist. (That checklist doesn't apply.)
- Add scripts for taste. (No `scripts/score_haiku.py`.)

It does:

- Escalate to Workshop or Production if the draft turns out to be
  safety-critical, plugin-shaped, or processing untrusted input.
- Refuse the same things every mode refuses (see the core SKILL.md
  safety section).

## Handing it back

Three lines is enough:

> Here's the draft at `houseplant-mode/SKILL.md`. I assumed gentle
> affirmation rather than satire — say the word if you want it sharper.
> Try it and tell me what to change.

If you escalated out of Vibe mid-flight, name the reason in one
sentence and continue in the new mode. Follow the mid-session transition
protocol in `SKILL.md` under "Mid-session mode transitions" — it specifies
what to preserve, what to regenerate, and which gates to add.
