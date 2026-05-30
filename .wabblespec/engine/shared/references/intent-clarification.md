# Intent Clarification Protocol

Reference for use by Recipe and Guard when a user request's ambiguity needs to be scored before routing to a skill or module.

**Source:** Adapted from vibecode-pro-max-kit `process/development-protocols/intent-clarification.md` (supporting-reference, 8/10). Patterns extracted 2026-05-30.

---

## Signal Scoring

Score each binary signal as +1. Sum to get the ambiguity score.

| Signal | Description |
|---|---|
| Ambiguous scope | Request touches multiple modules or targets without naming one |
| No explicit path | No file, module, or skill name mentioned |
| Multiple intents | Request could be a build, fix, refactor, or question |
| First interaction | No established workflow context in current session |

Score thresholds:

| Score | Tier | Action |
|---|---|---|
| 0–1 | Tier 0 | Auto-route silently. No friction added. |
| 2 | Tier 1 | Show routing summary. Wait for confirmation before proceeding. |
| 3+ | Tier 2 | Full clarification checkpoint with multiple-choice questions. |

---

## Auto-Skip Conditions

These force Tier 0 regardless of score:

- User said "go", "continue", "just do it", or a similar continuation phrase
- Mid-execution with an active locked wave plan
- Trivial change (single-file, no schema/auth changes)
- Explicit skill invocation (`/recipe`, `/execute`, `/guard`, etc.)
- Resuming an existing active task session
- Pure information question ("What is X?", "How does Y work?") with an obvious routing target

---

## Tier 0: Silent Auto-Route

Route to the detected skill or module immediately. No user interaction added.

---

## Tier 1: Routing Summary with Confirmation Pause

Present a compact routing summary and wait for the user's next message before proceeding:

```
Routing: [detected intent] → [target skill/module]
Scope: [what I think you want changed]
Plan: [existing task if found, or "new work"]
```

Do NOT auto-proceed after presenting this summary. Wait for the user to confirm or correct. Do NOT say "I'll proceed unless you correct me."

---

## Tier 2: Full Clarification Checkpoint

Pick 2–4 questions from the category menu below. Use multiple-choice format. Wait for answers before routing. Ask at most two rounds of questions; after that, default to the narrowest reasonable research pass.

| Category | Template |
|---|---|
| Scope | "Which areas? [A] just {X} [B] {X} and {Y} [C] the whole {module}" |
| Direction | "Approach? [A] quick fix [B] proper rebuild [C] you decide" |
| Constraints | "Constraints? [A] must not touch {Z} [B] backward compat required [C] none" |
| Acceptance | "Done looks like? [A] receipts pass [B] tests pass [C] deployed" |
| Context | "Related to existing work? [A] yes, {task X} [B] no, fresh [C] not sure" |
| Priority | "Priority? [A] do it now [B] plan it for later [C] just research" |

---

## Autonomy Mode

**Grants autonomy:** Explicit phrases — "you decide", "just do it", "full autonomy", "don't ask".

**Phrase matching rule:** Autonomy phrases must be standalone or sentence-initial. "just do the simple version" is NOT autonomy (descriptive scope specification).

**What autonomy means:** All tiers collapse to Tier 0 for the current task chain. Clarification questions are skipped.

**What autonomy does NOT override:**
- Wave plan review and explicit `/execute` confirmation gate
- Attestation verification mode (irreversible action requiring human sign-off)
- Phase-locked boundaries (cannot skip Guard or Verifier)
- High-risk evidence pack requirements

---

## Light Research Pass (for Tier 1/2)

Before presenting the routing summary or questions, run a lightweight context pass:

Budget: 3–5 file reads, under 30 seconds.

Check:
1. Active task session (`session-state.py show`)
2. Scope.md for boundary keywords matching the request
3. Recent receipts for any in-progress work matching the request
4. If a specific module or file is named, one read of that file

Use the results to populate `{X}`, `{Y}`, `{Z}`, and `{task X}` placeholders in Tier 2 questions. Do not run a full research subagent — this is an orchestrator-level pre-check only.

---

## Intent Revalidation

After research completes, if the request turns out to be fundamentally different from what was assumed, present a Tier 1 routing summary with the updated understanding before proceeding. Do not repeat clarification questions that were already resolved.
