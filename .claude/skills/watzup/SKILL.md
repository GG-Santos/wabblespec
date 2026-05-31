---
name: watzup
description: Display the current WabbleSpec session state, active wave, pending receipts, and recent git commits as a human-readable handoff report.
---

# watzup

Runs `watzup-scan.py` and presents the result. Read-only -- makes no changes to session state, wave plans, or receipts. Does not interpret or act on the state it reports; it only displays it.

## When to use

- `/watzup` is invoked to check current session status
- Resuming a session after a break and needing a quick orientation
- User asks "what's going on?" or "where are we?" in a WabbleSpec session

## When NOT to use

- User wants to actually advance the wave -- use `/execute` or continue the Executor
- User wants to see full receipt contents -- read the specific receipt file directly
- User wants to change session state -- use `session-state.py set` directly

## How to do it

Run:

```bash
python .wabblespec/engine/shared/scripts/watzup-scan.py
```

Present the output verbatim. The output contains four sections:
- **Current Session**: session ID, active module, enforcement state, required receipts
- **Active Wave**: wave plan generation timestamp, task card path, recent checkpoints
- **Pending Receipts**: last 10 receipts with type, status, and timestamp
- **Recent Commits**: last 8 git commits and working tree status

If `watzup-scan.py` fails (script not found, no .wabblespec directory), surface the error clearly. Do not attempt to reconstruct the report manually.

For JSON output (useful for programmatic use):

```bash
python .wabblespec/engine/shared/scripts/watzup-scan.py --json
```
