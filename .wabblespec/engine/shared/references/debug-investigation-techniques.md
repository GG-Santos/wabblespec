# Debug Investigation Techniques

Eight techniques for systematic bug investigation. Select based on the situation. Techniques compose — use multiple together when needed.

Sourced from: `research/ref-eval/get-shit-done-redux.md` → B15.

---

## Technique Selection Guide

| Situation | Technique |
|---|---|
| Large codebase, long execution path, many possible failure points | Binary search |
| Confused about what's happening, mental model doesn't match reality | Rubber duck |
| Large change set, "it worked before this change" | Delta debugging |
| Complex system, many moving parts, unclear which part fails | Minimal reproduction |
| Know the desired output, don't know why it isn't happening | Working backwards |
| Something used to work and now doesn't | Differential debugging |
| Need visibility before making changes | Observability first (always) |
| Paths, URLs, keys, or identifiers constructed from variables | Follow the indirection |
| Multiple plausible causes that need differentiating | Strong inference (one experiment, multiple hypotheses) |

Observability first applies before any other technique. Always add visibility before changing behavior.

---

## 1 — Observability First

Add visibility before making any change. Never change behavior to observe behavior.

Strategic logging at key transition points:
```
[component/function]: Input received: {input}
[component/function]: State before: {state}
[component/function]: Result: {result}
```

Add assertion checks at boundaries:
```
assert expected_type(value), f"Expected X but got {type(value)}"
```

For shell scripts and Python hooks: emit diagnostic output to stderr before the main operation. This survives even if the main operation crashes.

**Workflow:** Add logging → run → observe output → form hypothesis → then make changes.

---

## 2 — Binary Search / Divide and Conquer

For large codebases, long execution paths, or many possible failure points.

1. Identify boundaries: where does the system work, where does it fail?
2. Add a check or log at the midpoint of the suspect range
3. Determine which half contains the problem
4. Repeat on the failing half

**Example for a WabbleSpec hook chain:**
- Hook fires: YES
- Hook reads session file: YES
- Hook parses JSON: NO → bug is in JSON parsing, not hook firing

4–5 binary search steps eliminate 90% of the code.

---

## 3 — Rubber Duck Debugging

For when you are stuck, confused, or your mental model contradicts what you observe.

Write or say aloud:
1. "The system should do X"
2. "Instead it does Y"
3. "I think this is because Z"
4. "The execution path is: A → B → C → D"
5. "I have verified that..." (list everything tested)
6. "I am assuming that..." (list assumptions not yet tested)

Mid-explanation you often spot the bug: "Wait, I never verified that B returns what I think it does."

---

## 4 — Delta Debugging

For when "it worked before this change" is the symptom. Binary search over the change space.

**Over commits (use git bisect):**
```bash
git bisect start
git bisect bad              # current commit is broken
git bisect good <hash>      # this commit worked
# git checks out the middle commit — test, then:
git bisect bad|good
# repeat until the breaking commit is identified
```

100 commits between working and broken → ~7 bisect steps to find the exact breaking commit.

**Over code (systematic elimination):**
1. Identify what changed between the working and broken state
2. Split the differences in half; apply only half to the known-good state
3. If broken: bug is in the applied half. If not: bug is in the other half.
4. Repeat until the minimal change set that causes the failure is found.

---

## 5 — Minimal Reproduction

For complex systems with many moving parts.

Strip away everything until the smallest possible input or code path reproduces the bug.

1. Start with the failing case
2. Remove one component, dependency, or parameter
3. Test: does it still reproduce? YES → keep removed. NO → put it back.
4. Repeat until bare minimum
5. The bug is now visible in the stripped-down case

A minimal reproduction also reveals which code path is being exercised, which narrows the search.

---

## 6 — Working Backwards

For when you know the correct output but not why you're not getting it.

1. Define the desired output precisely — not "it should work" but "it should return {x: 1, status: 'pass'}"
2. What function or step produces this output?
3. Test that function with the expected input — does it produce the correct output?
   - YES: bug is upstream (wrong input is reaching this step)
   - NO: bug is here
4. Repeat backwards through the call chain
5. Find the divergence point (where expected vs. actual first differ)

---

## 7 — Differential Debugging

For when something used to work and now doesn't, or works in one environment but not another.

**Time-based (worked, now doesn't):**
- What changed in code since it worked?
- What changed in the environment (Python version, package versions)?
- What changed in configuration or state files?
- What changed in the input data?

**Environment-based (works locally, fails in CI or in the hook):**
- Environment variables present vs. absent
- Working directory differences
- File permissions
- Path resolution differences (absolute vs. relative)

List all differences between the working and broken state. Test each difference in isolation. Find which difference causes the failure.

---

## 8 — Follow the Indirection

For bugs where paths, URLs, keys, or identifiers are constructed from variables.

The trap: you read code that builds a path like `os.path.join(config_dir, 'hooks')` and assume it is correct because it looks reasonable. But you never verified the constructed path matches where another part of the system actually writes or reads.

**How:**
1. Find the code that **produces** the value (writer, installer, creator)
2. Find the code that **consumes** the value (reader, checker, validator)
3. Trace the actual resolved value in both — do they agree on the same path/key/identifier?
4. Check every variable in the construction — where does each come from? What is its actual value at runtime?

**Common indirection bugs in WabbleSpec:**
- A hook writes to `~/.claude/hooks/` but the validator checks `~/.claude/get-shit-done/hooks/`
- A receipt path is constructed from `session_id` which has an unexpected prefix
- A template placeholder (`{{GSD_VERSION}}`) was not substituted in all code paths
- An environment variable resolves differently inside vs. outside a hook subprocess

**Discipline:** Never assume a constructed path is correct. Resolve it to its actual value and verify the other side agrees.

---

## Strong Inference (Multiple Hypotheses)

When multiple plausible causes exist, design one experiment that differentiates between them.

Instead of testing one hypothesis, then another, then another — add instrumentation at the decision points that would distinguish between all candidates simultaneously.

**Example:** A hook is not injecting `additionalContext`. Four possible causes: hook not registered, hook exits early, metrics file is stale, session_id is missing.

One experiment: add logging at each branch point in the hook. Run once. Observe which branch was taken. Outcome eliminates three of the four hypotheses in one step.
