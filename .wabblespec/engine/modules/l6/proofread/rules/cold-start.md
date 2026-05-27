# Cold-Start Behavior — Proofread

Defines what Proofread does when its input documents or rule files are absent.

## Absent: target document

Condition: Proofread invoked with no document specified or document path returns 404.
Detection: File read returns empty or 404.
Action: Surface: "Proofread requires a target document. Specify the file path to proofread."
Do NOT: Proofread the wrong document by inferring from context.

## Absent: rule files

Condition: `rules/consistency.md`, `rules/readability-gates.md`, or `rules/technical-accuracy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md rules for the missing file. Log: "Proofread rule file missing: [path] — using SKILL.md defaults."
Do NOT: Skip the corresponding check. Defaults from SKILL.md are sufficient to run.

## Absent: prior proofread receipt

Condition: No prior proofread receipt for this document.
Detection: Receipt absent.
Action: Treat as first pass — no diff to compute. Produce issues list only.

## Default state on cold start

| Field | Default |
|---|---|
| `passes` | All 3 passes run (consistency, readability, technical accuracy) |
| `diff_required` | false on first pass (no prior state to diff against) |
| `block_threshold` | 0 critical issues — any critical = block delivery |
| `flag_threshold` | 1+ non-critical issues = flag (does not block) |
| `scope` | Full document unless `--section` flag provided |
