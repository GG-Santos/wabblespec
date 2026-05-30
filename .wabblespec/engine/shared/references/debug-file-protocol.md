# Debug File Protocol

Defines the 5-section structure, section mutability rules, and status lifecycle for debug session files at `.wabblespec/state/debug/{slug}.md`.

Sourced from: `research/ref-eval/get-shit-done-redux.md` → B15.

---

## File Structure

```markdown
---
status: gathering | investigating | fixing | verifying | awaiting_human_verify | resolved
trigger: "[verbatim user input — never paraphrased]"
created: [ISO-8601]
updated: [ISO-8601]
---

## Current Focus
<!-- OVERWRITE on each update — reflects what is happening RIGHT NOW -->

hypothesis: [current theory]
test: [how testing it]
expecting: [what result means]
next_action: [immediate next step — must be concrete and actionable]

## Symptoms
<!-- Written during gathering, then IMMUTABLE -->

expected: [what should happen]
actual: [what actually happens]
errors: [exact error messages — verbatim, not paraphrased]
reproduction: [how to trigger — exact steps]
started: [when it broke / always been broken]

## Eliminated
<!-- APPEND only — prevents re-investigating dead ends -->

- hypothesis: [theory that was wrong]
  evidence: [what disproved it]
  timestamp: [when eliminated]

## Evidence
<!-- APPEND only — facts discovered during investigation -->

- timestamp: [when found]
  checked: [what was examined]
  found: [what was observed — specific, not paraphrased]
  implication: [what this means for the investigation]

## Resolution
<!-- OVERWRITE as understanding evolves — empty until root cause confirmed -->

root_cause: [empty until confirmed]
fix: [empty until applied]
verification: [empty until verified]
files_changed: []
```

---

## Section Update Rules

| Section | Rule | When |
|---|---|---|
| Frontmatter.status | OVERWRITE | Each phase transition |
| Frontmatter.updated | OVERWRITE | Every file update |
| Current Focus | OVERWRITE | Before every action |
| Symptoms | IMMUTABLE | After gathering is complete |
| Eliminated | APPEND | When a hypothesis is disproved |
| Evidence | APPEND | After each finding |
| Resolution | OVERWRITE | As understanding evolves |

**Critical rule:** Update the file BEFORE taking action, not after. If context resets mid-action, the file must show what was about to happen. This is the only way the session can be resumed accurately after a context reset.

---

## next_action Format

`next_action` must be concrete and immediately executable. It tells a fresh agent exactly what to do next without re-reading all evidence.

**Bad:** "continue investigating", "look at the code", "investigate further"

**Good:** "Add logging at line 47 of wabblespec-session-start.js to observe the flag file write result before the file is renamed", "Run `python .wabblespec/engine/shared/scripts/receipt-writer.py --type guard --dry-run` to observe the JSON output shape", "Read `.wabblespec/engine/hooks/wabblespec-prompt-guard.js` fully to find where `additionalContext` is constructed"

---

## Status Lifecycle

```
gathering → investigating → fixing → verifying → awaiting_human_verify → resolved
                 ↑              ↓         ↓                  ↓
                 └──────────────┴─────────┴──────────────────┘
                          (if verification fails or user reports issue)
```

---

## Resume Protocol

When reading an existing debug file after a context reset:

1. Parse frontmatter status → know current phase
2. Read Current Focus → know exactly what was happening and what to do next
3. Read Eliminated → know what NOT to retry
4. Read Evidence → know what has been discovered
5. Resume from `next_action` in Current Focus

The file is the debugging brain. A well-maintained file makes context resets recoverable without losing any investigation progress.

---

## Knowledge Base Format

Resolved sessions are archived to `.wabblespec/state/debug/knowledge-base.md`. Each entry:

```markdown
## {slug} — {one-line description of the bug}
- **Date:** {ISO date}
- **Error patterns:** {comma-separated keywords from errors + actual fields}
- **Root cause:** {Resolution.root_cause}
- **Fix:** {Resolution.fix}
- **Files changed:** {Resolution.files_changed as comma list}
---
```

Matching at investigation start: extract nouns and error substrings from symptoms. Scan entries for 2+ keyword overlap (case-insensitive). A match is a hypothesis candidate, not a confirmed diagnosis.
