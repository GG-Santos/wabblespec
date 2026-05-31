---
name: prototype
description: Builds a throwaway artifact to answer a specific design question about business logic or UI layout before committing to full implementation waves. Use when the question is "does this state model feel right?" or "what should this look like?" and spending a full wave on a wrong answer would be costly.
---

# Prototype

You build a throwaway artifact that answers a specific question. The question determines the shape. You do not build production code — prototypes are deleted or absorbed once the question is answered. All prototype code is explicitly marked throwaway.

## What this skill does

Routes to either LOGIC branch (terminal TUI for state/business-logic questions) or UI branch (multi-variant route for layout/design questions) based on the question being asked. Produces a runnable artifact in one command. Captures the answer in a durable artifact before deletion. Does not produce tests, error handling, or abstractions.

## When to use

- "Does this state machine handle the edge case where X then Y?"
- "What should this page/screen look like?"
- "I want to feel out the API design before writing it."
- User says "prototype this," "let me play with it," or "try a few designs"

## When NOT to use

- The design question is already resolved and only implementation remains — skip to Executor
- The artifact being explored is a full wave in an active task — use Decompose to plan it properly, not this skill
- The user wants to validate that existing code works correctly — use the test skill or Verifier instead

---

## Pick a branch

Identify which question is being answered. If the user is not available to clarify, default to the branch that matches the surrounding code (backend module → LOGIC; page or component → UI) and state the assumption.

- **"Does this logic or state model feel right?"** → LOGIC branch
- **"What should this look like?"** → UI branch

The two branches produce very different artifacts. Getting this wrong wastes the prototype.

---

## LOGIC branch — terminal state explorer

Build a tiny interactive terminal app that lets the user drive a state model by hand.

### Process

1. **State the question** in one paragraph at the top of the prototype file. A prototype that answers the wrong question is waste — make the question explicit.

2. **Pick the language** — use whatever the host project uses.

3. **Isolate the logic** in a pure, portable module behind a small interface:
   - Pure reducer: `(state, action) → state` — for discrete-event state machines
   - State machine: explicit states and transitions — when "which actions are legal" is part of the question
   - Small set of pure functions over a plain data type — for transformations with no implicit state

   Keep it pure: no I/O, no terminal code. The TUI imports it and calls into it.

4. **Build the smallest TUI** that exposes the state. On every keystroke, clear the screen and re-render the full frame:
   - Frame top: current state, pretty-printed (one field per line or formatted JSON)
   - Frame bottom: keyboard shortcuts list (`[a] add item  [d] delete  [q] quit`)
   
   Loop: initialize state → read one keystroke → dispatch to handler → re-render. The full frame fits on one screen.

5. **One command to run** — add a script to the project's existing task runner.

6. **Capture the answer** — when done, write what was learned to a NOTES.md next to the prototype (or to a commit message, ADR, or issue if the user is present).

### Anti-patterns

- Do not add tests — a prototype that needs tests is no longer a prototype
- Do not wire to the real database — use an in-memory store
- Do not blur the logic module and the TUI — if the reducer references console output, it cannot be lifted into production

---

## UI branch — multi-variant route

Generate several radically different UI variations on a single route, switchable from a floating bottom bar.

### Process

1. **State the question and pick N variants** — default to 3. More than 5 stops being radically different.

2. **Generate structurally different variants** — different layout, information hierarchy, and primary affordance. Three slightly-tweaked card grids is not a UI prototype. Hold to the project's existing component library and styling system.

3. **Wire via `?variant=` URL param** — all variants live on the same route (preferred) or a throwaway route named to indicate it is a prototype:

   ```
   const variant = searchParams.get('variant') ?? 'A';
   return variant === 'A' ? <VariantA /> : variant === 'B' ? <VariantB /> : <VariantC />;
   ```

4. **Add a floating switcher** — fixed-position bottom bar with: left arrow / variant label / right arrow. Clicking updates the URL param (use the framework's router). Arrow-key navigation supported. Hidden in production builds — gate on the project's existing environment check (e.g., `process.env.NODE_ENV`) or equivalent.

5. **Hand it over** — surface the URL and variant keys. The user flips through whenever they reach it.

6. **Capture and clean up** — once a variant wins: record which one and why. For an existing route: delete losing variants and the switcher, fold the winner in. For a throwaway route: promote the winner to a real route, delete the throwaway.

## Outputs

- A runnable throwaway artifact (terminal TUI for LOGIC branch, or a variant-switchable route for UI branch)
- A captured answer in a durable form (NOTES.md, commit message, ADR, or issue)
- Deleted prototype files or the winning variant promoted to production code

### Anti-patterns

- Variants that differ only in color or copy — that is a tweak, not a prototype
- Sharing `<Layout>` between variants — each variant should be free to rethink the layout
- Wiring variants to real mutations — prototype reads are fine; point mutations at a stub
- Promoting prototype code directly to production without rewriting — prototype code was written without tests or error handling
