---
name: diagnose
description: Structured debugging protocol for hard bugs and performance regressions encountered during product-space development. Use when a bug is confirmed but the cause is unknown, a performance regression appeared, or a prior fix attempt failed.
---

# Diagnose

You apply a disciplined debugging protocol to find the cause of a confirmed bug or regression. You do not implement the fix — you identify the root cause, write a regression test, and hand off to Executor. Every phase gate must pass before proceeding to the next phase.

## What this skill does

Builds a reproducible feedback loop, reproduces the failure, generates ranked hypotheses, instruments to confirm the cause, and writes a regression test. Does not modify production code — diagnosis only.

Not guaranteed: Diagnosis identifies the cause and surfaces architectural gaps; the fix decision belongs to the caller (Executor or user).

## When to use

- User reports a confirmed bug with observed symptoms
- A performance regression appeared between two known states
- A prior fix attempt failed and the cause is still unknown
- Explicit `/diagnose` command

## When NOT to use

- The bug is already understood and only needs a fix — skip to Executor
- The task is exploratory (trying to find bugs that might exist) — use gateway-security or code-review instead
- The system is working correctly but the user dislikes the behavior — that is a feature request, not a bug

---

## Phase 1 — Build a feedback loop

This is the skill. Everything else follows from having a fast, deterministic, agent-runnable pass/fail signal. Spend disproportionate effort here before proceeding.

Try strategies in order, stopping at the first one that produces a reliable signal:

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **HTTP/CLI script** — curl or CLI invocation against a running dev server, diffing output against a known-good snapshot.
3. **Headless browser script** — drives the UI and asserts on DOM, console, or network.
4. **Replay a captured trace** — save a real request/payload/event log to disk and replay through the code path in isolation.
5. **Throwaway harness** — spin up a minimal subset of the system with mocked deps that exercises the bug code path.
6. **Property/fuzz loop** — if the bug is "sometimes wrong output," run a loop of varied inputs and look for the failure mode.
7. **Bisection harness** — if the bug appeared between two known states (commit, version, dataset), automate boot-at-state-X and check.
8. **Differential loop** — run the same input through old-version vs new-version and diff outputs.
9. **HITL script** — last resort; see `scripts/hitl-loop.template.sh`. Use when a human must click or interact.

Iterate on the loop: make it faster, make the signal sharper, make it deterministic. A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower.

If no loop can be built: stop, say so explicitly, list what was tried, and ask the user for access to a reproducing environment or captured artifact (HAR file, log dump, screen recording with timestamps).

**Do not proceed to Phase 2 without a loop you believe in.**

## Phase 2 — Reproduce

Run the loop. Confirm:
- [ ] The failure matches the symptom the user described — not a different nearby failure
- [ ] The failure is reproducible across multiple runs (or at a high-enough rate for non-deterministic bugs)
- [ ] The exact symptom is captured (error message, wrong output, slow timing) for later verification

## Phase 3 — Hypothesize

Generate 3–5 ranked hypotheses before testing any. Each must be falsifiable:

Format: "If `X` is the cause, then changing `Y` will make the bug disappear / changing `Z` will make it worse."

Show the ranked list before testing. The user often has domain knowledge that re-ranks instantly or knows already-ruled-out hypotheses. Don't block on a response — proceed with your ranking if the user is not reachable.

## Phase 4 — Instrument

Each probe maps to a specific prediction from Phase 3. Change one variable at a time.

Tool preference:
1. Debugger or REPL inspection (one breakpoint beats ten logs)
2. Targeted logs at boundaries that distinguish hypotheses
3. Never "log everything and grep"

**Tag every debug log** with a unique prefix, e.g., `[DEBUG-a4f2]`. All debug instrumentation is cleaned up by grepping the prefix at Phase 6. Untagged debug logs survive and create permanent clutter.

For performance regressions: establish a baseline measurement first (timing harness, profiler, query plan), then bisect. Measure first, fix second.

## Phase 5 — Fix and regression test

Write the regression test before the fix — but only at a correct seam.

A correct seam exercises the real bug pattern as it occurs at the call site. If the only available seam is too shallow (unit test when the bug needs multiple callers), a test there gives false confidence.

If no correct seam exists: note it. The architecture is preventing the bug from being locked down. Flag for the architecture improvement skill after the fix.

If a correct seam exists:
1. Turn the minimised repro into a failing test at that seam
2. Watch it fail
3. Apply the fix
4. Watch it pass
5. Re-run the Phase 1 loop against the original (un-minimised) scenario

## Phase 6 — Cleanup

Required before declaring done:
- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of a correct seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (grep the prefix)
- [ ] Throwaway prototypes deleted
- [ ] The correct hypothesis is stated in the commit/PR message

Then ask: what would have prevented this bug? If the answer involves architectural change (no good test seam, tangled callers), surface to the architecture skill with the specifics.

## Outputs

- Root cause statement (which hypothesis was confirmed and how)
- Regression test at the correct seam (or documented gap if no seam exists)
- Cleanup confirmation (all `[DEBUG-...]` instrumentation removed)
- Optional: architectural gap flag for the architecture improvement skill

## Reference Routing

| Situation | Reference |
|---|---|
| HITL reproduction loop | `scripts/hitl-loop.template.sh` |
