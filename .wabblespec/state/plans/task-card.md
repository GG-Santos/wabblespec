# Task Card

**goal:** queue-orchestrator.py exists and provides populate/ready/advance subcommands that enable parallel wave task execution from a Claude Code Executor.
**target:** Library-Package
**complexity:** Medium
**change_class:** ADDITIVE
**locked_at:** 2026-05-28T16:00:00Z
**session_id:** queue-orchestrator-20260528

## Non-Goals

- SKILL.md modifications
- Changes to wave-queue.py
- Actual Agent tool invocation

## Assumptions

- queue-orchestrator.py delegates all queue writes to wave-queue.py
- ready output is consumed by Executor to fire parallel Agent calls

## Acceptance Criteria

### AC1 — ready outputs parallel manifest

Given a queue exists with wave 1 all PASS and wave 2 PENDING
When ready is run
Then outputs JSON array of wave-2 tasks ready to claim in parallel

### AC2 — advance reports wave status

Given queue exists with all waves PASS
When advance is run
Then exits 0 and prints DONE; exits 1 when work remains; exits 2 on any FAIL

### AC3 — populate wraps wave-queue

Given a wave plan exists
When populate is run with session-id and wave-plan path
Then queue is created with correct task count and all tasks PENDING

### AC4 — script parses cleanly

Given no queue exists
When queue-orchestrator.py --help is run
Then exits 0 with all subcommands listed; no import errors
