# Revision Guidance Standards

Revision guidance is required when verdict = REVISE. It is instruction to the originating module — Grader writes it, does not act on it.

## Quality standard

Revision guidance must be specific and actionable. The originating module must be able to act on the guidance without asking for clarification.

**Not guidance:**
- "Improve the error handling"
- "The output needs work on criterion 3"
- "Consider the Adversary concerns more carefully"

**Guidance:**
- "The error handler at line 34 exits with code 0 on missing input. Criterion 2 requires exit code 1. Revise: update the error handler to call `sys.exit(1)` on FileNotFoundError."
- "Criterion 4 requires that the response include a `retry_after` header on 429 responses. Current output does not include this header. Add it."
- "Adversary identified that the cache key does not include the user's locale. Criterion 6 requires locale-aware responses. Revise: include locale in the cache key."

## Required components

Each piece of revision guidance must include:

1. **What is wrong** — which criterion or requirement is not met, or which Adversary concern applies
2. **Where it is wrong** — specific location in the output (line, function, section, field)
3. **What to change** — concrete action the originating module takes to fix it

If guidance cannot be written to this standard, the issue is likely beyond REVISE — escalate instead.

## Multiple REVISE points

When multiple issues exist, write separate guidance for each. Number them. The originating module addresses each in turn.

## Guidance is not implementation

Grader writes guidance; Grader does not implement it. Do not produce corrected code, corrected artifacts, or alternative implementations. Return the guidance to the originating module.
