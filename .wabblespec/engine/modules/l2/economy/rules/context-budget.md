# Economy — Context Budget Policy

**Module:** Economy (L2)
**Applies to:** All executor waves, all LLM-guided module calls within a WabbleSpec session.

Context budget is a hard constraint, not a soft guideline. Every policy here is measurable and can be enforced by script or hook.

---

## Policy 1 — Verbose Output Capture

**Threshold:** Any command output exceeding 200 lines must be redirected to a file.

**Rule:**
- Before running commands known to produce verbose output (test runners, build logs, linters, install commands), redirect stdout+stderr to `.wabblespec/captures/<module>-<timestamp>.txt`.
- Cite the capture path in the current module's receipt under `verbose_captures[]`.
- Never paste raw verbose output inline into a receipt or tool call response.

**Enforcement signal:**
- Inline output > 200 lines in a receipt = Economy violation.
- Health check 4.3 reports capture directory file count.

**Format for receipt field:**
```json
"verbose_captures": [
  ".wabblespec/captures/executor-wave2-2026-05-23T10-00-00Z.txt"
]
```

---

## Policy 2 — Exact Error Preservation

**Rule:** Error text is always preserved verbatim. Never summarize, paraphrase, or truncate an error message.

**Applies to:**
- Stack traces from test failures
- Compiler/linter error output
- Hook exit messages
- Schema validation failure details

**Rationale:** Summarized errors hide the line number, the specific assertion, and the actual vs. expected values. These are the three fields a human needs to debug. Lossy error handling costs more tokens to resolve than it saves to capture.

**Receipt field:** Errors go in `errors[]` as exact strings, not prose descriptions.

```json
"errors": [
  "TypeError: Cannot read properties of undefined (reading 'split')\n  at line 47 in src/parser.ts"
]
```

**Exception:** If error output exceeds 500 lines, apply Policy 1 (capture to file) and cite the path. Preserve the first 20 lines and last 20 lines inline.

---

## Policy 3 — Reference Load Budget

**Maximum files per ReferenceLoad call:** 8

**Rule:** A single ReferenceLoad invocation must not load more than 8 files. If the task requires more than 8 reference files, split into sequential ReferenceLoad calls and declare the split in the receipt.

**Rationale:** Loading more than 8 files in a single call produces a context window where the model cannot reliably cite the correct source. The 8-file cap keeps each call verifiable.

**Receipt field:** Each ReferenceLoad call is logged in `reference_loads[]`:

```json
"reference_loads": [
  {
    "call": 1,
    "files": [".wabblespec/engine/shared/references/invariants.md", ".wabblespec/engine/shared/schemas/receipt.base.schema.json"],
    "purpose": "invariant authority + receipt contract"
  }
]
```

---

## Policy 4 — Context Pressure Escalation

When estimated remaining context < 20% of model context window:

1. Complete the current atomic unit (wave, check, schema validation).
2. Write a checkpoint receipt with `status: CHECKPOINT` and field `context_pressure: true`.
3. Stop. Do not begin new work.
4. The next session resumes from the checkpoint receipt.

**No silent continuation past context pressure.** Continuing without a checkpoint receipt loses provenance of what was verified in the current session.

---

## Thresholds Summary

| Policy | Threshold | Action |
|---|---|---|
| Verbose output | > 200 lines | Redirect to capture file |
| Error verbatim | always | Never summarize |
| Error capture | > 500 lines | Capture file + preserve first/last 20 lines |
| Reference load | > 8 files per call | Split into sequential calls |
| Context pressure | < 20% remaining | Checkpoint receipt + stop |
